"""
Тестирование эндпоинтов Reports
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def print_json(data, title=""):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(json.dumps(data, indent=2, ensure_ascii=False))

# 1. Логин
print("="*60)
print("1. ЛОГИН")
print("="*60)

response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
login_data = response.json()
print(f"Статус: {response.status_code}")
print(f"Token получен: {login_data.get('success')}")

token = login_data["token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Список всех отчетов
response = requests.get(f"{BASE_URL}/api/reports?page=1&limit=5", headers=headers)
reports_data = response.json()
print_json(reports_data, "2. СПИСОК ОТЧЕТОВ (первая страница)")
print(f"Всего отчетов: {reports_data['total']}")
print(f"Страниц: {reports_data['pages']}")

# Сохраним ID первого отчета
report_id = reports_data['data'][0]['id'] if reports_data['data'] else None

# 3. Фильтр по типу
response = requests.get(f"{BASE_URL}/api/reports?type=production&page=1&limit=10", headers=headers)
production_reports = response.json()
print_json(production_reports, "3. ПРОИЗВОДСТВЕННЫЕ ОТЧЕТЫ")
print(f"Найдено производственных отчетов: {production_reports['total']}")

# 4. Фильтр по статусу
response = requests.get(f"{BASE_URL}/api/reports?status=ready&page=1&limit=10", headers=headers)
ready_reports = response.json()
print_json(ready_reports, "4. ГОТОВЫЕ ОТЧЕТЫ")
print(f"Готовых отчетов: {ready_reports['total']}")

# 5. Фильтр по дате
response = requests.get(f"{BASE_URL}/api/reports?date=week&page=1&limit=10", headers=headers)
week_reports = response.json()
print_json(week_reports, "5. ОТЧЕТЫ ЗА НЕДЕЛЮ")
print(f"Отчетов за неделю: {week_reports['total']}")

# 6. Детали отчета
if report_id:
    response = requests.get(f"{BASE_URL}/api/reports/{report_id}", headers=headers)
    report_detail = response.json()
    print_json(report_detail, "6. ДЕТАЛИ ОТЧЕТА")
    print(f"Заголовок: {report_detail['data']['title']}")
    print(f"Деталей: {len(report_detail['data'].get('details', []))}")
    print(f"Причин простоя: {len(report_detail['data'].get('downtimeReasons', []))}")

# 7. Создание нового отчета
print("\n" + "="*60)
print("7. СОЗДАНИЕ НОВОГО ОТЧЕТА")
print("="*60)

new_report = {
    "title": "Тестовый отчет",
    "date": "2025-10-29",
    "type": "analytics",
    "author": "Тестер А.А.",
    "status": "inProgress",
    "content": "Это тестовый отчет, созданный через API",
    "period": "Октябрь 2025",
    "department": "Тестовый отдел",
    "kpi": "Тестовый KPI"
}

response = requests.post(f"{BASE_URL}/api/reports", json=new_report, headers=headers)
print(f"Статус: {response.status_code}")
if response.status_code == 201:
    created_report = response.json()
    print_json(created_report, "ОТЧЕТ СОЗДАН")
    new_report_id = created_report['id']
else:
    print(f"Ошибка: {response.text}")
    new_report_id = None

# 8. Скачивание PDF
if report_id:
    print("\n" + "="*60)
    print("8. СКАЧИВАНИЕ PDF")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/reports/{report_id}/download?format=pdf", headers=headers)
    print(f"Статус: {response.status_code}")
    if response.status_code == 200:
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Размер файла: {len(response.content)} байт")
        # Сохраняем для проверки
        with open("test_report.pdf", "wb") as f:
            f.write(response.content)
        print("PDF сохранен как test_report.pdf")

# 9. Скачивание CSV
if report_id:
    print("\n" + "="*60)
    print("9. СКАЧИВАНИЕ CSV")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/reports/{report_id}/download?format=csv", headers=headers)
    print(f"Статус: {response.status_code}")
    if response.status_code == 200:
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print("Содержимое CSV:")
        print(response.text[:500])  # Первые 500 символов

# 10. Экспорт всех отчетов в CSV
print("\n" + "="*60)
print("10. ЭКСПОРТ ВСЕХ ОТЧЕТОВ")
print("="*60)

response = requests.get(f"{BASE_URL}/api/reports/export/csv?type=production", headers=headers)
print(f"Статус: {response.status_code}")
if response.status_code == 200:
    print("Содержимое экспорта:")
    print(response.text[:500])

# 11. Отправка отчета менеджеру
if report_id:
    print("\n" + "="*60)
    print("11. ОТПРАВКА ОТЧЕТА МЕНЕДЖЕРУ")
    print("="*60)
    
    send_data = {
        "managerId": "manager-123",
        "message": "Пожалуйста, ознакомьтесь с отчетом"
    }
    
    response = requests.post(f"{BASE_URL}/api/reports/{report_id}/send", json=send_data, headers=headers)
    print(f"Статус: {response.status_code}")
    send_result = response.json()
    print_json(send_result, "РЕЗУЛЬТАТ ОТПРАВКИ")

# 12. Удаление отчета (только admin)
if new_report_id:
    print("\n" + "="*60)
    print("12. УДАЛЕНИЕ ОТЧЕТА")
    print("="*60)
    
    response = requests.delete(f"{BASE_URL}/api/reports/{new_report_id}", headers=headers)
    print(f"Статус: {response.status_code}")
    delete_result = response.json()
    print_json(delete_result, "РЕЗУЛЬТАТ УДАЛЕНИЯ")

# 13. Проверка несуществующего отчета (404)
print("\n" + "="*60)
print("13. НЕСУЩЕСТВУЮЩИЙ ОТЧЕТ (404)")
print("="*60)

response = requests.get(f"{BASE_URL}/api/reports/invalid-id", headers=headers)
print(f"Статус: {response.status_code}")
if response.status_code == 404:
    print("Корректно возвращена ошибка 404")

# 14. Попытка удаления с недостаточными правами
print("\n" + "="*60)
print("14. ПОПЫТКА УДАЛЕНИЯ С ПРАВАМИ USER (403)")
print("="*60)

# Логин как user
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "username": "user",
    "password": "user123"
})
user_token = response.json()["token"]
user_headers = {"Authorization": f"Bearer {user_token}"}

if report_id:
    response = requests.delete(f"{BASE_URL}/api/reports/{report_id}", headers=user_headers)
    print(f"Статус: {response.status_code}")
    if response.status_code == 403:
        print("Корректно возвращена ошибка 403 (нет прав)")

print("\n" + "="*60)
print("ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")
print("="*60)
print(f"\nAPI документация: {BASE_URL}/docs")
print("\nПроверенные эндпоинты Reports:")
print("- GET /api/reports (с фильтрами: date, type, status)")
print("- GET /api/reports/{id}")
print("- GET /api/reports/{id}/download?format=pdf")
print("- GET /api/reports/{id}/download?format=csv")
print("- GET /api/reports/export/csv")
print("- POST /api/reports")
print("- POST /api/reports/{id}/send")
print("- DELETE /api/reports/{id}")


