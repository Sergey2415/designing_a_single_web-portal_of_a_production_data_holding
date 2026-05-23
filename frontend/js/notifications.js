const API_URL = 'http://localhost:8000/api';

document.addEventListener("DOMContentLoaded", async () => {
    const listContainer = document.querySelector(".notifications-list");
    const filterButtons = document.querySelectorAll(".filter-btn");
    const refreshBtn = document.querySelector(".refresh-btn");
    
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'auth.html';
        return;
    }

    let currentFilter = 'all';
    let currentSort = 'time';
    let notifications = [];

    // === Загрузка данных ===
    async function loadData() {
        try {
            // Загрузить summary
            const summaryRes = await fetch(`${API_URL}/notifications/summary`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            
            if (summaryRes.ok) {
                const summary = await summaryRes.json();
                updateSummary(summary);
            }

            // Загрузить уведомления
            const notifRes = await fetch(
                `${API_URL}/notifications?type=${currentFilter}&sort=${currentSort}&limit=50`,
                { headers: { 'Authorization': `Bearer ${token}` } }
            );
            
            if (notifRes.ok) {
                notifications = await notifRes.json();
                renderList();
            }

            console.log('✅ Данные уведомлений загружены');
        } catch (error) {
            console.error('Error loading notifications:', error);
        }
    }

    // === Обновление карточек summary ===
    function updateSummary(summary) {
        const cards = document.querySelectorAll('.summary-item .value');
        if (cards[0]) cards[0].textContent = summary.newNotifications || 0;
        if (cards[1]) cards[1].textContent = summary.openTasks || 0;
        if (cards[2]) cards[2].textContent = summary.criticalErrors || 0;
        if (cards[3]) cards[3].textContent = summary.newTasks || 0;
    }

    // === Отрисовка списка уведомлений ===
    function renderList() {
        listContainer.innerHTML = "";
        
        if (notifications.length === 0) {
            listContainer.innerHTML = `<p class="empty" style="text-align: center; padding: 40px; color: var(--text-light);">Нет уведомлений данного типа 💤</p>`;
            return;
        }

        notifications.forEach(n => {
            const item = document.createElement("div");
            item.className = `notification-item ${n.type}`;
            item.dataset.id = n.id;
            
            const timeStr = formatTime(n.time);
            
            item.innerHTML = `
                <div class="notif-icon">${getIcon(n.type)}</div>
                <div class="notif-content">
                    <h3>${n.title || 'Уведомление'}</h3>
                    <p>${n.text}</p>
                    <span class="notif-time">${timeStr}</span>
                    <div class="notif-actions">
                        ${n.type === "error" ? `<button class="btn btn-outline comment-btn" data-id="${n.id}">💬 Комментарий</button>` : ""}
                        ${n.type === "error" ? `<button class="btn btn-outline assign-btn" data-id="${n.id}">Назначить ответственного</button>` : ""}
                        ${n.type === "report" && n.reportId ? `<button class="btn btn-primary" onclick="window.location.href='report-details.html?id=${n.reportId}'">Посмотреть отчёт</button>` : ""}
                        ${n.type === "task" && n.taskId ? `<button class="btn btn-primary" onclick="window.location.href='tasks.html?id=${n.taskId}'">Посмотреть задачу</button>` : ""}
                        ${!n.isRead ? `<button class="btn btn-outline mark-read-btn" data-id="${n.id}">Отметить прочитанным</button>` : ""}
                        ${n.type === "info" ? `<button class="btn btn-outline mark-read-btn" data-id="${n.id}">Понял</button>` : ""}
                    </div>
                </div>
            `;
            
            listContainer.appendChild(item);
        });

        // Добавить обработчики
        attachEventHandlers();
    }

    // === Форматирование времени ===
    function formatTime(dateStr) {
        const date = new Date(dateStr);
        const now = new Date();
        const diff = Math.floor((now - date) / 1000); // секунды

        if (diff < 60) return 'только что';
        if (diff < 3600) return `${Math.floor(diff / 60)} мин назад`;
        if (diff < 86400) return `${Math.floor(diff / 3600)} ч назад`;
        if (diff < 604800) return `${Math.floor(diff / 86400)} дн назад`;
        
        return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
    }

    // === Иконки по типу ===
    function getIcon(type) {
        switch (type) {
            case "error": return "⚠️";
            case "task": return "✅";
            case "report": return "📄";
            case "info": return "ℹ️";
            case "success": return "✔️";
            case "warning": return "⚠️";
            default: return "🔔";
        }
    }

    // === Обработчики действий ===
    function attachEventHandlers() {
        // Отметить прочитанным
        document.querySelectorAll('.mark-read-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const id = e.target.dataset.id;
                await markAsRead(id);
            });
        });

        // Добавить комментарий
        document.querySelectorAll('.comment-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const id = e.target.dataset.id;
                await addComment(id);
            });
        });

        // Назначить ответственного
        document.querySelectorAll('.assign-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const id = e.target.dataset.id;
                await assignResponsible(id);
            });
        });
    }

    // === Отметить как прочитанное ===
    async function markAsRead(notificationId) {
        try {
            const res = await fetch(`${API_URL}/notifications/${notificationId}/mark-read`, {
                method: 'POST',
                headers: { 
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (res.ok) {
                // Обновить список
                await loadData();
            }
        } catch (error) {
            console.error('Error marking as read:', error);
        }
    }

    // === Добавить комментарий ===
    async function addComment(notificationId) {
        const comment = prompt('Введите комментарий:');
        if (!comment) return;

        try {
            const res = await fetch(`${API_URL}/notifications/${notificationId}/comment`, {
                method: 'POST',
                headers: { 
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ comment })
            });

            if (res.ok) {
                alert('✅ Комментарий добавлен');
                await loadData();
            }
        } catch (error) {
            console.error('Error adding comment:', error);
            alert('Ошибка при добавлении комментария');
        }
    }

    // === Назначить ответственного ===
    async function assignResponsible(notificationId) {
        const assigneeId = prompt('Введите ID ответственного пользователя:');
        if (!assigneeId) return;

        try {
            const res = await fetch(`${API_URL}/notifications/${notificationId}/assign`, {
                method: 'POST',
                headers: { 
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ assigneeId })
            });

            if (res.ok) {
                alert('✅ Ответственный назначен');
                await loadData();
            } else {
                const error = await res.json();
                alert('Ошибка: ' + (error.detail || 'Неизвестная ошибка'));
            }
        } catch (error) {
            console.error('Error assigning responsible:', error);
            alert('Ошибка при назначении ответственного');
        }
    }

    // === Обработчики фильтров ===
    filterButtons.forEach(btn => {
        btn.addEventListener("click", async () => {
            filterButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            
            const text = btn.textContent.trim().toLowerCase();
            const map = { "все": "all", "ошибки": "error", "задачи": "task", "отчёты": "report" };
            currentFilter = map[text] || "all";
            
            await loadData();
        });
    });

    // === Сортировка ===
    const sortSelect = document.querySelector('.filter-row select');
    if (sortSelect) {
        sortSelect.addEventListener('change', async (e) => {
            const value = e.target.value;
            const sortMap = { 
                "По времени": "time", 
                "По типу": "type", 
                "По приоритету": "priority" 
            };
            currentSort = sortMap[value] || "time";
            await loadData();
        });
    }

    // === Обновление ===
    refreshBtn.addEventListener("click", async () => {
        refreshBtn.textContent = "🔄 Обновление...";
        refreshBtn.disabled = true;
        
        await loadData();
        
        setTimeout(() => {
            refreshBtn.textContent = "🔄 Обновить";
            refreshBtn.disabled = false;
        }, 500);
    });

    // === Инициализация ===
    await loadData();
});

