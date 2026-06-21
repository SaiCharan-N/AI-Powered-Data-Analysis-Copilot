from uuid import uuid4

import pandas as pd
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.models.dataset import Dataset
from app.schemas.csv import CsvUploadResponse
from app.utils.database import engine
from app.utils.file_utils import ensure_directory, safe_stem


class CsvIngestionError(ValueError):
    """Raised when a CSV upload cannot be validated or stored."""


async def ingest_csv_upload(file: UploadFile, db: Session) -> CsvUploadResponse:
    if not file.filename:
        raise CsvIngestionError("A CSV file name is required.")

    if not file.filename.lower().endswith(".csv"):
        raise CsvIngestionError("Only .csv files are supported.")

    upload_bytes = await file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(upload_bytes) > max_bytes:
        raise CsvIngestionError(f"File exceeds the {settings.max_upload_mb} MB upload limit.")

    upload_dir = ensure_directory(settings.upload_dir)
    unique_id = uuid4().hex
    original_stem = safe_stem(file.filename)
    stored_filename = f"{original_stem}_{unique_id}.csv"
    stored_path = upload_dir / stored_filename
    stored_path.write_bytes(upload_bytes)

    try:
        dataframe = pd.read_csv(stored_path)
    except Exception as exc:
        stored_path.unlink(missing_ok=True)
        raise CsvIngestionError("Uploaded file could not be parsed as CSV.") from exc

    if dataframe.empty:
        stored_path.unlink(missing_ok=True)
        raise CsvIngestionError("Uploaded CSV is empty.")

    table_name = f"csv_{original_stem}_{unique_id[:12]}"
    _store_dataframe(dataframe=dataframe, table_name=table_name)

    dataset = Dataset(
        original_filename=file.filename,
        stored_filename=stored_filename,
        table_name=table_name,
        row_count=len(dataframe.index),
        column_count=len(dataframe.columns),
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    return CsvUploadResponse(
        dataset_id=dataset.id,
        original_filename=dataset.original_filename,
        table_name=dataset.table_name,
        rows=dataset.row_count,
        columns=dataset.column_count,
        column_names=[str(column) for column in dataframe.columns],
        created_at=dataset.created_at,
    )


def _store_dataframe(dataframe: pd.DataFrame, table_name: str) -> None:
    dataframe.to_sql(
        name=table_name,
        con=engine,
        if_exists="fail",
        index=False,
    )
