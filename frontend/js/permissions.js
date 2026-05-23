/**
 * RBAC (Role-Based Access Control) Utility для Frontend
 *
 * Этот модуль управляет проверкой разрешений пользователей
 * и скрытием/показом элементов интерфейса на основе ролей
 */

// Глобальная переменная API_URL
window.API_URL = 'http://localhost:8000/api';

// Кеш разрешений пользователя
let userPermissionsCache = null;
let userRoleCache = null;

// Определение ролей (синхронизировано с бэкендом)
const Role = {
    ADMIN: 'admin',
    USER: 'user'
};

// Определение разрешений (синхронизировано с бэкендом)
const Permission = {
    // Отчеты
    VIEW_REPORTS: 'view_reports',
    CREATE_REPORTS: 'create_reports',
    EDIT_REPORTS: 'edit_reports',
    DELETE_REPORTS: 'delete_reports',
    DOWNLOAD_REPORTS: 'download_reports',
    SEND_REPORTS: 'send_reports',

    // Оборудование
    VIEW_EQUIPMENT: 'view_equipment',
    EDIT_EQUIPMENT: 'edit_equipment',
    DELETE_EQUIPMENT: 'delete_equipment',
    CREATE_MAINTENANCE_PLANS: 'create_maintenance_plans',
    DELETE_MAINTENANCE_PLANS: 'delete_maintenance_plans',

    // Задачи
    VIEW_TASKS: 'view_tasks',
    CREATE_TASKS: 'create_tasks',
    COMPLETE_TASKS: 'complete_tasks',
    ASSIGN_TASKS: 'assign_tasks',

    // Данные
    INPUT_DATA: 'input_data',
    UPLOAD_DATA: 'upload_data',
    VALIDATE_DATA: 'validate_data',
    CONSOLIDATE_DATA: 'consolidate_data',
    VIEW_DATA_HISTORY: 'view_data_history',

    // Финансы
    VIEW_FINANCES: 'view_finances',
    UPLOAD_FINANCIAL_REPORTS: 'upload_financial_reports',
    EXPORT_FINANCIAL_REPORTS: 'export_financial_reports',

    // Профиль
    VIEW_OWN_PROFILE: 'view_own_profile',
    EDIT_OWN_PROFILE: 'edit_own_profile',
    DELETE_OWN_ACCOUNT: 'delete_own_account',
    MANAGE_USERS: 'manage_users',

    // Система
    VIEW_SYSTEM_INFO: 'view_system_info',
    REPORT_BUGS: 'report_bugs',
    CHECK_UPDATES: 'check_updates',

    // Уведомления
    VIEW_NOTIFICATIONS: 'view_notifications',
    CREATE_NOTIFICATIONS: 'create_notifications',
    MARK_NOTIFICATIONS_READ: 'mark_notifications_read',
    COMMENT_NOTIFICATIONS: 'comment_notifications',
    ASSIGN_NOTIFICATIONS: 'assign_notifications'
};

/**
 * Загрузить разрешения текущего пользователя с сервера
 * @returns {Promise<void>}
 */
