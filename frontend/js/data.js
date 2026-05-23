// API_URL определён глобально в permissions.js (window.API_URL)

let currentPage = 1;
let currentStatus = 'all';
let currentUserId = null;

document.addEventListener('DOMContentLoaded', async () => {
    console.log("[Data] Страница загружена, начало инициализации");

    // Инициализация RBAC
    try {
        if (typeof initializePermissions !== 'undefined') {
            await initializePermissions();
        } else {
            console.error('[Data] initializePermissions не определена!');
        }
    } catch (error) {
        console.error('[Data] Ошибка инициализации RBAC:', error);
    }

    // Получаем текущего пользователя
    const token = localStorage.getItem('token');
    if (token) {
        try {
            const res = await fetch(`${window.API_URL}/auth/check`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const result = await res.json();
            if (result.success && result.user) {
                currentUserId = result.user.id;
            }
        } catch (error) {
            console.error('Error getting user:', error);
        }
    }

    // Timestamp
    const timestamp = document.getElementById('updateTimestamp');
    function updateTimestamp() {
        const now = new Date().toLocaleString('ru-RU', { timeZone: 'Europe/Moscow', hour12: false });
        timestamp.textContent = `Последнее обновление: ${now}`;
    }
    updateTimestamp();
    setInterval(updateTimestamp, 60000);

    // Загрузка истории
    await loadHistory();

    // Обработчики кнопок карточек
    document.getElementById('openManualBtn').onclick = openManualModal;
    document.getElementById('openUploadBtn').onclick = openUploadModal;
    document.getElementById('openValidateBtn').onclick = openValidateModal;
    document.getElementById('openConsolidateBtn').onclick = openConsolidateModal;

    // Обработчики модальных окон
    document.getElementById('saveManualBtn').onclick = saveManualData;
    document.getElementById('uploadFileBtn').onclick = uploadFile;
    document.getElementById('validateBtn').onclick = validateData;
    document.getElementById('consolidateBtn').onclick = consolidateData;

    // Фильтр статуса
    document.getElementById('statusFilter').addEventListener('change', async (e) => {
        currentStatus = e.target.value;
        currentPage = 1;
        await loadHistory();
    });

    // Пагинация
    document.getElementById('prevPageBtn').onclick = async () => {
        if (currentPage > 1) {
            currentPage--;
            await loadHistory();
        }
    };
    document.getElementById('nextPageBtn').onclick = async () => {
        currentPage++;
        await loadHistory();
    };
});

// === Загрузка истории ===
async function loadHistory() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'auth.html';
        return;
    }

    try {
        const res = await fetch(
            `${window.API_URL}/data/history?page=${currentPage}&limit=10&status=${currentStatus}`,
            { headers: { 'Authorization': `Bearer ${token}` } }
        );

        const result = await res.json();
        
        if (result.success) {
            renderHistory(result.data);
            renderPagination(result.page, result.pages);
        }
    } catch (error) {
        console.error('Error loading history:', error);
        document.getElementById('historyTableBody').innerHTML = `
            <tr><td colspan="4" style="text-align: center; color: var(--danger);">Ошибка загрузки данных</td></tr>
        `;
    }
}

// === Рендеринг истории ===
function renderHistory(data) {
    const tbody = document.getElementById('historyTableBody');
    
    if (!data || data.length === 0) {
        tbody.innerHTML = `
            <tr><td colspan="4" style="text-align: center; color: var(--text-light);">Нет данных</td></tr>
        `;
        return;
    }

    tbody.innerHTML = data.map(item => `
        <tr>
            <td>${formatDate(item.date)}</td>
            <td><span class="status ${getStatusClass(item.status)}">${getStatusText(item.status)}</span></td>
            <td>${item.comment}</td>
            <td><code style="font-size: 13px; background: var(--bg); padding: 6px 10px; border-radius: 4px; font-family: monospace; user-select: all; cursor: pointer;" title="Нажмите, чтобы скопировать" onclick="copyToClipboard('${item.recordId}')">${item.recordId || 'N/A'}</code></td>
        </tr>
    `).join('');
}

