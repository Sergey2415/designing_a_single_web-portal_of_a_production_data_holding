"""
Тестирование скачивания улучшенных отчетов
"""
import requests

BASE_URL = "http://localhost:8000"

# 1. Логин
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
token = response.json()["token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Получить список отчетов
response = requests.get(f"{BASE_URL}/api/reports?page=1&limit=1", headers=headers)
reports = response.json()

if reports['data']:
    report_id = reports['data'][0]['id']
    report_title = reports['data'][0]['type']
    
    print(f"Тестируем отчет: {report_title} (ID: {report_id})")
    print("="*60)
    
    # 3. Скачать PDF
    print("\n1. Скачивание PDF...")
    response = requests.get(f"{BASE_URL}/api/reports/{report_id}/download?format=pdf", headers=headers)
    
    if response.status_code == 200:
        filename = f"test_report_improved.pdf"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"[OK] PDF сохранен: {filename}")
        print(f"  Размер: {len(response.content):,} байт")
    else:
        print(f"[FAIL] Ошибка: {response.status_code}")
    
    # 4. Скачать CSV
    print("\n2. Скачивание CSV...")
    response = requests.get(f"{BASE_URL}/api/reports/{report_id}/download?format=csv", headers=headers)
    
    if response.status_code == 200:
        filename = f"test_report_improved.csv"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"[OK] CSV сохранен: {filename}")
        print(f"  Размер: {len(response.content):,} байт")
        print("\nПервые 1000 символов CSV:")
        print("-"*60)
        print(response.text[:1000])
        print("-"*60)
    else:
        print(f"[FAIL] Ошибка: {response.status_code}")
    
    print("\n" + "="*60)
    print("ТЕСТ ЗАВЕРШЕН!")
    print("Проверьте файлы:")
    print("- test_report_improved.pdf")
    print("- test_report_improved.csv")
else:
    print("Нет доступных отчетов для тестирования")

