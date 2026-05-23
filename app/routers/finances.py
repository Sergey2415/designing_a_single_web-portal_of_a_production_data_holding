from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
import uuid
import io
import csv

from app.database import get_db
from app.models import FinancialMetric, CostComparison, User
from app.schemas import (
    FinancialMetricsResponse, FinancialMetricsData, MetricValue,
    CostDynamicsResponse, CostDynamicsData,
    CostComparisonResponse, CostComparisonItem,
    BudgetEfficiencyResponse, BudgetEfficiencyData, BudgetDataset,
    ErrorResponse
)
from app.auth import get_current_user

router = APIRouter(prefix="/api/finances", tags=["finances"])


@router.get("/metrics", response_model=FinancialMetricsResponse)
def get_financial_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение финансовых метрик"""
    try:
        # Получить последнюю метрику
        metric = db.query(FinancialMetric).order_by(
            FinancialMetric.updated_at.desc()
        ).first()
        
        if not metric:
            # Создать дефолтную метрику если нет
            metric = FinancialMetric(
                id=str(uuid.uuid4()),
                unit_cost=125.50,
                change_percentage=5.2,
                change_direction="down",
                updated_at=datetime.utcnow()
            )
            db.add(metric)
            db.commit()
        
        return FinancialMetricsResponse(
            success=True,
            data=FinancialMetricsData(
                unitCost=MetricValue(
                    value=metric.unit_cost,
                    changePercentage=metric.change_percentage,
                    changeDirection=metric.change_direction
                ),
                updatedAt=metric.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            )
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка получения метрик: {str(e)}")


@router.get("/cost-dynamics", response_model=CostDynamicsResponse)
def get_cost_dynamics(
    period: str = "all",  # all, q1, q2, q3, q4
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение динамики затрат по кварталам или месяцам"""
    try:
        if period == "all":
            # Возвращаем все 4 квартала
            costs = {
                "q1": 0.0,
                "q2": 0.0,
                "q3": 0.0,
                "q4": 0.0
            }
            
            for quarter in ["Q1", "Q2", "Q3", "Q4"]:
                total = db.query(func.sum(CostComparison.amount)).filter(
                    CostComparison.period.like(f"%{quarter}%")
                ).scalar()
                
                costs[quarter.lower()] = float(total) if total else 0.0
            
            return CostDynamicsResponse(
                success=True,
                data=CostDynamicsData(**costs)
            )
        else:
            # Возвращаем детализацию по месяцам выбранного квартала
            quarter_map = {
                "q1": ["01", "02", "03"],
                "q2": ["04", "05", "06"],
                "q3": ["07", "08", "09"],
                "q4": ["10", "11", "12"]
            }
            
            months = quarter_map.get(period.lower(), ["01", "02", "03"])
            
            # Для каждого месяца квартала получаем сумму
            costs = {}
            for i, month in enumerate(months, 1):
                total = db.query(func.sum(CostComparison.amount)).filter(
                    CostComparison.period.like(f"%2025-{month}%") |
                    CostComparison.period.like(f"%{period.upper()}%")
                ).scalar()
                
                # Используем q1, q2, q3, q4 как ключи, но значения будут для месяцев
                costs[f"q{i}"] = float(total) if total else 50000.0 + (i * 10000)  # демо данные если нет
            
            # Заполняем оставшиеся 0
            if len(costs) < 4:
                for i in range(len(costs) + 1, 5):
                    costs[f"q{i}"] = 0.0
            
            return CostDynamicsResponse(
                success=True,
                data=CostDynamicsData(**costs)
            )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка получения динамики: {str(e)}")


