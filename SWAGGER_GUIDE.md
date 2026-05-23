# Руководство по Swagger документации

## Доступ к документации

После запуска сервера (`python run.py`), документация доступна по адресам:

### 1. Swagger UI (рекомендуется)
```
http://localhost:8000/docs
```

**Особенности:**
- Интерактивное тестирование API
- Кнопка "Try it out" для каждого эндпоинта
- Автоматическая генерация примеров запросов
- Встроенный клиент для отправки запросов

### 2. ReDoc
```
http://localhost:8000/redoc
```

**Особенности:**
- Более читаемый формат документации
- Удобная навигация по разделам
- Лучше для изучения структуры API
- Нет интерактивного тестирования

## Как использовать Swagger UI

### Шаг 1: Авторизация

1. Откройте `http://localhost:8000/docs`
2. Найдите эндпоинт `POST /api/auth/login` в разделе **auth**
3. Нажмите "Try it out"
4. Введите тестовые данные:
   ```json
   {
     "username": "admin",
     "password": "admin123"
   }
   ```
5. Нажмите "Execute"
6. Скопируйте `token` из ответа
7. Нажмите кнопку **Authorize** (🔒) в правом верхнем углу
8. Введите: `Bearer <ваш_токен>`
9. Нажмите "Authorize"

Теперь все запросы будут автоматически включать токен!

### Шаг 2: Тестирование эндпоинтов

1. Выберите любой эндпоинт
2. Нажмите "Try it out"
3. Заполните параметры (Swagger покажет примеры)
4. Нажмите "Execute"
5. Просмотрите ответ в разделе "Responses"

## Особенности документации

### 1. Enum'ы (выпадающие списки)

Для полей с ограниченным набором значений Swagger показывает dropdown:

**Примеры:**
- `type` в Reports: `production`, `financial`, `equipment`, `analytics`
- `status` в Equipment: `ready`, `inprogress`, `accepted`
- `priority` в Tasks: `Высокий`, `Средний`, `Низкий`
- `role`: `admin`, `user`

**Как использовать:**
- Кликните на поле
- Выберите значение из списка
- Нельзя ввести другое значение - валидация защитит от ошибок

### 2. Примеры (Examples)

Каждое поле имеет пример значения:

```json
{
  "username": "admin",           // ← пример
  "password": "admin123",        // ← пример
  "email": "user@example.com"    // ← пример
}
```

**Кнопка "Example Value":**
- Нажмите, чтобы автоматически заполнить все поля примерами
- Удобно для быстрого тестирования

### 3. Валидация (Constraints)

Swagger показывает ограничения для полей:

- **string** (min/max length):
  - `password`: минимум 6 символов
  - `title`: минимум 3 символа
  
- **number** (min/max value):
  - `soundVolume`: от 0 до 100
  - `percentage`: от 0 до 100
  
- **array** (min items):
  - `equipmentIds`: минимум 1 элемент
  
- **format**:
  - `email`: валидация email формата
  - `date`: формат YYYY-MM-DD

### 4. Описания (Descriptions)

Каждый параметр имеет описание на русском языке:

- **Что это за поле**
- **Какие значения допустимы**
- **Для чего используется**

## Структура API по разделам

### 🔐 auth (Авторизация)
- `POST /api/auth/login` - Вход в систему
- `GET /api/auth/check` - Проверка токена

### 🏢 branches (Филиалы)
- `GET /api/branches` - Список филиалов

### 📊 kpi (KPI Dashboard)
- `GET /api/kpi` - KPI метрики
- `GET /api/kpi/production-data` - Данные производства
- `GET /api/kpi/downtime-data` - Данные простоев

### 📈 kpi (KPI Page)
- `GET /api/kpi/list` - Список KPI
- `GET /api/kpi/filters` - Фильтры
- `GET /api/kpi/{id}/details` - Детали KPI

### 📉 trends (Графики)
- `GET /api/trends/production` - Тренды производства
- `GET /api/trends/downtime` - Тренды простоев

### 🔔 notifications (Уведомления)
- `GET /api/notifications` - Список уведомлений
- `POST /api/notifications/{id}/read` - Отметить как прочитанное
- `POST /api/notifications/{id}/comment` - Добавить комментарий
- И другие...

### ⚙️ user (Настройки пользователя)
- `GET /api/user/settings` - Получить настройки
- `PUT /api/user/settings` - Обновить настройки
- `GET /api/user/profile` - Профиль
- `POST /api/user/avatar` - Загрузить аватар
- И другие...

### 🖥️ system (Система)
- `GET /api/system/info` - Информация о системе
- `GET /api/system/updates` - Проверка обновлений
- `POST /api/system/bug-report` - Отчет об ошибке

### ✅ tasks (Задачи)
- `GET /api/tasks` - Список задач (с фильтром status)
- `GET /api/tasks/history` - История
- `GET /api/tasks/responsibles` - Ответственные
- `POST /api/tasks` - Создать задачу

### 📝 reports (Отчеты)
- `GET /api/reports` - Список отчетов
- `GET /api/reports/{id}` - Детали отчета
- `GET /api/reports/{id}/download` - Скачать (PDF/CSV)
- `POST /api/reports` - Создать отчет
- И другие...