// === Рендеринг пагинации ===
function renderPagination(page, totalPages) {
    const pagination = document.getElementById('historyPagination');
    const pagesDiv = document.getElementById('paginationPages');
    const prevBtn = document.getElementById('prevPageBtn');
    const nextBtn = document.getElementById('nextPageBtn');

    if (totalPages <= 1) {
        pagination.style.display = 'none';
        return;
    }

    pagination.style.display = 'flex';
    prevBtn.disabled = page <= 1;
    nextBtn.disabled = page >= totalPages;

    // Генерация кнопок страниц
    let pages = [];
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= page - 1 && i <= page + 1)) {
            pages.push(i);
        } else if (pages[pages.length - 1] !== '...') {
            pages.push('...');
        }
    }

    pagesDiv.innerHTML = pages.map(p => {
        if (p === '...') {
            return `<span class="page-dots">...</span>`;
        }
        return `<span class="page ${p === page ? 'active' : ''}" onclick="goToPage(${p})">${p}</span>`;
    }).join('');
}

async function goToPage(page) {
    currentPage = page;
    await loadHistory();
}

// === Модальное окно: Ручной ввод ===
function openManualModal() {
    document.getElementById('manualModal').classList.add('active');
    document.getElementById('manualDate').value = new Date().toISOString().split('T')[0];
}

function closeManualModal() {
    document.getElementById('manualModal').classList.remove('active');
}

async function saveManualData() {
    const token = localStorage.getItem('token');
    if (!token || !currentUserId) {
        alert('Ошибка аутентификации');
        return;
    }

    const date = document.getElementById('manualDate').value;
    const type = document.getElementById('manualType').value;
    const value = parseFloat(document.getElementById('manualValue').value);
    const comment = document.getElementById('manualComment').value.trim();

    if (!date || isNaN(value)) {
        alert('Заполните все обязательные поля');
        return;
    }

    try {
        const res = await fetch(`${window.API_URL}/data/manual`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                date,
                type,
                value,
                comment: comment || null,
                userId: currentUserId
            })
        });

        const result = await res.json();

        if (result.success) {
            alert(`✅ Данные добавлены! ID: ${result.id}`);
            closeManualModal();
            await loadHistory();
            // Очистка формы
            document.getElementById('manualValue').value = '';
            document.getElementById('manualComment').value = '';
        } else {
            alert('Ошибка: ' + (result.message || 'Неизвестная ошибка'));
        }
    } catch (error) {
        console.error('Error saving manual data:', error);
        alert('Ошибка при сохранении данных');
    }
}

// === Модальное окно: Загрузка файла ===
function openUploadModal() {
    document.getElementById('uploadModal').classList.add('active');
    document.getElementById('uploadResult').innerHTML = '';
}

function closeUploadModal() {
    document.getElementById('uploadModal').classList.remove('active');
}

