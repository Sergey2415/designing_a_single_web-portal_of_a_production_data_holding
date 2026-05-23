from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid
import csv
import io
import os

from app.database import get_db
from app.models import DataRecord, DataHistory, User
from app.schemas import (
    DataManualRequest, DataManualResponse, DataUploadResponse,
    DataValidateRequest, DataValidateResponse, ValidationIssue,
    DataConsolidateRequest, DataConsolidateResponse,
    DataHistoryResponse, DataHistoryItem, ErrorResponse
)
from app.auth import get_current_user

router = APIRouter(prefix="/api/data", tags=["data"])


@router.post("/manual", response_model=DataManualResponse)
def add_manual_data(
    request: DataManualRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ручной ввод данных"""
    try:
        # Валидация типа
        if request.type not in ["production", "downtime"]:
            raise HTTPException(status_code=400, detail="Неверный тип данных")
        
        # Парсинг даты
        try:
            data_date = datetime.strptime(request.date, "%Y-%m-%d").date()
        except:
            raise HTTPException(status_code=400, detail="Неверный формат даты")
        
        # Валидация значения
        if request.value < 0:
            raise HTTPException(status_code=400, detail="Значение не может быть отрицательным")
        
        record_id = str(uuid.uuid4())
        
        # Создание записи
        record = DataRecord(
            id=record_id,
            date=data_date,
            type=request.type,
            value=request.value,
            comment=request.comment,
            user_id=request.userId,
            status="pending"
        )
        
        db.add(record)
        
        # Создание записи в истории
        history = DataHistory(
            id=str(uuid.uuid4()),
            date=datetime.utcnow(),
            status="inProgress",
            comment=f"Ручной ввод: {request.type}, значение {request.value}",
            user=current_user.username,
            record_id=record_id,
            action="manual"
        )
        
        db.add(history)
        db.commit()
        
        return DataManualResponse(
            success=True,
            id=record_id,
            message="Данные добавлены"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка валидации: {str(e)}")


@router.post("/upload", response_model=DataUploadResponse)
async def upload_data_file(
    file: UploadFile = File(...),
    userId: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Загрузка файла CSV/XLSX"""
    try:
        print(f"📤 Загрузка файла: {file.filename}, userId: {userId}")
        
        # Проверка расширения
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ['.csv', '.xlsx']:
            print(f"❌ Неверный формат файла: {file_ext}")
            raise HTTPException(status_code=400, detail="Неверный формат файла. Используйте CSV или XLSX")
        
        # Чтение файла
        contents = await file.read()
        print(f"📊 Размер файла: {len(contents)} байт")
        
        if len(contents) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="Файл слишком большой (макс 10MB)")
        
        upload_id = str(uuid.uuid4())
        records_count = 0
        errors = []
        
        # Обработка CSV
        if file_ext == '.csv':
            try:
                content_str = contents.decode('utf-8-sig')
                csv_reader = csv.DictReader(io.StringIO(content_str), delimiter=';')
                
                print(f"📋 Колонки CSV: {csv_reader.fieldnames}")
            except Exception as e:
                print(f"❌ Ошибка чтения CSV: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Ошибка чтения CSV файла: {str(e)}")
            
            for idx, row in enumerate(csv_reader, start=1):
                try:
                    # Ожидаем колонки: date, type, value, comment
                    record_date = datetime.strptime(row.get('date', ''), "%Y-%m-%d").date()
                    record_type = row.get('type', '').strip()
                    record_value = float(row.get('value', 0))
                    record_comment = row.get('comment', '').strip()
                    
                    if record_type not in ["production", "downtime"]:
                        errors.append(f"Строка {idx}: неверный тип '{record_type}'")
                        continue
                    
                    record = DataRecord(
                        id=str(uuid.uuid4()),
                        date=record_date,
                        type=record_type,
                        value=record_value,
                        comment=record_comment if record_comment else None,
                        user_id=userId,
                        upload_id=upload_id,
                        status="pending"
                    )
                    
                    db.add(record)
                    records_count += 1
                except Exception as row_error:
                    errors.append(f"Строка {idx}: {str(row_error)}")
                    print(f"⚠️ Ошибка в строке {idx}: {str(row_error)}")
                    continue
        
        # Обработка XLSX
        elif file_ext == '.xlsx':
            import pandas as pd
            
            df = pd.read_excel(io.BytesIO(contents))
            
            for _, row in df.iterrows():
                try:
                    record_date = pd.to_datetime(row.get('date')).date()
                    record_type = str(row.get('type', '')).strip()
                    record_value = float(row.get('value', 0))
                    record_comment = str(row.get('comment', '')).strip()
                    
                    if record_type not in ["production", "downtime"]:
                        continue
                    
                    record = DataRecord(
                        id=str(uuid.uuid4()),
                        date=record_date,
                        type=record_type,
                        value=record_value,
                        comment=record_comment if record_comment else None,
                        user_id=userId,
                        upload_id=upload_id,
                        status="pending"
                    )
                    
                    db.add(record)
                    records_count += 1
                except:
                    continue
        
        if records_count == 0:
            error_msg = "Не найдено валидных данных в файле"
            if errors:
                error_msg += f". Ошибки: {'; '.join(errors[:3])}"
            print(f"❌ {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        print(f"✅ Успешно обработано записей: {records_count}")
        
        # История
        history = DataHistory(
            id=str(uuid.uuid4()),
            date=datetime.utcnow(),
            status="inProgress",
            comment=f"Загружен файл {file.filename}, записей: {records_count}",
            user=current_user.username,
            record_id=upload_id,
            action="upload"
        )
        
        db.add(history)
        db.commit()
        
        return DataUploadResponse(
            success=True,
            id=upload_id,
            message=f"Файл загружен, обработано записей: {records_count}"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Ошибка загрузки файла: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Ошибка загрузки: {str(e)}")


@router.post("/validate", response_model=DataValidateResponse)
def validate_data(
    request: DataValidateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Валидация загруженных данных"""
    try:
        print(f"🔍 Валидация для uploadId: {request.uploadId}")
        
        # Получить записи по upload_id ИЛИ по id записи
        records = db.query(DataRecord).filter(
            (DataRecord.upload_id == request.uploadId) | 
            (DataRecord.id == request.uploadId)
        ).all()
        
        print(f"📊 Найдено записей: {len(records)}")
        
        if not records:
            # Попробуем найти в истории
            history_exists = db.query(DataHistory).filter(
                DataHistory.record_id == request.uploadId
            ).first()
            
            if history_exists:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Данные с ID {request.uploadId} уже обработаны или не найдены в базе"
                )
            else:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Данные с ID {request.uploadId} не найдены. Убедитесь, что ID корректный"
                )
        
        issues = []
        validated = True
        row_num = 1
        
        for record in records:
            # Проверка значения
            if record.value < 0:
                issues.append(ValidationIssue(
                    row=row_num,
                    message=f"Отрицательное значение: {record.value}"
                ))
                validated = False
            
            # Проверка даты (не в будущем)
            if record.date > datetime.utcnow().date():
                issues.append(ValidationIssue(
                    row=row_num,
                    message=f"Дата в будущем: {record.date}"
                ))
                validated = False
            
            # Проверка типа
            if record.type not in ["production", "downtime"]:
                issues.append(ValidationIssue(
                    row=row_num,
                    message=f"Неверный тип: {record.type}"
                ))
                validated = False
            
            row_num += 1
        
        # Обновить статус записей
        if validated:
            for record in records:
                record.status = "validated"
            db.commit()
        
        # История
        history = DataHistory(
            id=str(uuid.uuid4()),
            date=datetime.utcnow(),
            status="ready" if validated else "inProgress",
            comment=f"Валидация: {'успешна' if validated else f'найдено проблем: {len(issues)}'}",
            user=current_user.username,
            record_id=request.uploadId,
            action="validate"
        )
        
        db.add(history)
        db.commit()
        
        return DataValidateResponse(
            success=True,
            validated=validated,
            issues=issues,
            message="Проверено" if validated else f"Найдено проблем: {len(issues)}"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка валидации: {str(e)}")


@router.post("/consolidate", response_model=DataConsolidateResponse)
def consolidate_data(
    request: DataConsolidateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Консолидация данных (только администраторы)"""
    # Проверка прав - только администратор может консолидировать данные
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Недостаточно прав. Консолидация данных доступна только администраторам"
        )
    try:
        print(f"🔍 Консолидация для uploadId: {request.uploadId}, отдел: {request.department}")
        
        # Получить валидированные записи по upload_id ИЛИ id
        records = db.query(DataRecord).filter(
            ((DataRecord.upload_id == request.uploadId) | (DataRecord.id == request.uploadId)),
            DataRecord.status == "validated"
        ).all()
        
        print(f"📊 Найдено валидированных записей: {len(records)}")
        
        if not records:
            # Проверим, есть ли вообще такие записи (не валидированные)
            any_records = db.query(DataRecord).filter(
                (DataRecord.upload_id == request.uploadId) | (DataRecord.id == request.uploadId)
            ).all()
            
            if not any_records:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Данные с ID {request.uploadId} не найдены"
                )
            elif any_records[0].status == "pending":
                raise HTTPException(
                    status_code=400, 
                    detail=f"Данные еще не валидированы. Сначала выполните валидацию"
                )
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Нет валидированных данных для консолидации (статус: {any_records[0].status})"
                )
        
        consolidation_id = str(uuid.uuid4())
        
        # Обновить записи
        for record in records:
            record.status = "consolidated"
            record.department = request.department
        
        # История
        history = DataHistory(
            id=str(uuid.uuid4()),
            date=datetime.utcnow(),
            status="accepted",
            comment=f"Консолидировано {len(records)} записей для отдела {request.department}",
            user=current_user.username,
            record_id=consolidation_id,
            action="consolidate"
        )
        
        db.add(history)
        db.commit()
        
        return DataConsolidateResponse(
            success=True,
            id=consolidation_id,
            message=f"Консолидировано записей: {len(records)}"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка консолидации: {str(e)}")


@router.get("/history", response_model=DataHistoryResponse)
def get_data_history(
    page: int = 1,
    limit: int = 10,
    status: str = "all",  # all, ready, inProgress, accepted
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """История изменений данных"""
    try:
        query = db.query(DataHistory)
        
        # Фильтр по статусу
        if status != "all":
            query = query.filter(DataHistory.status == status)
        
        # Пагинация
        total = query.count()
        pages = (total + limit - 1) // limit
        
        history = query.order_by(DataHistory.date.desc()).offset((page - 1) * limit).limit(limit).all()
        
        data = [
            DataHistoryItem(
                id=h.id,
                date=h.date.strftime("%Y-%m-%d %H:%M:%S"),
                status=h.status,
                comment=h.comment,
                user=h.user,
                recordId=h.record_id
            ) for h in history
        ]
        
        return DataHistoryResponse(
            success=True,
            data=data,
            total=total,
            page=page,
            pages=pages
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка получения истории: {str(e)}")