### 📊 data (Управление данными)
- `POST /api/data/manual` - Ручной ввод
- `POST /api/data/upload` - Загрузка файла
- `POST /api/data/validate` - Валидация
- `POST /api/data/consolidate` - Консолидация
- `GET /api/data/history` - История

### 💰 finances (Финансы)
- `GET /api/finances/metrics` - Метрики
- `GET /api/finances/cost-dynamics` - Динамика затрат
- `GET /api/finances/cost-comparison` - Сравнение
- `GET /api/finances/budget-efficiency` - Бюджет
- И другие...

### ⚙️ equipment (Оборудование)
- `GET /api/equipment` - Список оборудования
- `PUT /api/equipment/{id}` - Обновить
- `DELETE /api/equipment/{id}` - Удалить
- `POST /api/equipment/maintenance-plan` - План обслуживания
- `GET /api/equipment/downtime-analysis` - Анализ простоев
- `GET /api/equipment/downtime-analysis/export` - Экспорт

### 👤 profile (Профиль)
- `GET /api/profile` - Данные профиля
- `PUT /api/profile` - Обновить профиль
- `POST /api/profile/password` - Сменить пароль
- `GET /api/profile/metrics` - Персональные метрики
- `GET /api/profile/activity` - Активность
- `GET /api/profile/tasks` - Задачи
- `GET /api/profile/team` - Команда
- `GET /api/profile/reports` - Отчеты

## Типичные сценарии

### Сценарий 1: Получить список отчетов

1. Авторизуйтесь (см. выше)
2. Перейдите к `GET /api/reports`
3. Нажмите "Try it out"
4. Заполните параметры:
   - `page`: 1
   - `limit`: 10
   - `type`: выберите из dropdown (например, `production`)
5. Нажмите "Execute"
6. Смотрите результат

### Сценарий 2: Создать задачу

1. Авторизуйтесь
2. Перейдите к `POST /api/tasks`
3. Нажмите "Try it out"
4. Нажмите "Example Value" для автозаполнения
5. Измените значения:
   ```json
   {
     "title": "Моя новая задача",
     "description": "Описание задачи",
     "responsible": "eng",
     "due": "2025-11-15",
     "priority": "Высокий"
   }
   ```
6. Добавьте файл (если нужно)
7. Нажмите "Execute"
8. Получите `taskId` в ответе

### Сценарий 3: Скачать отчет

1. Авторизуйтесь
2. Получите список отчетов (`GET /api/reports`)
3. Скопируйте `id` нужного отчета
4. Перейдите к `GET /api/reports/{id}/download`
5. Укажите:
   - `report_id`: скопированный ID
   - `format`: выберите `pdf` или `csv`
6. Нажмите "Execute"
7. Swagger покажет кнопку "Download file"

## Коды ответов

### Успешные (2xx):
- **200 OK** - Запрос выполнен успешно
- **201 Created** - Ресурс создан

### Клиентские ошибки (4xx):
- **400 Bad Request** - Неверные данные
- **401 Unauthorized** - Требуется авторизация
- **403 Forbidden** - Нет прав доступа
- **404 Not Found** - Ресурс не найден
- **413 Payload Too Large** - Файл слишком большой

### Серверные ошибки (5xx):
- **500 Internal Server Error** - Ошибка на сервере

## Schemas (Модели данных)

В нижней части Swagger UI есть раздел **Schemas**:

- Все модели данных
- Структура запросов и ответов
- Enum'ы с возможными значениями
- Примеры для каждой модели

**Полезно для:**
- Понимания структуры данных
- Копирования примеров
- Проверки типов полей

## Tips & Tricks

### 1. Быстрое тестирование
- Используйте "Example Value" для быстрого заполнения
- Сохраните токен в буфер обмена для переавторизации
- Используйте Ctrl+F для поиска эндпоинтов

### 2. Отладка
- Смотрите "Request URL" - полный URL запроса
- Проверяйте "Request headers" - какие заголовки отправлены
- Изучайте "Response headers" - метаданные ответа

### 3. Экспорт
- Нажмите на ссылку в верхней части: `/openapi.json`
- Скачайте спецификацию OpenAPI
- Используйте для генерации клиентов (SDK)

### 4. Фильтрация
- Используйте поиск в браузере (Ctrl+F)
- Разделы сгруппированы по тегам
- Сворачивайте/разворачивайте разделы

## Генерация клиента

Swagger/OpenAPI позволяет генерировать клиенты для разных языков:

### JavaScript/TypeScript:
```bash
npx @openapitools/openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g typescript-axios \
  -o ./api-client
```

### Python:
```bash
pip install openapi-python-client
openapi-python-client generate --url http://localhost:8000/openapi.json
```

### Другие языки:
- Java
- C#
- Go
- PHP
- Ruby
- Swift
- Kotlin
- И многие другие...

## Заключение

Swagger документация - это:
- ✅ Всегда актуальная документация
- ✅ Интерактивное тестирование
- ✅ Понятные примеры
- ✅ Автоматическая валидация
- ✅ Генерация клиентов

**Используйте Swagger для:**
1. Изучения API
2. Тестирования эндпоинтов
3. Отладки запросов
4. Понимания структуры данных
5. Генерации документации для команды

Наслаждайтесь работой с API! 🚀







