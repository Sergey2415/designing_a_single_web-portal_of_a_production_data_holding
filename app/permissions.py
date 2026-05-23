"""
Role-Based Access Control (RBAC) для Production Management System

Этот модуль предоставляет декораторы и функции для управления доступом
на основе ролей пользователей.
"""

from functools import wraps
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.auth import get_current_user
from app.models import User
from typing import List, Callable


class Role:
    """Определение ролей в системе"""
    ADMIN = "admin"
    USER = "user"


class Permission:
    """Определение разрешений для различных операций"""

    # Управление отчетами
    VIEW_REPORTS = "view_reports"
    CREATE_REPORTS = "create_reports"
    EDIT_REPORTS = "edit_reports"
    DELETE_REPORTS = "delete_reports"
    DOWNLOAD_REPORTS = "download_reports"
    SEND_REPORTS = "send_reports"

    # Управление оборудованием
    VIEW_EQUIPMENT = "view_equipment"
    EDIT_EQUIPMENT = "edit_equipment"
    DELETE_EQUIPMENT = "delete_equipment"
    CREATE_MAINTENANCE_PLANS = "create_maintenance_plans"
    DELETE_MAINTENANCE_PLANS = "delete_maintenance_plans"

    # Управление задачами
    VIEW_TASKS = "view_tasks"
    CREATE_TASKS = "create_tasks"
    COMPLETE_TASKS = "complete_tasks"
    ASSIGN_TASKS = "assign_tasks"

    # Управление данными
    INPUT_DATA = "input_data"
    UPLOAD_DATA = "upload_data"
    VALIDATE_DATA = "validate_data"
    CONSOLIDATE_DATA = "consolidate_data"
    VIEW_DATA_HISTORY = "view_data_history"

    # Финансы
    VIEW_FINANCES = "view_finances"
    UPLOAD_FINANCIAL_REPORTS = "upload_financial_reports"
    EXPORT_FINANCIAL_REPORTS = "export_financial_reports"

    # Управление пользователями
    VIEW_OWN_PROFILE = "view_own_profile"
    EDIT_OWN_PROFILE = "edit_own_profile"
    DELETE_OWN_ACCOUNT = "delete_own_account"
    MANAGE_USERS = "manage_users"

    # Система
    VIEW_SYSTEM_INFO = "view_system_info"
    REPORT_BUGS = "report_bugs"
    CHECK_UPDATES = "check_updates"

    # Уведомления
    VIEW_NOTIFICATIONS = "view_notifications"
    CREATE_NOTIFICATIONS = "create_notifications"
    MARK_NOTIFICATIONS_READ = "mark_notifications_read"
    COMMENT_NOTIFICATIONS = "comment_notifications"
    ASSIGN_NOTIFICATIONS = "assign_notifications"


# Матрица разрешений: какие роли имеют какие разрешения
ROLE_PERMISSIONS = {
    Role.ADMIN: [
        # Администратор имеет все разрешения
        Permission.VIEW_REPORTS,
        Permission.CREATE_REPORTS,
        Permission.EDIT_REPORTS,
        Permission.DELETE_REPORTS,
        Permission.DOWNLOAD_REPORTS,
        Permission.SEND_REPORTS,

        Permission.VIEW_EQUIPMENT,
        Permission.EDIT_EQUIPMENT,
        Permission.DELETE_EQUIPMENT,
        Permission.CREATE_MAINTENANCE_PLANS,
        Permission.DELETE_MAINTENANCE_PLANS,

        Permission.VIEW_TASKS,
        Permission.CREATE_TASKS,
        Permission.COMPLETE_TASKS,
        Permission.ASSIGN_TASKS,

        Permission.INPUT_DATA,
        Permission.UPLOAD_DATA,
        Permission.VALIDATE_DATA,
        Permission.CONSOLIDATE_DATA,
        Permission.VIEW_DATA_HISTORY,

        Permission.VIEW_FINANCES,
        Permission.UPLOAD_FINANCIAL_REPORTS,
        Permission.EXPORT_FINANCIAL_REPORTS,

        Permission.VIEW_OWN_PROFILE,
        Permission.EDIT_OWN_PROFILE,
        Permission.DELETE_OWN_ACCOUNT,
        Permission.MANAGE_USERS,

        Permission.VIEW_SYSTEM_INFO,
        Permission.REPORT_BUGS,
        Permission.CHECK_UPDATES,

        Permission.VIEW_NOTIFICATIONS,
        Permission.CREATE_NOTIFICATIONS,
        Permission.MARK_NOTIFICATIONS_READ,
        Permission.COMMENT_NOTIFICATIONS,
        Permission.ASSIGN_NOTIFICATIONS,
    ],

    Role.USER: [
        # Обычный пользователь имеет ограниченные разрешения
        Permission.VIEW_REPORTS,
        Permission.CREATE_REPORTS,
        Permission.DOWNLOAD_REPORTS,
        # НЕТ: DELETE_REPORTS, EDIT_REPORTS (кроме своих)

        Permission.VIEW_EQUIPMENT,
        # НЕТ: EDIT_EQUIPMENT, DELETE_EQUIPMENT

        Permission.VIEW_TASKS,
        Permission.CREATE_TASKS,
        Permission.COMPLETE_TASKS,
        # НЕТ: ASSIGN_TASKS (только admin может назначать)

        Permission.INPUT_DATA,
        Permission.UPLOAD_DATA,
        Permission.VALIDATE_DATA,
        # НЕТ: CONSOLIDATE_DATA (только admin)
        Permission.VIEW_DATA_HISTORY,

        Permission.VIEW_FINANCES,
        # НЕТ: UPLOAD_FINANCIAL_REPORTS (только admin)
        Permission.EXPORT_FINANCIAL_REPORTS,

        Permission.VIEW_OWN_PROFILE,
        Permission.EDIT_OWN_PROFILE,
        Permission.DELETE_OWN_ACCOUNT,
        # НЕТ: MANAGE_USERS

        Permission.VIEW_SYSTEM_INFO,
        Permission.REPORT_BUGS,
        # НЕТ: CHECK_UPDATES (только admin)

        Permission.VIEW_NOTIFICATIONS,
        Permission.MARK_NOTIFICATIONS_READ,
        Permission.COMMENT_NOTIFICATIONS,
        # НЕТ: CREATE_NOTIFICATIONS, ASSIGN_NOTIFICATIONS (только admin)
    ]
}


