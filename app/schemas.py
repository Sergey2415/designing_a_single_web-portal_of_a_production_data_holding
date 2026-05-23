from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime, date
from enum import Enum


# ============================================================================
# ENUMS - Определенные значения для полей
# ============================================================================

class UserRole(str, Enum):
    """Роли пользователей"""
    ADMIN = "admin"
    USER = "user"


class NotificationType(str, Enum):
    """Типы уведомлений"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"
    TASK = "task"
    REPORT = "report"


class NotificationPriority(str, Enum):
    """Приоритет уведомлений"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(str, Enum):
    """Статусы задач"""
    IN_PROGRESS = "В процессе"
    COMPLETED = "Выполнена"
    OVERDUE = "Просрочена"


class TaskPriority(str, Enum):
    """Приоритеты задач"""
    HIGH = "Высокий"
    MEDIUM = "Средний"
    LOW = "Низкий"


class ReportType(str, Enum):
    """Типы отчетов"""
    PRODUCTION = "production"
    FINANCIAL = "financial"
    EQUIPMENT = "equipment"
    ANALYTICS = "analytics"


class ReportStatus(str, Enum):
    """Статусы отчетов"""
    READY = "ready"
    IN_PROGRESS = "inProgress"
    ACCEPTED = "accepted"


class EquipmentType(str, Enum):
    """Типы оборудования"""
    PRODUCTION = "production"
    AUXILIARY = "auxiliary"
    TRANSPORT = "transport"


class EquipmentStatus(str, Enum):
    """Статусы оборудования"""
    READY = "ready"
    IN_PROGRESS = "inprogress"
    ACCEPTED = "accepted"


class DataType(str, Enum):
    """Типы данных"""
    PRODUCTION = "production"
    DOWNTIME = "downtime"


class DataHistoryStatus(str, Enum):
    """Статусы истории данных"""
    READY = "ready"
    IN_PROGRESS = "inProgress"
    ACCEPTED = "accepted"


class CostType(str, Enum):
    """Типы затрат"""
    MATERIALS = "materials"
    LABOR = "labor"
    EQUIPMENT = "equipment"
    OVERHEAD = "overhead"


class FinancialReportType(str, Enum):
    """Типы финансовых отчетов"""
    DAILY = "daily"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class TeamMemberStatus(str, Enum):
    """Статусы членов команды"""
    ACTIVE = "active"
    OFFLINE = "offline"
    BUSY = "busy"


# ============================================================================
# COMMON / SHARED SCHEMAS
# ============================================================================

class ErrorResponse(BaseModel):
    """Стандартный ответ с ошибкой"""
    success: bool = Field(False, description="Успешность операции")
    message: str = Field(..., description="Сообщение об ошибке", example="Ошибка при обработке запроса")


class MetricValue(BaseModel):
    """Значение метрики с изменением"""
    value: float = Field(..., description="Текущее значение", example=95.5)
    changePercentage: float = Field(..., description="Процент изменения", example=2.3)
    changeDirection: str = Field(..., description="Направление изменения (up/down)", example="down")


# ============================================================================
# AUTH SCHEMAS
# ============================================================================

class LoginRequest(BaseModel):
    """Запрос на авторизацию"""
    username: str = Field(..., description="Имя пользователя", example="admin")
    password: str = Field(..., description="Пароль", example="admin123")


class UserResponse(BaseModel):
    """Информация о пользователе"""
    id: str = Field(..., description="ID пользователя")
    name: str = Field(..., description="Имя пользователя", example="Администратор")
    role: UserRole = Field(..., description="Роль пользователя")


class LoginResponse(BaseModel):
    """Ответ при авторизации"""
    success: bool = Field(..., description="Успешность операции")
    token: Optional[str] = Field(None, description="JWT токен")
    user: Optional[UserResponse] = Field(None, description="Данные пользователя")
    message: Optional[str] = Field(None, description="Сообщение")


class AuthCheckResponse(BaseModel):
    """Проверка авторизации"""
    success: bool
    user: Optional[UserResponse] = None
    message: Optional[str] = None


# ============================================================================
# BRANCH SCHEMAS
# ============================================================================

class BranchResponse(BaseModel):
    """Информация о филиале"""
    id: int = Field(..., description="ID филиала")
    name: str = Field(..., description="Название филиала", example="Москва")


