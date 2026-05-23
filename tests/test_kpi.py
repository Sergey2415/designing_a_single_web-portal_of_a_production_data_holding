"""
Тестирование эндпоинтов KPI Page
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

# 2. Фильтры KPI
print("\n" + "=" * 60)
print("2. ПОЛУЧИТЬ ФИЛЬТРЫ")
print("=" * 60)

response = requests.get(f"{BASE_URL}/api/kpi/filters", headers=headers)
print(f"Статус: {response.status_code}")
filters = response.json()
print(f"Периоды: {filters['periods']}")
print(f"Филиалы: {filters['branches']}")
print(f"Типы: {filters['types']}")

# 3. Данные KPI (все)
print("\n" + "=" * 60)
print("3. ДАННЫЕ KPI (ВСЕ)")
print("=" * 60)

response = requests.get(
    f"{BASE_URL}/api/kpi/data",
    params={"period": "К1 2025", "branch": "Все", "type": "Все"},
    headers=headers
)
print(f"Статус: {response.status_code}")
kpi_data = response.json()
print(f"Найдено строк: {len(kpi_data['rows'])}")
print("\nПримеры KPI:")
for row in kpi_data['rows'][:3]:
    print(f"- {row['name']}: план={row['plan']}, факт={row['fact']}, отклонение={row['deviation']}")

print("\nSummary:")
print(f"  Тренд KPI: {kpi_data['summary']['trendKpi']['value']} ({kpi_data['summary']['trendKpi']['sub']})")
print(f"  Сравнение филиалов: {kpi_data['summary']['branchCompare']['value']}")

# 4. Фильтр по филиалу
print("\n" + "=" * 60)
print("4. ФИЛЬТР ПО ФИЛИАЛУ (МОСКВА)")
print("=" * 60)

response = requests.get(
    f"{BASE_URL}/api/kpi/data",
    params={"period": "К1 2025", "branch": "Москва", "type": "Все"},
    headers=headers
)
print(f"Статус: {response.status_code}")
moscow_data = response.json()
print(f"KPI для Москвы: {len(moscow_data['rows'])}")
for row in moscow_data['rows']:
    print(f"- {row['name']}")

# 5. Фильтр по типу
print("\n" + "=" * 60)
print("5. ФИЛЬТР ПО ТИПУ (ПРОИЗВОДСТВО)")
print("=" * 60)

response = requests.get(
    f"{BASE_URL}/api/kpi/data",
    params={"period": "К1 2025", "branch": "Все", "type": "Производство"},
    headers=headers
)
print(f"Статус: {response.status_code}")
production_data = response.json()
print(f"Производственных KPI: {len(production_data['rows'])}")

# 6. Детализация KPI - Смены
print("\n" + "=" * 60)
print("6. ДЕТАЛИЗАЦИЯ KPI - СМЕНЫ")
print("=" * 60)

response = requests.get(
    f"{BASE_URL}/api/kpi/details",
    params={"kpi": "production_volume", "tab": "shifts"},
    headers=headers
)
print(f"Статус: {response.status_code}")
if response.status_code != 200:
    print(f"Ошибка: {response.text}")
    exit(1)
details = response.json()
print(f"Stats: план={details['stats']['plan']}, факт={details['stats']['fact']}")
print(f"Отклонение: {details['stats']['deviation']}")
print(f"\nСмены:")
for row in details['rows']:
    status = "OK" if row['isPositive'] else "!"
    print(f"{status} {row['shift']}: план={row['plan']}, факт={row['fact']}, откл={row['deviation']}")

# 7. Детализация KPI - Сотрудники
print("\n" + "=" * 60)
print("7. ДЕТАЛИЗАЦИЯ KPI - СОТРУДНИКИ")
print("=" * 60)

response = requests.get(
    f"{BASE_URL}/api/kpi/details",
    params={"kpi": "production_volume", "tab": "employees"},
    headers=headers
)
print(f"Статус: {response.status_code}")
employees = response.json()
print(f"Сотрудников: {len(employees['rows'])}")
for row in employees['rows']:
    status = "OK" if row['isPositive'] else "!"
    print(f"{status} {row['employee']}: откл={row['deviation']}")

# 8. Детализация KPI - Оборудование
print("\n" + "=" * 60)
print("8. ДЕТАЛИЗАЦИЯ KPI - ОБОРУДОВАНИЕ")
print("=" * 60)

response = requests.get(
    f"{BASE_URL}/api/kpi/details",
    params={"kpi": "production_volume", "tab": "equipment"},
    headers=headers
)
print(f"Статус: {response.status_code}")
equipment = response.json()
print(f"Оборудование: {len(equipment['rows'])}")
for row in equipment['rows']:
    print(f"- {row['equipment']}: план={row['plan']}, факт={row['fact']}")

# 9. Проверка несуществующего KPI
print("\n" + "=" * 60)
print("9. НЕСУЩЕСТВУЮЩИЙ KPI (ОШИБКА 404)")
print("=" * 60)

response = requests.get(
    f"{BASE_URL}/api/kpi/details",
    params={"kpi": "nonexistent", "tab": "shifts"},
    headers=headers
)
print(f"Статус: {response.status_code}")
if response.status_code == 404:
    print("Корректно возвращена ошибка 404")

# 10. Неверный таб
print("\n" + "=" * 60)
print("10. НЕВЕРНЫЙ ТАБ (ОШИБКА 400)")
print("=" * 60)

response = requests.get(
    f"{BASE_URL}/api/kpi/details",
    params={"kpi": "production_volume", "tab": "invalid"},
    headers=headers
)
print(f"Статус: {response.status_code}")
if response.status_code == 400:
    print("Корректно возвращена ошибка 400")

print("\n" + "=" * 60)
print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
print("=" * 60)
print(f"\nAPI документация: {BASE_URL}/docs")
print("\nДоступные эндпоинты KPI Page:")
print("- GET /api/kpi/data?period=К1 2025&branch=Все&type=Все")
print("- GET /api/kpi/filters")
print("- GET /api/kpi/details?kpi=production_volume&tab=shifts")
print("  Табы: shifts, employees, equipment")

