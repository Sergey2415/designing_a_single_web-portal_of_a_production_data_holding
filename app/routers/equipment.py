from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta
import uuid
import json
import io
import csv

from app.database import get_db
from app.models import Equipment, MaintenancePlan, User, DowntimeData
from app.schemas import (
    EquipmentListResponse, EquipmentItem,
    EquipmentUpdateRequest, EquipmentUpdateResponse,
    EquipmentDeleteResponse,
    MaintenancePlanCreateRequest, MaintenancePlanCreateResponse,
    DowntimeAnalysisResponse, DowntimeAnalysisData,
    DowntimeHistoryItem, DowntimeReason,
    ErrorResponse
)
from app.auth import get_current_user
from app.permissions import check_admin, Permission, has_permission

router = APIRouter(prefix="/api/equipment", tags=["equipment"])


@router.get("", response_model=EquipmentListResponse)
def get_equipment_list(
    page: int = 1,
    limit: int = 10,
    branch: Optional[str] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение списка оборудования с фильтрами"""
    try:
        query = db.query(Equipment)
        
        # Фильтры
        if branch:
            query = query.filter(Equipment.branch == branch)
        if type:
            query = query.filter(Equipment.type == type)
        if status:
            query = query.filter(Equipment.status == status)
        
        # Пагинация
        total = query.count()
        pages = (total + limit - 1) // limit if limit > 0 else 1
        
        equipment_list = query.order_by(
            Equipment.created_at.desc()
        ).offset((page - 1) * limit).limit(limit).all()
        
        data = [
            EquipmentItem(
                id=eq.id,
                name=eq.name,
                branch=eq.branch,
                type=eq.type,
                status=eq.status,
                lastCheck=eq.last_check.strftime("%Y-%m-%d") if eq.last_check else None,
                responsible=eq.responsible,
                createdAt=eq.created_at.strftime("%Y-%m-%d %H:%M:%S")
            ) for eq in equipment_list
        ]
        
        return EquipmentListResponse(
            success=True,
            data=data,
            total=total,
            page=page,
            pages=pages
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка получения: {str(e)}")


@router.put("/{equipment_id}", response_model=EquipmentUpdateResponse)
def update_equipment(
    equipment_id: str,
    request: EquipmentUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(check_admin)  # Только администраторы могут редактировать
):
    """Обновление оборудования (только администраторы)"""
    try:
        equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()

        if not equipment:
            raise HTTPException(status_code=404, detail="Оборудование не найдено")

        # Обновление полей
        if request.status:
            equipment.status = request.status
        if request.lastCheck:
            equipment.last_check = datetime.strptime(request.lastCheck, "%Y-%m-%d").date()
        if request.responsible:
            equipment.responsible = request.responsible

        db.commit()

        return EquipmentUpdateResponse(
            success=True,
            message="Обновлено"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка обновления: {str(e)}")


@router.delete("/{equipment_id}", response_model=EquipmentDeleteResponse)
def delete_equipment(
    equipment_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(check_admin)  # Используем dependency для проверки admin
):
    """Удаление оборудования (только администраторы)"""
    try:
        equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()

        if not equipment:
            raise HTTPException(status_code=404, detail="Оборудование не найдено")

        db.delete(equipment)
        db.commit()

        return EquipmentDeleteResponse(
            success=True,
            message="Удалено"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка удаления: {str(e)}")


@router.get("/maintenance-plans")
def get_maintenance_plans(
    branch: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение списка планов ТО"""
    try:
        query = db.query(MaintenancePlan)
        
        if branch:
            query = query.filter(MaintenancePlan.branch == branch)
        
        plans = query.order_by(MaintenancePlan.date.desc()).all()
        
        data = []
        for plan in plans:
            equipment_ids = json.loads(plan.equipment_ids) if plan.equipment_ids else []
            
            # Получаем названия оборудования
            equipment_list = []
            for eq_id in equipment_ids:
                eq = db.query(Equipment).filter(Equipment.id == eq_id).first()
                if eq:
                    equipment_list.append({
                        "id": eq.id,
                        "name": eq.name,
                        "status": eq.status
                    })
            
            data.append({
                "id": plan.id,
                "date": plan.date.strftime("%Y-%m-%d"),
                "branch": plan.branch,
                "equipmentIds": equipment_ids,
                "equipment": equipment_list,
                "equipmentCount": len(equipment_ids)
            })
        
        return {
            "success": True,
            "data": data
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка получения: {str(e)}")


@router.get("/maintenance-plan/{plan_id}")
def get_maintenance_plan_details(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение деталей плана ТО"""
    try:
        plan = db.query(MaintenancePlan).filter(MaintenancePlan.id == plan_id).first()
        
        if not plan:
            raise HTTPException(status_code=404, detail="План не найден")
        
        equipment_ids = json.loads(plan.equipment_ids) if plan.equipment_ids else []
        
        # Получаем полную информацию об оборудовании
        equipment_list = []
        for eq_id in equipment_ids:
            eq = db.query(Equipment).filter(Equipment.id == eq_id).first()
            if eq:
                equipment_list.append({
                    "id": eq.id,
                    "name": eq.name,
                    "type": eq.type,
                    "status": eq.status,
                    "branch": eq.branch,
                    "lastCheck": eq.last_check.strftime("%Y-%m-%d") if eq.last_check else None,
                    "responsible": eq.responsible
                })
        
        return {
            "success": True,
            "data": {
                "id": plan.id,
                "date": plan.date.strftime("%Y-%m-%d"),
                "branch": plan.branch,
                "equipment": equipment_list,
                "equipmentCount": len(equipment_list)
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка получения: {str(e)}")


@router.post("/maintenance-plan", response_model=MaintenancePlanCreateResponse)
def create_maintenance_plan(
    request: MaintenancePlanCreateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(check_admin)  # Только администраторы
):
    """Создание плана технического обслуживания (только администраторы)"""
    try:
        plan_id = str(uuid.uuid4())
        
        # Проверка существования оборудования
        for eq_id in request.equipmentIds:
            equipment = db.query(Equipment).filter(Equipment.id == eq_id).first()
            if not equipment:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Оборудование с ID {eq_id} не найдено"
                )
        
        plan = MaintenancePlan(
            id=plan_id,
            date=datetime.strptime(request.date, "%Y-%m-%d").date(),
            branch=request.branch,
            equipment_ids=json.dumps(request.equipmentIds)
        )
        
        db.add(plan)
        db.commit()
        
        return MaintenancePlanCreateResponse(
            success=True,
            id=plan_id,
            message="План создан"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка создания: {str(e)}")


@router.delete("/maintenance-plan/{plan_id}")
def delete_maintenance_plan(
    plan_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(check_admin)  # Только администраторы
):
    """Удаление плана ТО (только администраторы)"""
    try:
        plan = db.query(MaintenancePlan).filter(MaintenancePlan.id == plan_id).first()
        
        if not plan:
            raise HTTPException(status_code=404, detail="План не найден")
        
        db.delete(plan)
        db.commit()
        
        return {
            "success": True,
            "message": "План удален"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка удаления: {str(e)}")


@router.get("/downtime-analysis", response_model=DowntimeAnalysisResponse)
def get_downtime_analysis(
    branch: Optional[str] = None,
    period: str = "last30days",  # last7days, last30days
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Анализ простоев оборудования"""
    try:
        # Определение периода
        days = 30 if period == "last30days" else 7
        start_date = datetime.now() - timedelta(days=days)
        
        # DowntimeData имеет поля: id, category, value, color, period, branch_id
        # Для демонстрации используем моковые данные
        
        # Генерируем демо-данные для анализа
        downtime_percentage = 12.5  # 12.5% простоя
        trend = -3.2  # Снижение на 3.2%
        
        # История по дням
        history = []
        import random
        for i in range(days):
            date_obj = datetime.now() - timedelta(days=days - i - 1)
            # Генерируем случайные часы простоя (от 1 до 3)
            daily_hours = round(random.uniform(1.0, 3.0), 2)
            history.append(
                DowntimeHistoryItem(
                    date=date_obj.strftime("%Y-%m-%d"),
                    value=daily_hours
                )
            )
        
        # Причины простоев (статические для демонстрации)
        reasons = [
            DowntimeReason(name="Плановое обслуживание", percentage=45.0),
            DowntimeReason(name="Аварийные поломки", percentage=30.0),
            DowntimeReason(name="Нехватка материалов", percentage=15.0),
            DowntimeReason(name="Другое", percentage=10.0)
        ]
        
        return DowntimeAnalysisResponse(
            success=True,
            data=DowntimeAnalysisData(
                downtimePercentage=round(downtime_percentage, 2),
                trend=round(trend, 2),
                history=history,
                reasons=reasons
            )
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка получения: {str(e)}")


@router.get("/downtime-analysis/export")
def export_downtime_analysis(
    branch: Optional[str] = None,
    period: str = "last30days",
    format: str = "excel",  # excel, pdf
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Экспорт анализа простоев"""
    try:
        # Получить данные анализа (используем моковые данные для демонстрации)
        days = 30 if period == "last30days" else 7
        
        if format == "excel" or format == "csv":
            # Генерация CSV (можно импортировать в Excel)
            output = io.StringIO()
            writer = csv.writer(output, delimiter=';')
            
            # Заголовок
            writer.writerow([f'=== АНАЛИЗ ПРОСТОЕВ ОБОРУДОВАНИЯ ({period.upper()}) ==='])
            writer.writerow(['Филиал', branch or 'Все'])
            writer.writerow(['Период', f'{days} дней'])
            writer.writerow(['Сгенерирован', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow([])
            
            # Детальные данные (демо)
            writer.writerow(['Дата', 'Часы простоя', 'Причина'])
            
            import random
            total_hours = 0
            for i in range(days):
                date_obj = datetime.now() - timedelta(days=days - i - 1)
                hours = round(random.uniform(1.0, 3.0), 2)
                total_hours += hours
                reasons = ["Плановое обслуживание", "Аварийные поломки", "Нехватка материалов", "Другое"]
                reason = random.choice(reasons)
                writer.writerow([
                    date_obj.strftime('%Y-%m-%d'),
                    hours,
                    reason
                ])
            
            # Итоги
            writer.writerow([])
            writer.writerow(['=== ИТОГИ ==='])
            writer.writerow(['Всего часов простоя', round(total_hours, 2)])
            writer.writerow(['Среднее в день', round(total_hours / days, 2)])
            writer.writerow(['Процент простоя', '12.5%'])
            
            output.seek(0)
            
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode('utf-8-sig')),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=downtime_analysis_{period}_{datetime.now().strftime('%Y%m%d')}.csv"
                }
            )
        
        elif format == "pdf":
            # Генерация PDF
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas as pdf_canvas
            
            buffer = io.BytesIO()
            c = pdf_canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            
            y = height - 50
            
            # Заголовок
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, y, "DOWNTIME ANALYSIS")
            y -= 30
            
            # Основная информация
            c.setFont("Helvetica", 10)
            c.drawString(50, y, f"Branch: {branch or 'All'}")
            y -= 15
            c.drawString(50, y, f"Period: {period} ({days} days)")
            y -= 15
            c.drawString(50, y, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            y -= 30
            
            # Таблица данных (демо)
            c.setFont("Helvetica-Bold", 9)
            c.drawString(50, y, "Date")
            c.drawString(150, y, "Hours")
            c.drawString(220, y, "Reason")
            y -= 15
            
            c.setFont("Helvetica", 8)
            import random
            total_hours = 0
            for i in range(min(days, 30)):  # Первые 30 дней
                if y < 100:
                    c.showPage()
                    y = height - 50
                    c.setFont("Helvetica", 8)
                
                date_obj = datetime.now() - timedelta(days=days - i - 1)
                hours = round(random.uniform(1.0, 3.0), 2)
                total_hours += hours
                reasons = ["Planned maintenance", "Equipment failure", "Material shortage", "Other"]
                reason = random.choice(reasons)
                
                c.drawString(50, y, date_obj.strftime('%Y-%m-%d'))
                c.drawString(150, y, str(hours))
                c.drawString(220, y, reason[:40])
                y -= 12
            
            # Итоги
            y -= 20
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, y, "SUMMARY")
            y -= 15
            
            c.setFont("Helvetica", 9)
            c.drawString(50, y, f"Total downtime hours: {round(total_hours, 2)}")
            y -= 15
            c.drawString(50, y, f"Average per day: {round(total_hours / days, 2)}")
            y -= 15
            c.drawString(50, y, f"Downtime percentage: 12.5%")
            
            c.save()
            buffer.seek(0)
            
            return StreamingResponse(
                buffer,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=downtime_analysis_{period}_{datetime.now().strftime('%Y%m%d')}.pdf"
                }
            )
        
        else:
            raise HTTPException(status_code=400, detail="Неподдерживаемый формат")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка экспорта: {str(e)}")

