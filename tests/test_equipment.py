"""
Тестирование эндпоинтов Equipment
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

# 2. Список оборудования (все)
print_section("2. СПИСОК ОБОРУДОВАНИЯ (ВСЕ)")
response = requests.get(f"{BASE_URL}/api/equipment?page=1&limit=10", headers=headers)
print(f"Статус: {response.status_code}")
equipment_list = response.json()
print(f"Всего оборудования: {equipment_list.get('total')}")
print(f"Страниц: {equipment_list.get('pages')}")
print("\nПервые записи:")
for item in equipment_list.get('data', [])[:3]:
    print(f"  - {item['name']}: {item['branch']}, {item['status']} (Проверка: {item.get('lastCheck', 'Не указана')})")

# Сохраним ID для дальнейших тестов
equipment_id = equipment_list['data'][0]['id'] if equipment_list.get('data') else None
print(f"\nВыбрано для тестов: {equipment_id}")

# 3. Фильтр по филиалу (Москва)
print_section("3. ФИЛЬТР ПО ФИЛИАЛУ (МОСКВА)")
response = requests.get(f"{BASE_URL}/api/equipment?branch=Москва", headers=headers)
print(f"Статус: {response.status_code}")
moscow_equipment = response.json()
print(f"Оборудование в Москве: {moscow_equipment.get('total')}")
for item in moscow_equipment.get('data', []):
    print(f"  - {item['name']}: {item['type']}")

# 4. Фильтр по типу (production)
print_section("4. ФИЛЬТР ПО ТИПУ (PRODUCTION)")
response = requests.get(f"{BASE_URL}/api/equipment?type=production", headers=headers)
print(f"Статус: {response.status_code}")
production_equipment = response.json()
print(f"Производственное оборудование: {production_equipment.get('total')}")

# 5. Фильтр по статусу (ready)
print_section("5. ФИЛЬТР ПО СТАТУСУ (READY)")
response = requests.get(f"{BASE_URL}/api/equipment?status=ready", headers=headers)
print(f"Статус: {response.status_code}")
ready_equipment = response.json()
print(f"Готовое оборудование: {ready_equipment.get('total')}")

# 6. Обновление оборудования
if equipment_id:
    print_section("6. ОБНОВЛЕНИЕ ОБОРУДОВАНИЯ")
    update_request = {
        "status": "accepted",
        "lastCheck": "2025-10-29",
        "responsible": "Новый ответственный И.И."
    }
    response = requests.put(f"{BASE_URL}/api/equipment/{equipment_id}", json=update_request, headers=headers)
    print(f"Статус: {response.status_code}")
    update_result = response.json()
    print(json.dumps(update_result, indent=2, ensure_ascii=False))
    
    # Проверка обновления
    response = requests.get(f"{BASE_URL}/api/equipment?page=1&limit=1", headers=headers)
    updated = response.json()
    if updated.get('data'):
        print(f"\nПроверка: статус теперь '{updated['data'][0]['status']}'")

# 7. Создание плана обслуживания
print_section("7. СОЗДАНИЕ ПЛАНА ОБСЛУЖИВАНИЯ")
# Получим несколько ID оборудования
response = requests.get(f"{BASE_URL}/api/equipment?limit=3", headers=headers)
equipment_ids = [item['id'] for item in response.json().get('data', [])]

if equipment_ids:
    plan_request = {
        "date": "2025-11-15",
        "branch": "Москва",
        "equipmentIds": equipment_ids[:2]
    }
    response = requests.post(f"{BASE_URL}/api/equipment/maintenance-plan", json=plan_request, headers=headers)
    print(f"Статус: {response.status_code}")
    plan_result = response.json()
    print(json.dumps(plan_result, indent=2, ensure_ascii=False))

# 8. Анализ простоев (last30days, все филиалы)
print_section("8. АНАЛИЗ ПРОСТОЕВ (30 ДНЕЙ, ВСЕ)")
response = requests.get(f"{BASE_URL}/api/equipment/downtime-analysis?period=last30days", headers=headers)
print(f"Статус: {response.status_code}")
downtime = response.json()
print(json.dumps(downtime, indent=2, ensure_ascii=False))

if downtime.get('success'):
    data = downtime['data']
    print(f"\nПроцент простоя: {data['downtimePercentage']}%")
    print(f"Тренд: {data['trend']}%")
    print(f"История записей: {len(data['history'])}")
    print(f"Причин простоя: {len(data['reasons'])}")
    
    if data['reasons']:
        print("\nОсновные причины:")
        for reason in data['reasons'][:3]:
            print(f"  - {reason['name']}: {reason['percentage']}%")

# 9. Анализ простоев (last7days, Москва)
print_section("9. АНАЛИЗ ПРОСТОЕВ (7 ДНЕЙ, МОСКВА)")
response = requests.get(f"{BASE_URL}/api/equipment/downtime-analysis?period=last7days&branch=Москва", headers=headers)
print(f"Статус: {response.status_code}")
moscow_downtime = response.json()
if moscow_downtime.get('success'):
    print(f"Процент простоя в Москве: {moscow_downtime['data']['downtimePercentage']}%")

# 10. Экспорт анализа в CSV (Excel)
print_section("10. ЭКСПОРТ АНАЛИЗА (CSV)")
response = requests.get(
    f"{BASE_URL}/api/equipment/downtime-analysis/export?period=last30days&format=excel",
    headers=headers
)
print(f"Статус: {response.status_code}")
if response.status_code == 200:
    filename = "downtime_analysis_test.csv"
    with open(filename, "wb") as f:
        f.write(response.content)
    print(f"CSV файл сохранен: {filename}")
    print(f"Размер: {len(response.content)} байт")

# 11. Экспорт анализа в PDF
print_section("11. ЭКСПОРТ АНАЛИЗА (PDF)")
response = requests.get(
    f"{BASE_URL}/api/equipment/downtime-analysis/export?period=last7days&format=pdf",
    headers=headers
)
print(f"Статус: {response.status_code}")
if response.status_code == 200:
    filename = "downtime_analysis_test.pdf"
    with open(filename, "wb") as f:
        f.write(response.content)
    print(f"PDF файл сохранен: {filename}")
    print(f"Размер: {len(response.content)} байт")

# 12. Удаление оборудования (последнее из списка)
print_section("12. УДАЛЕНИЕ ОБОРУДОВАНИЯ (ADMIN)")
response = requests.get(f"{BASE_URL}/api/equipment?page=1&limit=1", headers=headers)
last_equipment = response.json()
if last_equipment.get('data'):
    delete_id = last_equipment['data'][0]['id']
    response = requests.delete(f"{BASE_URL}/api/equipment/{delete_id}", headers=headers)
    print(f"Статус: {response.status_code}")
    delete_result = response.json()
    print(json.dumps(delete_result, indent=2, ensure_ascii=False))

# 13. Тест ошибки (попытка удаления от пользователя)
print_section("13. ТЕСТ ОШИБКИ (УДАЛЕНИЕ БЕЗ ПРАВ)")
# Логин как обычный пользователь
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "username": "user",
    "password": "user123"
})
user_token = response.json()["token"]
user_headers = {"Authorization": f"Bearer {user_token}"}

response = requests.get(f"{BASE_URL}/api/equipment?page=1&limit=1", headers=user_headers)
if response.json().get('data'):
    test_id = response.json()['data'][0]['id']
    response = requests.delete(f"{BASE_URL}/api/equipment/{test_id}", headers=user_headers)
    print(f"Статус: {response.status_code}")
    if response.status_code == 403:
        print("Корректно: доступ запрещен для обычного пользователя")

print_section("ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")
print(f"\nAPI документация: {BASE_URL}/docs")
print("\nДоступные эндпоинты Equipment:")
print("- GET /api/equipment?page=1&limit=10&branch=&type=&status=")
print("- PUT /api/equipment/{id}")
print("- DELETE /api/equipment/{id}")
print("- POST /api/equipment/maintenance-plan")
print("- GET /api/equipment/downtime-analysis?branch=&period=last30days")
print("- GET /api/equipment/downtime-analysis/export?format=excel|pdf")


