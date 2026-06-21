import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.query import QueryGenerateRequest, QueryGenerateResponse, QueryRunResponse
from app.services.llm_service import LLMConfigurationError
from app.services.query_executor import QueryExecutionError, execute_read_only_query
from app.services.schema_service import get_database_schema
from app.services.sql_generator import SQLGenerationError, generate_sql_from_question

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/query/generate", response_model=QueryGenerateResponse)
def generate_query(request: QueryGenerateRequest) -> QueryGenerateResponse:
    schema = get_database_schema()

    try:
        sql = generate_sql_from_question(question=request.question, schema=schema)
    except LLMConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except SQLGenerationError as exc:
        logger.warning("SQL generation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected SQL generation error.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected SQL generation error.",
        ) from exc

    return QueryGenerateResponse(sql=sql)


@router.post("/query/run", response_model=QueryRunResponse)
def run_query(request: QueryGenerateRequest) -> QueryRunResponse:
    schema = get_database_schema()

    try:
        sql = generate_sql_from_question(question=request.question, schema=schema)
        result = execute_read_only_query(sql, question=request.question)
    except LLMConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except SQLGenerationError as exc:
        logger.warning("SQL generation failed before execution: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except QueryExecutionError as exc:
        logger.warning("SQL execution failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected query run error.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected query run error.",
        ) from exc

    return QueryRunResponse(**result)