# ============================================================================
# KPI SCHEMAS
# ============================================================================

class KPIItem(BaseModel):
    """Элемент KPI"""
    value: str = Field(..., description="Значение", example="95%")
    change: str = Field(..., description="Изменение", example="+2.3%")
    isPositive: bool = Field(..., description="Положительное ли изменение")


class KPIResponse(BaseModel):
    """KPI метрики"""
    productivity: KPIItem
    costPerTon: KPIItem
    uptime: KPIItem
    efficiencyIndex: KPIItem


class ProductionDataPoint(BaseModel):
    """Точка данных производства"""
    date: str = Field(..., description="Дата", example="2025-10-29")
    value: float = Field(..., description="Значение", example=1050.5)


class DowntimeDataPoint(BaseModel):
    """Точка данных простоев"""
    category: str = Field(..., description="Категория", example="Плановое обслуживание")
    value: float = Field(..., description="Значение часов", example=12.5)
    color: str = Field(..., description="Цвет для графика", example="#FF6384")


# ============================================================================
# NOTIFICATION SCHEMAS
# ============================================================================

class NotificationResponse(BaseModel):
    """Краткое уведомление"""
    id: int
    type: NotificationType
    message: str = Field(..., example="Требуется проверка оборудования")
    icon: str = Field(..., example="⚠")
    timestamp: datetime


class NotificationDetailedResponse(BaseModel):
    """Детальное уведомление"""
    id: int
    type: NotificationType
    title: Optional[str] = None
    text: str
    time: datetime
    priority: NotificationPriority
    isNew: bool
    isRead: bool
    reportId: Optional[int] = None
    taskId: Optional[int] = None
    status: Optional[str] = None


class NotificationSummaryResponse(BaseModel):
    """Сводка уведомлений"""
    newNotifications: int = Field(..., description="Новые уведомления", example=5)
    openTasks: int = Field(..., description="Открытые задачи", example=3)
    criticalErrors: int = Field(..., description="Критические ошибки", example=1)
    newTasks: int = Field(..., description="Новые задачи", example=2)


class MarkReadRequest(BaseModel):
    """Отметить как прочитанное"""
    notification_id: int = Field(..., description="ID уведомления", example=1)


class MarkReadResponse(BaseModel):
    status: str = Field(..., example="success")


class CommentRequest(BaseModel):
    """Добавить комментарий"""
    comment: str = Field(..., description="Текст комментария", example="Взял в работу")


class CommentResponse(BaseModel):
    status: str
    commentId: int


class AssignRequest(BaseModel):
    """Назначить исполнителя"""
    assigneeId: str = Field(..., description="ID исполнителя")


class AssignResponse(BaseModel):
    status: str


class TaskCompleteResponse(BaseModel):
    status: str


class NotificationsRefreshResponse(BaseModel):
    """Обновленные уведомления"""
    summary: NotificationSummaryResponse
    notifications: List[NotificationDetailedResponse]


# ============================================================================
# USER SETTINGS SCHEMAS
# ============================================================================

class GeneralSettings(BaseModel):
    language: Optional[Literal["ru", "en", "de", "fr"]] = Field(None, description="Язык интерфейса", example="ru")
    timeFormat: Optional[Literal["24h", "12h"]] = Field(None, description="Формат времени", example="24h")
    dateFormat: Optional[Literal["DD.MM.YYYY", "MM/DD/YYYY", "YYYY-MM-DD"]] = Field(None, example="DD.MM.YYYY")
    regional: Optional[str] = Field(None, description="Региональные настройки", example="ru-RU")


class ThemeSettings(BaseModel):
    selected: Optional[Literal["light", "dark", "auto"]] = Field(None, description="Тема", example="dark")
    autoByTime: Optional[bool] = Field(None, description="Автопереключение по времени")


class NotificationSettings(BaseModel):
    newReports: Optional[bool] = None
    equipmentFailures: Optional[bool] = None
    dailySummaryEmail: Optional[bool] = None
    pushBrowser: Optional[bool] = None
    telegram: Optional[bool] = None
    soundVolume: Optional[int] = Field(None, ge=0, le=100, description="Громкость звука", example=50)
    doNotDisturb: Optional[bool] = None


class UserSettingsResponse(BaseModel):
    general: GeneralSettings
    theme: ThemeSettings
    notifications: NotificationSettings


