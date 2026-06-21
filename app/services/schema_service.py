from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from app.schemas.database_schema import ColumnSchema, DatabaseSchemaResponse, TableSchema
from app.utils.database import engine


def get_database_schema(db_engine: Engine = engine) -> DatabaseSchemaResponse:
    inspector = inspect(db_engine)
    schema: DatabaseSchemaResponse = {}

    for table_name in inspector.get_table_names():
        columns = [
            ColumnSchema(
                name=column["name"],
                type=str(column["type"]),
                sample_values=_get_sample_values(
                    db_engine=db_engine,
                    table_name=table_name,
                    column_name=column["name"],
                ),
            )
            for column in inspector.get_columns(table_name)
        ]
        schema[table_name] = TableSchema(
            columns=columns,
            foreign_keys=_get_foreign_keys(inspector=inspector, table_name=table_name),
        )

    return schema


def _get_sample_values(
    db_engine: Engine,
    table_name: str,
    column_name: str,
    sample_size: int = 3,
) -> list[str | int | float | None]:
    safe_table = table_name.replace('"', '""')
    safe_column = column_name.replace('"', '""')
    query = text(
        f'SELECT DISTINCT "{safe_column}" FROM "{safe_table}" '
        f'WHERE "{safe_column}" IS NOT NULL LIMIT :sample_size'
    )

    try:
        with db_engine.connect() as connection:
            values = connection.execute(query, {"sample_size": sample_size}).scalars().all()
    except Exception:
        return []

    return [_json_safe_value(value) for value in values]


def _get_foreign_keys(inspector, table_name: str) -> list[dict[str, str | None]]:
    foreign_keys: list[dict[str, str | None]] = []

    for foreign_key in inspector.get_foreign_keys(table_name):
        constrained_columns = foreign_key.get("constrained_columns") or []
        referred_columns = foreign_key.get("referred_columns") or []

        for index, constrained_column in enumerate(constrained_columns):
            foreign_keys.append(
                {
                    "column": constrained_column,
                    "referred_table": foreign_key.get("referred_table"),
                    "referred_column": referred_columns[index] if index < len(referred_columns) else None,
                }
            )

    return foreign_keys


def _json_safe_value(value):
    if hasattr(value, "item"):
        return value.item()
    return value
