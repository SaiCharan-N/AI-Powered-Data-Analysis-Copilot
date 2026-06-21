import json
import logging
from typing import Any

import pandas as pd
from langchain_core.messages import HumanMessage

from app.services.llm_service import LLMConfigurationError, get_groq_llm

logger = logging.getLogger(__name__)

MAX_SAMPLE_ROWS = 5
MAX_SUMMARY_COLUMNS = 12
MAX_INSIGHT_WORDS = 90


class InsightGenerationError(RuntimeError):
    """Raised when insight narration cannot be generated."""


def generate_insights(
    question: str,
    dataframe: pd.DataFrame,
    visualization: dict[str, Any] | None,
    ml_insights: dict[str, Any] | None,
) -> str:
    if dataframe is None or dataframe.empty:
        return "No rows were returned, so there is not enough data to summarize."

    prompt = _build_insight_prompt(
        question=question,
        result_summary=_build_result_summary(dataframe),
        visualization=visualization or {},
        ml_insights=ml_insights or {},
        sample_rows=_sample_rows(dataframe),
    )

    try:
        logger.info("Generating business insight narration.")
        response = get_groq_llm().invoke([HumanMessage(content=prompt)])
    except LLMConfigurationError:
        raise
    except Exception as exc:
        raise InsightGenerationError(f"Insight generation failed: {exc}") from exc

    return _clean_insights(str(response.content))


def generate_fallback_insights(
    dataframe: pd.DataFrame,
    visualization: dict[str, Any] | None,
    ml_insights: dict[str, Any] | None,
) -> str:
    if dataframe is None or dataframe.empty:
        return "No rows were returned, so there is not enough data to summarize."

    row_count = len(dataframe.index)
    column_count = len(dataframe.columns)
    chart_type = (visualization or {}).get("chart_type", "table")
    anomaly_count = (
        (ml_insights or {})
        .get("anomaly_detection", {})
        .get("outlier_count", 0)
    )
    cluster_count = (
        (ml_insights or {})
        .get("clustering", {})
        .get("cluster_count")
    )
    forecast = (ml_insights or {}).get("forecasting", {})

    parts = [
        f"The query returned {row_count} rows across {column_count} columns, with a {chart_type} view recommended."
    ]

    if anomaly_count:
        parts.append(f"Anomaly detection flagged {anomaly_count} potential outlier records.")

    if cluster_count:
        parts.append(f"Clustering identified {cluster_count} distinct groups in the numeric data.")

    if forecast.get("enabled"):
        parts.append(f"A {forecast.get('horizon', 0)}-period forecast was generated for {forecast.get('y_axis')}.")

    return " ".join(parts)


def _build_insight_prompt(
    question: str,
    result_summary: dict[str, Any],
    visualization: dict[str, Any],
    ml_insights: dict[str, Any],
    sample_rows: list[dict[str, Any]],
) -> str:
    payload = {
        "question": question,
        "result_summary": result_summary,
        "visualization": visualization,
        "ml_insights": ml_insights,
        "sample_rows": sample_rows,
    }

    return f"""
You are an AI data analysis copilot writing concise business insights.

Use only the information in the JSON payload. Do not invent causes, dates, trends, anomalies, clusters, or business context that is not supported by the data.

Style rules:
- 2 to 4 sentences maximum.
- Professional, concise, and non-technical.
- Mention trends only when the summary or sample rows support them.
- Mention anomalies only when anomaly_detection.enabled is true.
- Mention clusters only when clustering.enabled is true.
- Do not mention model names, algorithms, SQL, JSON, or implementation details.
- Return plain text only.

JSON payload:
{json.dumps(payload, default=str, indent=2)}
""".strip()


def _build_result_summary(dataframe: pd.DataFrame) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "row_count": int(len(dataframe.index)),
        "column_count": int(len(dataframe.columns)),
        "columns": [str(column) for column in dataframe.columns[:MAX_SUMMARY_COLUMNS]],
        "numeric_columns": {},
    }

    numeric_dataframe = dataframe.select_dtypes(include="number")
    for column in numeric_dataframe.columns[:MAX_SUMMARY_COLUMNS]:
        series = numeric_dataframe[column].dropna()
        if series.empty:
            continue

        summary["numeric_columns"][str(column)] = {
            "min": _json_safe_number(series.min()),
            "max": _json_safe_number(series.max()),
            "mean": _json_safe_number(series.mean()),
        }

    return summary


def _sample_rows(dataframe: pd.DataFrame) -> list[dict[str, Any]]:
    safe_dataframe = dataframe.head(MAX_SAMPLE_ROWS).where(pd.notnull(dataframe.head(MAX_SAMPLE_ROWS)), None)
    return safe_dataframe.to_dict(orient="records")


def _clean_insights(text: str) -> str:
    cleaned = text.strip().strip('"').strip("'")
    cleaned = cleaned.replace("```", "").strip()

    words = cleaned.split()
    if len(words) > MAX_INSIGHT_WORDS:
        cleaned = " ".join(words[:MAX_INSIGHT_WORDS]).rstrip(".,;:") + "."

    return cleaned or "No concise insight could be generated for this result."


def _json_safe_number(value: Any) -> int | float | None:
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        value = value.item()

    if isinstance(value, float):
        return round(value, 4)

    return value