class UserSettingsUpdate(BaseModel):
    general: Optional[GeneralSettings] = None
    theme: Optional[ThemeSettings] = None
    notifications: Optional[NotificationSettings] = None


class SettingsUpdateResponse(BaseModel):
    status: str
    message: str


# ============================================================================
# USER PROFILE SCHEMAS
# ============================================================================

class UserProfileResponse(BaseModel):
    name: str
    role: UserRole
    department: Optional[str] = None
    avatarUrl: Optional[str] = None


class AvatarUploadResponse(BaseModel):
    status: str
    avatarUrl: str


class ChangePasswordRequest(BaseModel):
    """Смена пароля"""
    oldPassword: str = Field(..., description="Старый пароль")
    newPassword: str = Field(..., description="Новый пароль", min_length=6)
    confirmNewPassword: str = Field(..., description="Подтверждение нового пароля")


class ChangePasswordResponse(BaseModel):
    status: str


class TwoFactorStatusResponse(BaseModel):
    enabled: bool
    setupUrl: Optional[str] = None


class TwoFactorEnableRequest(BaseModel):
    code: str = Field(..., description="6-значный код", example="123456", min_length=6, max_length=6)


class TwoFactorEnableResponse(BaseModel):
    status: str


class LoginHistoryItem(BaseModel):
    device: str = Field(..., example="Chrome on Windows")
    ip: str = Field(..., example="192.168.1.1")
    date: datetime


class AccountDeleteResponse(BaseModel):
    status: str


# ============================================================================
# SYSTEM SCHEMAS
# ============================================================================

class SystemInfoResponse(BaseModel):
    version: str = Field(..., example="1.0.0")
    lastUpdate: datetime
    serverStatus: Literal["online", "offline", "maintenance"] = Field(..., example="online")


class CheckUpdatesResponse(BaseModel):
    updateAvailable: bool
    newVersion: Optional[str] = None
    releaseNotes: Optional[str] = None


class BugReportRequest(BaseModel):
    description: str = Field(..., description="Описание проблемы", min_length=10)
    steps: Optional[str] = Field(None, description="Шаги воспроизведения")
    attachments: Optional[List[str]] = None


class BugReportResponse(BaseModel):
    status: str
    ticketId: str


# ============================================================================
# KPI PAGE SCHEMAS
# ============================================================================

class KPIRowResponse(BaseModel):
    name: str
    plan: float
    fact: float
    deviation: str
    trend: str
    link: str


class KPISummaryItem(BaseModel):
    value: str
    sub: str
    isPositive: bool


class KPISummaryResponse(BaseModel):
    trendKpi: KPISummaryItem
    branchCompare: KPISummaryItem


class KPIDataResponse(BaseModel):
    rows: List[KPIRowResponse]
    summary: KPISummaryResponse


class KPIFiltersResponse(BaseModel):
    periods: List[str] = Field(..., example=["Q1 2025", "Q2 2025", "Q3 2025"])
    branches: List[str] = Field(..., example=["Москва", "Санкт-Петербург", "Казань"])
    types: List[str] = Field(..., example=["production", "financial", "equipment"])


class KPIStatsResponse(BaseModel):
    plan: float
    fact: float
    deviation: str
    trend: str
    isPositive: bool


class KPIDetailRowResponse(BaseModel):
    shift: Optional[str] = None
    employee: Optional[str] = None
    equipment: Optional[str] = None
    plan: float
    fact: float
    deviation: str
    trend: str
    isPositive: bool


class KPIDetailsResponse(BaseModel):
    stats: KPIStatsResponse
    rows: List[KPIDetailRowResponse]


# ============================================================================
# TASKS SCHEMAS
# ============================================================================

class TaskItemResponse(BaseModel):
    id: int
    title: str
    report: Optional[str] = None
    responsible: Optional[str] = None
    due: Optional[str] = None
    status: TaskStatus


class TaskHistoryItemResponse(BaseModel):
    id: int
    icon: str
    text: str
    author: str
    date: str


class ResponsibleResponse(BaseModel):
    value: str = Field(..., example="eng")
    label: str = Field(..., example="Инженерная команда")


