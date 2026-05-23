const API_URL = 'http://localhost:8000/api';

document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'auth.html';
        return;
    }

    try {
        // === 1. Загружаем данные пользователя из localStorage ===
        const user = JSON.parse(localStorage.getItem("user") || "{}");

        if (user && user.name) {
            const userNameEl = document.querySelector(".user-name");
            if (userNameEl) userNameEl.textContent = user.name;

            const profileNameEl = document.querySelector(".profile-name");
            if (profileNameEl) profileNameEl.textContent = user.name;
        }

        // === 2. Загружаем данные профиля с API ===
        await loadProfileData();
        
        // === 3. Загружаем метрики ===
        await loadMetrics();
        
        // === 4. Загружаем активность ===
        await loadActivity();
        
        // === 5. Загружаем задачи ===
        await loadTasks();
        
        // === 6. Загружаем команду ===
        await loadTeam();
        
        // === 7. Загружаем отчеты ===
        await loadReports();

        // === 8. Кнопки профиля ===
        // Редактирование профиля
        document.querySelector(".btn-gradient")?.addEventListener("click", openEditProfileModal);
        
        // Смена пароля
        document.querySelector(".btn-border")?.addEventListener("click", openChangePasswordModal);
        
        // Клик по аватару для загрузки
        document.querySelector(".profile-avatar")?.addEventListener("click", () => {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = 'image/*';
            input.onchange = handleAvatarUpload;
            input.click();
        });

        // === 9. Кнопка отчёта ===
        document.querySelector(".reports-actions .btn--primary")?.addEventListener("click", () => {
            window.location.href = "reports.html";
        });

    } catch (err) {
        console.warn("Ошибка при инициализации профиля:", err);
    }
});

