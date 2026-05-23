"""
Скрипт для инициализации БД тестовыми данными
"""
import uuid
import json
from datetime import datetime, timedelta, date
from app.database import SessionLocal, engine, Base
from app.models import (
    User, Branch, KPIMetric, ProductionData, DowntimeData, Notification,
    UserSettings, LoginHistory, SystemInfo, BugReport, Task, Comment,
    KPIIndicator, KPIDetail, TaskHistory, Department, Report,
    DataRecord, DataHistory, FinancialMetric, CostComparison,
    Equipment, MaintenancePlan, UserMetric, UserActivity, UserTask,
    TeamMember, UserReport
)
from app.auth import get_password_hash

# Создаем таблицы
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Очистка существующих данных (опционально)
db.query(UserReport).delete()
db.query(TeamMember).delete()
db.query(UserTask).delete()
db.query(UserActivity).delete()
db.query(UserMetric).delete()
db.query(MaintenancePlan).delete()
db.query(Equipment).delete()
db.query(CostComparison).delete()
db.query(FinancialMetric).delete()
db.query(DataHistory).delete()
db.query(DataRecord).delete()
db.query(Report).delete()
db.query(TaskHistory).delete()
db.query(Department).delete()
db.query(KPIDetail).delete()
db.query(KPIIndicator).delete()
db.query(Comment).delete()
db.query(BugReport).delete()
db.query(LoginHistory).delete()
db.query(UserSettings).delete()
db.query(Notification).delete()
db.query(Task).delete()
db.query(DowntimeData).delete()
db.query(ProductionData).delete()
db.query(KPIMetric).delete()
db.query(Branch).delete()
db.query(SystemInfo).delete()
db.query(User).delete()
db.commit()

# Создание пользователей
admin_id = str(uuid.uuid4())
user_id = str(uuid.uuid4())

users = [
    User(
        id=admin_id,
        username="admin",
        password=get_password_hash("admin123"),
        name="Администратор",
        role="admin",
        department="Производственный цех №1",
        email="admin@production.local",
        avatar_url="/uploads/avatars/default-admin.png"
    ),
    User(
        id=user_id,
        username="user",
        password=get_password_hash("user123"),
        name="Пользователь",
        role="user",
        department="Производственный цех №2",
        email="user@production.local",
        avatar_url="/uploads/avatars/default-user.png"
    )
]
db.add_all(users)
db.commit()

# Создание настроек пользователей
user_settings = [
    UserSettings(user_id=admin_id),
    UserSettings(user_id=user_id)
]
db.add_all(user_settings)
db.commit()

# Создание истории входов
login_history = [
    LoginHistory(
        user_id=admin_id,
        device="Chrome on Windows",
        ip="192.168.1.10",
        date=datetime.utcnow() - timedelta(hours=2)
    ),
    LoginHistory(
        user_id=admin_id,
        device="Mobile App (iOS)",
        ip="10.0.0.5",
        date=datetime.utcnow() - timedelta(days=1)
    ),
    LoginHistory(
        user_id=admin_id,
        device="Firefox on Linux",
        ip="88.201.54.9",
        date=datetime.utcnow() - timedelta(days=2)
    ),
    LoginHistory(
        user_id=user_id,
        device="Chrome on Windows",
        ip="192.168.1.15",
        date=datetime.utcnow() - timedelta(hours=5)
    )
]
db.add_all(login_history)
db.commit()

# Создание системной информации
system_info = SystemInfo(
    version="2.10-beta",
    last_update=datetime.utcnow() - timedelta(days=5),
    server_status="Online"
)
db.add(system_info)
db.commit()

# Создание филиалов
branches = [
    Branch(id=1, name="Москва"),
    Branch(id=2, name="Иркутск"),
    Branch(id=3, name="Санкт-Петербург")
]
db.add_all(branches)
db.commit()

