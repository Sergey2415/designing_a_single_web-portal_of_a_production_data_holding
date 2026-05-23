const API_URL = 'http://localhost:8000/api';

document.addEventListener('DOMContentLoaded', async () => {
    console.log("✅ settings.js загружен");

    // Загрузить все данные
    await loadSettings();
    await loadProfile();
    await loadLoginHistory();

    // Обработчики кнопок сохранения
    document.getElementById('saveGeneralBtn')?.addEventListener('click', saveGeneralSettings);
    document.getElementById('saveNotificationsBtn')?.addEventListener('click', saveNotificationsSettings);

    // Обработчик темы
    document.querySelectorAll('input[name="theme"]').forEach(radio => {
        radio.addEventListener('change', handleThemeChange);
    });

    document.getElementById('autoThemeByTime')?.addEventListener('change', handleThemeChange);

    // Обработчики аккаунта
    document.getElementById('avatarUpload')?.addEventListener('change', handleAvatarUpload);
    document.getElementById('changePasswordBtn')?.addEventListener('click', openChangePasswordModal);
    document.getElementById('setup2faBtn')?.addEventListener('click', open2FAModal);
    document.getElementById('deleteAccountBtn')?.addEventListener('click', deleteAccount);
});

// === Загрузка настроек ===
async function loadSettings() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'auth.html';
        return;
    }

    try {
        const res = await fetch(`${API_URL}/user/settings`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!res.ok) throw new Error('Failed to load settings');

        const data = await res.json();

        // Общие параметры
        document.getElementById('language').value = data.general.language;
        document.getElementById('timeFormat').value = data.general.timeFormat;
        document.getElementById('dateFormat').value = data.general.dateFormat;
        document.getElementById('regional').value = data.general.regional;

        // Тема (конвертируем auto -> system для UI)
        const themeValue = data.theme.selected === 'auto' ? 'system' : data.theme.selected;
        const themeRadio = document.querySelector(`input[name="theme"][value="${themeValue}"]`);
        if (themeRadio) {
            themeRadio.checked = true;
            themeRadio.closest('.theme-card').classList.add('active');
        }
        document.getElementById('autoThemeByTime').checked = data.theme.autoByTime;

        // Уведомления
        document.getElementById('notifyNewReports').checked = data.notifications.newReports;
        document.getElementById('notifyEquipmentFailures').checked = data.notifications.equipmentFailures;
        document.getElementById('notifyDailyEmail').checked = data.notifications.dailySummaryEmail;
        document.getElementById('notifyPushBrowser').checked = data.notifications.pushBrowser;
        document.getElementById('notifyTelegram').checked = data.notifications.telegram;
        document.getElementById('soundVolume').value = data.notifications.soundVolume;
        document.getElementById('doNotDisturb').checked = data.notifications.doNotDisturb;

        console.log('✅ Настройки загружены');
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

// === Загрузка профиля ===
async function loadProfile() {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        const res = await fetch(`${API_URL}/user/profile`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!res.ok) throw new Error('Failed to load profile');

        const data = await res.json();

        document.getElementById('userName').textContent = data.name;
        document.getElementById('userRole').textContent = data.role;
        document.getElementById('userDept').textContent = data.department;

        if (data.avatarUrl) {
            const avatarUrl = data.avatarUrl.startsWith('http') 
                ? data.avatarUrl 
                : `http://localhost:8000${data.avatarUrl}`;
            document.getElementById('userAvatar').src = avatarUrl;
        }

        console.log('✅ Профиль загружен');
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

// === Загрузка истории входов ===
async function loadLoginHistory() {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        const res = await fetch(`${API_URL}/user/login-history?limit=5`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!res.ok) throw new Error('Failed to load history');

        const history = await res.json();

        const historyList = document.getElementById('loginHistory');
        if (history.length === 0) {
            historyList.innerHTML = '<li style="color: var(--text-light);">Нет записей</li>';
        } else {
            historyList.innerHTML = history.map(h => `
                <li>${h.device} — <span class="gray">${h.ip} — ${new Date(h.date).toLocaleDateString('ru-RU')}</span></li>
            `).join('');
        }

        console.log('✅ История загружена');
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

// === Сохранение общих настроек ===
async function saveGeneralSettings() {
    const token = localStorage.getItem('token');
    if (!token) return;

    const btn = document.getElementById('saveGeneralBtn');
    btn.disabled = true;
    btn.textContent = 'Сохранение...';

    try {
        const data = {
            general: {
                language: document.getElementById('language').value,
                timeFormat: document.getElementById('timeFormat').value,
                dateFormat: document.getElementById('dateFormat').value,
                regional: document.getElementById('regional').value
            }
        };

        const res = await fetch(`${API_URL}/user/settings`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!res.ok) throw new Error('Failed to save settings');

        alert('✅ Настройки сохранены');
        console.log('✅ Общие настройки сохранены');
    } catch (error) {
        console.error('Error saving settings:', error);
        alert('Ошибка при сохранении настроек');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Сохранить изменения';
    }
}

// === Обработка изменения темы ===
async function handleThemeChange() {
    const selectedTheme = document.querySelector('input[name="theme"]:checked')?.value || 'light';
    const autoByTime = document.getElementById('autoThemeByTime').checked;

    // Применить тему немедленно (для UI используем system)
    if (selectedTheme === 'system' || selectedTheme === 'auto') {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    } else {
        document.documentElement.setAttribute('data-theme', selectedTheme);
    }

    localStorage.setItem('theme', selectedTheme);

    // Обновить активный класс
    document.querySelectorAll('.theme-card').forEach(c => c.classList.remove('active'));
    document.querySelector(`input[name="theme"]:checked`)?.closest('.theme-card')?.classList.add('active');

    // Сохранить на бэкенд (конвертируем system -> auto для бэкенда)
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        const themeForBackend = selectedTheme === 'system' ? 'auto' : selectedTheme;
        
        const data = {
            theme: {
                selected: themeForBackend,
                autoByTime: autoByTime
            }
        };

        await fetch(`${API_URL}/user/settings`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        console.log('✅ Тема сохранена');
    } catch (error) {
        console.error('Error saving theme:', error);
    }
}

// === Сохранение настроек уведомлений ===
async function saveNotificationsSettings() {
    const token = localStorage.getItem('token');
    if (!token) return;

    const btn = document.getElementById('saveNotificationsBtn');
    btn.disabled = true;
    btn.textContent = 'Сохранение...';

    try {
        const data = {
            notifications: {
                newReports: document.getElementById('notifyNewReports').checked,
                equipmentFailures: document.getElementById('notifyEquipmentFailures').checked,
                dailySummaryEmail: document.getElementById('notifyDailyEmail').checked,
                pushBrowser: document.getElementById('notifyPushBrowser').checked,
                telegram: document.getElementById('notifyTelegram').checked,
                soundVolume: parseInt(document.getElementById('soundVolume').value),
                doNotDisturb: document.getElementById('doNotDisturb').checked
            }
        };

        const res = await fetch(`${API_URL}/user/settings`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!res.ok) throw new Error('Failed to save settings');

        alert('✅ Настройки уведомлений сохранены');
        console.log('✅ Настройки уведомлений сохранены');
    } catch (error) {
        console.error('Error saving notifications:', error);
        alert('Ошибка при сохранении настроек');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Сохранить настройки уведомлений';
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

        if (!res.ok) throw new Error('Failed to upload avatar');

        const result = await res.json();

        // Обновить аватар на странице с кэшбастером
        const avatarUrl = result.avatarUrl.startsWith('http') 
            ? result.avatarUrl 
            : `http://localhost:8000${result.avatarUrl}`;
        const avatarUrlWithCache = `${avatarUrl}?t=${Date.now()}`;
        
        document.getElementById('userAvatar').src = avatarUrlWithCache;
        
        // Обновить аватар в header (синхронизация)
        const headerAvatar = document.querySelector('.user-avatar');
        if (headerAvatar) {
            headerAvatar.src = avatarUrlWithCache;
        }

        alert('✅ Фото загружено');
        console.log('✅ Аватар загружен:', avatarUrl);
    } catch (error) {
        console.error('Error uploading avatar:', error);
        alert('Ошибка при загрузке фото');
    }
}

// === Изменение пароля ===
function openChangePasswordModal() {
    const oldPassword = prompt('Введите старый пароль:');
    if (!oldPassword) return;

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

    changePassword(oldPassword, newPassword, confirmPassword);
}

async function changePassword(oldPassword, newPassword, confirmNewPassword) {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        const res = await fetch(`${API_URL}/user/change-password`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                oldPassword,
                newPassword,
                confirmNewPassword
            })
        });

        if (!res.ok) {
            const error = await res.json();
            throw new Error(error.detail || 'Failed to change password');
        }

        alert('✅ Пароль успешно изменен');
        console.log('✅ Пароль изменен');
    } catch (error) {
        console.error('Error changing password:', error);
        alert('Ошибка: ' + error.message);
    }
}

// === Настройка 2FA ===
function open2FAModal() {
    alert('Функция двухфакторной аутентификации будет реализована');
    // TODO: Реализовать модальное окно с QR кодом
}

// === Удаление аккаунта ===
async function deleteAccount() {
    if (!confirm('Вы уверены, что хотите удалить аккаунт? Это действие необратимо!')) {
        return;
    }

    if (!confirm('Повторите: вы действительно хотите удалить аккаунт?')) {
        return;
    }

    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        const res = await fetch(`${API_URL}/user/account`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!res.ok) throw new Error('Failed to delete account');

        alert('Аккаунт удален');
        localStorage.removeItem('token');
        window.location.href = 'auth.html';
    } catch (error) {
        console.error('Error deleting account:', error);
        alert('Ошибка при удалении аккаунта');
    }
}

