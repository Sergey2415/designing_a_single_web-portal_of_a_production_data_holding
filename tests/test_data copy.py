"""
Тестирование эндпоинтов Data Management
"""
import requests
import json
import io

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
login_data = response.json()
print(f"Статус: {response.status_code}")
token = login_data["token"]
# Получаем user_id из поля user
user_id = login_data["user"]["id"]
headers = {"Authorization": f"Bearer {token}"}
print(f"User ID: {user_id}")

# 2. Ручной ввод данных
print_section("2. РУЧНОЙ ВВОД ДАННЫХ")
manual_data = {
    "date": "2025-10-29",
    "type": "production",
    "value": 1500.0,
    "comment": "Тестовая запись через API",
    "userId": user_id
}
response = requests.post(f"{BASE_URL}/api/data/manual", json=manual_data, headers=headers)
print(f"Статус: {response.status_code}")
result = response.json()
print(f"Результат: {json.dumps(result, indent=2, ensure_ascii=False)}")

# 3. Создание CSV файла для загрузки
print_section("3. ПОДГОТОВКА CSV ДЛЯ ЗАГРУЗКИ")
csv_content = """date;type;value;comment
2025-10-28;production;1200.5;Производство смена 1
2025-10-28;downtime;1.5;Простой оборудования
2025-10-27;production;1150.0;Производство смена 2
"""
print(f"CSV содержимое:\n{csv_content}")

# 4. Загрузка CSV файла
print_section("4. ЗАГРУЗКА CSV ФАЙЛА")
files = {"file": ("test_data.csv", io.BytesIO(csv_content.encode('utf-8-sig')), "text/csv")}
data = {"userId": user_id}
response = requests.post(f"{BASE_URL}/api/data/upload", files=files, data=data, headers=headers)
print(f"Статус: {response.status_code}")
upload_result = response.json()
print(f"Результат: {json.dumps(upload_result, indent=2, ensure_ascii=False)}")

upload_id = upload_result.get("id") if upload_result.get("success") else None

# 5. Валидация загруженных данных
if upload_id:
    print_section("5. ВАЛИДАЦИЯ ДАННЫХ")
    validate_data = {
        "uploadId": upload_id,
        "userId": user_id
    }
    response = requests.post(f"{BASE_URL}/api/data/validate", json=validate_data, headers=headers)
    print(f"Статус: {response.status_code}")
    validate_result = response.json()
    print(f"Результат: {json.dumps(validate_result, indent=2, ensure_ascii=False)}")
    print(f"Валидация успешна: {validate_result.get('validated')}")
    print(f"Проблем найдено: {len(validate_result.get('issues', []))}")

# 6. Консолидация данных
if upload_id:
    print_section("6. КОНСОЛИДАЦИЯ ДАННЫХ")
    consolidate_data = {
        "uploadId": upload_id,
        "department": "Производственный отдел",
        "userId": user_id
    }
    response = requests.post(f"{BASE_URL}/api/data/consolidate", json=consolidate_data, headers=headers)
    print(f"Статус: {response.status_code}")
    consolidate_result = response.json()
    print(f"Результат: {json.dumps(consolidate_result, indent=2, ensure_ascii=False)}")

# 7. История изменений (все)
print_section("7. ИСТОРИЯ ИЗМЕНЕНИЙ (ВСЕ)")
response = requests.get(f"{BASE_URL}/api/data/history?page=1&limit=5&status=all", headers=headers)
print(f"Статус: {response.status_code}")
history = response.json()
print(f"Всего записей: {history.get('total')}")
print(f"Страниц: {history.get('pages')}")
print(f"\nПоследние записи:")
for item in history.get('data', [])[:3]:
    print(f"  - [{item['status']}] {item['comment']} (пользователь: {item['user']}, дата: {item['date']})")

# 8. История по статусу (accepted)
print_section("8. ИСТОРИЯ ПО СТАТУСУ (ACCEPTED)")
response = requests.get(f"{BASE_URL}/api/data/history?page=1&limit=5&status=accepted", headers=headers)
print(f"Статус: {response.status_code}")
history_accepted = response.json()
print(f"Записей со статусом 'accepted': {history_accepted.get('total')}")
for item in history_accepted.get('data', []):
    print(f"  - {item['comment']}")

# 9. Ошибка валидации (отрицательное значение)
print_section("9. ТЕСТ ОШИБКИ (ОТРИЦАТЕЛЬНОЕ ЗНАЧЕНИЕ)")
bad_manual_data = {
    "date": "2025-10-29",
    "type": "production",
    "value": -100.0,
    "comment": "Невалидные данные",
    "userId": user_id
}
response = requests.post(f"{BASE_URL}/api/data/manual", json=bad_manual_data, headers=headers)
print(f"Статус: {response.status_code}")
if response.status_code == 400:
    print("Корректно возвращена ошибка 400")
    print(f"Сообщение: {response.json()}")

# 10. Ошибка валидации (неверная дата)
print_section("10. ТЕСТ ОШИБКИ (НЕВЕРНАЯ ДАТА)")
bad_date_data = {
    "date": "invalid-date",
    "type": "production",
    "value": 100.0,
    "comment": "Невалидная дата",
    "userId": user_id
}
response = requests.post(f"{BASE_URL}/api/data/manual", json=bad_date_data, headers=headers)
print(f"Статус: {response.status_code}")
if response.status_code == 400:
    print("Корректно возвращена ошибка 400")

print_section("ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")
print(f"\nAPI документация: {BASE_URL}/docs")
print("\nДоступные эндпоинты Data Management:")
print("- POST /api/data/manual")
print("- POST /api/data/upload")
print("- POST /api/data/validate")
print("- POST /api/data/consolidate")
print("- GET /api/data/history?page=1&limit=10&status=all")

