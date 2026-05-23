from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # password_hash in auth.py
    name = Column(String, nullable=False)
    position = Column(String, nullable=True)  # Должность
    location = Column(String, nullable=True)  # Местоположение
    phone = Column(String, nullable=True)  # Телефон
    role = Column(String, nullable=False)
    department = Column(String, nullable=True)
    email = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    two_fa_secret = Column(String, nullable=True)
    two_fa_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    settings = relationship("UserSettings", back_populates="user", uselist=False)
    login_history = relationship("LoginHistory", back_populates="user")
    bug_reports = relationship("BugReport", back_populates="user")


class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    kpi_metrics = relationship("KPIMetric", back_populates="branch")
    production_data = relationship("ProductionData", back_populates="branch")
    downtime_data = relationship("DowntimeData", back_populates="branch")
    notifications = relationship("Notification", back_populates="branch")


class KPIMetric(Base):
    __tablename__ = "kpi_metrics"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    productivity_value = Column(String)
    productivity_change = Column(String)
    is_positive_productivity = Column(Boolean)
    
    cost_per_ton_value = Column(String)
    cost_per_ton_change = Column(String)
    is_positive_cost = Column(Boolean)
    
    uptime_value = Column(String)
    uptime_change = Column(String)
    is_positive_uptime = Column(Boolean)
    
    efficiency_index_value = Column(String)
    efficiency_index_change = Column(String)
    is_positive_efficiency = Column(Boolean)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    branch = relationship("Branch", back_populates="kpi_metrics")


class ProductionData(Base):
    __tablename__ = "production_data"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    value = Column(Float, nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    branch = relationship("Branch", back_populates="production_data")


class DowntimeData(Base):
    __tablename__ = "downtime_data"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    color = Column(String, nullable=True)
    period = Column(String, nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    branch = relationship("Branch", back_populates="downtime_data")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    type = Column(String, nullable=False)  # error, task, report, info
    title = Column(String, nullable=True)
    message = Column(Text, nullable=False)  # text
    icon = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)  # time
    priority = Column(String, default="medium")  # low, medium, high, critical
    is_new = Column(Boolean, default=True)
    is_read = Column(Boolean, default=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    report_id = Column(Integer, nullable=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    assignee_id = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    branch = relationship("Branch", back_populates="notifications")
    task = relationship("Task", back_populates="notifications")
    comments = relationship("Comment", back_populates="notification")
    user = relationship("User", foreign_keys=[user_id])
    assignee = relationship("User", foreign_keys=[assignee_id])


class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    language = Column(String, default="ru")  # Изменено с "Русский" на "ru"
    time_format = Column(String, default="24h")  # Изменено с "24-часовой" на "24h"
    date_format = Column(String, default="DD.MM.YYYY")
    regional = Column(String, default="RUB, кг")
    theme = Column(String, default="light")
    auto_theme_by_time = Column(Boolean, default=True)
    notify_new_reports = Column(Boolean, default=True)
    notify_equipment_failures = Column(Boolean, default=True)
    notify_daily_email = Column(Boolean, default=True)
    notify_push_browser = Column(Boolean, default=True)
    notify_telegram = Column(Boolean, default=False)
    sound_volume = Column(Integer, default=70)
    do_not_disturb = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="settings")


class LoginHistory(Base):
    __tablename__ = "login_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    device = Column(String, nullable=False)
    ip = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="login_history")


class SystemInfo(Base):
    __tablename__ = "system_info"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, nullable=False)
    last_update = Column(DateTime, nullable=False)
    server_status = Column(String, default="Online")


class BugReport(Base):
    __tablename__ = "bug_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    description = Column(Text, nullable=False)
    steps = Column(Text, nullable=True)
    attachments = Column(Text, nullable=True)  # JSON array as string
    status = Column(String, default="open")
    ticket_id = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bug_reports")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    report = Column(String, nullable=True)  # Название отчета
    responsible = Column(String, nullable=True)  # Отдел или сотрудник
    status = Column(String, default="В процессе")  # В процессе, Выполнена, Просрочена
    assignee_id = Column(String, ForeignKey("users.id"), nullable=True)
    creator_id = Column(String, ForeignKey("users.id"), nullable=True)
    due_date = Column(DateTime, nullable=True)  # Срок выполнения
    priority = Column(String, default="Средний")  # Низкий, Средний, Высокий
    report_file_url = Column(String, nullable=True)  # Путь к файлу отчета
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assignee = relationship("User", foreign_keys=[assignee_id])
    creator = relationship("User", foreign_keys=[creator_id])
    notifications = relationship("Notification", back_populates="task")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    notification = relationship("Notification", back_populates="comments")
    user = relationship("User")


