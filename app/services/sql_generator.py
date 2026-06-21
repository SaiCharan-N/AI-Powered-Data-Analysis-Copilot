import logging

from langchain_core.messages import HumanMessage

from app.config import settings
from app.schemas.database_schema import DatabaseSchemaResponse
from app.services.llm_service import get_groq_llm
from app.services.query_executor import (
    QueryExecutionError,
    normalize_sql,
    validate_read_only_sql,
    validate_sql_executes,
)
from app.utils.prompt_builder import build_sql_generation_prompt

logger = logging.getLogger(__name__)


class SQLGenerationError(RuntimeError):
    """Raised when SQL cannot be generated or validated."""


def generate_sql_from_question(
    question: str,
    schema: DatabaseSchemaResponse,
) -> str:
    if not schema:
        raise SQLGenerationError("Database schema is empty. Upload a CSV before generating SQL.")

    llm = get_groq_llm()
    previous_sql: str | None = None
    execution_error: str | None = None

    for attempt in range(1, settings.sql_generation_max_retries + 1):
        prompt = build_sql_generation_prompt(
            question=question,
            schema=schema,
            previous_sql=previous_sql,
            execution_error=execution_error,
        )

        logger.info("Generating SQL with Groq. attempt=%s", attempt)
        response = llm.invoke([HumanMessage(content=prompt)])
        sql = normalize_sql(str(response.content))

        try:
            _validate_read_only_sql(sql)
            _validate_sql_executes(sql)
            logger.info("Generated SQL validated successfully. attempt=%s", attempt)
            return sql
        except SQLGenerationError as exc:
            previous_sql = sql
            execution_error = str(exc)
            logger.warning(
                "Generated SQL failed validation. attempt=%s error=%s",
                attempt,
                execution_error,
            )

    raise SQLGenerationError("Failed to generate valid SQLite SQL after retries.")


def _validate_read_only_sql(sql: str) -> None:
    try:
        validate_read_only_sql(sql)
    except QueryExecutionError as exc:
        raise SQLGenerationError(str(exc)) from exc


def _validate_sql_executes(sql: str) -> None:
    try:
        validate_sql_executes(sql)
    except QueryExecutionError as exc:
        raise SQLGenerationError(str(exc)) from exc
