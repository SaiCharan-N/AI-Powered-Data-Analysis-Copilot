import logging
import re
import time
from typing import Any

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.services.chart_service import recommend_visualization
from app.services.insight_service import (
    InsightGenerationError,
    generate_fallback_insights,
    generate_insights,
)
from app.services.llm_service import LLMConfigurationError, is_groq_configured
from app.services.ml_service import enrich_dataframe_with_ml
from app.utils.database import engine

logger = logging.getLogger(__name__)

DISALLOWED_SQL_PATTERN = re.compile(
    r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|TRUNCATE|PRAGMA|CREATE|ATTACH|DETACH|VACUUM|REPLACE)\b",
    re.IGNORECASE,
)
LIMIT_PATTERN = re.compile(r"\bLIMIT\b", re.IGNORECASE)


class QueryExecutionError(RuntimeError):
    """Raised when a SQL query is unsafe or cannot be executed."""


def execute_read_only_query(sql: str, question: str | None = None) -> dict[str, Any]:
    safe_sql = prepare_read_only_sql(sql)
    logger.info("Executing read-only SQL query.")

    try:
        dataframe = _read_sql_with_timeout(safe_sql)
    except QueryExecutionError:
        raise
    except SQLAlchemyError as exc:
        raise QueryExecutionError(f"SQLite execution failed: {exc}") from exc
    except Exception as exc:
        raise QueryExecutionError(f"Query execution failed: {exc}") from exc

    visualization = recommend_visualization(dataframe)
    dataframe, ml_insights = enrich_dataframe_with_ml(dataframe)
    insights = _generate_result_insights(
        question=question or "Summarize the query result.",
        dataframe=dataframe,
        visualization=visualization,
        ml_insights=ml_insights,
    )
    dataframe = dataframe.where(pd.notnull(dataframe), None)
    rows = dataframe.to_dict(orient="records")

    return {
        "sql": safe_sql,
        "columns": [str(column) for column in dataframe.columns],
        "row_count": len(rows),
        "rows": rows,
        "visualization": visualization,
        "ml_insights": ml_insights,
        "insights": insights,
    }


def prepare_read_only_sql(sql: str) -> str:
    normalized_sql = normalize_sql(sql)
    validate_read_only_sql(normalized_sql)
    return enforce_limit(normalized_sql)


def normalize_sql(sql: str) -> str:
    cleaned = sql.strip()
    cleaned = re.sub(r"^```(?:sql)?", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    return cleaned.rstrip(";").strip()


def validate_read_only_sql(sql: str) -> None:
    if not sql:
        raise QueryExecutionError("SQL query is empty.")

    if not sql.lstrip().upper().startswith("SELECT"):
        raise QueryExecutionError("Only SELECT queries are allowed.")

    if DISALLOWED_SQL_PATTERN.search(sql):
        raise QueryExecutionError("SQL query contains a blocked statement.")

    if _has_multiple_statements(sql):
        raise QueryExecutionError("Multiple SQL statements are not allowed.")


def enforce_limit(sql: str) -> str:
    if LIMIT_PATTERN.search(sql):
        return sql

    return f"SELECT * FROM ({sql}) AS limited_query LIMIT {settings.sql_query_max_rows}"


def validate_sql_executes(sql: str) -> None:
    safe_sql = prepare_read_only_sql(sql)
    validation_sql = f"SELECT * FROM ({safe_sql}) AS generated_query LIMIT 1"

    try:
        with engine.connect() as connection:
            transaction = connection.begin()
            try:
                connection.execute(text(validation_sql))
            finally:
                transaction.rollback()
    except SQLAlchemyError as exc:
        raise QueryExecutionError(f"SQLite execution failed: {exc}") from exc


def _read_sql_with_timeout(sql: str) -> pd.DataFrame:
    start_time = time.monotonic()

    with engine.connect() as connection:
        raw_connection = _get_raw_sqlite_connection(connection.connection)

        if hasattr(raw_connection, "set_progress_handler"):
            raw_connection.set_progress_handler(
                lambda: int(time.monotonic() - start_time > settings.sql_query_timeout_seconds),
                1000,
            )

        try:
            return pd.read_sql_query(sql=text(sql), con=connection)
        finally:
            if hasattr(raw_connection, "set_progress_handler"):
                raw_connection.set_progress_handler(None, 0)


def _get_raw_sqlite_connection(connection: Any) -> Any:
    return getattr(connection, "driver_connection", connection)


def _generate_result_insights(
    question: str,
    dataframe: pd.DataFrame,
    visualization: dict[str, Any],
    ml_insights: dict[str, Any],
) -> str:
    if not is_groq_configured():
        logger.info("Using fallback insights because GROQ_API_KEY is not configured.")
        return generate_fallback_insights(
            dataframe=dataframe,
            visualization=visualization,
            ml_insights=ml_insights,
        )

    try:
        return generate_insights(
            question=question,
            dataframe=dataframe,
            visualization=visualization,
            ml_insights=ml_insights,
        )
    except LLMConfigurationError:
        logger.info("Using fallback insights because GROQ_API_KEY is not configured.")
    except InsightGenerationError as exc:
        logger.warning("Using fallback insights after narration failure. error=%s", exc)
    except Exception as exc:
        logger.exception("Using fallback insights after unexpected narration error. error=%s", exc)

    return generate_fallback_insights(
        dataframe=dataframe,
        visualization=visualization,
        ml_insights=ml_insights,
    )


def _has_multiple_statements(sql: str) -> bool:
    in_single_quote = False
    in_double_quote = False

    for index, char in enumerate(sql):
        previous_char = sql[index - 1] if index > 0 else ""

        if char == "'" and not in_double_quote and previous_char != "\\":
            in_single_quote = not in_single_quote
        elif char == '"' and not in_single_quote and previous_char != "\\":
            in_double_quote = not in_double_quote
        elif char == ";" and not in_single_quote and not in_double_quote:
            return True

    return False
