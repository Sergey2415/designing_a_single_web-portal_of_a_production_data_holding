from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.routers import auth, branches, kpi, trends, notifications, user, system, tasks, reports, data, kpi_page, finances, equipment, profile, permissions_router
import os

# Create tables
Base.metadata.create_all(bind=engine)

# Metadata для улучшенной документации Swagger
tags_metadata = [
    {
        "name": "auth",
        "description": "Авторизация и аутентификация пользователей",
    },
    {
        "name": "branches",
        "description": "Управление филиалами",
    },
    {
        "name": "kpi",
        "description": "KPI метрики и показатели производительности",
    },
    {
        "name": "trends",
        "description": "Графики трендов производства и простоев",
    },
    {
        "name": "notifications",
        "description": "Система уведомлений и задач",
    },
    {
        "name": "user",
        "description": "Управление настройками пользователя",
    },
    {
        "name": "system",
        "description": "Системная информация и отчеты об ошибках",
    },
    {
        "name": "tasks",
        "description": "Управление задачами и контроль исполнения",
    },
    {
        "name": "reports",
        "description": "Отчеты с деталями и экспортом",
    },
    {
        "name": "data",
        "description": "Управление данными: ввод, загрузка, валидация",
    },
    {
        "name": "finances",
        "description": "Финансово-аналитический модуль",
    },
    {
        "name": "equipment",
        "description": "Оборудование и техническое обслуживание",
    },
    {
        "name": "profile",
        "description": "Профиль пользователя и персональная аналитика",
    },
    {
        "name": "permissions",
        "description": "Управление разрешениями и проверка доступа",
    },
]

app = FastAPI(
    title="Production Management API",
    description="""
    ## Backend API для системы управления производством
    
    Полнофункциональный REST API для управления производственными процессами, включающий:
    
    * 🔐 **Аутентификацию** с JWT токенами и 2FA
    * 📊 **KPI и аналитику** производительности
    * 📝 **Отчеты** с экспортом в PDF/CSV
    * ⚙️ **Управление оборудованием** и планирование обслуживания
    * 💰 **Финансовый модуль** с анализом затрат
    * 📋 **Задачи и уведомления** для контроля исполнения
    * 👤 **Персональные профили** с метриками
    
    ### Авторизация
    
    Большинство эндпоинтов требуют авторизации. Используйте:
    1. `POST /api/auth/login` для получения токена
    2. Добавьте заголовок `Authorization: Bearer <token>` в запросы
    
    ### Тестовые пользователи
    
    - **Admin**: `admin` / `admin123`
    - **User**: `user` / `user123`
    """,
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Support Team",
        "email": "support@production.local",
    },
    license_info={
        "name": "MIT",
    },
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files для аватаров и отчетов
os.makedirs("uploads/avatars", exist_ok=True)
os.makedirs("uploads/reports", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(branches.router)
app.include_router(kpi.router)  # Dashboard KPI
app.include_router(kpi_page.router)  # KPI Page
app.include_router(trends.router)
app.include_router(notifications.router)
app.include_router(user.router)
app.include_router(system.router)
app.include_router(tasks.router)
app.include_router(reports.router)
app.include_router(data.router)
app.include_router(finances.router)
app.include_router(equipment.router)
app.include_router(profile.router)
app.include_router(permissions_router.router)


@app.get("/")
def root():
    return {"message": "Production Management API"}

