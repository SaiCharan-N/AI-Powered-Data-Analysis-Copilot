from pydantic import BaseModel, Field


class ColumnSchema(BaseModel):
    name: str
    type: str
    sample_values: list[str | int | float | None] = Field(default_factory=list)


class TableSchema(BaseModel):
    columns: list[ColumnSchema]
    foreign_keys: list[dict[str, str | None]] = Field(default_factory=list)


DatabaseSchemaResponse = dict[str, TableSchema]