@router.get("/cost-comparison", response_model=CostComparisonResponse)
def get_cost_comparison(
    page: int = 1,
    limit: int = 10,
    period: Optional[str] = None,
    department: Optional[str] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение сравнения затрат с фильтрами"""
    try:
        query = db.query(CostComparison)
        
        # Фильтры
        if period:
            query = query.filter(CostComparison.period == period)
        if department:
            query = query.filter(CostComparison.department == department)
        if type:
            query = query.filter(CostComparison.type == type)
        
        # Пагинация
        total = query.count()
        pages = (total + limit - 1) // limit if total > 0 else 0
        
        comparisons = query.order_by(
            CostComparison.period.desc()
        ).offset((page - 1) * limit).limit(limit).all()
        
        data = [
            CostComparisonItem(
                period=c.period,
                department=c.department,
                type=c.type,
                amount=c.amount,
                comment=c.comment or "",
                status=c.status
            ) for c in comparisons
        ]
        
        return CostComparisonResponse(
            success=True,
            data=data,
            total=total,
            page=page,
            pages=pages
        )
    
    except Exception as e:
        import traceback
        print(f"Error in cost-comparison: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Ошибка получения сравнения: {str(e)}")


@router.get("/budget-efficiency", response_model=BudgetEfficiencyResponse)
def get_budget_efficiency(
    department: Optional[str] = None,
    period: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение данных для графика бюджета и эффективности"""
    try:
        query = db.query(CostComparison)
        
        if department:
            query = query.filter(CostComparison.department == department)
        if period:
            query = query.filter(CostComparison.period == period)
        
        comparisons = query.all()
        
        print(f"Found {len(comparisons)} comparisons")
        
        # Группировка по типам затрат
        types_data = {}
        for c in comparisons:
            print(f"Type: {c.type}, Amount: {c.amount}")
            if c.type not in types_data:
                types_data[c.type] = 0.0
            types_data[c.type] += c.amount
        
        print(f"Types data: {types_data}")
        
        labels = list(types_data.keys())
        data_values = list(types_data.values())
        
        # Разные цвета для каждого типа
        colors = ["#3b82f6", "#22c55e", "#eab308", "#ef4444", "#8b5cf6", "#f97316", "#06b6d4"]
        
        # Создаем отдельный dataset для каждого типа затрат
        datasets = []
        for i, (label, value) in enumerate(zip(labels, data_values)):
            datasets.append(
                BudgetDataset(
                    label=label.capitalize() if label else "Другое",
                    data=[value],
                    backgroundColor=colors[i % len(colors)]
                )
            )
        
        print(f"Labels: {labels}, Data: {data_values}")
        
        return BudgetEfficiencyResponse(
            success=True,
            data=BudgetEfficiencyData(
                labels=labels,
                datasets=datasets
            )
        )
    
    except Exception as e:
        import traceback
        print(f"Error in budget-efficiency: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Ошибка получения данных: {str(e)}")


@router.get("/reports/{report_type}")
def download_financial_report(
    report_type: str,  # daily, monthly, quarterly
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Скачивание финансового отчета"""
    try:
        if report_type not in ["daily", "monthly", "quarterly"]:
            raise HTTPException(status_code=400, detail="Неверный тип отчета")
        
        # Получить данные для отчета
        comparisons = db.query(CostComparison).order_by(
            CostComparison.created_at.desc()
        ).limit(100).all()
        
        if not comparisons:
            raise HTTPException(status_code=404, detail="Отчет не найден - нет данных")
        
        # Генерация CSV отчета
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        
        # Заголовок
        writer.writerow([f'=== ФИНАНСОВЫЙ ОТЧЕТ ({report_type.upper()}) ==='])
        writer.writerow(['Сгенерирован', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        
        # Данные
        writer.writerow(['Период', 'Отдел', 'Тип затрат', 'Сумма', 'Статус', 'Комментарий'])
        
        for c in comparisons:
            writer.writerow([
                c.period,
                c.department,
                c.type,
                c.amount,
                c.status,
                c.comment or ''
            ])
        
        # Итоги
        writer.writerow([])
        writer.writerow(['=== ИТОГИ ==='])
        total_amount = sum(c.amount for c in comparisons)
        writer.writerow(['Общая сумма затрат', total_amount])
        writer.writerow(['Количество записей', len(comparisons)])
        
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=financial_report_{report_type}_{datetime.now().strftime('%Y%m%d')}.csv"}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка генерации отчета: {str(e)}")


@router.post("/reports/upload")
async def upload_financial_report(
    file: UploadFile = File(...),
    type: str = Form(...),
    period: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Загрузка CSV файла с финансовыми данными"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Поддерживается только CSV формат")
        
        # Читаем содержимое CSV
        contents = await file.read()
        csv_text = contents.decode('utf-8-sig')  # utf-8-sig для корректной работы с BOM
        
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        
        # Удаляем старые записи для этого типа отчета
        db.query(CostComparison).filter(
            CostComparison.period.like(f"%{period}%")
        ).delete()
        
        # Добавляем новые записи
        records_added = 0
        for row in csv_reader:
            # Валидация обязательных полей
            if not all(k in row for k in ['period', 'department', 'type', 'amount']):
                continue
                
            # Маппинг типов затрат
            cost_type_map = {
                'materials': 'materials',
                'labor': 'labor',
                'transport': 'transport',
                'equipment': 'equipment',
                'it': 'it',
                'quality': 'quality',
                'other': 'other'
            }
            
            cost_type = cost_type_map.get(row['type'].lower(), 'other')
            
            comparison = CostComparison(
                id=str(uuid.uuid4()),
                period=row['period'],
                department=row['department'],
                type=cost_type,
                amount=float(row['amount']),
                comment=row.get('comment', ''),
                status=row.get('status', 'В рамках бюджета')
            )
            
            db.add(comparison)
            records_added += 1
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Загружено {records_added} записей",
            "recordsAdded": records_added
        }
    
    except csv.Error as e:
        raise HTTPException(status_code=400, detail=f"Ошибка чтения CSV: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Неверный формат данных: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Ошибка загрузки: {str(e)}")

