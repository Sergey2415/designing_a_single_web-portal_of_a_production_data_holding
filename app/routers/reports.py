from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from typing import List, Optional
from datetime import datetime, timedelta, date
import json
import uuid
import csv
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

from app.database import get_db
from app.models import Report, User
from app.schemas import (
    ReportsListResponse, ReportListItem, ReportDetailResponse,
    ReportDetailData, ReportCreateRequest, ReportCreateResponse,
    ReportDeleteResponse, ReportSendRequest, ReportSendResponse,
    ErrorResponse, ReportDetailItem, ReportDowntimeReason
)
from app.auth import get_current_user
from app.permissions import check_admin, Permission, has_permission

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("", response_model=ReportsListResponse)
def get_reports_list(
    date: str = "all",  # today, week, month, quarter, all
    type: str = "all",  # production, financial, equipment, analytics, all
    status: str = "all",  # ready, inProgress, accepted, all
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        query = db.query(Report)
        
        # Фильтр по дате
        if date == "today":
            query = query.filter(Report.date == datetime.utcnow().date())
        elif date == "week":
            week_ago = datetime.utcnow().date() - timedelta(days=7)
            query = query.filter(Report.date >= week_ago)
        elif date == "month":
            month_ago = datetime.utcnow().date() - timedelta(days=30)
            query = query.filter(Report.date >= month_ago)
        elif date == "quarter":
            quarter_ago = datetime.utcnow().date() - timedelta(days=90)
            query = query.filter(Report.date >= quarter_ago)
        
        # Фильтр по типу
        if type != "all":
            query = query.filter(Report.type == type)
        
        # Фильтр по статусу
        if status != "all":
            query = query.filter(Report.status == status)
        
        # Пагинация
        total = query.count()
        pages = (total + limit - 1) // limit  # Округление вверх
        
        reports = query.order_by(Report.date.desc()).offset((page - 1) * limit).limit(limit).all()
        
        data = [
            ReportListItem(
                id=r.id,
                date=r.date.strftime("%Y-%m-%d"),
                type=r.type,
                author=r.author,
                status=r.status
            ) for r in reports
        ]
        
        return ReportsListResponse(
            success=True,
            data=data,
            total=total,
            page=page,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка фильтрации: {str(e)}")


@router.get("/{report_id}", response_model=ReportDetailResponse)
def get_report_detail(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Отчет не найден")
    
    # Парсинг JSON данных
    details = []
    if report.details:
        try:
            details_data = json.loads(report.details)
            details = [ReportDetailItem(**item) for item in details_data]
        except:
            pass
    
    downtime_reasons = []
    if report.downtime_reasons:
        try:
            downtime_data = json.loads(report.downtime_reasons)
            downtime_reasons = [ReportDowntimeReason(**item) for item in downtime_data]
        except:
            pass
    
    data = ReportDetailData(
        id=report.id,
        title=report.title,
        date=report.date.strftime("%Y-%m-%d"),
        type=report.type,
        author=report.author,
        status=report.status,
        content=report.content,
        period=report.period,
        department=report.department,
        kpi=report.kpi,
        details=details,
        downtimeReasons=downtime_reasons
    )
    
    return ReportDetailResponse(success=True, data=data)


@router.get("/{report_id}/download")
def download_report(
    report_id: str,
    format: str = "pdf",  # pdf или csv
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Отчет не найден")
    
    if format == "pdf":
        # Генерация улучшенного PDF с использованием canvas (более стабильно)
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.pdfgen import canvas as pdf_canvas
        
        buffer = io.BytesIO()
        c = pdf_canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Безопасный заголовок (только ASCII)
        safe_title = (report.title or "Report").encode('ascii', 'ignore').decode('ascii')
        if not safe_title:
            safe_title = "Production Report"
        
        y = height - 50
        
        # Заголовок
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, y, safe_title[:50])  # Ограничение длины
        y -= 40
        
        # Основная информация
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Report Information")
        y -= 25
        
        c.setFont("Helvetica", 10)
        info_lines = [
            f"Date: {report.date}",
            f"Type: {report.type}",
            f"Author: {report.author}",
            f"Status: {report.status}",
        ]
        
        if report.period:
            info_lines.append(f"Period: {report.period}")
        if report.department:
            info_lines.append(f"Department: {report.department}")
        if report.kpi:
            info_lines.append(f"KPI: {report.kpi}")
        
        for line in info_lines:
            c.drawString(70, y, line)
            y -= 15
        
        y -= 10
        
        # Содержание
        if report.content and y > 200:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "Content")
            y -= 20
            
            c.setFont("Helvetica", 9)
            content_lines = report.content.split('\n')
            for line in content_lines[:15]:  # Ограничение строк
                if y < 100:
                    c.showPage()
                    y = height - 50
                    c.setFont("Helvetica", 9)
                
                safe_line = line.encode('ascii', 'ignore').decode('ascii')
                if safe_line.strip():
                    c.drawString(70, y, safe_line[:80])
                    y -= 12
            
            y -= 10
        
        # Детальные показатели
        if report.details and y > 250:
            try:
                details = json.loads(report.details)
                if details:
                    if y < 300:
                        c.showPage()
                        y = height - 50
                    
                    c.setFont("Helvetica-Bold", 12)
                    c.drawString(50, y, "Performance Details")
                    y -= 25
                    
                    # Заголовки таблицы
                    c.setFont("Helvetica-Bold", 9)
                    c.drawString(70, y, "Parameter")
                    c.drawString(220, y, "Target")
                    c.drawString(290, y, "Actual")
                    c.drawString(360, y, "Deviation")
                    c.drawString(450, y, "Status")
                    y -= 15
                    
                    # Данные
                    c.setFont("Helvetica", 8)
                    for item in details[:10]:  # Ограничение строк
                        if y < 80:
                            c.showPage()
                            y = height - 50
                            c.setFont("Helvetica", 8)
                        
                        param = str(item.get('parameter', 'N/A'))[:25].encode('ascii', 'ignore').decode('ascii')
                        c.drawString(70, y, param)
                        c.drawString(220, y, str(item.get('target', '')))
                        c.drawString(290, y, str(item.get('actual', '')))
                        c.drawString(360, y, f"{item.get('deviation', '')}%")
                        c.drawString(450, y, str(item.get('status', '')))
                        y -= 12
                    
                    y -= 10
            except:
                pass
        
        # Причины простоя
        if report.downtime_reasons and y > 200:
            try:
                downtime = json.loads(report.downtime_reasons)
                if downtime:
                    if y < 250:
                        c.showPage()
                        y = height - 50
                    
                    c.setFont("Helvetica-Bold", 12)
                    c.drawString(50, y, "Downtime Reasons")
                    y -= 25
                    
                    # Заголовки
                    c.setFont("Helvetica-Bold", 9)
                    c.drawString(70, y, "Reason")
                    c.drawString(350, y, "Percentage")
                    y -= 15
                    
                    # Данные
                    c.setFont("Helvetica", 8)
                    for item in downtime[:10]:
                        if y < 80:
                            c.showPage()
                            y = height - 50
                            c.setFont("Helvetica", 8)
                        
                        reason = str(item.get('reason', 'N/A'))[:40].encode('ascii', 'ignore').decode('ascii')
                        c.drawString(70, y, reason)
                        c.drawString(350, y, f"{item.get('percentage', '')}%")
                        y -= 12
            except:
                pass
        
        # Футер
        c.setFont("Helvetica", 8)
        c.drawString(50, 30, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        c.drawString(450, 30, f"Page 1")
        
        c.save()
        buffer.seek(0)
        
        safe_filename = safe_title.replace(' ', '_')
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=report_{safe_filename}_{report.date}.pdf"}
        )
    
    elif format == "csv":
        # Генерация улучшенного CSV
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        
        # Основная информация
        writer.writerow(['=== ИНФОРМАЦИЯ ОБ ОТЧЕТЕ ==='])
        writer.writerow(['Report ID', report.id])
        writer.writerow(['Название', report.title])
        writer.writerow(['Дата', report.date])
        writer.writerow(['Тип', report.type])
        writer.writerow(['Автор', report.author])
        writer.writerow(['Статус', report.status])
        
        if report.period:
            writer.writerow(['Период', report.period])
        if report.department:
            writer.writerow(['Отдел', report.department])
        if report.kpi:
            writer.writerow(['KPI', report.kpi])
        
        writer.writerow([])
        
        # Содержание
        if report.content:
            writer.writerow(['=== СОДЕРЖАНИЕ ==='])
            for line in report.content.split('\n'):
                if line.strip():
                    writer.writerow([line])
            writer.writerow([])
        
        # Детальные показатели
        if report.details:
            try:
                details = json.loads(report.details)
                if details:
                    writer.writerow(['=== ДЕТАЛЬНЫЕ ПОКАЗАТЕЛИ ==='])
                    writer.writerow(['Параметр', 'План', 'Факт', 'Отклонение (%)', 'Статус'])
                    
                    for item in details:
                        writer.writerow([
                            item.get('parameter', ''),
                            item.get('target', ''),
                            item.get('actual', ''),
                            item.get('deviation', ''),
                            item.get('status', '')
                        ])
                    writer.writerow([])
            except:
                pass
        
        # Причины простоя
        if report.downtime_reasons:
            try:
                downtime = json.loads(report.downtime_reasons)
                if downtime:
                    writer.writerow(['=== ПРИЧИНЫ ПРОСТОЯ ==='])
                    writer.writerow(['Причина', 'Процент (%)'])
                    
                    for item in downtime:
                        writer.writerow([
                            item.get('reason', ''),
                            item.get('percentage', '')
                        ])
                    writer.writerow([])
            except:
                pass
        
        # Итоги
        writer.writerow(['=== ИТОГИ ==='])
        writer.writerow(['Отчет сгенерирован', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow(['Создан пользователем', current_user.username])
        
        output.seek(0)
        
        # Безопасное имя файла
        safe_filename = (report.title or "report").encode('ascii', 'ignore').decode('ascii').replace(' ', '_')
        if not safe_filename:
            safe_filename = "report"
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),  # utf-8-sig для корректного отображения в Excel
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={safe_filename}_{report.date}.csv"}
        )
    
    else:
        raise HTTPException(status_code=400, detail="Неподдерживаемый формат")


@router.delete("/{report_id}", response_model=ReportDeleteResponse)
def delete_report(
    report_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(check_admin)  # Используем новый dependency для проверки admin
):
    """Удаление отчета (только администраторы)"""
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Отчет не найден")

    db.delete(report)
    db.commit()

    return ReportDeleteResponse(success=True, message="Отчет удален")


@router.post("", response_model=ReportCreateResponse, status_code=201)
def create_report(
    request: ReportCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Парсинг даты
        try:
            report_date = datetime.strptime(request.date, "%Y-%m-%d").date()
        except:
            raise HTTPException(status_code=400, detail="Неверный формат даты")
        
        report_id = str(uuid.uuid4())
        
        report = Report(
            id=report_id,
            title=request.title,
            date=report_date,
            type=request.type,
            author=request.author,
            status=request.status,
            content=request.content,
            period=request.period,
            department=request.department,
            kpi=request.kpi
        )
        
        db.add(report)
        db.commit()
        
        return ReportCreateResponse(
            success=True,
            id=report_id,
            message="Отчет создан"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка создания: {str(e)}")


@router.get("/export/csv")
def export_reports(
    date: str = "all",
    type: str = "all",
    status: str = "all",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        query = db.query(Report)
        
        # Применяем те же фильтры, что и в списке
        if date == "today":
            query = query.filter(Report.date == datetime.utcnow().date())
        elif date == "week":
            week_ago = datetime.utcnow().date() - timedelta(days=7)
            query = query.filter(Report.date >= week_ago)
        elif date == "month":
            month_ago = datetime.utcnow().date() - timedelta(days=30)
            query = query.filter(Report.date >= month_ago)
        elif date == "quarter":
            quarter_ago = datetime.utcnow().date() - timedelta(days=90)
            query = query.filter(Report.date >= quarter_ago)
        
        if type != "all":
            query = query.filter(Report.type == type)
        
        if status != "all":
            query = query.filter(Report.status == status)
        
        reports = query.all()
        
        # Генерация CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(["ID", "Title", "Date", "Type", "Author", "Status", "Period", "Department"])
        
        for r in reports:
            writer.writerow([
                r.id,
                r.title,
                r.date.strftime("%Y-%m-%d"),
                r.type,
                r.author,
                r.status,
                r.period or "",
                r.department or ""
            ])
        
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=reports_export.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка экспорта: {str(e)}")


@router.post("/{report_id}/send", response_model=ReportSendResponse)
def send_report(
    report_id: str,
    request: ReportSendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Отчет не найден")
    
    # Имитация отправки (в реальной системе - email/notification)
    # В будущем можно добавить таблицу report_sends для логирования
    
    return ReportSendResponse(
        success=True,
        message=f"Отчет отправлен менеджеру {request.managerId or 'по умолчанию'}"
    )