// === Загрузка данных профиля ===
async function loadProfileData() {
    const token = localStorage.getItem('token');
    try {
        // Используем /api/user/profile для получения профиля с аватаром
        const res = await fetch(`${API_URL}/user/profile`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (res.ok) {
            const data = await res.json();
            updateProfileUI(data);
        }
        
        // Загружаем расширенные данные профиля
        const profileRes = await fetch(`${API_URL}/profile`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (profileRes.ok) {
            const profileData = await profileRes.json();
            if (profileData.success && profileData.data) {
                updateExtendedProfileUI(profileData.data);
            }
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

function updateProfileUI(profile) {
    // Обновить аватар (как в settings.js)
    const avatarEl = document.querySelector('.profile-avatar');
    if (avatarEl) {
        if (profile.avatarUrl) {
            // Если URL уже полный (начинается с http), используем как есть
            // Иначе добавляем базовый URL
            const avatarUrl = profile.avatarUrl.startsWith('http') 
                ? profile.avatarUrl 
                : `http://localhost:8000${profile.avatarUrl}`;
            avatarEl.src = avatarUrl;
        } else {
            avatarEl.src = 'img/user.png'; // Дефолтная картинка
        }
        avatarEl.style.display = 'block'; // Показать аватар после загрузки
    }
    
    // Обновить имя
    const nameEl = document.querySelector('.profile-name');
    if (nameEl) nameEl.textContent = profile.name;
    
    // Обновить роль
    const detailValues = document.querySelectorAll('.detail-value');
    if (detailValues[0]) {
        detailValues[0].textContent = profile.role === 'admin' ? 'Администратор' : 'Руководитель филиала';
    }
}

function updateExtendedProfileUI(profile) {
    // Обновить должность
    const positionEl = document.querySelector('.profile-position');
    if (positionEl) positionEl.textContent = profile.position;
    
    // Обновить местоположение
    const locationEl = document.querySelector('.profile-location');
    if (locationEl) locationEl.textContent = profile.location;
    
    // Обновить детали
    const detailValues = document.querySelectorAll('.detail-value');
    
    // Обновить email
    if (detailValues[1] && profile.email) {
        detailValues[1].textContent = profile.email;
    }
    
    // Обновить телефон
    if (detailValues[2] && profile.phone) {
        detailValues[2].textContent = profile.phone;
    }
}

// === Загрузка метрик ===
async function loadMetrics() {
    const token = localStorage.getItem('token');
    try {
        const res = await fetch(`${API_URL}/profile/metrics`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (res.ok) {
            const data = await res.json();
            if (data.success && data.data) {
                updateMetricsUI(data.data);
                animateMetrics();
            }
        }
    } catch (error) {
        console.error('Error loading metrics:', error);
        // Показать дефолтные значения
        animateMetrics();
    }
}

function updateMetricsUI(metrics) {
    // Обновление значений метрик с учетом структуры данных
    updateMetricCard('laborProductivity', metrics.laborProductivity);
    updateMetricCard('repairEfficiency', metrics.repairEfficiency);
    updateMetricCard('equipmentDowntime', metrics.equipmentDowntime);
    updateMetricCard('cost', metrics.cost);
}

function updateMetricCard(metricName, metricData) {
    const card = document.querySelector(`[data-metric="${metricName}"]`);
    if (!card) return;
    
    const valueEl = card.querySelector('.metric-value');
    const changeEl = card.querySelector('.metric-change');
    
    if (valueEl) {
        if (metricName === 'cost') {
            valueEl.setAttribute('data-target', metricData.value);
            valueEl.textContent = `${Math.round(metricData.value).toLocaleString('ru-RU')} ₽`;
        } else if (metricName === 'equipmentDowntime') {
            valueEl.setAttribute('data-target', metricData.value);
            valueEl.textContent = `${metricData.value.toFixed(1)} ч`;
        } else {
            valueEl.setAttribute('data-target', metricData.value);
            valueEl.textContent = `${Math.round(metricData.value)}%`;
        }
    }
    
    if (changeEl && metricData.changePercentage !== undefined) {
        const sign = metricData.changePercentage > 0 ? '+' : '';
        changeEl.textContent = `${sign}${metricData.changePercentage}%`;
        
        // Установить класс направления
        if (metricData.changeDirection === 'up') {
            changeEl.classList.add('positive');
            changeEl.classList.remove('negative');
        } else if (metricData.changeDirection === 'down') {
            changeEl.classList.add('negative');
            changeEl.classList.remove('positive');
        }
    }
}

// === Загрузка активности ===
async function loadActivity() {
    const token = localStorage.getItem('token');
    try {
        const res = await fetch(`${API_URL}/profile/activity?limit=10`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (res.ok) {
            const data = await res.json();
            if (data.success && data.data) {
                updateActivityUI(data.data);
            }
        }
    } catch (error) {
        console.error('Error loading activity:', error);
    }
}

function updateActivityUI(activities) {
    const container = document.querySelector('.activity-list');
    if (!container) return;
    
    if (activities.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-light); padding: 20px;">Нет данных</p>';
        return;
    }
    
    container.innerHTML = activities.map(a => `
        <div class="activity-item">
            <span class="activity-icon">${getActivityIcon(a.type)}</span>
            <div class="activity-content">
                <p>${a.description}</p>
                <span class="activity-time">${formatTime(a.timestamp)}</span>
            </div>
        </div>
    `).join('');
}

function getActivityIcon(type) {
    const icons = {
        'login': '🔐',
        'report_created': '📄',
        'task_completed': '✅',
        'task_updated': '📝'
    };
    return icons[type] || '📌';
}

// === Загрузка задач ===
async function loadTasks() {
    const token = localStorage.getItem('token');
    try {
        const res = await fetch(`${API_URL}/profile/tasks?limit=10`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (res.ok) {
            const data = await res.json();
            if (data.success && data.data) {
                updateTasksUI(data.data);
            }
        }
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

function updateTasksUI(tasks) {
    const container = document.querySelector('.tasks-list');
    if (!container) return;
    
    if (tasks.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-light); padding: 20px;">Нет задач</p>';
        return;
    }
    
    container.innerHTML = tasks.map(t => `
        <div class="task-item ${t.isNotification ? 'notification' : ''}">
            <h3 class="task-title">${t.title}</h3>
            <span class="task-priority task-priority--${t.priority.toLowerCase()}">${getPriorityLabel(t.priority)}</span>
            ${t.deadline ? `<span class="task-deadline">Срок: ${formatDate(t.deadline)}</span>` : ''}
        </div>
    `).join('');
}

function getPriorityLabel(priority) {
    const labels = {
        'Высокий': '🔴 Высокий',
        'Средний': '🟡 Средний',
        'Низкий': '🟢 Низкий'
    };
    return labels[priority] || priority;
}

// === Загрузка команды ===
async function loadTeam() {
    const token = localStorage.getItem('token');
    try {
        const res = await fetch(`${API_URL}/profile/team`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (res.ok) {
            const data = await res.json();
            if (data.success && data.data) {
                updateTeamUI(data.data);
            }
        }
    } catch (error) {
        console.error('Error loading team:', error);
    }
}

function updateTeamUI(team) {
    const container = document.querySelector('.team-list');
    if (!container) return;
    
    if (team.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-light); padding: 20px;">Нет данных о команде</p>';
        return;
    }
    
    container.innerHTML = team.map(m => `
        <div class="team-member">
            <div class="member-avatar">
                <img src="img/icons/user.svg" alt="user icon">
            </div>
            <div class="member-info">
                <span class="member-name">${m.name}</span>
                <span class="member-status member-status--${m.status}">${getStatusLabel(m.status)}</span>
            </div>
        </div>
    `).join('');
}

function getStatusLabel(status) {
    const labels = {
        'active': 'Online',
        'offline': 'Offline',
        'busy': 'Занят'
    };
    return labels[status] || status;
}

// === Загрузка отчетов ===
async function loadReports() {
    const token = localStorage.getItem('token');
    try {
        const res = await fetch(`${API_URL}/profile/reports`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (res.ok) {
            const data = await res.json();
            if (data.success && data.data) {
                updateReportsUI(data.data);
            }
        }
    } catch (error) {
        console.error('Error loading reports:', error);
    }
}

function updateReportsUI(reports) {
    const container = document.querySelector('.reports-table tbody');
    if (!container) return;
    
    if (reports.length === 0) {
        container.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 20px; color: var(--text-light);">Нет отчетов</td></tr>';
        return;
    }
    
    container.innerHTML = reports.map(r => `
        <tr>
            <td>${r.branch}</td>
            <td>${r.metric1.toFixed(1)}</td>
            <td>${r.metric2.toFixed(1)}</td>
            <td>${r.metric3.toFixed(1)}</td>
        </tr>
    `).join('');
}

// === Анимация чисел в метриках ===
const animateMetrics = () => {
    const metrics = document.querySelectorAll(".metric-value");

    metrics.forEach(metric => {
        const text = metric.textContent;
        const target = parseFloat(text.replace(/[^\d.]/g, ''));
        
        if (isNaN(target)) return;
        
        let current = 0;
        const duration = 1500;
        const stepTime = 30;
        const increment = target / (duration / stepTime);

        const interval = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(interval);
            }
            
            if (text.includes("₽")) {
                metric.textContent = `${Math.round(current).toLocaleString("ru-RU")} ₽`;
            } else if (text.includes("ч")) {
                metric.textContent = `${current.toFixed(1)} ч`;
            } else if (text.includes("%")) {
                metric.textContent = `${Math.round(current)}%`;
            }
        }, stepTime);
    });
};

// === Вспомогательные функции ===
function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);
    
    if (diff < 60) return 'только что';
    if (diff < 3600) return `${Math.floor(diff / 60)} мин назад`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} ч назад`;
    
    return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' });
}

// === Редактирование профиля ===
function openEditProfileModal() {
    const name = prompt('Введите ваше имя:', document.querySelector('.profile-name')?.textContent || '');
    if (!name) return;
    
    const position = prompt('Введите вашу должность:', document.querySelector('.profile-position')?.textContent || '');
    if (!position) return;
    
    const location = prompt('Введите местоположение:', document.querySelector('.profile-location')?.textContent || '');
    if (!location) return;
    
    const email = prompt('Введите email:', '');
    if (!email) return;
    
    const phone = prompt('Введите телефон:', '');
    if (!phone) return;
    
    updateProfile(name, position, location, email, phone);
}

async function updateProfile(name, position, location, email, phone) {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    try {
        const res = await fetch(`${API_URL}/profile`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, position, location, email, phone })
        });
        
        if (res.ok) {
            alert('✅ Профиль обновлен!');
            await loadProfileData();
        } else {
            const error = await res.json();
            alert('Ошибка: ' + (error.detail || 'Неизвестная ошибка'));
        }
    } catch (error) {
        console.error('Error updating profile:', error);
        alert('Ошибка при обновлении профиля');
    }
}

// === Смена пароля ===
function openChangePasswordModal() {
    const currentPassword = prompt('Введите текущий пароль:');
    if (!currentPassword) return;
    
    const newPassword = prompt('Введите новый пароль (минимум 6 символов):');
    if (!newPassword || newPassword.length < 6) {
        alert('Пароль должен быть не менее 6 символов');
        return;
    }
    
    const confirmPassword = prompt('Подтвердите новый пароль:');
    if (newPassword !== confirmPassword) {
        alert('Пароли не совпадают');
        return;
    }
    
    changePassword(currentPassword, newPassword, confirmPassword);
}

async function changePassword(currentPassword, newPassword, confirmPassword) {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    try {
        const res = await fetch(`${API_URL}/profile/password`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                currentPassword,
                newPassword,
                confirmPassword
            })
        });
        
        if (res.ok) {
            alert('✅ Пароль успешно изменен!');
        } else {
            const error = await res.json();
            alert('Ошибка: ' + (error.detail || 'Неизвестная ошибка'));
        }
    } catch (error) {
        console.error('Error changing password:', error);
        alert('Ошибка при смене пароля');
    }
}

// === Загрузка аватара ===
async function handleAvatarUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Проверка размера (5MB)
    if (file.size > 5 * 1024 * 1024) {
        alert('Файл слишком большой (макс. 5MB)');
        return;
    }
    
    // Проверка типа
    if (!file.type.startsWith('image/')) {
        alert('Выберите изображение');
        return;
    }
    
    const token = localStorage.getItem('token');
    if (!token) return;
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const res = await fetch(`${API_URL}/user/upload-avatar`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        if (res.ok) {
            const result = await res.json();
            
            // Обновить аватар на странице профиля
            const avatarEl = document.querySelector('.profile-avatar');
            if (avatarEl && result.avatarUrl) {
                const avatarUrlWithCache = `${result.avatarUrl}?t=${Date.now()}`;
                avatarEl.src = avatarUrlWithCache;
                
                // Обновить аватар в header (синхронизация)
                const headerAvatar = document.querySelector('.user-avatar');
                if (headerAvatar) {
                    headerAvatar.src = avatarUrlWithCache;
                }
            }
            
            alert('✅ Аватар обновлен!');
        } else {
            const error = await res.json();
            alert('Ошибка: ' + (error.detail || 'Неизвестная ошибка'));
        }
    } catch (error) {
        console.error('Error uploading avatar:', error);
        alert('Ошибка при загрузке аватара');
    }
}

// === Кнопка выхода ===
const logoutBtn = document.getElementById("logoutBtn");
if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
        localStorage.removeItem("user");
        localStorage.removeItem("token");
        window.location.href = "auth.html";
    });
}
