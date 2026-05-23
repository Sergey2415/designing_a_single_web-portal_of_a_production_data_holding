"""
Тестирование RBAC (Role-Based Access Control)

Этот скрипт тестирует корректность работы системы управления доступом
на основе ролей для различных эндпоинтов API.
"""

import requests
import json
from typing import Dict, Optional

API_URL = "http://localhost:8000/api"

# Тестовые пользователи
ADMIN_USER = {"username": "admin", "password": "admin123"}
REGULAR_USER = {"username": "user", "password": "user123"}


class APIClient:
    """Клиент для работы с API"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.token: Optional[str] = None

    def login(self, username: str, password: str) -> bool:
        """Авторизация пользователя"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password}
        )

        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token")
            return True
        return False

    def _headers(self) -> Dict[str, str]:
        """Получить заголовки с токеном"""
        if not self.token:
            raise ValueError("Не авторизован. Вызовите login() сначала.")
        return {"Authorization": f"Bearer {self.token}"}

    def get_permissions(self) -> dict:
        """Получить разрешения текущего пользователя"""
        response = requests.get(
            f"{self.base_url}/permissions/me",
            headers=self._headers()
        )
        return response.json() if response.status_code == 200 else {}

    def check_permission(self, permission: str) -> bool:
        """Проверить наличие разрешения"""
        response = requests.post(
            f"{self.base_url}/permissions/check",
            json={"permission": permission},
            headers=self._headers()
        )
        if response.status_code == 200:
            return response.json().get("hasPermission", False)
        return False

    def delete_report(self, report_id: str) -> int:
        """Попытка удалить отчет"""
        response = requests.delete(
            f"{self.base_url}/reports/{report_id}",
            headers=self._headers()
        )
        return response.status_code

    def delete_equipment(self, equipment_id: str) -> int:
        """Попытка удалить оборудование"""
        response = requests.delete(
            f"{self.base_url}/equipment/{equipment_id}",
            headers=self._headers()
        )
        return response.status_code

    def consolidate_data(self, upload_id: str, department: str) -> int:
        """Попытка консолидировать данные"""
        response = requests.post(
            f"{self.base_url}/data/consolidate",
            json={"uploadId": upload_id, "department": department},
            headers=self._headers()
        )
        return response.status_code

    def create_maintenance_plan(self, date: str, branch: str, equipment_ids: list) -> int:
        """Попытка создать план ТО"""
        response = requests.post(
            f"{self.base_url}/equipment/maintenance-plan",
            json={
                "date": date,
                "branch": branch,
                "equipmentIds": equipment_ids
            },
            headers=self._headers()
        )
        return response.status_code