class KPIIndicator(Base):
    __tablename__ = "kpi_indicators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    period = Column(String, nullable=False)  # К1 2025, К2 2025, etc.
    branch = Column(String, nullable=False)  # Москва, Иркутск, Все
    type = Column(String, nullable=False)  # Производство, Финансы, Все
    plan = Column(Float, nullable=False)
    fact = Column(Float, nullable=False)
    deviation = Column(String, nullable=False)  # +20, -500
    trend = Column(String, nullable=False)  # ▲ Повыш., ▼ Сниж.
    link = Column(String, nullable=True)  # kpivis.html?id=1
    kpi_key = Column(String, nullable=True)  # production_volume для детального просмотра
    created_at = Column(DateTime, default=datetime.utcnow)

    details = relationship("KPIDetail", back_populates="indicator")


class KPIDetail(Base):
    __tablename__ = "kpi_details"

    id = Column(Integer, primary_key=True, index=True)
    kpi_id = Column(Integer, ForeignKey("kpi_indicators.id"), nullable=False)
    tab_type = Column(String, nullable=False)  # shifts, employees, equipment
    name = Column(String, nullable=False)  # Смена 1, Иванов А., Машина RM-102
    plan = Column(Float, nullable=False)
    fact = Column(Float, nullable=False)
    deviation = Column(String, nullable=False)
    trend = Column(String, nullable=False)
    is_positive = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    indicator = relationship("KPIIndicator", back_populates="details")


class TaskHistory(Base):
    __tablename__ = "task_history"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    type = Column(String, default="success")  # success, warning, error
    icon = Column(String, default="✔")
    text = Column(Text, nullable=False)
    author = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, unique=True, nullable=False)  # eng, sec, log
    label = Column(String, nullable=False)  # Инженерная команда, Отдел безопасности


class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    type = Column(String, nullable=False)  # production, financial, equipment, analytics
    author = Column(String, nullable=False)
    status = Column(String, default="inProgress")  # ready, inProgress, accepted
    content = Column(Text, nullable=True)
    period = Column(String, nullable=True)  # Q1 2025, Январь 2025
    department = Column(String, nullable=True)
    kpi = Column(String, nullable=True)
    details = Column(Text, nullable=True)  # JSON string
    downtime_reasons = Column(Text, nullable=True)  # JSON string
    file_path = Column(String, nullable=True)  # Путь к PDF/CSV файлу
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DataRecord(Base):
    __tablename__ = "data_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    date = Column(Date, nullable=False)
    type = Column(String, nullable=False)  # production, downtime
    value = Column(Float, nullable=False)
    comment = Column(String, nullable=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    upload_id = Column(String, nullable=True)  # ID загрузки файла
    status = Column(String, default="pending")  # pending, validated, consolidated
    department = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")


class DataHistory(Base):
    __tablename__ = "data_history"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    date = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)  # ready, inProgress, accepted
    comment = Column(String, nullable=True)
    user = Column(String, nullable=False)
    record_id = Column(String, nullable=True)  # ID связанной записи
    action = Column(String, nullable=True)  # manual, upload, validate, consolidate
    created_at = Column(DateTime, default=datetime.utcnow)


class FinancialMetric(Base):
    __tablename__ = "financial_metrics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    unit_cost = Column(Float, nullable=False)
    change_percentage = Column(Float, nullable=False)
    change_direction = Column(String, nullable=False)  # up, down
    updated_at = Column(DateTime, default=datetime.utcnow)


class CostComparison(Base):
    __tablename__ = "cost_comparisons"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    period = Column(String, nullable=False)  # Q1 2025, Январь 2025, etc.
    department = Column(String, nullable=False)
    type = Column(String, nullable=False)  # materials, labor, overhead, etc.
    amount = Column(Float, nullable=False)
    comment = Column(String, nullable=True)
    status = Column(String, default="approved")  # approved, pending, rejected
    created_at = Column(DateTime, default=datetime.utcnow)


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    branch = Column(String, nullable=False)
    type = Column(String, nullable=False)  # production, auxiliary, transport, etc.
    status = Column(String, default="ready")  # ready, inprogress, accepted
    last_check = Column(Date, nullable=True)
    responsible = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class MaintenancePlan(Base):
    __tablename__ = "maintenance_plans"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    date = Column(Date, nullable=False)
    branch = Column(String, nullable=False)
    equipment_ids = Column(Text, nullable=False)  # JSON array
    created_at = Column(DateTime, default=datetime.utcnow)


class UserMetric(Base):
    __tablename__ = "user_metrics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    labor_productivity = Column(Text, nullable=True)  # JSON: {"value": num, "change": num}
    repair_efficiency = Column(Text, nullable=True)  # JSON
    equipment_downtime = Column(Text, nullable=True)  # JSON
    cost = Column(Text, nullable=True)  # JSON
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")


class UserActivity(Base):
    __tablename__ = "user_activity"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # login, task_completed, report_created, etc.
    description = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")


class UserTask(Base):
    __tablename__ = "user_tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    priority = Column(String, nullable=False)  # high, medium, low
    deadline = Column(Date, nullable=True)
    is_notification = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)  # Чья команда
    name = Column(String, nullable=False)
    status = Column(String, default="active")  # active, offline, busy
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")


class UserReport(Base):
    __tablename__ = "user_reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    branch = Column(String, nullable=False)
    metric1 = Column(Float, nullable=True)
    metric2 = Column(Float, nullable=True)
    metric3 = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")

