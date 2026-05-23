# Production Management Backend

FastAPI + SQLAlchemy приложение для управления производством.

## Установка

1. Создать виртуальное окружение:
```bash
python -m venv venv
venv\Scripts\activate
```

2. Установить зависимости:
```bash
pip install -r requirements.txt
```

3. Инициализировать БД:
```bash
python init_db.py
```

4. Запустить сервер:
```bash
python run.py
```

API доступен на `http://localhost:8000`  
Документация на `http://localhost:8000/docs`

## Тестовые пользователи

- **admin** / **admin123** (роль: admin)
- **user** / **user123** (роль: user)

## Структура эндпоинтов

### Авторизация
- `POST /api/auth/login` - Авторизация
- `GET /api/auth/check` - Проверка токена

### Dashboard (INDEX.HTML)
- `GET /api/branches` - Список филиалов
- `GET /api/kpi?branch_id=0` - KPI метрики
- `GET /api/trends/production?period=month` - График производства
- `GET /api/trends/downtime?period=month` - График простоев
- `GET /api/notifications?limit=10&unread_only=false` - Уведомления
- `POST /api/notifications/mark-read` - Отметить прочитанным

### Settings (SETTINGS.HTML)

**Настройки пользователя:**
- `GET /api/user/settings` - Получить настройки
- `PUT /api/user/settings` - Сохранить настройки
- `GET /api/user/profile` - Профиль пользователя
- `POST /api/user/upload-avatar` - Загрузить аватар
- `POST /api/user/change-password` - Изменить пароль

**Безопасность:**
- `GET /api/user/2fa` - Статус 2FA
- `POST /api/user/2fa/enable` - Включить 2FA
- `GET /api/user/login-history?limit=10` - История входов
- `DELETE /api/user/account` - Удалить аккаунт

**Системные:**
- `GET /api/system/info` - Информация о системе
- `GET /api/system/check-updates` - Проверить обновления
- `POST /api/system/report-bug` - Отправить баг-репорт

### Notifications (NOTIFICATIONS.HTML)

**Получение данных:**
- `GET /api/notifications/summary` - Сводка (новые, задачи, ошибки)
- `GET /api/notifications/refresh` - Обновить все данные (summary + список)
- `GET /api/notifications?type=all&sort=time&limit=20&offset=0` - Список уведомлений
  - `type`: all, error, task, report, info
  - `sort`: time, type, priority
  - Пагинация через `limit` и `offset`

**Действия с уведомлениями:**
- `POST /api/notifications/{id}/mark-read` - Отметить прочитанным
- `POST /api/notifications/{id}/comment` - Добавить комментарий
- `POST /api/notifications/{id}/assign` - Назначить ответственного

**Задачи:**
- `POST /api/tasks/{id}/mark-complete` - Завершить задачу

### KPI (KPI.HTML и KPIVIS.HTML)

**Список KPI и фильтры:**
- `GET /api/kpi/data?period=К1 2025&branch=Все&type=Все` - Список KPI с фильтрами
  - `period`: К1 2025, К2 2025, и т.д.
  - `branch`: Все, Москва, Иркутск
  - `type`: Все, Производство, Финансы
  - Возвращает: rows (таблица) + summary (сводка)
- `GET /api/kpi/filters` - Получить списки для фильтров (periods, branches, types)

**Детализация KPI (KPIVIS.HTML):**
- `GET /api/kpi/details?kpi=production_volume&tab=shifts` - Детальная статистика KPI
  - `kpi`: ключ или ID показателя
  - `tab`: shifts (смены), employees (сотрудники), equipment (оборудование)
  - Возвращает: stats (агрегированная статистика) + rows (детали по табу)

### Tasks (TASKS.HTML и создание задач)

**Список задач:**
- `GET /api/tasks?status=in_progress&limit=20` - Получить список задач
  - `status`: in_progress, completed, overdue
  - `limit`: количество записей
- `GET /api/tasks/history?limit=10` - История решений

**Управление задачами:**
- `POST /api/tasks` - Создать задачу (multipart/form-data для файла)
  - Поля: title, description, responsible, due, priority, report, reportFile
  - Поддержка загрузки отчета (макс 10MB)
- `POST /api/tasks/{id}/mark-complete` - Завершить задачу
- `GET /api/tasks/responsibles` - Список ответственных (отделы)

### Reports (REPORTS.HTML и REPORTS_DETAILS.HTML)

**Список отчетов:**
- `GET /api/reports?date=all&type=all&status=all&page=1&limit=10` - Список отчетов с фильтрами
  - `date`: today, week, month, quarter, all
  - `type`: production, financial, equipment, analytics, all
  - `status`: ready, inProgress, accepted, all
  - `page`, `limit`: пагинация
  - Возвращает: `{success, data, total, page, pages}`

