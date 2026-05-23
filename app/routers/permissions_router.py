"""
API эндпоинты для получения информации о разрешениях пользователя
"""

from fastapi import APIRouter, Depends
from typing import List
from pydantic import BaseModel

from app.auth import get_current_user
from app.models import User
from app.permissions import get_user_permissions, Role, Permission, has_permission


router = APIRouter(prefix="/api/permissions", tags=["permissions"])


class PermissionsResponse(BaseModel):
    """Ответ с разрешениями пользователя"""
    role: str
    permissions: List[str]
    isAdmin: bool


class PermissionCheckRequest(BaseModel):
    """Запрос для проверки конкретного разрешения"""
    permission: str


class PermissionCheckResponse(BaseModel):
    """Ответ о наличии разрешения"""
    hasPermission: bool
    permission: str


@router.get("/me", response_model=PermissionsResponse)
def get_my_permissions(current_user: User = Depends(get_current_user)):
    """
    Получить все разрешения текущего пользователя

    Этот эндпоинт позволяет фронтенду узнать, какие операции
    доступны текущему пользователю, чтобы скрыть/показать
    соответствующие кнопки и функции
    """
    permissions = get_user_permissions(current_user)

    return PermissionsResponse(
        role=current_user.role,
        permissions=permissions,
        isAdmin=(current_user.role == Role.ADMIN)
    )


@router.post("/check", response_model=PermissionCheckResponse)
def check_permission(
    request: PermissionCheckRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Проверить наличие конкретного разрешения у пользователя

    Пример запроса:
    POST /api/permissions/check
    {
        "permission": "delete_reports"
    }
    """
    has_perm = has_permission(current_user, request.permission)

    return PermissionCheckResponse(
        hasPermission=has_perm,
        permission=request.permission
    )


@router.get("/roles", response_model=dict)
def get_available_roles():
    """
    Получить список всех доступных ролей в системе

    Полезно для администраторов при управлении пользователями
    """
    return {
        "roles": [
            {
                "value": Role.ADMIN,
                "label": "Администратор",
                "description": "Полный доступ ко всем функциям системы"
            },
            {
                "value": Role.USER,
                "label": "Пользователь",
                "description": "Ограниченный доступ к функциям системы"
            }
        ]
    }


@router.get("/all-permissions", response_model=dict)
def get_all_permissions(current_user: User = Depends(get_current_user)):
    """
    Получить список всех разрешений с описаниями

    Только для администраторов - используется при настройке системы
    """
    if current_user.role != Role.ADMIN:
        return {
            "error": "Доступно только администраторам"
        }

    return {
        "permissions": [
            {
                "category": "Отчеты",
                "items": [
                    {"value": Permission.VIEW_REPORTS, "label": "Просмотр отчетов"},
                    {"value": Permission.CREATE_REPORTS, "label": "Создание отчетов"},
                    {"value": Permission.EDIT_REPORTS, "label": "Редактирование отчетов"},
                    {"value": Permission.DELETE_REPORTS, "label": "Удаление отчетов"},
                    {"value": Permission.DOWNLOAD_REPORTS, "label": "Скачивание отчетов"},
                    {"value": Permission.SEND_REPORTS, "label": "Отправка отчетов"},
                ]
            },
            {
                "category": "Оборудование",
                "items": [
                    {"value": Permission.VIEW_EQUIPMENT, "label": "Просмотр оборудования"},
                    {"value": Permission.EDIT_EQUIPMENT, "label": "Редактирование оборудования"},
                    {"value": Permission.DELETE_EQUIPMENT, "label": "Удаление оборудования"},
                    {"value": Permission.CREATE_MAINTENANCE_PLANS, "label": "Создание планов ТО"},
                    {"value": Permission.DELETE_MAINTENANCE_PLANS, "label": "Удаление планов ТО"},
                ]
            },
            {
                "category": "Задачи",
                "items": [
                    {"value": Permission.VIEW_TASKS, "label": "Просмотр задач"},
                    {"value": Permission.CREATE_TASKS, "label": "Создание задач"},
                    {"value": Permission.COMPLETE_TASKS, "label": "Завершение задач"},
                    {"value": Permission.ASSIGN_TASKS, "label": "Назначение задач"},
                ]
            },
            {
                "category": "Данные",
                "items": [
                    {"value": Permission.INPUT_DATA, "label": "Ввод данных"},
                    {"value": Permission.UPLOAD_DATA, "label": "Загрузка данных"},
                    {"value": Permission.VALIDATE_DATA, "label": "Валидация данных"},
                    {"value": Permission.CONSOLIDATE_DATA, "label": "Консолидация данных"},
                    {"value": Permission.VIEW_DATA_HISTORY, "label": "История данных"},
                ]
            },
            {
                "category": "Финансы",
                "items": [
                    {"value": Permission.VIEW_FINANCES, "label": "Просмотр финансов"},
                    {"value": Permission.UPLOAD_FINANCIAL_REPORTS, "label": "Загрузка фин. отчетов"},
                    {"value": Permission.EXPORT_FINANCIAL_REPORTS, "label": "Экспорт фин. отчетов"},
                ]
            },
            {
                "category": "Профиль",
                "items": [
                    {"value": Permission.VIEW_OWN_PROFILE, "label": "Просмотр профиля"},
                    {"value": Permission.EDIT_OWN_PROFILE, "label": "Редактирование профиля"},
                    {"value": Permission.DELETE_OWN_ACCOUNT, "label": "Удаление аккаунта"},
                    {"value": Permission.MANAGE_USERS, "label": "Управление пользователями"},
                ]
            },
            {
                "category": "Система",
                "items": [
                    {"value": Permission.VIEW_SYSTEM_INFO, "label": "Информация о системе"},
                    {"value": Permission.REPORT_BUGS, "label": "Отчеты об ошибках"},
                    {"value": Permission.CHECK_UPDATES, "label": "Проверка обновлений"},
                ]
            },
            {
                "category": "Уведомления",
                "items": [
                    {"value": Permission.VIEW_NOTIFICATIONS, "label": "Просмотр уведомлений"},
                    {"value": Permission.CREATE_NOTIFICATIONS, "label": "Создание уведомлений"},
                    {"value": Permission.MARK_NOTIFICATIONS_READ, "label": "Отметка прочитанными"},
                    {"value": Permission.COMMENT_NOTIFICATIONS, "label": "Комментарии"},
                    {"value": Permission.ASSIGN_NOTIFICATIONS, "label": "Назначение"},
                ]
            }
        ]
    }