class TaskCreateRequest(BaseModel):
    title: str = Field(..., description="Заголовок задачи", min_length=3)
    description: Optional[str] = None
    responsible: str = Field(..., description="Ответственный", example="eng")
    due: str = Field(..., description="Срок выполнения", example="2025-11-01")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Приоритет")
    report: Optional[str] = None


class TaskCreateResponse(BaseModel):
    status: str
    taskId: int


# ============================================================================
# REPORTS SCHEMAS
# ============================================================================

class ReportListItem(BaseModel):
    id: str
    date: str
    type: ReportType
    author: str
    status: ReportStatus


class ReportsListResponse(BaseModel):
    success: bool
    data: List[ReportListItem]
    total: int
    page: int
    pages: int


class ReportDetailItem(BaseModel):
    parameter: str
    target: float
    actual: float
    deviation: float
    status: Literal["good", "normal", "bad"] = Field(..., example="good")


class ReportDowntimeReason(BaseModel):
    reason: str
    percentage: float = Field(..., ge=0, le=100)


class ReportDetailData(BaseModel):
    id: str
    title: str
    date: str
    type: ReportType
    author: str
    status: ReportStatus
    content: Optional[str] = None
    period: Optional[str] = None
    department: Optional[str] = None
    kpi: Optional[str] = None
    details: Optional[List[ReportDetailItem]] = []
    downtimeReasons: Optional[List[ReportDowntimeReason]] = []


class ReportDetailResponse(BaseModel):
    success: bool
    data: ReportDetailData


class ReportCreateRequest(BaseModel):
    title: str = Field(..., min_length=3)
    date: str = Field(..., example="2025-10-29")
    type: ReportType
    author: str
    status: ReportStatus = ReportStatus.IN_PROGRESS
    content: Optional[str] = None
    period: Optional[str] = None
    department: Optional[str] = None
    kpi: Optional[str] = None


class ReportCreateResponse(BaseModel):
    success: bool
    id: str
    message: str


class ReportDeleteResponse(BaseModel):
    success: bool
    message: str


class ReportSendRequest(BaseModel):
    managerId: Optional[str] = None
    message: Optional[str] = None


class ReportSendResponse(BaseModel):
    success: bool
    message: str


# ============================================================================
# DATA MANAGEMENT SCHEMAS
# ============================================================================

class DataManualRequest(BaseModel):
    date: str = Field(..., example="2025-10-29")
    type: DataType
    value: float = Field(..., example=1050.5)
    comment: Optional[str] = None
    userId: str


class DataManualResponse(BaseModel):
    success: bool
    id: str
    message: str


class DataUploadResponse(BaseModel):
    success: bool
    id: str
    message: str


class ValidationIssue(BaseModel):
    row: int
    message: str


class DataValidateRequest(BaseModel):
    uploadId: str
    userId: str


class DataValidateResponse(BaseModel):
    success: bool
    validated: bool
    issues: List[ValidationIssue]
    message: str


class DataConsolidateRequest(BaseModel):
    uploadId: str
    department: str
    userId: str


class DataConsolidateResponse(BaseModel):
    success: bool
    id: str
    message: str


class DataHistoryItem(BaseModel):
    id: str
    date: str
    status: DataHistoryStatus
    comment: Optional[str] = None
    user: str
    recordId: Optional[str] = None


class DataHistoryResponse(BaseModel):
    success: bool
    data: List[DataHistoryItem]
    total: int
    page: int
    pages: int


# ============================================================================
# FINANCES SCHEMAS
# ============================================================================

class FinancialMetricsData(BaseModel):
    unitCost: MetricValue
    updatedAt: str


class FinancialMetricsResponse(BaseModel):
    success: bool
    data: FinancialMetricsData


class CostDynamicsData(BaseModel):
    q1: float = Field(..., description="Q1 затраты", example=350000.0)
    q2: float = Field(..., description="Q2 затраты", example=245000.0)
    q3: float = Field(..., description="Q3 затраты", example=215000.0)
    q4: float = Field(..., description="Q4 затраты", example=180000.0)


class CostDynamicsResponse(BaseModel):
    success: bool
    data: CostDynamicsData


class CostComparisonItem(BaseModel):
    period: str = Field(..., example="Q1 2025")
    department: str = Field(..., example="Производственный отдел")
    type: CostType
    amount: float = Field(..., ge=0)
    comment: Optional[str] = None
    status: Literal["approved", "pending", "rejected"] = Field(..., example="approved")