**Детали и управление:**
- `GET /api/reports/{id}` - Детали отчета (расширенные с details и downtimeReasons)
- `GET /api/reports/{id}/download?format=pdf` - Скачивание в PDF (полный отчет с таблицами)
  - Включает: заголовок, информацию, содержание, детальные показатели, причины простоя
- `GET /api/reports/{id}/download?format=csv` - Скачивание в CSV (структурированный экспорт)
  - Включает: все поля отчета, детали, причины простоя
  - Формат: разделитель `;`, кодировка UTF-8 с BOM (для Excel)
- `POST /api/reports` - Создание отчета
  - Поля: title, date, type, author, status, content, period, department, kpi
- `DELETE /api/reports/{id}` - Удаление отчета (только admin)
- `POST /api/reports/{id}/send` - Отправка менеджеру
  - Поля: managerId, message
- `GET /api/reports/export/csv` - Экспорт всех отчетов в CSV (с фильтрами)

### Data Management (DATA.HTML)

**Ручной ввод:**
- `POST /api/data/manual` - Ручной ввод данных
  - Поля: date, type (production/downtime), value, comment, userId
  - Валидация: тип, дата, неотрицательное значение

**Загрузка файлов:**
- `POST /api/data/upload` - Загрузка CSV/XLSX (multipart/form-data)
  - Поля формы: file (CSV/XLSX), userId
  - Формат CSV: `date;type;value;comment` (разделитель `;`)
  - Макс размер: 10MB
  - Возвращает: uploadId для последующей валидации/консолидации

**Валидация и консолидация:**
- `POST /api/data/validate` - Валидация загруженных данных
  - Поля: uploadId, userId
  - Проверяет: отрицательные значения, даты в будущем, типы данных
  - Возвращает: validated (true/false), issues (массив проблем)
- `POST /api/data/consolidate` - Консолидация валидированных данных
  - Поля: uploadId, department, userId
  - Применяет данные к отделу
  - Возвращает: consolidationId

**История:**
- `GET /api/data/history?page=1&limit=10&status=all` - История изменений
  - Параметры: page, limit, status (all/ready/inProgress/accepted)
  - Возвращает: записи с действиями (manual, upload, validate, consolidate)

### Finances (FINANCES.HTML)

**Метрики и аналитика:**
- `GET /api/finances/metrics` - Финансовые метрики
  - Возвращает: unitCost (value, changePercentage, changeDirection), updatedAt
- `GET /api/finances/cost-dynamics?period=all` - Динамика затрат по кварталам
  - Параметр: period (all/q1/q2/q3/q4)
  - Возвращает: {q1, q2, q3, q4} - суммы по кварталам

**Сравнение затрат:**
- `GET /api/finances/cost-comparison?page=1&limit=10&period=&department=&type=` - Сравнение затрат
  - Фильтры: period, department, type
  - Пагинация: page, limit
  - Возвращает: записи затрат с деталями

**Графики и отчеты:**
- `GET /api/finances/budget-efficiency?department=&period=` - Данные для графиков
  - Возвращает: labels[], datasets[] (для Chart.js)
  - Группировка по типам затрат
- `GET /api/finances/reports/{type}` - Скачать финансовый отчет (CSV)
  - type: daily, monthly, quarterly
- `POST /api/finances/reports` - Создать финансовый отчет
  - Поля: type, period, department

### Equipment (EQUIPMENT.HTML)

**Управление оборудованием:**
- `GET /api/equipment?page=1&limit=10&branch=&type=&status=` - Список оборудования
  - Фильтры: branch, type (production/auxiliary/transport), status (ready/inprogress/accepted)
  - Пагинация: page, limit
  - Возвращает: список с полной информацией о каждой единице
- `PUT /api/equipment/{id}` - Обновление оборудования
  - Поля: status, lastCheck, responsible
- `DELETE /api/equipment/{id}` - Удаление оборудования (только admin)

**Техническое обслуживание:**
- `POST /api/equipment/maintenance-plan` - Создать план обслуживания
  - Поля: date, branch, equipmentIds[]

**Анализ простоев:**
- `GET /api/equipment/downtime-analysis?branch=&period=last30days` - Анализ простоев
  - Параметры: branch, period (last7days/last30days)
  - Возвращает: downtimePercentage, trend, history[], reasons[]
- `GET /api/equipment/downtime-analysis/export?format=excel&period=last30days` - Экспорт анализа
  - Форматы: excel (CSV), pdf
  - Параметры: branch, period

### Profile (PROFILE.HTML)

**Управление профилем:**
- `GET /api/profile` - Получить данные профиля
  - Возвращает: name, position, location, accessLevel, email, phone
