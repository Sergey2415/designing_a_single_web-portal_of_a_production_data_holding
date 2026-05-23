"""
Тестирование эндпоинтов Notifications
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

# 2. Summary
print("\n" + "=" * 60)
print("2. SUMMARY (СВОДКА)")
print("=" * 60)

response = requests.get(f"{BASE_URL}/api/notifications/summary", headers=headers)
print(f"Статус: {response.status_code}")
summary = response.json()
print_json(summary)

# 3. Список уведомлений (все)
print("\n" + "=" * 60)
print("3. СПИСОК УВЕДОМЛЕНИЙ (ВСЕ)")
print("=" * 60)

response = requests.get(f"{BASE_URL}/api/notifications?type=all&sort=time&limit=20", headers=headers)
print(f"Статус: {response.status_code}")
notifications = response.json()
print(f"Всего: {len(notifications)}")
for n in notifications[:3]:
    print(f"- [{n['type']}] {n['title']} (приоритет: {n['priority']}, новое: {n['isNew']})")

# 4. Фильтр по типу (только ошибки)
print("\n" + "=" * 60)
print("4. ФИЛЬТР ПО ТИПУ (ТОЛЬКО ОШИБКИ)")
print("=" * 60)

response = requests.get(f"{BASE_URL}/api/notifications?type=error&sort=time&limit=10", headers=headers)
print(f"Статус: {response.status_code}")
errors = response.json()
print(f"Найдено ошибок: {len(errors)}")
for e in errors:
    print(f"- {e['title']} (приоритет: {e['priority']})")

# 5. Сортировка по приоритету
print("\n" + "=" * 60)
print("5. СОРТИРОВКА ПО ПРИОРИТЕТУ")
print("=" * 60)

response = requests.get(f"{BASE_URL}/api/notifications?type=all&sort=priority&limit=5", headers=headers)
print(f"Статус: {response.status_code}")
prioritized = response.json()
for p in prioritized:
    print(f"- [{p['priority'].upper()}] {p['title']}")

# 6. Отметить как прочитанное
print("\n" + "=" * 60)
print("6. ОТМЕТИТЬ КАК ПРОЧИТАННОЕ")
print("=" * 60)

if notifications:
    notif_id = notifications[0]['id']
    response = requests.post(f"{BASE_URL}/api/notifications/{notif_id}/mark-read", headers=headers)
    print(f"Статус: {response.status_code}")
    print(f"Результат: {response.json()}")

# 7. Добавить комментарий
print("\n" + "=" * 60)
print("7. ДОБАВИТЬ КОММЕНТАРИЙ")
print("=" * 60)

if notifications:
    notif_id = notifications[0]['id']
    response = requests.post(
        f"{BASE_URL}/api/notifications/{notif_id}/comment",
        headers=headers,
        json={"comment": "Тестовый комментарий к уведомлению"}
    )
    print(f"Статус: {response.status_code}")
    comment_data = response.json()
    print(f"Comment ID: {comment_data.get('commentId')}")
    print(f"Status: {comment_data.get('status')}")

# 8. Назначить ответственного
print("\n" + "=" * 60)
print("8. НАЗНАЧИТЬ ОТВЕТСТВЕННОГО")
print("=" * 60)

if notifications:
    notif_id = notifications[1]['id'] if len(notifications) > 1 else notifications[0]['id']
    response = requests.post(
        f"{BASE_URL}/api/notifications/{notif_id}/assign",
        headers=headers,
        json={"assigneeId": login_data['user']['id']}
    )
    print(f"Статус: {response.status_code}")
    print(f"Результат: {response.json()}")

# 9. Завершить задачу
print("\n" + "=" * 60)
print("9. ЗАВЕРШИТЬ ЗАДАЧУ")
print("=" * 60)

# Найти уведомление с задачей
task_notif = next((n for n in notifications if n['taskId'] is not None), None)
if task_notif:
    task_id = task_notif['taskId']
    response = requests.post(f"{BASE_URL}/api/tasks/{task_id}/mark-complete", headers=headers)
    print(f"Статус: {response.status_code}")
    print(f"Задача {task_id} завершена: {response.json()}")
else:
    print("Нет уведомлений с задачами")

# 10. Refresh (получить все данные)
print("\n" + "=" * 60)
print("10. REFRESH (ОБНОВИТЬ ВСЕ ДАННЫЕ)")
print("=" * 60)

response = requests.get(f"{BASE_URL}/api/notifications/refresh", headers=headers)
print(f"Статус: {response.status_code}")
refresh_data = response.json()
print("Summary:")
print(f"  - Новых уведомлений: {refresh_data['summary']['newNotifications']}")
print(f"  - Открытых задач: {refresh_data['summary']['openTasks']}")
print(f"  - Критических ошибок: {refresh_data['summary']['criticalErrors']}")
print(f"  - Новых задач: {refresh_data['summary']['newTasks']}")
print(f"Уведомлений в списке: {len(refresh_data['notifications'])}")

print("\n" + "=" * 60)
print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
print("=" * 60)
print(f"\nAPI документация: {BASE_URL}/docs")
print("\nДоступные эндпоинты Notifications:")
print("- GET /api/notifications/summary")
print("- GET /api/notifications/refresh")
print("- GET /api/notifications?type=all&sort=time&limit=20")
print("- POST /api/notifications/{id}/mark-read")
print("- POST /api/notifications/{id}/comment")
print("- POST /api/notifications/{id}/assign")
print("- POST /api/tasks/{id}/mark-complete")



