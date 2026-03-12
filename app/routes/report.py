import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.property import Report
from app.schemas.property import ReportResponse


router = APIRouter(tags=["reports"])

# Project root for resolving relative report paths
_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _resolve_report_path(report_url: str) -> Path:
    """Resolve report_url (absolute or relative) to filesystem path."""
    p = Path(report_url)
    if not p.is_absolute():
        p = _PROJECT_ROOT / report_url
    return p


@router.get("/report/{report_id}", summary="Download report by ID")
async def download_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Return the Excel file for the given report ID."""
    report = await db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    path = _resolve_report_path(report.report_url)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report file not found")
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=path.name,
    )


@router.get("/property/{property_id}/reports", response_model=list[ReportResponse])
async def list_property_reports(
    property_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[ReportResponse]:
    """List all reports for a property (newest first)."""
    result = await db.execute(
        select(Report).where(Report.property_id == property_id).order_by(Report.created_at.desc())
    )
    reports = result.scalars().all()
    return [ReportResponse.model_validate(r) for r in reports]