async function uploadFile() {
    const token = localStorage.getItem('token');
    if (!token || !currentUserId) {
        alert('Ошибка аутентификации');
        return;
    }

    const fileInput = document.getElementById('uploadFile');
    const file = fileInput.files[0];

    if (!file) {
        alert('Выберите файл');
        return;
    }

    const resultDiv = document.getElementById('uploadResult');
    resultDiv.innerHTML = '<p style="color: var(--text-light);">Загрузка...</p>';

    const formData = new FormData();
    formData.append('file', file);
    formData.append('userId', currentUserId);

    try {
        const res = await fetch(`${window.API_URL}/data/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        const result = await res.json();

        if (result.success) {
            resultDiv.innerHTML = `
                <div style="padding: 15px; background: #22c55e; color: white; border-radius: 8px;">
                    <strong>✅ ${result.message}</strong><br>
                    <small>ID загрузки: ${result.id}</small><br>
                    <small>Используйте этот ID для валидации и консолидации</small>
                </div>
            `;
            await loadHistory();
        } else {
            resultDiv.innerHTML = `
                <div style="padding: 15px; background: #ef4444; color: white; border-radius: 8px;">
                    <strong>❌ Ошибка</strong><br>
                    <small>${result.detail || result.message || 'Неизвестная ошибка'}</small>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error uploading file:', error);
        resultDiv.innerHTML = `
            <div style="padding: 15px; background: #ef4444; color: white; border-radius: 8px;">
                <strong>❌ Ошибка загрузки файла</strong>
            </div>
        `;
    }
}

// === Модальное окно: Валидация ===
function openValidateModal() {
    document.getElementById('validateModal').classList.add('active');
    document.getElementById('validateResult').innerHTML = '';
}

function closeValidateModal() {
    document.getElementById('validateModal').classList.remove('active');
}

async function validateData() {
    const token = localStorage.getItem('token');
    if (!token || !currentUserId) {
        alert('Ошибка аутентификации');
        return;
    }

    const uploadId = document.getElementById('validateUploadId').value.trim();

    if (!uploadId) {
        alert('Введите ID загрузки');
        return;
    }

    const resultDiv = document.getElementById('validateResult');
    resultDiv.innerHTML = '<p style="color: var(--text-light);">Валидация...</p>';

    try {
        const res = await fetch(`${window.API_URL}/data/validate`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                uploadId,
                userId: currentUserId
            })
        });

        const result = await res.json();

        if (result.success) {
            if (result.validated) {
                resultDiv.innerHTML = `
                    <div style="padding: 15px; background: #22c55e; color: white; border-radius: 8px;">
                        <strong>✅ Валидация успешна</strong><br>
                        <small>${result.message}</small>
                    </div>
                `;
            } else {
                resultDiv.innerHTML = `
                    <div style="padding: 15px; background: #f59e0b; color: white; border-radius: 8px;">
                        <strong>⚠️ Найдены проблемы</strong><br>
                        <small>${result.message}</small>
                        <ul style="margin-top: 10px; padding-left: 20px;">
                            ${result.issues.map(issue => `<li>Строка ${issue.row}: ${issue.message}</li>`).join('')}
                        </ul>
                    </div>
                `;
            }
            await loadHistory();
        } else {
            resultDiv.innerHTML = `
                <div style="padding: 15px; background: #ef4444; color: white; border-radius: 8px;">
                    <strong>❌ Ошибка</strong><br>
                    <small>${result.detail || result.message || 'Неизвестная ошибка'}</small>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error validating data:', error);
        resultDiv.innerHTML = `
            <div style="padding: 15px; background: #ef4444; color: white; border-radius: 8px;">
                <strong>❌ Ошибка валидации</strong>
            </div>
        `;
    }
}

// === Модальное окно: Консолидация ===
function openConsolidateModal() {
    document.getElementById('consolidateModal').classList.add('active');
    document.getElementById('consolidateResult').innerHTML = '';
}

function closeConsolidateModal() {
    document.getElementById('consolidateModal').classList.remove('active');
}

async function consolidateData() {
    const token = localStorage.getItem('token');
    if (!token || !currentUserId) {
        alert('Ошибка аутентификации');
        return;
    }

    const uploadId = document.getElementById('consolidateUploadId').value.trim();
    const department = document.getElementById('consolidateDepartment').value;

    if (!uploadId) {
        alert('Введите ID загрузки');
        return;
    }

    const resultDiv = document.getElementById('consolidateResult');
    resultDiv.innerHTML = '<p style="color: var(--text-light);">Консолидация...</p>';

    try {
        const res = await fetch(`${window.API_URL}/data/consolidate`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                uploadId, 
                department,
                userId: currentUserId
            })
        });

        const result = await res.json();

        if (result.success) {
            resultDiv.innerHTML = `
                <div style="padding: 15px; background: #22c55e; color: white; border-radius: 8px;">
                    <strong>✅ Консолидация завершена</strong><br>
                    <small>${result.message}</small><br>
                    <small>ID: ${result.id}</small>
                </div>
            `;
            await loadHistory();
        } else {
            resultDiv.innerHTML = `
                <div style="padding: 15px; background: #ef4444; color: white; border-radius: 8px;">
                    <strong>❌ Ошибка</strong><br>
                    <small>${result.detail || result.message || 'Неизвестная ошибка'}</small>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error consolidating data:', error);
        resultDiv.innerHTML = `
            <div style="padding: 15px; background: #ef4444; color: white; border-radius: 8px;">
                <strong>❌ Ошибка консолидации</strong>
            </div>
        `;
    }
}

// === Вспомогательные функции ===
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getStatusClass(status) {
    const map = {
        'ready': 'ready',
        'inProgress': 'progress',
        'accepted': 'accepted'
    };
    return map[status] || 'progress';
}

function getStatusText(status) {
    const map = {
        'ready': 'Готово',
        'inProgress': 'В процессе',
        'accepted': 'Принято'
    };
    return map[status] || status;
}

// === Копирование в буфер обмена ===
function copyToClipboard(text) {
    if (!text || text === 'N/A') return;
    
    navigator.clipboard.writeText(text).then(() => {
        // Показываем уведомление
        const notification = document.createElement('div');
        notification.textContent = '✅ ID скопирован';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #22c55e;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            animation: slideInRight 0.3s ease;
        `;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 2000);
    }).catch(err => {
        console.error('Ошибка копирования:', err);
    });
}

// Глобальные функции для onclick
window.closeManualModal = closeManualModal;
window.closeUploadModal = closeUploadModal;
window.closeValidateModal = closeValidateModal;
window.closeConsolidateModal = closeConsolidateModal;
window.goToPage = goToPage;
window.copyToClipboard = copyToClipboard;
