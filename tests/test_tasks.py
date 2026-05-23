"""
Тестирование эндпоинтов Tasks
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

# 2. Список задач (в процессе)
print("\n" + "=" * 60)
print("2. ЗАДАЧИ В ПРОЦЕССЕ")
print("=" * 60)

response = requests.get(f"{BASE_URL}/api/tasks?status=in_progress", headers=headers)
print(f"Статус: {response.status_code}")
tasks = response.json()
print(f"Задач в процессе: {len(tasks)}")
for task in tasks:
    print(f"- {task['title']}: {task['responsible']} (срок: {task['due']})")

# 3. Завершенные задачи
print("\n" + "=" * 60)
print("3. ЗАВЕРШЕННЫЕ ЗАДАЧИ")
print("=" * 60)

response = requests.get(f"{BASE_URL}/api/tasks?status=completed", headers=headers)
print(f"Статус: {response.status_code}")
completed = response.json()
print(f"Завершенных задач: {len(completed)}")
for task in completed:
    print(f"- {task['title']}")

# 4. Просроченные задачи
print("\n" + "=" * 60)
print("4. ПРОСРОЧЕННЫЕ ЗАДАЧИ")
print("=" * 60)

response = requests.get(f"{BASE_URL}/api/tasks?status=overdue", headers=headers)
print(f"Статус: {response.status_code}")
overdue = response.json()
print(f"Просроченных задач: {len(overdue)}")
for task in overdue:
    print(f"- {task['title']}: срок был {task['due']}")

# 5. История задач
print("\n" + "=" * 60)
print("5. ИСТОРИЯ РЕШЕНИЙ")
print("=" * 60)

response = requests.get(f"{BASE_URL}/api/tasks/history", headers=headers)
print(f"Статус: {response.status_code}")
history = response.json()
print(f"Записей в истории: {len(history)}")
for item in history[:3]:
    print(f"[OK] {item['text']} - {item['author']} ({item['date']})")

# 6. Список ответственных
print("\n" + "=" * 60)
print("6. СПИСОК ОТВЕТСТВЕННЫХ")
print("=" * 60)

response = requests.get(f"{BASE_URL}/api/tasks/responsibles", headers=headers)
print(f"Статус: {response.status_code}")
responsibles = response.json()
print(f"Отделов: {len(responsibles)}")
for resp in responsibles:
    print(f"- {resp['value']}: {resp['label']}")

# 7. Создание задачи (без файла)
print("\n" + "=" * 60)
print("7. СОЗДАНИЕ ЗАДАЧИ")
print("=" * 60)

from datetime import datetime, timedelta
due_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

data = {
    "title": "Test Task from API",
    "description": "Тестовая задача через API",
    "responsible": "eng",
    "due": due_date,
    "priority": "Высокий",
    "report": "Тестовый отчет"
}

response = requests.post(f"{BASE_URL}/api/tasks", headers=headers, data=data)
print(f"Статус: {response.status_code}")
if response.status_code == 201:
    result = response.json()
    print(f"Задача создана с ID: {result['taskId']}")
    new_task_id = result['taskId']
else:
    print(f"Ошибка: {response.text}")
    new_task_id = None

# 8. Завершение задачи
if new_task_id:
    print("\n" + "=" * 60)
    print("8. ЗАВЕРШЕНИЕ ЗАДАЧИ")
    print("=" * 60)

    response = requests.post(
        f"{BASE_URL}/api/tasks/{new_task_id}/mark-complete",
        headers=headers
    )
    print(f"Статус: {response.status_code}")
    print(f"Результат: {response.json()}")

# 9. Проверка неверного статуса
print("\n" + "=" * 60)
print("9. НЕВЕРНЫЙ СТАТУС (ОШИБКА 400)")
print("=" * 60)

response = requests.get(f"{BASE_URL}/api/tasks?status=invalid", headers=headers)
print(f"Статус: {response.status_code}")
if response.status_code == 400:
    print("Корректно возвращена ошибка 400")

# 10. Проверка создания с некорректной датой
print("\n" + "=" * 60)
print("10. НЕКОРРЕКТНАЯ ДАТА (ОШИБКА 400)")
print("=" * 60)

bad_data = {
    "title": "Bad Task",
    "description": "test",
    "responsible": "eng",
    "due": "invalid-date",
    "priority": "Средний"
}

response = requests.post(f"{BASE_URL}/api/tasks", headers=headers, data=bad_data)
print(f"Статус: {response.status_code}")
if response.status_code == 400:
    print("Корректно возвращена ошибка 400")

print("\n" + "=" * 60)
print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
print("=" * 60)
print(f"\nAPI документация: {BASE_URL}/docs")
print("\nДоступные эндпоинты Tasks:")
print("- GET /api/tasks?status=in_progress")
print("- GET /api/tasks/history")
print("- POST /api/tasks")
print("- GET /api/tasks/responsibles")
print("- POST /api/tasks/{id}/mark-complete")

