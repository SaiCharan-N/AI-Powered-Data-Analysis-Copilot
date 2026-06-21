from fastapi import APIRouter

from app.schemas.database_schema import DatabaseSchemaResponse
from app.services.schema_service import get_database_schema

router = APIRouter()


@router.get("/schema", response_model=DatabaseSchemaResponse)
def read_schema() -> DatabaseSchemaResponse:
    return get_database_schema()
