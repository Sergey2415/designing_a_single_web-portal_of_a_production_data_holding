"""
Тестирование эндпоинтов Profile
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")

# 1. Логин
print_section("1. ЛОГИН")
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
token = response.json()["token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"Статус: {response.status_code}")
print("Token получен")

# 2. Получение профиля
print_section("2. ПОЛУЧЕНИЕ ПРОФИЛЯ")
response = requests.get(f"{BASE_URL}/api/profile", headers=headers)
print(f"Статус: {response.status_code}")
profile = response.json()
print(json.dumps(profile, indent=2, ensure_ascii=False))
if profile.get("success"):
    data = profile["data"]
    print(f"\nИмя: {data['name']}")
    print(f"Должность: {data['position']}")
    print(f"Местоположение: {data['location']}")
    print(f"Уровень доступа: {data['accessLevel']}")

# 3. Обновление профиля
print_section("3. ОБНОВЛЕНИЕ ПРОФИЛЯ")
update_request = {
    "name": "Иванов Иван Иванович (Обновлено)",
    "position": "Главный директор",
    "location": "Москва, ул. Центральная, 1",
    "email": "ivan.ivanov@company.com",
    "phone": "+7 (495) 999-99-99"
}
response = requests.put(f"{BASE_URL}/api/profile", json=update_request, headers=headers)
print(f"Статус: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# Проверка обновления
response = requests.get(f"{BASE_URL}/api/profile", headers=headers)
updated_profile = response.json()
if updated_profile.get("success"):
    print(f"\nПроверка: Имя теперь '{updated_profile['data']['name']}'")

# 4. Смена пароля
print_section("4. СМЕНА ПАРОЛЯ")
password_request = {
    "currentPassword": "admin123",
    "newPassword": "newpassword123",
    "confirmPassword": "newpassword123"
}
response = requests.post(f"{BASE_URL}/api/profile/password", json=password_request, headers=headers)
print(f"Статус: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# Вернем пароль обратно
if response.status_code == 200:
    restore_request = {
        "currentPassword": "newpassword123",
        "newPassword": "admin123",
        "confirmPassword": "admin123"
    }
    requests.post(f"{BASE_URL}/api/profile/password", json=restore_request, headers=headers)
    print("Пароль восстановлен обратно")

# 5. Тест ошибки смены пароля (неверный текущий)
print_section("5. ТЕСТ: НЕВЕРНЫЙ ТЕКУЩИЙ ПАРОЛЬ")
wrong_password = {
    "currentPassword": "wrongpassword",
    "newPassword": "test123",
    "confirmPassword": "test123"
}
response = requests.post(f"{BASE_URL}/api/profile/password", json=wrong_password, headers=headers)
print(f"Статус: {response.status_code}")
if response.status_code == 400:
    print("Корректно: ошибка при неверном текущем пароле")

# 6. Тест ошибки смены пароля (пароли не совпадают)
print_section("6. ТЕСТ: ПАРОЛИ НЕ СОВПАДАЮТ")
mismatch_password = {
    "currentPassword": "admin123",
    "newPassword": "test123",
    "confirmPassword": "test456"
}
response = requests.post(f"{BASE_URL}/api/profile/password", json=mismatch_password, headers=headers)
print(f"Статус: {response.status_code}")
if response.status_code == 400:
    print("Корректно: ошибка при несовпадении паролей")

# 7. Персональные метрики
print_section("7. ПЕРСОНАЛЬНЫЕ МЕТРИКИ")
response = requests.get(f"{BASE_URL}/api/profile/metrics", headers=headers)
print(f"Статус: {response.status_code}")
metrics = response.json()
print(json.dumps(metrics, indent=2, ensure_ascii=False))
if metrics.get("success"):
    data = metrics["data"]
    print(f"\nПроизводительность труда: {data['laborProductivity']['value']}% (изменение: {data['laborProductivity']['change']}%)")
    print(f"Эффективность ремонта: {data['repairEfficiency']['value']}% (изменение: {data['repairEfficiency']['change']}%)")
    print(f"Простой оборудования: {data['equipmentDowntime']['value']}% (изменение: {data['equipmentDowntime']['change']}%)")
    print(f"Себестоимость: {data['cost']['value']} (изменение: {data['cost']['change']}%)")

# 8. Активность пользователя
print_section("8. АКТИВНОСТЬ ПОЛЬЗОВАТЕЛЯ")
response = requests.get(f"{BASE_URL}/api/profile/activity?limit=5", headers=headers)
print(f"Статус: {response.status_code}")
activity = response.json()
if activity.get("success"):
    print(f"Найдено активностей: {len(activity['data'])}")
    for item in activity['data']:
        print(f"  - [{item['type']}] {item['description']} ({item['timestamp']})")

# 9. Задачи пользователя
print_section("9. ЗАДАЧИ И УВЕДОМЛЕНИЯ")
response = requests.get(f"{BASE_URL}/api/profile/tasks?limit=5", headers=headers)
print(f"Статус: {response.status_code}")
tasks_data = response.json()
if tasks_data.get("success"):
    print(f"Найдено задач: {len(tasks_data['data'])}")
    for item in tasks_data['data']:
        task_type = "Уведомление" if item['isNotification'] else "Задача"
        deadline = f" (срок: {item['deadline']})" if item.get('deadline') else ""
        print(f"  - [{task_type}] {item['title']} - приоритет: {item['priority']}{deadline}")

# 10. Команда пользователя
print_section("10. КОМАНДА")
response = requests.get(f"{BASE_URL}/api/profile/team", headers=headers)
print(f"Статус: {response.status_code}")
team = response.json()
if team.get("success"):
    print(f"Членов команды: {len(team['data'])}")
    for member in team['data']:
        print(f"  - {member['name']}: {member['status']}")

# 11. Отчеты пользователя
print_section("11. ОТЧЕТЫ")
response = requests.get(f"{BASE_URL}/api/profile/reports", headers=headers)
print(f"Статус: {response.status_code}")
reports = response.json()
if reports.get("success"):
    print(f"Отчетов: {len(reports['data'])}")
    for report in reports['data']:
        print(f"  - {report['branch']}: Метрика1={report['metric1']}, Метрика2={report['metric2']}, Метрика3={report['metric3']}")

# 12. Тест с обычным пользователем
print_section("12. ТЕСТ: ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ")
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "username": "user",
    "password": "user123"
})
user_token = response.json()["token"]
user_headers = {"Authorization": f"Bearer {user_token}"}

response = requests.get(f"{BASE_URL}/api/profile", headers=user_headers)
user_profile = response.json()
if user_profile.get("success"):
    print(f"Имя: {user_profile['data']['name']}")
    print(f"Должность: {user_profile['data']['position']}")
    print(f"Уровень доступа: {user_profile['data']['accessLevel']}")

# Метрики обычного пользователя
response = requests.get(f"{BASE_URL}/api/profile/metrics", headers=user_headers)
user_metrics = response.json()
if user_metrics.get("success"):
    print(f"\nМетрики пользователя:")
    print(f"  Производительность: {user_metrics['data']['laborProductivity']['value']}%")

print_section("ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")
print(f"\nAPI документация: {BASE_URL}/docs")
print("\nДоступные эндпоинты Profile:")
print("- GET /api/profile")
print("- PUT /api/profile")
print("- POST /api/profile/password")
print("- GET /api/profile/metrics")
print("- GET /api/profile/activity?limit=10")
print("- GET /api/profile/tasks?limit=10")
print("- GET /api/profile/team")
print("- GET /api/profile/reports")


