from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from app.database import get_db
from app.models import ProductionData, DowntimeData, User
from app.schemas import ProductionDataPoint, DowntimeDataPoint
from app.auth import get_current_user

router = APIRouter(prefix="/api/trends", tags=["trends"])


@router.get("/production", response_model=List[ProductionDataPoint])
def get_production_trends(
    period: str = "month",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Фильтрация по периоду
    if period == "week":
        cutoff_date = datetime.utcnow().date() - timedelta(days=7)
    else:  # month
        cutoff_date = datetime.utcnow().date() - timedelta(days=30)
    
    data = db.query(ProductionData).filter(
        ProductionData.date >= cutoff_date
    ).order_by(ProductionData.date).all()
    
    return [
        ProductionDataPoint(
            date=d.date.isoformat(),
            value=d.value
        ) for d in data
    ]


@router.get("/downtime", response_model=List[DowntimeDataPoint])
def get_downtime_trends(
    period: str = "month",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data = db.query(DowntimeData).filter(
        DowntimeData.period == period
    ).all()
    
    return [
        DowntimeDataPoint(
            category=d.category,
            value=d.value,
            color=d.color or "#000000"
        ) for d in data
    ]








