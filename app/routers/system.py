from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import json
from app.database import get_db
from app.models import SystemInfo, BugReport, User
from app.schemas import (
    SystemInfoResponse, CheckUpdatesResponse,
    BugReportRequest, BugReportResponse
)
from app.auth import get_current_user

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/info", response_model=SystemInfoResponse)
def get_system_info(db: Session = Depends(get_db)):
    info = db.query(SystemInfo).first()
    
    if not info:
        # Создать запись по умолчанию
        info = SystemInfo(
            version="2.10-beta",
            last_update=datetime.utcnow(),
            server_status="Online"
        )
        db.add(info)
        db.commit()
        db.refresh(info)
    
    return SystemInfoResponse(
        version=info.version,
        lastUpdate=info.last_update,
        serverStatus=info.server_status
    )


@router.get("/check-updates", response_model=CheckUpdatesResponse)
def check_updates():
    # Симуляция проверки обновлений
    # В продакшене здесь был бы реальный запрос к серверу обновлений
    return CheckUpdatesResponse(
        updateAvailable=False,
        newVersion=None,
        releaseNotes=None
    )


@router.post("/report-bug", response_model=BugReportResponse)
def report_bug(
    request: BugReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Генерировать ticket ID
    ticket_id = f"BUG-{uuid.uuid4().hex[:6].upper()}"
    
    # Создать отчет
    bug_report = BugReport(
        user_id=current_user.id,
        description=request.description,
        steps=request.steps,
        attachments=json.dumps(request.attachments) if request.attachments else None,
        ticket_id=ticket_id,
        status="open"
    )
    
    db.add(bug_report)
    db.commit()
    
    return BugReportResponse(
        status="success",
        ticketId=ticket_id
    )








