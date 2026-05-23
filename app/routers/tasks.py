from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime, date
import os
import uuid
from app.database import get_db
from app.models import Task, User, TaskHistory, Department
from app.schemas import (
    TaskCompleteResponse, TaskItemResponse, TaskHistoryItemResponse,
    ResponsibleResponse, TaskCreateResponse
)
from app.auth import get_current_user

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=List[TaskItemResponse])
def get_tasks(
    status: str = "in_progress",
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Task)
    
    # Маппинг статусов
    status_map = {
        "in_progress": "В процессе",
        "completed": "Выполнена",
        "overdue": "Просрочена"
    }
    
    if status == "overdue":
        # Просроченные: срок < текущей даты и не выполнена
        query = query.filter(
            and_(
                Task.due_date < datetime.utcnow(),
                Task.status != "Выполнена"
            )
        )
    elif status in status_map:
        query = query.filter(Task.status == status_map[status])
    else:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    tasks = query.limit(limit).all()
    
    return [
        TaskItemResponse(
            id=t.id,
            title=t.title,
            report=t.report,
            responsible=t.responsible,
            due=t.due_date.strftime("%Y-%m-%d") if t.due_date else None,
            status=t.status
        ) for t in tasks
    ]


@router.get("/history", response_model=List[TaskHistoryItemResponse])
def get_task_history(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    history = db.query(TaskHistory).order_by(
        TaskHistory.date.desc()
    ).limit(limit).all()
    
    return [
        TaskHistoryItemResponse(
            id=h.id,
            icon=h.icon,
            text=h.text,
            author=h.author,
            date=h.date.strftime("%Y-%m-%d")
        ) for h in history
    ]


@router.post("", response_model=TaskCreateResponse, status_code=201)
async def create_task(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    responsible: str = Form(...),
    due: str = Form(...),
    priority: str = Form("Средний"),
    report: Optional[str] = Form(None),
    reportFile: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Обработка файла если есть
    report_file_url = None
    if reportFile:
        # Проверка размера
        contents = await reportFile.read()
        if len(contents) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=413, detail="File too large (max 10MB)")
        
        # Сохранение файла
        upload_dir = "uploads/reports"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_ext = os.path.splitext(reportFile.filename)[1]
        filename = f"report_{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(upload_dir, filename)
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        report_file_url = f"/uploads/reports/{filename}"
    
    # Парсинг даты
    try:
        due_date = datetime.strptime(due, "%Y-%m-%d")
    except:
        raise HTTPException(status_code=400, detail="Invalid date format (use YYYY-MM-DD)")
    
    # Создание задачи
    task = Task(
        title=title,
        description=description,
        report=report,
        responsible=responsible,
        due_date=due_date,
        priority=priority,
        status="В процессе",
        creator_id=current_user.id,
        report_file_url=report_file_url
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    return TaskCreateResponse(
        status="success",
        taskId=task.id
    )


@router.post("/{task_id}/mark-complete", response_model=TaskCompleteResponse)
def mark_task_complete(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = "Выполнена"
    db.commit()
    
    return TaskCompleteResponse(status="success")


@router.get("/responsibles", response_model=List[ResponsibleResponse])
def get_responsibles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    departments = db.query(Department).all()
    
    return [
        ResponsibleResponse(
            value=d.value,
            label=d.label
        ) for d in departments
    ]

