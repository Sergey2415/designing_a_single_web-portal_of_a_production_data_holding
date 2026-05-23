"""
Простой тест одного запроса для проверки ошибки
"""
import requests

BASE_URL = "http://localhost:8000"

# Логин
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
token = response.json()["token"]
headers = {"Authorization": f"Bearer {token}"}

# Получить отчеты
response = requests.get(f"{BASE_URL}/api/reports", headers=headers)
reports = response.json()
report_id = reports['data'][0]['id']

print(f"Скачиваем отчет ID: {report_id}")

# Попытка скачать PDF
response = requests.get(f"{BASE_URL}/api/reports/{report_id}/download?format=pdf", headers=headers)
print(f"Статус: {response.status_code}")

if response.status_code == 500:
    print("Ошибка сервера:")
    print(response.text)
elif response.status_code == 200:
    print(f"Успех! Размер: {len(response.content)} байт")
    with open("test.pdf", "wb") as f:
        f.write(response.content)
    print("Файл сохранен как test.pdf")