async function loadUserPermissions() {
    const token = localStorage.getItem('token');
    if (!token) {
        console.warn('[RBAC] Нет токена авторизации, используем дефолтные настройки');
        userRoleCache = Role.USER;
        userPermissionsCache = [];
        return;
    }

    try {
        const response = await fetch(`${window.API_URL}/permissions/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Ошибка загрузки разрешений');
        }

        const data = await response.json();
        userPermissionsCache = data.permissions || [];
        userRoleCache = data.role || Role.USER;

        console.log('[RBAC] Разрешения загружены:', {
            role: userRoleCache,
            permissions: userPermissionsCache,
            isAdmin: data.isAdmin
        });

    } catch (error) {
        console.error('[RBAC] Ошибка загрузки разрешений:', error);
        // Fallback: попытаться получить роль из localStorage
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        userRoleCache = user.role || Role.USER;
        userPermissionsCache = [];
    }
}

/**
 * Проверить, является ли пользователь администратором
 * @returns {boolean}
 */
function isAdmin() {
    return userRoleCache === Role.ADMIN;
}

/**
 * Проверить, имеет ли пользователь определенное разрешение
 * @param {string} permission - Название разрешения из Permission
 * @returns {boolean}
 */
function hasPermission(permission) {
    if (!userPermissionsCache) {
        console.warn('Разрешения еще не загружены. Вызовите loadUserPermissions() сначала.');
        // Fallback на проверку роли администратора
        return isAdmin();
    }
    return userPermissionsCache.includes(permission);
}

/**
 * Скрыть элемент, если у пользователя нет разрешения
 * @param {string|HTMLElement} element - Селектор или элемент DOM
 * @param {string} permission - Требуемое разрешение
 */
function hideIfNoPermission(element, permission) {
    const el = typeof element === 'string' ? document.querySelector(element) : element;
    if (!el) return;

    if (!hasPermission(permission)) {
        el.style.display = 'none';
        el.setAttribute('data-hidden-by-permission', permission);
    }
}

/**
 * Скрыть элемент, если пользователь не администратор
 * @param {string|HTMLElement} element - Селектор или элемент DOM
 */
function hideIfNotAdmin(element) {
    const el = typeof element === 'string' ? document.querySelector(element) : element;
    if (!el) return;

    if (!isAdmin()) {
        el.style.display = 'none';
        el.setAttribute('data-admin-only', 'true');
    }
}

/**
 * Отключить элемент (disabled), если нет разрешения
 * @param {string|HTMLElement} element - Селектор или элемент DOM
 * @param {string} permission - Требуемое разрешение
 */
function disableIfNoPermission(element, permission) {
    const el = typeof element === 'string' ? document.querySelector(element) : element;
    if (!el) return;

    if (!hasPermission(permission)) {
        el.disabled = true;
        el.style.opacity = '0.5';
        el.style.cursor = 'not-allowed';
        el.title = 'Недостаточно прав';
    }
}

/**
 * Применить правила RBAC ко всем элементам на странице
 * Элементы с data-атрибутами будут автоматически скрыты/отключены
 *
 * Поддерживаемые атрибуты:
 * - data-require-permission="permission_name" - требует конкретное разрешение
 * - data-require-admin="true" - требует роль администратора
 * - data-action="hide|disable" - что делать при отсутствии доступа (по умолчанию hide)
 */
function applyPermissions() {
    // Элементы с требованием конкретных разрешений
    document.querySelectorAll('[data-require-permission]').forEach(el => {
        const requiredPermission = el.getAttribute('data-require-permission');
        const action = el.getAttribute('data-action') || 'hide';

        if (!hasPermission(requiredPermission)) {
            if (action === 'disable') {
                el.disabled = true;
                el.style.opacity = '0.5';
                el.style.cursor = 'not-allowed';
                el.title = 'Недостаточно прав';
            } else {
                el.style.display = 'none';
            }
        }
    });

    // Элементы только для администраторов
    document.querySelectorAll('[data-require-admin="true"]').forEach(el => {
        const action = el.getAttribute('data-action') || 'hide';

        if (!isAdmin()) {
            if (action === 'disable') {
                el.disabled = true;
                el.style.opacity = '0.5';
                el.style.cursor = 'not-allowed';
                el.title = 'Только для администраторов';
            } else {
                el.style.display = 'none';
            }
        }
    });

    // Показать элементы только для обычных пользователей
    document.querySelectorAll('[data-require-user="true"]').forEach(el => {
        if (isAdmin()) {
            el.style.display = 'none';
        }
    });
}

/**
 * Инициализация RBAC на странице
 * Вызывать при загрузке каждой страницы после аутентификации
 */
async function initializePermissions() {
    console.log('[RBAC] Начало инициализации разрешений');
    try {
        await loadUserPermissions();
        applyPermissions();
        console.log('[RBAC] Инициализация завершена успешно');
    } catch (error) {
        console.error('[RBAC] Ошибка при инициализации:', error);
        // Устанавливаем дефолтные значения
        userRoleCache = Role.USER;
        userPermissionsCache = [];
        applyPermissions();
    }
}

/**
 * Показать/скрыть элементы на основе роли
 * Устаревшая функция, используйте applyPermissions()
 * @deprecated
 */
function applyRoleBasedUI() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const isAdminUser = user.role === 'admin';

    // Скрыть кнопки удаления для обычных пользователей
    if (!isAdminUser) {
        document.querySelectorAll('.delete-btn, [data-action="delete"]').forEach(el => {
            el.style.display = 'none';
        });

        // Скрыть кнопки редактирования оборудования
        document.querySelectorAll('.edit-equipment-btn').forEach(el => {
            el.style.display = 'none';
        });

        // Скрыть кнопку консолидации данных
        const consolidateBtn = document.getElementById('consolidateBtn');
        if (consolidateBtn) {
            consolidateBtn.style.display = 'none';
        }
    }
}

/**
 * Показать роль пользователя в интерфейсе
 */
function displayUserRole() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const roleElement = document.querySelector('.user-role');

    if (roleElement && user.role) {
        const roleLabel = user.role === 'admin' ? 'Администратор' : 'Пользователь';
        roleElement.textContent = roleLabel;
        roleElement.style.padding = '4px 12px';
        roleElement.style.borderRadius = '12px';
        roleElement.style.fontSize = '0.85em';
        roleElement.style.fontWeight = '500';

        if (user.role === 'admin') {
            roleElement.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
            roleElement.style.color = 'white';
        } else {
            roleElement.style.background = 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
            roleElement.style.color = 'white';
        }
    }
}

// Экспорт для использования в браузере (глобальный scope)
// Делаем функции доступными глобально
if (typeof window !== 'undefined') {
    window.Role = Role;
    window.Permission = Permission;
    window.isAdmin = isAdmin;
    window.hasPermission = hasPermission;
    window.hideIfNoPermission = hideIfNoPermission;
    window.hideIfNotAdmin = hideIfNotAdmin;
    window.disableIfNoPermission = disableIfNoPermission;
    window.applyPermissions = applyPermissions;
    window.initializePermissions = initializePermissions;
    window.loadUserPermissions = loadUserPermissions;
    window.applyRoleBasedUI = applyRoleBasedUI;
    window.displayUserRole = displayUserRole;
}

// Экспорт для использования в Node.js модулях (если нужно)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        Role,
        Permission,
        isAdmin,
        hasPermission,
        hideIfNoPermission,
        hideIfNotAdmin,
        disableIfNoPermission,
        applyPermissions,
        initializePermissions,
        loadUserPermissions,
        applyRoleBasedUI,
        displayUserRole
    };
}
