from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database import get_db
from app.models import KPIIndicator, KPIDetail, User
from app.schemas import (
    KPIDataResponse, KPIRowResponse, KPISummaryResponse, KPISummaryItem,
    KPIFiltersResponse, KPIDetailsResponse, KPIStatsResponse, KPIDetailRowResponse
)
from app.auth import get_current_user

router = APIRouter(prefix="/api/kpi", tags=["kpi"])


@router.get("/data", response_model=KPIDataResponse)
def get_kpi_data(
    period: str = "К1 2025",
    branch: str = "Все",
    type: str = "Все",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Построить запрос с фильтрами
    query = db.query(KPIIndicator)
    
    if period != "Все":
        query = query.filter(KPIIndicator.period == period)
    
    if branch != "Все":
        query = query.filter(KPIIndicator.branch == branch)
    
    if type != "Все":
        query = query.filter(KPIIndicator.type == type)
    
    indicators = query.all()
    
    # Сформировать rows
    rows = [
        KPIRowResponse(
            name=ind.name,
            plan=ind.plan,
            fact=ind.fact,
            deviation=ind.deviation,
            trend=ind.trend,
            link=ind.link or f"kpivis.html?kpi={ind.kpi_key or ind.id}"
        ) for ind in indicators
    ]
    
    # Вычислить summary
    if indicators:
        # Средняя тенденция KPI (упрощенная логика)
        try:
            deviations = []
            for ind in indicators:
                dev_str = ind.deviation.replace('+', '').replace('%', '').replace(',', '.')
                try:
                    deviations.append(float(dev_str))
                except:
                    pass
            total_deviation = sum(deviations)
            avg_deviation = total_deviation / len(deviations) if deviations else 0
        except:
            avg_deviation = 0
        
        trend_kpi = KPISummaryItem(
            value=f"{'+' if avg_deviation >= 0 else ''}{avg_deviation:.1f}%",
            sub=f"{'+2%' if avg_deviation > 0 else '-2%'} с предыдущего периода",
            isPositive=avg_deviation >= 0
        )
        
        # Сравнение филиала
        branch_compare = KPISummaryItem(
            value="+10%",
            sub="+5% от среднего",
            isPositive=True
        )
    else:
        trend_kpi = KPISummaryItem(value="0%", sub="Нет данных", isPositive=True)
        branch_compare = KPISummaryItem(value="0%", sub="Нет данных", isPositive=True)
    
    return KPIDataResponse(
        rows=rows,
        summary=KPISummaryResponse(
            trendKpi=trend_kpi,
            branchCompare=branch_compare
        )
    )


@router.get("/filters", response_model=KPIFiltersResponse)
def get_kpi_filters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Получить уникальные значения для фильтров
    periods = db.query(KPIIndicator.period).distinct().all()
    branches = db.query(KPIIndicator.branch).distinct().all()
    types = db.query(KPIIndicator.type).distinct().all()
    
    return KPIFiltersResponse(
        periods=["Все"] + sorted([p[0] for p in periods]),
        branches=["Все"] + sorted([b[0] for b in branches if b[0] != "Все"]),
        types=["Все"] + sorted([t[0] for t in types if t[0] != "Все"])
    )


@router.get("/details", response_model=KPIDetailsResponse)
def get_kpi_details(
    kpi: str,
    tab: str = "shifts",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Найти KPI по ключу или ID
        if kpi.isdigit():
            indicator = db.query(KPIIndicator).filter(KPIIndicator.id == int(kpi)).first()
        else:
            indicator = db.query(KPIIndicator).filter(KPIIndicator.kpi_key == kpi).first()
        
        if not indicator:
            raise HTTPException(status_code=404, detail="KPI не найден")
        
        # Проверить валидность таба
        if tab not in ["shifts", "employees", "equipment"]:
            raise HTTPException(status_code=400, detail="Неверный тип таба")
        
        # Получить детали по табу
        details = db.query(KPIDetail).filter(
            KPIDetail.kpi_id == indicator.id,
            KPIDetail.tab_type == tab
        ).all()
        
        # Вычислить stats (агрегация)
        if details:
            total_plan = sum(d.plan for d in details)
            total_fact = sum(d.fact for d in details)
            total_deviation = total_fact - total_plan
            deviation_str = f"{'+' if total_deviation >= 0 else ''}{total_deviation:.0f}"
            trend_pct = (total_deviation / total_plan * 100) if total_plan > 0 else 0
            
            stats = KPIStatsResponse(
                plan=total_plan,
                fact=total_fact,
                deviation=deviation_str,
                trend=f"{'▲' if total_deviation >= 0 else '▼'} {'+' if trend_pct >= 0 else ''}{trend_pct:.1f}%",
                isPositive=total_deviation >= 0
            )
        else:
            stats = KPIStatsResponse(
                plan=indicator.plan,
                fact=indicator.fact,
                deviation=indicator.deviation,
                trend=indicator.trend,
                isPositive="▲" in indicator.trend or "+" in indicator.deviation
            )
        
        # Сформировать rows в зависимости от таба
        rows = []
        for d in details:
            row_data = {
                "plan": d.plan,
                "fact": d.fact,
                "deviation": d.deviation,
                "trend": d.trend,
                "isPositive": d.is_positive
            }
            
            if tab == "shifts":
                row_data["shift"] = d.name
            elif tab == "employees":
                row_data["employee"] = d.name
            elif tab == "equipment":
                row_data["equipment"] = d.name
            
            rows.append(KPIDetailRowResponse(**row_data))
        
        return KPIDetailsResponse(
            stats=stats,
            rows=rows
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