# Создание KPI метрик
kpi_metrics = [
    KPIMetric(
        branch_id=1,
        productivity_value="120 тонн/чел",
        productivity_change="+10%",
        is_positive_productivity=True,
        cost_per_ton_value="3450₽/тонн",
        cost_per_ton_change="−5%",
        is_positive_cost=False,
        uptime_value="95%",
        uptime_change="+2%",
        is_positive_uptime=True,
        efficiency_index_value="8.5",
        efficiency_index_change="+1%",
        is_positive_efficiency=True
    ),
    KPIMetric(
        branch_id=2,
        productivity_value="110 тонн/чел",
        productivity_change="+8%",
        is_positive_productivity=True,
        cost_per_ton_value="3600₽/тонн",
        cost_per_ton_change="−3%",
        is_positive_cost=False,
        uptime_value="92%",
        uptime_change="+1%",
        is_positive_uptime=True,
        efficiency_index_value="8.2",
        efficiency_index_change="+0.5%",
        is_positive_efficiency=True
    ),
    KPIMetric(
        branch_id=3,
        productivity_value="115 тонн/чел",
        productivity_change="+12%",
        is_positive_productivity=True,
        cost_per_ton_value="3500₽/тонн",
        cost_per_ton_change="−7%",
        is_positive_cost=False,
        uptime_value="97%",
        uptime_change="+3%",
        is_positive_uptime=True,
        efficiency_index_value="8.8",
        efficiency_index_change="+1.5%",
        is_positive_efficiency=True
    )
]
db.add_all(kpi_metrics)
db.commit()

