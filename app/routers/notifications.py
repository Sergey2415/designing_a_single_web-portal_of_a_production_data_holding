from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List
from app.database import get_db
from app.models import Notification, User, Task, Comment
from app.schemas import (
    NotificationResponse, NotificationDetailedResponse,
    NotificationSummaryResponse, MarkReadRequest, MarkReadResponse,
    CommentRequest, CommentResponse, AssignRequest, AssignResponse,
    TaskCompleteResponse, NotificationsRefreshResponse
)
from app.auth import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/summary", response_model=NotificationSummaryResponse)
def get_notifications_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Подсчет новых уведомлений
    new_notifications = db.query(func.count(Notification.id)).filter(
        Notification.is_new == True
    ).scalar()
    
    # Подсчет открытых задач
    open_tasks = db.query(func.count(Task.id)).filter(
        Task.status == "open"
    ).scalar()
    
    # Подсчет критических ошибок
    critical_errors = db.query(func.count(Notification.id)).filter(
        Notification.type == "error",
        Notification.priority == "critical",
        Notification.is_read == False
    ).scalar()
    
    # Подсчет новых задач
    new_tasks = db.query(func.count(Task.id)).filter(
        Task.status == "open",
        Task.created_at >= func.date('now', '-7 days')  # Задачи за последнюю неделю
    ).scalar()
    
    return NotificationSummaryResponse(
        newNotifications=new_notifications or 0,
        openTasks=open_tasks or 0,
        criticalErrors=critical_errors or 0,
        newTasks=new_tasks or 0
    )


@router.get("/refresh", response_model=NotificationsRefreshResponse)
def refresh_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Получить summary
    summary = get_notifications_summary(db=db, current_user=current_user)
    
    # Получить список уведомлений
    notifications = get_notifications_list(
        type="all",
        sort="time",
        limit=20,
        offset=0,
        db=db,
        current_user=current_user
    )
    
    return NotificationsRefreshResponse(
        summary=summary,
        notifications=notifications
    )


@router.get("", response_model=List[NotificationDetailedResponse])
def get_notifications_list(
    type: str = "all",
    sort: str = "time",
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Notification)
    
    # Фильтр по типу
    if type != "all":
        query = query.filter(Notification.type == type)
    
    # Сортировка
    if sort == "time":
        query = query.order_by(Notification.timestamp.desc())
    elif sort == "type":
        query = query.order_by(Notification.type)
    elif sort == "priority":
        # Сортировка по приоритету: critical > high > medium > low
        priority_order = {
            "critical": 0,
            "high": 1,
            "medium": 2,
            "low": 3
        }
        notifications = query.all()
        notifications.sort(key=lambda n: priority_order.get(n.priority, 4))
        notifications = notifications[offset:offset + limit]
    else:
        query = query.order_by(Notification.timestamp.desc())
    
    if sort != "priority":
        notifications = query.offset(offset).limit(limit).all()
    
    result = []
    for n in notifications:
        item = NotificationDetailedResponse(
            id=n.id,
            type=n.type,
            title=n.title or n.type.capitalize(),
            text=n.message,
            time=n.timestamp,
            priority=n.priority,
            isNew=n.is_new,
            isRead=n.is_read,
            reportId=n.report_id,
            taskId=n.task_id,
            status=n.task.status if n.task else None
        )
        result.append(item)
    
    return result


@router.post("/{notification_id}/mark-read", response_model=MarkReadResponse)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    notification.is_new = False
    db.commit()
    
    return MarkReadResponse(status="success")


@router.post("/{notification_id}/comment", response_model=CommentResponse)
def add_comment(
    notification_id: int,
    request: CommentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    comment = Comment(
        notification_id=notification_id,
        user_id=current_user.id,
        comment=request.comment
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return CommentResponse(
        status="success",
        commentId=comment.id
    )


@router.post("/{notification_id}/assign", response_model=AssignResponse)
def assign_notification(
    notification_id: int,
    request: AssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    # Проверить, существует ли пользователь
    assignee = db.query(User).filter(User.id == request.assigneeId).first()
    if not assignee:
        raise HTTPException(status_code=400, detail="Invalid user")
    
    notification.assignee_id = request.assigneeId
    db.commit()
    
    return AssignResponse(status="success")


# Старый эндпоинт для совместимости
@router.post("/mark-read", response_model=MarkReadResponse)
def mark_notification_read_legacy(
    request: MarkReadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return mark_notification_read(
        notification_id=request.notification_id,
        db=db,
        current_user=current_user
    )

