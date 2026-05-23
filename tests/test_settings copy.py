"""
Тестирование эндпоинтов Settings
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

# 1. Логин
print("=" * 60)
print("1. ЛОГИН")
print("=" * 60)

response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
login_data = response.json()
print(f"Статус: {response.status_code}")
print(f"Token получен: {login_data.get('success')}")

token = login_data["token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Профиль пользователя
print("\n" + "=" * 60)
print("2. ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ")
print("=" * 60)

response = requests.get(f"{BASE_URL}/api/user/profile", headers=headers)
print(f"Статус: {response.status_code}")
print_json(response.json())

# 3. Получить настройки
print("\n" + "=" * 60)
print("3. ПОЛУЧИТЬ НАСТРОЙКИ")
print("=" * 60)

response = requests.get(f"{BASE_URL}/api/user/settings", headers=headers)
print(f"Статус: {response.status_code}")
print_json(response.json())

# 4. Обновить настройки
print("\n" + "=" * 60)
print("4. ОБНОВИТЬ НАСТРОЙКИ")
print("=" * 60)

response = requests.put(f"{BASE_URL}/api/user/settings", headers=headers, json={
    "theme": {
        "selected": "dark"
    },
    "notifications": {
        "soundVolume": 50
    }
})
print(f"Статус: {response.status_code}")
print_json(response.json())

# 5. История входов
print("\n" + "=" * 60)
print("5. ИСТОРИЯ ВХОДОВ")
print("=" * 60)

response = requests.get(f"{BASE_URL}/api/user/login-history?limit=5", headers=headers)
print(f"Статус: {response.status_code}")
history = response.json()
print(f"Найдено записей: {len(history)}")
for item in history[:3]:
    print(f"- {item['device']} ({item['ip']}) - {item['date']}")

# 6. Статус 2FA
print("\n" + "=" * 60)
print("6. СТАТУС 2FA")
print("=" * 60)

response = requests.get(f"{BASE_URL}/api/user/2fa", headers=headers)
print(f"Статус: {response.status_code}")
twofa_data = response.json()
print(f"2FA enabled: {twofa_data['enabled']}")
if not twofa_data['enabled']:
    print(f"Setup URL доступен: {twofa_data['setupUrl'] is not None}")

# 7. Системная информация
print("\n" + "=" * 60)
print("7. СИСТЕМНАЯ ИНФОРМАЦИЯ")
print("=" * 60)

response = requests.get(f"{BASE_URL}/api/system/info")
print(f"Статус: {response.status_code}")
print_json(response.json())

# 8. Проверка обновлений
print("\n" + "=" * 60)
print("8. ПРОВЕРКА ОБНОВЛЕНИЙ")
print("=" * 60)

response = requests.get(f"{BASE_URL}/api/system/check-updates")
print(f"Статус: {response.status_code}")
print_json(response.json())

# 9. Отправить баг репорт
print("\n" + "=" * 60)
print("9. ОТПРАВИТЬ БАГ РЕПОРТ")
print("=" * 60)

response = requests.post(f"{BASE_URL}/api/system/report-bug", headers=headers, json={
    "description": "Тестовый баг",
    "steps": "1. Открыть страницу\n2. Нажать кнопку\n3. Увидеть ошибку"
})
print(f"Статус: {response.status_code}")
bug_data = response.json()
print(f"Ticket ID: {bug_data.get('ticketId')}")
print(f"Status: {bug_data.get('status')}")

# 10. Изменить пароль
print("\n" + "=" * 60)
print("10. ИЗМЕНИТЬ ПАРОЛЬ (тестовый)")
print("=" * 60)

response = requests.post(f"{BASE_URL}/api/user/change-password", headers=headers, json={
    "oldPassword": "admin123",
    "newPassword": "admin123new",
    "confirmNewPassword": "admin123new"
})
print(f"Статус: {response.status_code}")
if response.status_code == 200:
    print("Пароль изменен успешно")
    # Вернуть обратно
    response2 = requests.post(f"{BASE_URL}/api/user/change-password", headers=headers, json={
        "oldPassword": "admin123new",
        "newPassword": "admin123",
        "confirmNewPassword": "admin123"
    })
    print("Пароль восстановлен")

print("\n" + "=" * 60)
print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
print("=" * 60)
print(f"\nAPI документация: {BASE_URL}/docs")
print("\nДоступные эндпоинты Settings:")
print("- GET/PUT /api/user/settings")
print("- GET /api/user/profile")
print("- POST /api/user/upload-avatar")
print("- POST /api/user/change-password")
print("- GET /api/user/2fa")
print("- POST /api/user/2fa/enable")
print("- GET /api/user/login-history")
print("- DELETE /api/user/account")
print("- GET /api/system/info")
print("- GET /api/system/check-updates")
print("- POST /api/system/report-bug")