# Создание данных производства (последние 30 дней)
production_data = []
base_date = date.today() - timedelta(days=30)
for i in range(30):
    current_date = base_date + timedelta(days=i)
    value = 100 + (i % 7) * 5 + (i // 7) * 3
    production_data.append(ProductionData(
        date=current_date,
        value=float(value),
        branch_id=None  # Агрегированные данные
    ))
db.add_all(production_data)
db.commit()

# Создание данных простоев
downtime_data = [
    DowntimeData(category="Оборудование", value=40, color="#FF0000", period="month"),
    DowntimeData(category="Персонал", value=30, color="#FFA500", period="month"),
    DowntimeData(category="Материалы", value=20, color="#00FF00", period="month"),
    DowntimeData(category="Другое", value=10, color="#0000FF", period="month"),
    
    DowntimeData(category="Оборудование", value=35, color="#FF0000", period="week"),
    DowntimeData(category="Персонал", value=25, color="#FFA500", period="week"),
    DowntimeData(category="Материалы", value=30, color="#00FF00", period="week"),
    DowntimeData(category="Другое", value=10, color="#0000FF", period="week"),
]
db.add_all(downtime_data)
db.commit()

# Создание отделов
departments = [
    Department(value="eng", label="Инженерная команда"),
    Department(value="sec", label="Отдел безопасности"),
    Department(value="log", label="Логистика"),
    Department(value="prod", label="Производственный отдел"),
    Department(value="qa", label="Отдел качества")
]
db.add_all(departments)
db.commit()

# Создание задач
tasks = [
    Task(
        id=1,
        title="Implement new safety protocol",
        description="Внедрить новый протокол безопасности на производстве",
        report="Аудит безопасности 2025",
        responsible="Отдел безопасности",
        status="В процессе",
        assignee_id=admin_id,
        creator_id=admin_id,
        priority="Высокий",
        due_date=datetime.utcnow() + timedelta(days=5)
    ),
    Task(
        id=2,
        title="Upgrade production line 3",
        description="Модернизация производственной линии 3",
        report="Производственный отчёт за 2 квартал",
        responsible="Инженерная команда",
        status="В процессе",
        assignee_id=user_id,
        creator_id=admin_id,
        priority="Высокий",
        due_date=datetime.utcnow() + timedelta(days=3)
    ),
    Task(
        id=3,
        title="Quality inspection Q4",
        description="Проверка качества за 4 квартал",
        report="Отчет по качеству",
        responsible="Отдел качества",
        status="Выполнена",
        assignee_id=user_id,
        creator_id=admin_id,
        priority="Средний",
        due_date=datetime.utcnow() - timedelta(days=5)
    ),
    Task(
        id=4,
        title="Equipment maintenance check",
        description="Плановая проверка оборудования",
        report="Технический аудит",
        responsible="Инженерная команда",
        status="В процессе",
        assignee_id=admin_id,
        creator_id=user_id,
        priority="Средний",
        due_date=datetime.utcnow() - timedelta(days=2)  # Просрочена
    )
]
db.add_all(tasks)
db.commit()

# Создание истории задач
task_history = [
    TaskHistory(
        task_id=3,
        type="success",
        icon="✔",
        text="Одобрено внедрение нового протокола безопасности",
        author="Симонов Д.А.",
        date=date.today() - timedelta(days=9)
    ),
    TaskHistory(
        task_id=2,
        type="success",
        icon="✔",
        text="Утверждена модернизация производственной линии 3",
        author="Мартынова А.А.",
        date=date.today() - timedelta(days=15)
    ),
    TaskHistory(
        task_id=3,
        type="success",
        icon="✔",
        text="Завершена проверка качества за 4 квартал",
        author="Иванов И.И.",
        date=date.today() - timedelta(days=5)
    )
]
db.add_all(task_history)
db.commit()

# Создание отчетов
reports = [
    Report(
        id=str(uuid.uuid4()),
        title="Производственный отчет за октябрь 2025",
        date=date.today() - timedelta(days=2),
        type="production",
        author="Иванов И.И.",
        status="ready",
        content="Анализ производственных показателей за октябрь 2025 года",
        period="Октябрь 2025",
        department="Производственный отдел",
        kpi="Объем производства",
        details=json.dumps([
            {"parameter": "Объем производства", "target": 1000, "actual": 1050, "deviation": 5.0, "status": "good"},
            {"parameter": "Качество продукции", "target": 98, "actual": 97.5, "deviation": -0.5, "status": "normal"},
            {"parameter": "Использование оборудования", "target": 85, "actual": 88, "deviation": 3.5, "status": "good"}
        ]),
        downtime_reasons=json.dumps([
            {"reason": "Плановое обслуживание", "percentage": 45},
            {"reason": "Аварийные поломки", "percentage": 30},
            {"reason": "Нехватка материалов", "percentage": 15},
            {"reason": "Другое", "percentage": 10}
        ])
    ),
    Report(
        id=str(uuid.uuid4()),
        title="Финансовый отчет Q3 2025",
        date=date.today() - timedelta(days=10),
        type="financial",
        author="Петрова А.А.",
        status="accepted",
        content="Финансовые результаты третьего квартала 2025 года",
        period="Q3 2025",
        department="Финансовый отдел",
        kpi="Прибыль",
        details=json.dumps([
            {"parameter": "Выручка", "target": 5000000, "actual": 5200000, "deviation": 4.0, "status": "good"},
            {"parameter": "Расходы", "target": 3500000, "actual": 3450000, "deviation": -1.4, "status": "good"},
            {"parameter": "Прибыль", "target": 1500000, "actual": 1750000, "deviation": 16.7, "status": "excellent"}
        ]),
        downtime_reasons=json.dumps([])
    ),
    Report(
        id=str(uuid.uuid4()),
        title="Отчет по оборудованию линии 3",
        date=date.today() - timedelta(days=5),
        type="equipment",
        author="Сидоров С.С.",
        status="inProgress",
        content="Техническое состояние оборудования производственной линии 3",
        period="Октябрь 2025",
        department="Инженерная команда",
        kpi="Эффективность оборудования",
        details=json.dumps([
            {"parameter": "Время работы", "target": 720, "actual": 680, "deviation": -5.5, "status": "warning"},
            {"parameter": "Производительность", "target": 100, "actual": 95, "deviation": -5.0, "status": "warning"},
            {"parameter": "Энергопотребление", "target": 1000, "actual": 980, "deviation": -2.0, "status": "good"}
        ]),
        downtime_reasons=json.dumps([
            {"reason": "Замена деталей", "percentage": 60},
            {"reason": "Калибровка", "percentage": 25},
            {"reason": "Обучение персонала", "percentage": 15}
        ])
    ),
    Report(
        id=str(uuid.uuid4()),
        title="Аналитический отчет по эффективности",
        date=date.today() - timedelta(days=1),
        type="analytics",
        author="Морозова М.М.",
        status="ready",
        content="Комплексный анализ производственной эффективности",
        period="Октябрь 2025",
        department="Аналитический отдел",
        kpi="OEE",
        details=json.dumps([
            {"parameter": "Доступность", "target": 90, "actual": 92, "deviation": 2.2, "status": "good"},
            {"parameter": "Производительность", "target": 85, "actual": 83, "deviation": -2.3, "status": "normal"},
            {"parameter": "Качество", "target": 95, "actual": 96.5, "deviation": 1.6, "status": "good"}
        ]),
        downtime_reasons=json.dumps([
            {"reason": "Техническое обслуживание", "percentage": 40},
            {"reason": "Простои", "percentage": 35},
            {"reason": "Переналадка", "percentage": 25}
        ])
    ),
    Report(
        id=str(uuid.uuid4()),
        title="Недельный производственный отчет",
        date=date.today(),
        type="production",
        author="Козлов К.К.",
        status="inProgress",
        content="Производственные показатели за текущую неделю",
        period="Неделя 43, 2025",
        department="Производственный отдел",
        kpi="Выполнение плана",
        details=json.dumps([
            {"parameter": "План производства", "target": 250, "actual": 240, "deviation": -4.0, "status": "warning"},
            {"parameter": "Брак", "target": 2, "actual": 1.5, "deviation": -25.0, "status": "good"}
        ]),
        downtime_reasons=json.dumps([])
    )
]
db.add_all(reports)
db.commit()

# Создание тестовых записей данных
upload_id_1 = str(uuid.uuid4())
data_records = [
    DataRecord(
        id=str(uuid.uuid4()),
        date=date.today() - timedelta(days=1),
        type="production",
        value=1250.5,
        comment="Производство за смену 1",
        user_id=admin_id,
        upload_id=upload_id_1,
        status="consolidated",
        department="Производственный отдел"
    ),
    DataRecord(
        id=str(uuid.uuid4()),
        date=date.today() - timedelta(days=1),
        type="downtime",
        value=2.5,
        comment="Простой оборудования",
        user_id=admin_id,
        upload_id=upload_id_1,
        status="consolidated",
        department="Производственный отдел"
    ),
    DataRecord(
        id=str(uuid.uuid4()),
        date=date.today(),
        type="production",
        value=980.0,
        comment="Текущая смена",
        user_id=user_id,
        status="pending"
    )
]
db.add_all(data_records)
db.commit()

# История данных
data_history = [
    DataHistory(
        id=str(uuid.uuid4()),
        date=datetime.utcnow() - timedelta(hours=2),
        status="accepted",
        comment="Консолидировано 2 записей для отдела Производственный отдел",
        user=admin_id,
        record_id=upload_id_1,
        action="consolidate"
    ),
    DataHistory(
        id=str(uuid.uuid4()),
        date=datetime.utcnow() - timedelta(hours=3),
        status="ready",
        comment="Валидация: успешна",
        user=admin_id,
        record_id=upload_id_1,
        action="validate"
    ),
    DataHistory(
        id=str(uuid.uuid4()),
        date=datetime.utcnow() - timedelta(hours=4),
        status="inProgress",
        comment="Загружен файл production_data.csv, записей: 2",
        user=admin_id,
        record_id=upload_id_1,
        action="upload"
    )
]
db.add_all(data_history)
db.commit()

# Создание финансовых метрик
financial_metrics = [
    FinancialMetric(
        id=str(uuid.uuid4()),
        unit_cost=125.50,
        change_percentage=5.2,
        change_direction="down",
        updated_at=datetime.utcnow()
    )
]
db.add_all(financial_metrics)
db.commit()

# Создание сравнений затрат
cost_comparisons = [
    CostComparison(
        id=str(uuid.uuid4()),
        period="Q1 2025",
        department="Производственный отдел",
        type="materials",
        amount=150000.0,
        comment="Закупка сырья",
        status="approved"
    ),
    CostComparison(
        id=str(uuid.uuid4()),
        period="Q1 2025",
        department="Производственный отдел",
        type="labor",
        amount=200000.0,
        comment="Заработная плата",
        status="approved"
    ),
    CostComparison(
        id=str(uuid.uuid4()),
        period="Q2 2025",
        department="Производственный отдел",
        type="materials",
        amount=165000.0,
        comment="Закупка сырья Q2",
        status="approved"
    ),
    CostComparison(
        id=str(uuid.uuid4()),
        period="Q2 2025",
        department="Инженерная команда",
        type="equipment",
        amount=80000.0,
        comment="Новое оборудование",
        status="pending"
    ),
    CostComparison(
        id=str(uuid.uuid4()),
        period="Q3 2025",
        department="Производственный отдел",
        type="materials",
        amount=170000.0,
        comment="Закупка сырья Q3",
        status="approved"
    ),
    CostComparison(
        id=str(uuid.uuid4()),
        period="Q3 2025",
        department="Производственный отдел",
        type="overhead",
        amount=45000.0,
        comment="Накладные расходы",
        status="approved"
    ),
    CostComparison(
        id=str(uuid.uuid4()),
        period="Q4 2025",
        department="Производственный отдел",
        type="materials",
        amount=180000.0,
        comment="Закупка сырья Q4",
        status="approved"
    )
]
db.add_all(cost_comparisons)
db.commit()

# Создание оборудования
equipment_list = [
    Equipment(
        id=str(uuid.uuid4()),
        name="Производственная линия №1",
        branch="Москва",
        type="production",
        status="ready",
        last_check=date.today() - timedelta(days=5),
        responsible="Сидоров П.П."
    ),
    Equipment(
        id=str(uuid.uuid4()),
        name="Производственная линия №2",
        branch="Москва",
        type="production",
        status="inprogress",
        last_check=date.today() - timedelta(days=15),
        responsible="Петров А.А."
    ),
    Equipment(
        id=str(uuid.uuid4()),
        name="Конвейер №3",
        branch="Санкт-Петербург",
        type="auxiliary",
        status="ready",
        last_check=date.today() - timedelta(days=3),
        responsible="Иванов И.И."
    ),
    Equipment(
        id=str(uuid.uuid4()),
        name="Погрузчик №5",
        branch="Казань",
        type="transport",
        status="accepted",
        last_check=date.today() - timedelta(days=1),
        responsible="Смирнов В.В."
    ),
    Equipment(
        id=str(uuid.uuid4()),
        name="Станок CNC-01",
        branch="Москва",
        type="production",
        status="ready",
        last_check=date.today() - timedelta(days=10),
        responsible="Козлов Д.Д."
    ),
    Equipment(
        id=str(uuid.uuid4()),
        name="Компрессор №2",
        branch="Санкт-Петербург",
        type="auxiliary",
        status="inprogress",
        last_check=date.today() - timedelta(days=20),
        responsible="Новиков Е.Е."
    )
]
db.add_all(equipment_list)
db.commit()

# Создание планов обслуживания
maintenance_plans = [
    MaintenancePlan(
        id=str(uuid.uuid4()),
        date=date.today() + timedelta(days=7),
        branch="Москва",
        equipment_ids=json.dumps([equipment_list[0].id, equipment_list[4].id])
    ),
    MaintenancePlan(
        id=str(uuid.uuid4()),
        date=date.today() + timedelta(days=14),
        branch="Санкт-Петербург",
        equipment_ids=json.dumps([equipment_list[2].id, equipment_list[5].id])
    )
]
db.add_all(maintenance_plans)
db.commit()

# Создание метрик пользователей
user_metrics = [
    UserMetric(
        id=str(uuid.uuid4()),
        user_id=admin_id,
        labor_productivity=json.dumps({"value": 95.5, "change": 2.3}),
        repair_efficiency=json.dumps({"value": 88.2, "change": -1.5}),
        equipment_downtime=json.dumps({"value": 12.5, "change": -3.2}),
        cost=json.dumps({"value": 125.50, "change": -5.2})
    ),
    UserMetric(
        id=str(uuid.uuid4()),
        user_id=user_id,
        labor_productivity=json.dumps({"value": 92.3, "change": 1.8}),
        repair_efficiency=json.dumps({"value": 85.7, "change": -2.1}),
        equipment_downtime=json.dumps({"value": 15.2, "change": -1.5}),
        cost=json.dumps({"value": 132.20, "change": -3.8})
    )
]
db.add_all(user_metrics)
db.commit()

# Создание активности пользователей
user_activities = [
    UserActivity(
        id=str(uuid.uuid4()),
        user_id=admin_id,
        type="login",
        description="Вход в систему",
        timestamp=datetime.utcnow() - timedelta(hours=2)
    ),
    UserActivity(
        id=str(uuid.uuid4()),
        user_id=admin_id,
        type="report_created",
        description="Создан производственный отчет за октябрь",
        timestamp=datetime.utcnow() - timedelta(hours=5)
    ),
    UserActivity(
        id=str(uuid.uuid4()),
        user_id=admin_id,
        type="task_completed",
        description="Завершена задача 'Аудит безопасности'",
        timestamp=datetime.utcnow() - timedelta(days=1)
    ),
    UserActivity(
        id=str(uuid.uuid4()),
        user_id=user_id,
        type="login",
        description="Вход в систему",
        timestamp=datetime.utcnow() - timedelta(hours=1)
    ),
    UserActivity(
        id=str(uuid.uuid4()),
        user_id=user_id,
        type="task_updated",
        description="Обновлен статус задачи",
        timestamp=datetime.utcnow() - timedelta(hours=3)
    )
]
db.add_all(user_activities)
db.commit()

# Создание задач пользователей
user_tasks_list = [
    UserTask(
        id=str(uuid.uuid4()),
        user_id=admin_id,
        title="Проверить отчет по KPI за Q3",
        priority="high",
        deadline=date.today() + timedelta(days=2),
        is_notification=False
    ),
    UserTask(
        id=str(uuid.uuid4()),
        user_id=admin_id,
        title="Утвердить бюджет на следующий квартал",
        priority="medium",
        deadline=date.today() + timedelta(days=5),
        is_notification=False
    ),
    UserTask(
        id=str(uuid.uuid4()),
        user_id=admin_id,
        title="Новое уведомление: Требуется подпись",
        priority="high",
        deadline=None,
        is_notification=True
    ),
    UserTask(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Провести техническое обслуживание линии №3",
        priority="high",
        deadline=date.today() + timedelta(days=1),
        is_notification=False
    ),
    UserTask(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Подготовить отчет о простоях",
        priority="medium",
        deadline=date.today() + timedelta(days=3),
        is_notification=False
    )
]
db.add_all(user_tasks_list)
db.commit()

# Создание команд пользователей
team_members = [
    TeamMember(
        id=str(uuid.uuid4()),
        user_id=admin_id,
        name="Петров П.П.",
        status="active"
    ),
    TeamMember(
        id=str(uuid.uuid4()),
        user_id=admin_id,
        name="Сидоров С.С.",
        status="offline"
    ),
    TeamMember(
        id=str(uuid.uuid4()),
        user_id=admin_id,
        name="Козлов К.К.",
        status="busy"
    ),
    TeamMember(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name="Иванов И.И.",
        status="active"
    ),
    TeamMember(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name="Смирнов С.С.",
        status="active"
    )
]
db.add_all(team_members)
db.commit()

# Создание отчетов пользователей
user_reports = [
    UserReport(
        id=str(uuid.uuid4()),
        user_id=admin_id,
        branch="Москва",
        metric1=95.5,
        metric2=88.2,
        metric3=12.5
    ),
    UserReport(
        id=str(uuid.uuid4()),
        user_id=admin_id,
        branch="Санкт-Петербург",
        metric1=92.3,
        metric2=85.7,
        metric3=15.2
    ),
    UserReport(
        id=str(uuid.uuid4()),
        user_id=user_id,
        branch="Казань",
        metric1=89.8,
        metric2=82.1,
        metric3=18.3
    )
]
db.add_all(user_reports)
db.commit()

# Создание уведомлений
notifications = [
    Notification(
        type="error",
        title="Ошибка загрузки",
        message="Не удалось загрузить данные для производственной линии 3. Проверьте соединение и повторите попытку.",
        icon="🔴",
        timestamp=datetime.utcnow() - timedelta(hours=2),
        priority="high",
        is_new=True,
        is_read=False,
        user_id=admin_id
    ),
    Notification(
        type="report",
        title="Доступен новый отчёт",
        message="Производственный отчёт за третий квартал 2025 года уже доступен.",
        icon="📊",
        timestamp=datetime.utcnow() - timedelta(hours=8),
        priority="medium",
        is_new=True,
        is_read=False,
        report_id=123,
        user_id=admin_id
    ),
    Notification(
        type="task",
        title="Назначена новая задача",
        message="Рассмотреть и утвердить производственный график на следующую неделю.",
        icon="📋",
        timestamp=datetime.utcnow() - timedelta(hours=6),
        priority="high",
        is_new=True,
        is_read=False,
        task_id=1,
        user_id=admin_id
    ),
    Notification(
        type="info",
        title="Плановая проверка систем",
        message="Сервис интеграций будет недоступен завтра с 01:00 до 03:00 по Москве.",
        icon="ℹ️",
        timestamp=datetime.utcnow() - timedelta(days=1, hours=12),
        priority="low",
        is_new=False,
        is_read=True,
        user_id=admin_id
    ),
    Notification(
        type="error",
        title="Критическая ошибка",
        message="Простой оборудования — RM-102 остановлено, >2ч",
        icon="🔴",
        timestamp=datetime.utcnow() - timedelta(hours=1),
        priority="critical",
        is_new=True,
        is_read=False,
        user_id=admin_id
    ),
    Notification(
        type="task",
        title="Новая задача",
        message="Проверить оборудование линии 3",
        icon="📋",
        timestamp=datetime.utcnow() - timedelta(hours=10),
        priority="medium",
        is_new=True,
        is_read=False,
        task_id=2,
        user_id=user_id
    )
]
db.add_all(notifications)
db.commit()

# Создание KPI индикаторов
kpi_indicators = [
    KPIIndicator(
        id=1,
        name="Производственный отчет",
        period="К1 2025",
        branch="Москва",
        type="Производство",
        plan=100,
        fact=120,
        deviation="+20",
        trend="▲ Повыш.",
        kpi_key="production_volume",
        link="kpivis.html?kpi=production_volume"
    ),
    KPIIndicator(
        id=2,
        name="Финансовый показатель",
        period="К1 2025",
        branch="Москва",
        type="Финансы",
        plan=5000,
        fact=4500,
        deviation="-500",
        trend="▼ Сниж.",
        kpi_key="financial_metric",
        link="kpivis.html?kpi=financial_metric"
    ),
    KPIIndicator(
        id=3,
        name="Эффективность оборудования",
        period="К1 2025",
        branch="Иркутск",
        type="Производство",
        plan=85,
        fact=92,
        deviation="+7",
        trend="▲ Повыш.",
        kpi_key="equipment_efficiency",
        link="kpivis.html?kpi=equipment_efficiency"
    ),
    KPIIndicator(
        id=4,
        name="Качество продукции",
        period="К2 2025",
        branch="Москва",
        type="Производство",
        plan=95,
        fact=97,
        deviation="+2",
        trend="▲ Повыш.",
        kpi_key="quality_metric",
        link="kpivis.html?kpi=quality_metric"
    ),
    KPIIndicator(
        id=5,
        name="Прибыль",
        period="К2 2025",
        branch="Все",
        type="Финансы",
        plan=10000,
        fact=11500,
        deviation="+1500",
        trend="▲ Повыш.",
        kpi_key="profit",
        link="kpivis.html?kpi=profit"
    ),
    KPIIndicator(
        id=6,
        name="Объем производства",
        period="К1 2025",
        branch="Санкт-Петербург",
        type="Производство",
        plan=850,
        fact=920,
        deviation="+70",
        trend="▲ Повыш.",
        kpi_key="production_spb"
    ),
    KPIIndicator(
        id=7,
        name="Энергоэффективность",
        period="К1 2025",
        branch="Санкт-Петербург",
        type="Производство",
        plan=95,
        fact=92,
        deviation="-3",
        trend="▼ Сниж.",
        kpi_key="energy_spb"
    ),
    KPIIndicator(
        id=8,
        name="Производительность труда",
        period="К2 2025",
        branch="Санкт-Петербург",
        type="Производство",
        plan=120,
        fact=135,
        deviation="+15",
        trend="▲ Повыш.",
        kpi_key="productivity_spb"
    ),
    KPIIndicator(
        id=9,
        name="Производственный план",
        period="К1 2025",
        branch="Казань",
        type="Производство",
        plan=720,
        fact=750,
        deviation="+30",
        trend="▲ Повыш.",
        kpi_key="production_kzn"
    ),
    KPIIndicator(
        id=10,
        name="Рентабельность",
        period="К1 2025",
        branch="Казань",
        type="Финансы",
        plan=18.5,
        fact=21.3,
        deviation="+2.8",
        trend="▲ Повыш.",
        kpi_key="profitability_kzn"
    ),
    KPIIndicator(
        id=11,
        name="Качество продукции",
        period="К2 2025",
        branch="Казань",
        type="Производство",
        plan=98.5,
        fact=97.8,
        deviation="-0.7",
        trend="▼ Сниж.",
        kpi_key="quality_kzn"
    ),
    KPIIndicator(
        id=12,
        name="Загрузка оборудования",
        period="К3 2025",
        branch="Казань",
        type="Производство",
        plan=85,
        fact=88.5,
        deviation="+3.5",
        trend="▲ Повыш.",
        kpi_key="equipment_kzn"
    )
]
db.add_all(kpi_indicators)
db.commit()

# Создание детализации KPI (для production_volume)
kpi_details = [
    # Смены
    KPIDetail(
        kpi_id=1,
        tab_type="shifts",
        name="Смена 1",
        plan=300,
        fact=350,
        deviation="+50",
        trend="▲ Повыш.",
        is_positive=True
    ),
    KPIDetail(
        kpi_id=1,
        tab_type="shifts",
        name="Смена 2",
        plan=400,
        fact=380,
        deviation="-20",
        trend="▼ Сниж.",
        is_positive=False
    ),
    KPIDetail(
        kpi_id=1,
        tab_type="shifts",
        name="Смена 3",
        plan=300,
        fact=320,
        deviation="+20",
        trend="▲ Повыш.",
        is_positive=True
    ),
    # Сотрудники
    KPIDetail(
        kpi_id=1,
        tab_type="employees",
        name="Иванов А.",
        plan=100,
        fact=115,
        deviation="+15",
        trend="▲ Повыш.",
        is_positive=True
    ),
    KPIDetail(
        kpi_id=1,
        tab_type="employees",
        name="Петров Б.",
        plan=120,
        fact=110,
        deviation="-10",
        trend="▼ Сниж.",
        is_positive=False
    ),
    KPIDetail(
        kpi_id=1,
        tab_type="employees",
        name="Сидоров В.",
        plan=80,
        fact=95,
        deviation="+15",
        trend="▲ Повыш.",
        is_positive=True
    ),
    # Оборудование
    KPIDetail(
        kpi_id=1,
        tab_type="equipment",
        name="Машина RM-102",
        plan=500,
        fact=550,
        deviation="+50",
        trend="▲ Повыш.",
        is_positive=True
    ),
    KPIDetail(
        kpi_id=1,
        tab_type="equipment",
        name="Машина RM-103",
        plan=300,
        fact=280,
        deviation="-20",
        trend="▼ Сниж.",
        is_positive=False
    ),
    KPIDetail(
        kpi_id=1,
        tab_type="equipment",
        name="Машина RM-104",
        plan=200,
        fact=220,
        deviation="+20",
        trend="▲ Повыш.",
        is_positive=True
    )
]
db.add_all(kpi_details)
db.commit()

print("OK: База данных инициализирована!")
print("\nТестовые пользователи:")
print("- admin / admin123 (роль: admin)")
print("- user / user123 (роль: user)")
print("\nФилиалы: Москва, Иркутск, Санкт-Петербург")
print(f"\nСоздано задач: {len(tasks)}")
print(f"Создано уведомлений: {len(notifications)}")
print(f"Создано KPI индикаторов: {len(kpi_indicators)}")
print(f"Создано деталей KPI: {len(kpi_details)}")
print(f"Создано отделов: {len(departments)}")
print(f"Создано истории задач: {len(task_history)}")
print(f"Создано отчетов: {len(reports)}")
print(f"Создано записей данных: {len(data_records)}")
print(f"Создано истории данных: {len(data_history)}")
print(f"Создано финансовых метрик: {len(financial_metrics)}")
print(f"Создано сравнений затрат: {len(cost_comparisons)}")
print(f"Создано оборудования: {len(equipment_list)}")
print(f"Создано планов обслуживания: {len(maintenance_plans)}")
print(f"Создано метрик пользователей: {len(user_metrics)}")
print(f"Создано активностей: {len(user_activities)}")
print(f"Создано задач пользователей: {len(user_tasks_list)}")
print(f"Создано членов команды: {len(team_members)}")
print(f"Создано отчетов пользователей: {len(user_reports)}")
print("\nНовые эндпоинты (Profile Page):")
print("- GET /api/profile")
print("- PUT /api/profile")
print("- POST /api/profile/password")
print("- GET /api/profile/metrics")
print("- GET /api/profile/activity?limit=10")
print("- GET /api/profile/tasks?limit=10")
print("- GET /api/profile/team")
print("- GET /api/profile/reports")

db.close()

