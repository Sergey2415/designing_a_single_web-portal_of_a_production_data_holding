from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
import pyotp
from app.database import get_db
from app.models import User, UserSettings, LoginHistory
from app.schemas import (
    UserSettingsResponse, UserSettingsUpdate, SettingsUpdateResponse,
    UserProfileResponse, AvatarUploadResponse, ChangePasswordRequest,
    ChangePasswordResponse, TwoFactorStatusResponse, TwoFactorEnableRequest,
    TwoFactorEnableResponse, LoginHistoryItem, AccountDeleteResponse,
    GeneralSettings, ThemeSettings, NotificationSettings
)
from app.auth import get_current_user, verify_password, get_password_hash

router = APIRouter(prefix="/api/user", tags=["user"])


@router.get("/settings", response_model=UserSettingsResponse)
def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    
    if not settings:
        # Создать настройки по умолчанию
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    # Конвертировать старые значения БД в новые коды
    language_map = {'Русский': 'ru', 'English': 'en', 'Deutsch': 'de', 'Français': 'fr'}
    time_format_map = {'24-часовой': '24h', '12-часовой': '12h'}
    
    language = language_map.get(settings.language, settings.language if settings.language in ['ru', 'en', 'de', 'fr'] else 'ru')
    time_format = time_format_map.get(settings.time_format, settings.time_format if settings.time_format in ['24h', '12h'] else '24h')
    
    return UserSettingsResponse(
        general=GeneralSettings(
            language=language,
            timeFormat=time_format,
            dateFormat=settings.date_format,
            regional=settings.regional
        ),
        theme=ThemeSettings(
            selected=settings.theme,
            autoByTime=settings.auto_theme_by_time
        ),
        notifications=NotificationSettings(
            newReports=settings.notify_new_reports,
            equipmentFailures=settings.notify_equipment_failures,
            dailySummaryEmail=settings.notify_daily_email,
            pushBrowser=settings.notify_push_browser,
            telegram=settings.notify_telegram,
            soundVolume=settings.sound_volume,
            doNotDisturb=settings.do_not_disturb
        )
    )


@router.put("/settings", response_model=SettingsUpdateResponse)
def update_user_settings(
    updates: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
    
    # Обновить общие настройки
    if updates.general:
        if updates.general.language is not None:
            settings.language = updates.general.language
        if updates.general.timeFormat is not None:
            settings.time_format = updates.general.timeFormat
        if updates.general.dateFormat is not None:
            settings.date_format = updates.general.dateFormat
        if updates.general.regional is not None:
            settings.regional = updates.general.regional
    
    # Обновить тему
    if updates.theme:
        if updates.theme.selected is not None:
            settings.theme = updates.theme.selected
        if updates.theme.autoByTime is not None:
            settings.auto_theme_by_time = updates.theme.autoByTime
    
    # Обновить уведомления
    if updates.notifications:
        if updates.notifications.newReports is not None:
            settings.notify_new_reports = updates.notifications.newReports
        if updates.notifications.equipmentFailures is not None:
            settings.notify_equipment_failures = updates.notifications.equipmentFailures
        if updates.notifications.dailySummaryEmail is not None:
            settings.notify_daily_email = updates.notifications.dailySummaryEmail
        if updates.notifications.pushBrowser is not None:
            settings.notify_push_browser = updates.notifications.pushBrowser
        if updates.notifications.telegram is not None:
            settings.notify_telegram = updates.notifications.telegram
        if updates.notifications.soundVolume is not None:
            # Валидация
            if not 0 <= updates.notifications.soundVolume <= 100:
                raise HTTPException(status_code=400, detail="Sound volume must be between 0 and 100")
            settings.sound_volume = updates.notifications.soundVolume
        if updates.notifications.doNotDisturb is not None:
            settings.do_not_disturb = updates.notifications.doNotDisturb
    
    db.commit()
    
    return SettingsUpdateResponse(
        status="success",
        message="Настройки сохранены"
    )


@router.get("/profile", response_model=UserProfileResponse)
def get_user_profile(current_user: User = Depends(get_current_user)):
    # Если есть аватар, конвертируем в полный URL
    avatar_url = current_user.avatar_url
    if avatar_url and not avatar_url.startswith("http"):
        avatar_url = f"http://localhost:8000{avatar_url}"
    
    return UserProfileResponse(
        name=current_user.name,
        role=current_user.role,
        department=current_user.department,
        avatarUrl=avatar_url
    )


@router.post("/upload-avatar", response_model=AvatarUploadResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Валидация типа файла
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Валидация размера (макс 5MB)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 5MB)")
    
    # Сохранить файл
    upload_dir = "uploads/avatars"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{current_user.id}_{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, filename)
    
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Обновить URL в БД (сохраняем относительный путь)
    avatar_url = f"/uploads/avatars/{filename}"
    current_user.avatar_url = avatar_url
    db.commit()
    
    # Возвращаем полный URL для фронтенда
    full_avatar_url = f"http://localhost:8000{avatar_url}"
    
    return AvatarUploadResponse(
        status="success",
        avatarUrl=full_avatar_url
    )


@router.post("/change-password", response_model=ChangePasswordResponse)
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Проверить старый пароль
    if not verify_password(request.oldPassword, current_user.password):
        raise HTTPException(status_code=401, detail="Неверный старый пароль")
    
    # Проверить совпадение нового пароля
    if request.newPassword != request.confirmNewPassword:
        raise HTTPException(status_code=400, detail="Пароли не совпадают")
    
    # Валидация силы пароля (минимум 6 символов)
    if len(request.newPassword) < 6:
        raise HTTPException(status_code=400, detail="Пароль должен быть не менее 6 символов")
    
    # Обновить пароль
    current_user.password = get_password_hash(request.newPassword)
    db.commit()
    
    return ChangePasswordResponse(status="success")


@router.get("/2fa", response_model=TwoFactorStatusResponse)
def get_2fa_status(
    current_user: User = Depends(get_current_user)
):
    if current_user.two_fa_enabled and current_user.two_fa_secret:
        return TwoFactorStatusResponse(
            enabled=True,
            setupUrl=None
        )
    else:
        # Генерировать новый секрет для настройки
        secret = pyotp.random_base32()
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=current_user.username,
            issuer_name="Production Management"
        )
        return TwoFactorStatusResponse(
            enabled=False,
            setupUrl=totp_uri
        )


@router.post("/2fa/enable", response_model=TwoFactorEnableResponse)
def enable_2fa(
    request: TwoFactorEnableRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Генерировать секрет если его нет
    if not current_user.two_fa_secret:
        current_user.two_fa_secret = pyotp.random_base32()
    
    # Проверить код
    totp = pyotp.TOTP(current_user.two_fa_secret)
    if not totp.verify(request.code):
        raise HTTPException(status_code=400, detail="Invalid code")
    
    # Включить 2FA
    current_user.two_fa_enabled = True
    db.commit()
    
    return TwoFactorEnableResponse(status="success")


@router.get("/login-history", response_model=List[LoginHistoryItem])
def get_login_history(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    history = db.query(LoginHistory).filter(
        LoginHistory.user_id == current_user.id
    ).order_by(LoginHistory.date.desc()).limit(limit).all()
    
    return [
        LoginHistoryItem(
            device=h.device,
            ip=h.ip,
            date=h.date
        ) for h in history
    ]


@router.delete("/account", response_model=AccountDeleteResponse)
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # В продакшене здесь должно быть подтверждение пароля
    # Для демо просто удаляем
    db.delete(current_user)
    db.commit()
    
    return AccountDeleteResponse(status="success")






