from datetime import datetime

from pydantic import BaseModel


class CsvUploadResponse(BaseModel):
    dataset_id: int
    original_filename: str
    table_name: str
    rows: int
    columns: int
    column_names: list[str]
    created_at: datetime
