from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.schemas.csv import CsvUploadResponse
from app.services.csv_service import CsvIngestionError, ingest_csv_upload
from app.utils.database import get_db

router = APIRouter()


@router.post(
    "/csv/upload",
    response_model=CsvUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> CsvUploadResponse:
    try:
        return await ingest_csv_upload(file=file, db=db)
    except CsvIngestionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
