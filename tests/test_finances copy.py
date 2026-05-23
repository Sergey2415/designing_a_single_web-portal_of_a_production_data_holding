"""
Тестирование эндпоинтов Finances
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

# 2. Финансовые метрики
print_section("2. ФИНАНСОВЫЕ МЕТРИКИ")
response = requests.get(f"{BASE_URL}/api/finances/metrics", headers=headers)
print(f"Статус: {response.status_code}")
metrics = response.json()
print(json.dumps(metrics, indent=2, ensure_ascii=False))
if metrics.get("success"):
    unit_cost = metrics["data"]["unitCost"]
    print(f"\nСтоимость единицы: {unit_cost['value']}")
    print(f"Изменение: {unit_cost['changePercentage']}% ({unit_cost['changeDirection']})")

# 3. Динамика затрат
print_section("3. ДИНАМИКА ЗАТРАТ ПО КВАРТАЛАМ")
response = requests.get(f"{BASE_URL}/api/finances/cost-dynamics?period=all", headers=headers)
print(f"Статус: {response.status_code}")
dynamics = response.json()
print(json.dumps(dynamics, indent=2, ensure_ascii=False))
if dynamics.get("success"):
    data = dynamics["data"]
    print(f"\nQ1 2025: {data['q1']:,.2f}")
    print(f"Q2 2025: {data['q2']:,.2f}")
    print(f"Q3 2025: {data['q3']:,.2f}")
    print(f"Q4 2025: {data['q4']:,.2f}")

# 4. Сравнение затрат (все)
print_section("4. СРАВНЕНИЕ ЗАТРАТ (ВСЕ)")
response = requests.get(f"{BASE_URL}/api/finances/cost-comparison?page=1&limit=5", headers=headers)
print(f"Статус: {response.status_code}")
comparison = response.json()
print(f"Всего записей: {comparison.get('total')}")
print(f"Страниц: {comparison.get('pages')}")
print("\nПервые записи:")
for item in comparison.get('data', []):
    print(f"  - {item['period']}: {item['department']}, {item['type']} = {item['amount']:,.2f} ({item['status']})")

# 5. Сравнение затрат с фильтром (Q1 2025)
print_section("5. СРАВНЕНИЕ ЗАТРАТ (ФИЛЬТР: Q1 2025)")
response = requests.get(f"{BASE_URL}/api/finances/cost-comparison?period=Q1 2025", headers=headers)
print(f"Статус: {response.status_code}")
q1_data = response.json()
print(f"Записей за Q1 2025: {q1_data.get('total')}")
for item in q1_data.get('data', []):
    print(f"  - {item['department']}, {item['type']}: {item['amount']:,.2f}")

# 6. Сравнение затрат с фильтром (отдел)
print_section("6. СРАВНЕНИЕ ЗАТРАТ (ФИЛЬТР: ОТДЕЛ)")
response = requests.get(
    f"{BASE_URL}/api/finances/cost-comparison?department=Производственный отдел&limit=10",
    headers=headers
)
print(f"Статус: {response.status_code}")
dept_data = response.json()
print(f"Записей для отдела: {dept_data.get('total')}")

# 7. Бюджет и эффективность (все)
print_section("7. БЮДЖЕТ И ЭФФЕКТИВНОСТЬ (ВСЕ)")
response = requests.get(f"{BASE_URL}/api/finances/budget-efficiency", headers=headers)
print(f"Статус: {response.status_code}")
budget = response.json()
print(json.dumps(budget, indent=2, ensure_ascii=False))
if budget.get("success"):
    data = budget["data"]
    print(f"\nКатегории: {data['labels']}")
    for dataset in data['datasets']:
        print(f"Dataset: {dataset['label']}")
        print(f"  Данные: {dataset['data']}")

# 8. Бюджет и эффективность (по отделу)
print_section("8. БЮДЖЕТ И ЭФФЕКТИВНОСТЬ (ПО ОТДЕЛУ)")
response = requests.get(
    f"{BASE_URL}/api/finances/budget-efficiency?department=Производственный отдел",
    headers=headers
)
print(f"Статус: {response.status_code}")
dept_budget = response.json()
if dept_budget.get("success"):
    print(f"Категории для отдела: {dept_budget['data']['labels']}")

# 9. Создание финансового отчета
print_section("9. СОЗДАНИЕ ФИНАНСОВОГО ОТЧЕТА")
report_request = {
    "type": "quarterly",
    "period": "Q3 2025",
    "department": "Производственный отдел"
}
response = requests.post(f"{BASE_URL}/api/finances/reports", json=report_request, headers=headers)
print(f"Статус: {response.status_code}")
create_result = response.json()
print(json.dumps(create_result, indent=2, ensure_ascii=False))

# 10. Скачивание финансового отчета (quarterly)
print_section("10. СКАЧИВАНИЕ ФИНАНСОВОГО ОТЧЕТА")
response = requests.get(f"{BASE_URL}/api/finances/reports/quarterly", headers=headers)
print(f"Статус: {response.status_code}")
if response.status_code == 200:
    filename = "financial_report_quarterly_test.csv"
    with open(filename, "wb") as f:
        f.write(response.content)
    print(f"Отчет сохранен: {filename}")
    print(f"Размер: {len(response.content)} байт")
    print("\nОтчет успешно сгенерирован в CSV формате")

# 11. Скачивание monthly отчета
print_section("11. СКАЧИВАНИЕ MONTHLY ОТЧЕТА")
response = requests.get(f"{BASE_URL}/api/finances/reports/monthly", headers=headers)
print(f"Статус: {response.status_code}")
if response.status_code == 200:
    print(f"Monthly отчет доступен, размер: {len(response.content)} байт")

# 12. Ошибка - неверный тип отчета
print_section("12. ТЕСТ ОШИБКИ (НЕВЕРНЫЙ ТИП ОТЧЕТА)")
response = requests.get(f"{BASE_URL}/api/finances/reports/invalid_type", headers=headers)
print(f"Статус: {response.status_code}")
if response.status_code == 400:
    print("Корректно возвращена ошибка 400")

print_section("ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")
print(f"\nAPI документация: {BASE_URL}/docs")
print("\nДоступные эндпоинты Finances:")
print("- GET /api/finances/metrics")
print("- GET /api/finances/cost-dynamics?period=all")
print("- GET /api/finances/cost-comparison?page=1&limit=10&period=&department=&type=")
print("- GET /api/finances/budget-efficiency?department=&period=")
print("- GET /api/finances/reports/{type} (daily, monthly, quarterly)")
print("- POST /api/finances/reports")

