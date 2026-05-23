"""
Скрипт для запуска фронтенда на локальном HTTP сервере
"""
import http.server
import socketserver
import os

PORT = 3000
DIRECTORY = "frontend"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Добавляем CORS заголовки
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🌐 Фронтенд запущен на http://localhost:{PORT}")
        print(f"📂 Директория: {os.path.join(os.getcwd(), DIRECTORY)}")
        print(f"🔗 Откройте http://localhost:{PORT}/auth.html для входа")
        print(f"\n⚠️  Убедитесь, что бэкенд запущен на http://localhost:8000")
        print(f"   Для запуска бэкенда: python run.py\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✅ Сервер остановлен")

