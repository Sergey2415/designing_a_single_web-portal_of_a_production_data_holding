from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json

from app.database import get_db
from app.models import User, UserMetric, UserActivity, UserTask, TeamMember, UserReport
from app.schemas import (
    ProfileResponse, ProfileData,
    ProfileUpdateRequest, ProfileUpdateResponse,
    PasswordChangeRequest, PasswordChangeResponse,
    ProfileMetricsResponse, ProfileMetricsData, MetricValue,
    ProfileActivityResponse, ActivityItem,
    ProfileTasksResponse, TaskItem,
    ProfileTeamResponse, TeamMemberItem,
    ProfileReportsResponse, ReportItem,
    ErrorResponse
)
from app.auth import get_current_user, get_password_hash
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("", response_model=ProfileResponse)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение данных профиля"""
    try:
        return ProfileResponse(
            success=True,
            data=ProfileData(
                name=current_user.name or current_user.username,
                position=current_user.position or "Не указано",
                location=current_user.location or "Не указано",
                accessLevel=current_user.role,
                email=current_user.email or "Не указан",
                phone=current_user.phone or "Не указан"
            )
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка получения: {str(e)}")


@router.put("", response_model=ProfileUpdateResponse)
def update_profile(
    request: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновление профиля"""
    try:
        current_user.name = request.name
        current_user.position = request.position
        current_user.location = request.location
        current_user.email = request.email
        current_user.phone = request.phone
        
        db.commit()
        
        return ProfileUpdateResponse(
            success=True,
            message="Обновлен"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка обновления: {str(e)}")


@router.post("/password", response_model=PasswordChangeResponse)
def change_password(
    request: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Смена пароля"""
    try:
        # Проверка текущего пароля
        if not verify_password(request.currentPassword, current_user.password):
            raise HTTPException(status_code=400, detail="Неверный текущий пароль")
        
        # Проверка совпадения нового пароля
        if request.newPassword != request.confirmPassword:
            raise HTTPException(status_code=400, detail="Пароли не совпадают")
        
        # Обновление пароля
        current_user.password = get_password_hash(request.newPassword)
        db.commit()
        
        return PasswordChangeResponse(
            success=True,
            message="Пароль изменен"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка смены: {str(e)}")


@router.get("/metrics", response_model=ProfileMetricsResponse)
def get_profile_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение персональных метрик"""
    try:
        # Получить метрики пользователя
        metric = db.query(UserMetric).filter(
            UserMetric.user_id == current_user.id
        ).first()
        
        # Функция для нормализации метрик (поддержка старого и нового формата)
        def normalize_metric(data_str, default_direction="up"):
            if not data_str:
                return {"value": 0, "changePercentage": 0, "changeDirection": default_direction}
            
            try:
                data = json.loads(data_str)
                # Если есть старое поле "change", конвертируем в новый формат
                if "change" in data and "changePercentage" not in data:
                    data["changePercentage"] = data.pop("change")
                # Если нет changeDirection, определяем по знаку
                if "changeDirection" not in data and "changePercentage" in data:
                    data["changeDirection"] = "up" if data["changePercentage"] >= 0 else "down"
                return data
            except:
                return {"value": 0, "changePercentage": 0, "changeDirection": default_direction}
        
        if metric:
            # Парсинг JSON данных с нормализацией
            labor_prod = normalize_metric(metric.labor_productivity, "up")
            repair_eff = normalize_metric(metric.repair_efficiency, "down")
            equip_down = normalize_metric(metric.equipment_downtime, "down")
            cost_data = normalize_metric(metric.cost, "down")
        else:
            # Дефолтные значения
            labor_prod = {"value": 95.5, "changePercentage": 2.3, "changeDirection": "up"}
            repair_eff = {"value": 88.2, "changePercentage": -1.5, "changeDirection": "down"}
            equip_down = {"value": 12.5, "changePercentage": -3.2, "changeDirection": "down"}
            cost_data = {"value": 125.50, "changePercentage": -5.2, "changeDirection": "down"}
        
        return ProfileMetricsResponse(
            success=True,
            data=ProfileMetricsData(
                laborProductivity=MetricValue(**labor_prod),
                repairEfficiency=MetricValue(**repair_eff),
                equipmentDowntime=MetricValue(**equip_down),
                cost=MetricValue(**cost_data)
            )
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка получения: {str(e)}")


@router.get("/activity", response_model=ProfileActivityResponse)
def get_profile_activity(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение активности пользователя"""
    try:
        activities = db.query(UserActivity).filter(
            UserActivity.user_id == current_user.id
        ).order_by(UserActivity.timestamp.desc()).limit(limit).all()
        
        data = [
            ActivityItem(
                type=a.type,
                description=a.description,
                timestamp=a.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            ) for a in activities
        ]
        
        return ProfileActivityResponse(
            success=True,
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка получения: {str(e)}")


@router.get("/tasks", response_model=ProfileTasksResponse)
def get_profile_tasks(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение задач и уведомлений пользователя"""
    try:
        tasks = db.query(UserTask).filter(
            UserTask.user_id == current_user.id
        ).order_by(UserTask.created_at.desc()).limit(limit).all()
        
        # Маппинг приоритетов (если в БД английские значения)
        priority_map = {
            "high": "Высокий",
            "medium": "Средний",
            "low": "Низкий",
            "Высокий": "Высокий",
            "Средний": "Средний",
            "Низкий": "Низкий"
        }
        
        data = []
        for t in tasks:
            priority = priority_map.get(t.priority, "Средний")  # Дефолт - Средний
            data.append(TaskItem(
                title=t.title,
                priority=priority,
                deadline=t.deadline.strftime("%Y-%m-%d") if t.deadline else None,
                isNotification=t.is_notification
            ))
        
        return ProfileTasksResponse(
            success=True,
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка получения: {str(e)}")


@router.get("/team", response_model=ProfileTeamResponse)
def get_profile_team(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение команды пользователя"""
    try:
        team = db.query(TeamMember).filter(
            TeamMember.user_id == current_user.id
        ).all()
        
        data = [
            TeamMemberItem(
                name=m.name,
                status=m.status
            ) for m in team
        ]
        
        return ProfileTeamResponse(
            success=True,
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка получения: {str(e)}")


@router.get("/reports", response_model=ProfileReportsResponse)
def get_profile_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение отчетов пользователя"""
    try:
        reports = db.query(UserReport).filter(
            UserReport.user_id == current_user.id
        ).all()
        
        data = [
            ReportItem(
                branch=r.branch,
                metric1=r.metric1 or 0.0,
                metric2=r.metric2 or 0.0,
                metric3=r.metric3 or 0.0
            ) for r in reports
        ]
        
        return ProfileReportsResponse(
            success=True,
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка получения: {str(e)}")