- `PUT /api/profile` - Обновить профиль
  - Поля: name, position, location, email, phone
- `POST /api/profile/password` - Сменить пароль
  - Поля: currentPassword, newPassword, confirmPassword

**Персональная аналитика:**
- `GET /api/profile/metrics` - Персональные метрики
  - Возвращает: laborProductivity, repairEfficiency, equipmentDowntime, cost (value + change)
- `GET /api/profile/activity?limit=10` - История активности
  - Возвращает: type, description, timestamp
- `GET /api/profile/tasks?limit=10` - Задачи и уведомления
  - Возвращает: title, priority, deadline, isNotification
- `GET /api/profile/team` - Команда пользователя
  - Возвращает: name, status (active/offline/busy)
- `GET /api/profile/reports` - Отчеты пользователя
  - Возвращает: branch, metric1, metric2, metric3

## Тестирование

```bash
# Тестировать Dashboard
python test_api.py

# Тестировать Settings
python test_settings.py

# Тестировать Notifications
python test_notifications.py

# Тестировать KPI Page
python test_kpi.py

# Тестировать Tasks
python test_tasks.py

# Тестировать Reports
python test_reports.py

# Тестировать Data Management
python test_data.py

# Тестировать Finances
python test_finances.py

# Тестировать Equipment
python test_equipment.py

# Тестировать Profile
python test_profile.py
```

## База данных

Используется SQLite (файл `production.db`).  
Для продакшена можно переключиться на PostgreSQL в `app/config.py`.

Таблицы:
- `users` - пользователи
- `user_settings` - настройки пользователей
- `login_history` - история входов
- `branches` - филиалы
- `kpi_metrics` - KPI метрики
- `production_data` - данные производства
- `downtime_data` - данные простоев
- `notifications` - уведомления (расширенные: title, priority, is_new, task_id, report_id)
- `tasks` - задачи
- `comments` - комментарии к уведомлениям
- `kpi_indicators` - показатели KPI (план, факт, отклонение, тренд, фильтры)
- `kpi_details` - детализация KPI по сменам/сотрудникам/оборудованию
- `task_history` - история решений по задачам
- `departments` - отделы (исполнители задач)
- `reports` - отчеты (с деталями и причинами простоев в JSON)
- `data_records` - записи данных (ручной ввод и загрузка файлов)
- `data_history` - история изменений данных
- `financial_metrics` - финансовые метрики (стоимость единицы, изменения)
- `cost_comparisons` - сравнение затрат (период, отдел, тип, сумма)
- `equipment` - оборудование (название, филиал, тип, статус, дата проверки, ответственный)
- `maintenance_plans` - планы технического обслуживания (дата, филиал, список оборудования)
- `user_metrics` - персональные метрики пользователей (производительность, эффективность, простои, себестоимость)
- `user_activity` - история активности пользователей (тип, описание, время)
- `user_tasks` - задачи и уведомления пользователей (заголовок, приоритет, срок)
- `team_members` - команды пользователей (имя, статус)
- `user_reports` - отчеты пользователей (филиал, метрики)
- `system_info` - системная информация
- `bug_reports` - отчеты об ошибках

## Реализованные страницы

✅ **INDEX.HTML (Dashboard)** - главная панель с KPI, графиками, филиалами  
✅ **SETTINGS.HTML** - настройки пользователя, профиль, безопасность, система  
✅ **NOTIFICATIONS.HTML** - уведомления, задачи, фильтры, сортировка  
✅ **KPI.HTML** - список показателей KPI с фильтрами (период, филиал, тип)  
✅ **KPIVIS.HTML** - детализация KPI с табами (смены, сотрудники, оборудование)  
✅ **TASKS.HTML** - список задач с фильтрацией (в процессе, завершенные, просроченные) + история  
✅ **TASK-CREATE.HTML** - создание задачи с загрузкой файла отчета  
✅ **REPORTS.HTML** - список отчетов с фильтрами (дата, тип, статус) + пагинация  
✅ **REPORTS_DETAILS.HTML** - детали отчета с графиками/таблицами + скачивание PDF/CSV + отправка  
✅ **DATA.HTML** - управление данными: ручной ввод, загрузка CSV/XLSX, валидация, консолидация + история  
✅ **FINANCES.HTML** - финансовая аналитика: метрики, динамика затрат, сравнение, бюджет, скачивание отчетов  
✅ **EQUIPMENT.HTML** - оборудование и техобслуживание: список, фильтры, обновление, планы, анализ простоев, экспорт  
✅ **PROFILE.HTML** - профиль пользователя: данные, обновление, смена пароля, метрики, активность, задачи, команда, отчеты

