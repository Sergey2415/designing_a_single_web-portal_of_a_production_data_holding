from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import KPIMetric, User
from app.schemas import KPIResponse, KPIItem
from app.auth import get_current_user

router = APIRouter(prefix="/api", tags=["kpi"])


@router.get("/kpi", response_model=KPIResponse)
def get_kpi(
    branch_id: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if branch_id == 0:
        # Агрегация по всем филиалам - возвращаем средние/суммарные значения
        # Для упрощения берем первую запись, но можно сделать реальную агрегацию
        kpi = db.query(KPIMetric).first()
    else:
        kpi = db.query(KPIMetric).filter(KPIMetric.branch_id == branch_id).first()
    
    if not kpi:
        raise HTTPException(status_code=400, detail="Invalid branch_id")
    
    return KPIResponse(
        productivity=KPIItem(
            value=kpi.productivity_value,
            change=kpi.productivity_change,
            isPositive=kpi.is_positive_productivity
        ),
        costPerTon=KPIItem(
            value=kpi.cost_per_ton_value,
            change=kpi.cost_per_ton_change,
            isPositive=kpi.is_positive_cost
        ),
        uptime=KPIItem(
            value=kpi.uptime_value,
            change=kpi.uptime_change,
            isPositive=kpi.is_positive_uptime
        ),
        efficiencyIndex=KPIItem(
            value=kpi.efficiency_index_value,
            change=kpi.efficiency_index_change,
            isPositive=kpi.is_positive_efficiency
        )
    )