class CostComparisonResponse(BaseModel):
    success: bool
    data: List[CostComparisonItem]
    total: int
    page: int
    pages: int


class BudgetDataset(BaseModel):
    label: str
    data: List[float]
    backgroundColor: str = Field(..., example="#FF6384")


class BudgetEfficiencyData(BaseModel):
    labels: List[str]
    datasets: List[BudgetDataset]


class BudgetEfficiencyResponse(BaseModel):
    success: bool
    data: BudgetEfficiencyData


class FinancialReportCreateRequest(BaseModel):
    type: FinancialReportType
    period: str = Field(..., example="Q3 2025")
    department: str


class FinancialReportCreateResponse(BaseModel):
    success: bool
    id: str
    message: str


# ============================================================================
# EQUIPMENT SCHEMAS
# ============================================================================

class EquipmentItem(BaseModel):
    id: str
    name: str
    branch: str
    type: EquipmentType
    status: EquipmentStatus
    lastCheck: Optional[str] = None
    responsible: Optional[str] = None
    createdAt: str


class EquipmentListResponse(BaseModel):
    success: bool
    data: List[EquipmentItem]
    total: int
    page: int
    pages: int


class EquipmentUpdateRequest(BaseModel):
    status: Optional[EquipmentStatus] = None
    lastCheck: Optional[str] = Field(None, example="2025-10-29")
    responsible: Optional[str] = None


class EquipmentUpdateResponse(BaseModel):
    success: bool
    message: str


class EquipmentDeleteResponse(BaseModel):
    success: bool
    message: str


class MaintenancePlanCreateRequest(BaseModel):
    date: str = Field(..., example="2025-11-15")
    branch: str
    equipmentIds: List[str] = Field(..., min_items=1)


class MaintenancePlanCreateResponse(BaseModel):
    success: bool
    id: str
    message: str


class DowntimeHistoryItem(BaseModel):
    date: str
    value: float = Field(..., description="Часы простоя", ge=0)


class DowntimeReason(BaseModel):
    name: str
    percentage: float = Field(..., ge=0, le=100)


class DowntimeAnalysisData(BaseModel):
    downtimePercentage: float = Field(..., ge=0, le=100)
    trend: float = Field(..., description="Тренд изменения в %")
    history: List[DowntimeHistoryItem]
    reasons: List[DowntimeReason]


class DowntimeAnalysisResponse(BaseModel):
    success: bool
    data: DowntimeAnalysisData


# ============================================================================
# PROFILE SCHEMAS
# ============================================================================

class ProfileData(BaseModel):
    name: str
    position: str
    location: str
    accessLevel: UserRole
    email: str
    phone: str


class ProfileResponse(BaseModel):
    success: bool
    data: ProfileData


class ProfileUpdateRequest(BaseModel):
    name: str = Field(..., min_length=2)
    position: str
    location: str
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    phone: str


class ProfileUpdateResponse(BaseModel):
    success: bool
    message: str


class PasswordChangeRequest(BaseModel):
    currentPassword: str
    newPassword: str = Field(..., min_length=6)
    confirmPassword: str


class PasswordChangeResponse(BaseModel):
    success: bool
    message: str


class ProfileMetricsData(BaseModel):
    laborProductivity: MetricValue
    repairEfficiency: MetricValue
    equipmentDowntime: MetricValue
    cost: MetricValue


class ProfileMetricsResponse(BaseModel):
    success: bool
    data: ProfileMetricsData


class ActivityItem(BaseModel):
    type: Literal["login", "report_created", "task_completed", "task_updated"] = Field(..., example="login")
    description: str
    timestamp: str


class ProfileActivityResponse(BaseModel):
    success: bool
    data: List[ActivityItem]


class TaskItem(BaseModel):
    title: str
    priority: TaskPriority
    deadline: Optional[str] = None
    isNotification: bool


class ProfileTasksResponse(BaseModel):
    success: bool
    data: List[TaskItem]


class TeamMemberItem(BaseModel):
    name: str
    status: TeamMemberStatus


class ProfileTeamResponse(BaseModel):
    success: bool
    data: List[TeamMemberItem]


class ReportItem(BaseModel):
    branch: str
    metric1: float
    metric2: float
    metric3: float


class ProfileReportsResponse(BaseModel):
    success: bool
    data: List[ReportItem]
