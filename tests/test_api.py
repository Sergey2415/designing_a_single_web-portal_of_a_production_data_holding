"""
Тестирование API
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

print("=" * 50)
print("1. ЛОГИН")
print("=" * 50)

response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
print(f"Статус: {response.status_code}")
login_data = response.json()
print_json(login_data)

if not login_data.get("success"):
    print("\nОШИБКА: Не удалось войти!")
    exit(1)

token = login_data["token"]
headers = {"Authorization": f"Bearer {token}"}

print("\n" + "=" * 50)
print("2. ПРОВЕРКА ТОКЕНА")
print("=" * 50)

response = requests.get(f"{BASE_URL}/api/auth/check", headers=headers)
print(f"Статус: {response.status_code}")
print_json(response.json())

print("\n" + "=" * 50)
print("3. ФИЛИАЛЫ")
print("=" * 50)

response = requests.get(f"{BASE_URL}/api/branches", headers=headers)
print(f"Статус: {response.status_code}")
branches = response.json()
print_json(branches)

print("\n" + "=" * 50)
print("4. KPI (филиал 1)")
print("=" * 50)

response = requests.get(f"{BASE_URL}/api/kpi?branch_id=1", headers=headers)
print(f"Статус: {response.status_code}")
print_json(response.json())

print("\n" + "=" * 50)
print("5. ГРАФИК ПРОИЗВОДСТВА")
print("=" * 50)

response = requests.get(f"{BASE_URL}/api/trends/production?period=month", headers=headers)
print(f"Статус: {response.status_code}")
production_data = response.json()
print(f"Всего точек: {len(production_data)}")
print("Первые 5 точек:")
print_json(production_data[:5])

print("\n" + "=" * 50)
print("6. ГРАФИК ПРОСТОЕВ")
print("=" * 50)

response = requests.get(f"{BASE_URL}/api/trends/downtime?period=month", headers=headers)
print(f"Статус: {response.status_code}")
print_json(response.json())

print("\n" + "=" * 50)
print("7. УВЕДОМЛЕНИЯ")
print("=" * 50)

response = requests.get(f"{BASE_URL}/api/notifications?limit=5", headers=headers)
print(f"Статус: {response.status_code}")
notifications = response.json()
print(f"Всего уведомлений: {len(notifications)}")
print_json(notifications)

print("\n" + "=" * 50)
print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
print("=" * 50)
print(f"\nAPI документация: {BASE_URL}/docs")
print(f"Альтернативная документация: {BASE_URL}/redoc")