def has_permission(user: User, permission: str) -> bool:
    """
    Проверяет, имеет ли пользователь определенное разрешение

    Args:
        user: Объект пользователя
        permission: Название разрешения из класса Permission

    Returns:
        True если пользователь имеет разрешение, False иначе
    """
    user_permissions = ROLE_PERMISSIONS.get(user.role, [])
    return permission in user_permissions


def require_permission(permission: str):
    """
    Декоратор для проверки разрешения на выполнение операции

    Usage:
        @router.delete("/reports/{id}")
        @require_permission(Permission.DELETE_REPORTS)
        def delete_report(report_id: str, user: User = Depends(get_current_user)):
            ...

    Args:
        permission: Название разрешения из класса Permission
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Получаем пользователя из аргументов функции
            user = kwargs.get('current_user') or kwargs.get('user')

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Требуется авторизация"
                )

            if not has_permission(user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Недостаточно прав для выполнения операции"
                )

            return await func(*args, **kwargs) if callable(func) and hasattr(func, '__await__') else func(*args, **kwargs)

        return wrapper
    return decorator


def require_role(allowed_roles: List[str]):
    """
    Декоратор для проверки роли пользователя

    Usage:
        @router.delete("/equipment/{id}")
        @require_role([Role.ADMIN])
        def delete_equipment(equipment_id: str, user: User = Depends(get_current_user)):
            ...

    Args:
        allowed_roles: Список разрешенных ролей
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Получаем пользователя из аргументов функции
            user = kwargs.get('current_user') or kwargs.get('user')

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Требуется авторизация"
                )

            if user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Недостаточно прав для выполнения операции"
                )

            return await func(*args, **kwargs) if callable(func) and hasattr(func, '__await__') else func(*args, **kwargs)

        return wrapper
    return decorator


def check_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency для проверки, что пользователь является администратором

    Usage:
        @router.delete("/reports/{id}")
        def delete_report(report_id: str, admin: User = Depends(check_admin)):
            ...

    Args:
        current_user: Текущий аутентифицированный пользователь

    Returns:
        User объект если пользователь admin

    Raises:
        HTTPException: Если пользователь не является администратором
    """
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора"
        )
    return current_user


def check_permission(permission: str, current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency для проверки конкретного разрешения

    Usage:
        @router.post("/data/consolidate")
        def consolidate_data(
            data: ConsolidateRequest,
            user: User = Depends(lambda u=Depends(get_current_user): check_permission(Permission.CONSOLIDATE_DATA, u))
        ):
            ...

    Args:
        permission: Название разрешения
        current_user: Текущий аутентифицированный пользователь

    Returns:
        User объект если пользователь имеет разрешение

    Raises:
        HTTPException: Если у пользователя нет разрешения
    """
    if not has_permission(current_user, permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения операции"
        )
    return current_user


def get_user_permissions(user: User) -> List[str]:
    """
    Получить список всех разрешений для пользователя

    Args:
        user: Объект пользователя

    Returns:
        Список названий разрешений
    """
    return ROLE_PERMISSIONS.get(user.role, [])


def can_delete_report(user: User, report_author: str) -> bool:
    """
    Проверяет, может ли пользователь удалить отчет
    Admin может удалить любой отчет
    User может удалить только свой отчет

    Args:
        user: Объект пользователя
        report_author: Автор отчета

    Returns:
        True если пользователь может удалить отчет
    """
    if user.role == Role.ADMIN:
        return True
    return user.name == report_author


def can_edit_equipment(user: User) -> bool:
    """
    Проверяет, может ли пользователь редактировать оборудование
    Только администраторы могут редактировать оборудование

    Args:
        user: Объект пользователя

    Returns:
        True если пользователь может редактировать
    """
    return user.role == Role.ADMIN