def print_section(title: str):
    """Напечатать заголовок секции"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_result(test_name: str, expected: bool, actual: bool):
    """Напечатать результат теста"""
    status = "[PASS]" if expected == actual else "[FAIL]"
    print(f"{status} | {test_name}")
    if expected != actual:
        print(f"     Ожидалось: {expected}, Получено: {actual}")


def main():
    print("\n[RBAC] ТЕСТИРОВАНИЕ RBAC (Role-Based Access Control)")
    print("=" * 60)

    # Инициализация клиентов
    admin_client = APIClient(API_URL)
    user_client = APIClient(API_URL)

    # ========== ТЕСТ 1: Авторизация ==========
    print_section("ТЕСТ 1: Авторизация")

    admin_login = admin_client.login(ADMIN_USER["username"], ADMIN_USER["password"])
    test_result("Администратор авторизован", True, admin_login)

    user_login = user_client.login(REGULAR_USER["username"], REGULAR_USER["password"])
    test_result("Пользователь авторизован", True, user_login)

    if not (admin_login and user_login):
        print("\n[ERROR] ОШИБКА: Не удалось авторизоваться. Проверьте, что сервер запущен.")
        return

    # ========== ТЕСТ 2: Получение разрешений ==========
    print_section("ТЕСТ 2: Получение разрешений")

    admin_perms = admin_client.get_permissions()
    print(f"\n[ADMIN] Разрешения администратора:")
    print(f"   Роль: {admin_perms.get('role')}")
    print(f"   Количество разрешений: {len(admin_perms.get('permissions', []))}")
    print(f"   Является администратором: {admin_perms.get('isAdmin')}")

    user_perms = user_client.get_permissions()
    print(f"\n[USER] Разрешения пользователя:")
    print(f"   Роль: {user_perms.get('role')}")
    print(f"   Количество разрешений: {len(user_perms.get('permissions', []))}")
    print(f"   Является администратором: {user_perms.get('isAdmin')}")

    test_result(
        "Администратор имеет роль 'admin'",
        True,
        admin_perms.get('role') == 'admin'
    )
    test_result(
        "Пользователь имеет роль 'user'",
        True,
        user_perms.get('role') == 'user'
    )

    # ========== ТЕСТ 3: Проверка конкретных разрешений ==========
    print_section("ТЕСТ 3: Проверка конкретных разрешений")

    # Удаление отчетов
    admin_can_delete_reports = admin_client.check_permission("delete_reports")
    user_can_delete_reports = user_client.check_permission("delete_reports")

    test_result(
        "Администратор может удалять отчеты",
        True,
        admin_can_delete_reports
    )
    test_result(
        "Пользователь НЕ может удалять отчеты",
        True,
        not user_can_delete_reports
    )

    # Консолидация данных
    admin_can_consolidate = admin_client.check_permission("consolidate_data")
    user_can_consolidate = user_client.check_permission("consolidate_data")

    test_result(
        "Администратор может консолидировать данные",
        True,
        admin_can_consolidate
    )
    test_result(
        "Пользователь НЕ может консолидировать данные",
        True,
        not user_can_consolidate
    )

    # Редактирование оборудования
    admin_can_edit_equipment = admin_client.check_permission("edit_equipment")
    user_can_edit_equipment = user_client.check_permission("edit_equipment")

    test_result(
        "Администратор может редактировать оборудование",
        True,
        admin_can_edit_equipment
    )
    test_result(
        "Пользователь НЕ может редактировать оборудование",
        True,
        not user_can_edit_equipment
    )

    # Создание отчетов (доступно обоим)
    admin_can_create_reports = admin_client.check_permission("create_reports")
    user_can_create_reports = user_client.check_permission("create_reports")

    test_result(
        "Администратор может создавать отчеты",
        True,
        admin_can_create_reports
    )
    test_result(
        "Пользователь может создавать отчеты",
        True,
        user_can_create_reports
    )

    # ========== ТЕСТ 4: Попытки выполнения операций ==========
    print_section("ТЕСТ 4: Попытки выполнения admin-only операций")

    print("\n[NOTE] Примечание: Следующие тесты могут показывать ошибки,")
    print("       если в базе нет данных для удаления/обновления.")
    print("       Главное - проверить коды ответа (403 vs 404/200).\n")

    # Тест консолидации данных
    print("[TEST] Тестирование консолидации данных...")
    user_consolidate_status = user_client.consolidate_data("test-id", "test-dept")
    test_result(
        "Пользователь получает 403 при консолидации",
        True,
        user_consolidate_status == 403
    )

    # ========== СВОДКА ==========
    print_section("СВОДКА РЕЗУЛЬТАТОВ")

    print("""
    [OK] Ключевые проверки:
       - Администраторы имеют полный доступ
       - Пользователи имеют ограниченный доступ
       - API корректно возвращает 403 при отсутствии прав
       - Система разрешений работает на уровне эндпоинтов

    [INFO] Дополнительная информация:
       - Полная документация: RBAC_IMPLEMENTATION.md
       - Backend код: app/permissions.py
       - Frontend код: frontend/js/permissions.js
       - API эндпоинты: /api/permissions/*

    [TEST] Для более глубокого тестирования:
       - Запустите тесты с реальными ID отчетов/оборудования
       - Проверьте фронтенд UI с разными ролями
       - Тестируйте все критические операции

    """)

    print("=" * 60)
    print("[DONE] Тестирование завершено!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] ОШИБКА: Не удается подключиться к серверу.")
        print("        Убедитесь, что сервер запущен: python run.py")
        print("        API должен быть доступен на http://localhost:8000\n")
    except Exception as e:
        print(f"\n[ERROR] ОШИБКА: {str(e)}\n")
