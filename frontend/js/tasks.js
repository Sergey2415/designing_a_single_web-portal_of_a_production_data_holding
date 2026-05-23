const API_URL = 'http://localhost:8000/api';

let currentStatus = 'in_progress';

document.addEventListener("DOMContentLoaded", async () => {
    console.log("✅ tasks.js загружен");

    const tabs = document.querySelectorAll(".tab-btn");
    const tbody = document.querySelector(".table tbody");

    // Загрузить задачи и историю
    await loadTasks();
    await loadHistory();

    // Обработчики вкладок
    tabs.forEach((tab, index) => {
        tab.addEventListener("click", async () => {
            tabs.forEach((t) => t.classList.remove("active"));
            tab.classList.add("active");

            const statuses = ['in_progress', 'completed', 'overdue'];
            currentStatus = statuses[index];
            
            await loadTasks();
        });
    });
});

// === Загрузка задач ===
async function loadTasks() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'auth.html';
        return;
    }

    const tbody = document.querySelector(".table tbody");
    if (!tbody) return;

    try {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:20px;">Загрузка...</td></tr>';

        const res = await fetch(`${API_URL}/tasks?status=${currentStatus}&limit=20`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!res.ok) {
            throw new Error('Failed to load tasks');
        }

        const tasks = await res.json();

        renderTasks(tasks);
        console.log('✅ Задачи загружены:', tasks.length);
    } catch (error) {
        console.error('Error loading tasks:', error);
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color: #ef4444;">Ошибка загрузки задач</td></tr>';
    }
}

// === Рендеринг задач ===
function renderTasks(tasks) {
    const tbody = document.querySelector(".table tbody");
    if (!tbody) return;

    if (!tasks || tasks.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--text-light); padding:16px;">Нет задач</td></tr>`;
        return;
    }

    tbody.innerHTML = tasks.map(task => {
        const actionBtn = task.status === 'В процессе' || task.status === 'Просрочена' 
            ? `<button class="btn btn-sm btn-outline" onclick="markComplete(${task.id})">✓ Выполнено</button>`
            : '';

        return `
            <tr>
                <td>${task.title}</td>
                <td>${task.report || '—'}</td>
                <td>${task.responsible}</td>
                <td>${task.due || '—'}</td>
                <td>${renderStatus(task.status)}</td>
                <td>${actionBtn}</td>
            </tr>
        `;
    }).join('');
}

// === Отрисовка статуса ===
function renderStatus(status) {
    let className = "";
    switch (status) {
        case "В процессе":
            className = "in-progress";
            break;
        case "Выполнена":
            className = "completed";
            break;
        case "Просрочена":
            className = "overdue";
            break;
    }
    return `<span class="status ${className}">${status}</span>`;
}

// === Отметить задачу выполненной ===
async function markComplete(taskId) {
    const token = localStorage.getItem('token');
    if (!token) return;

    if (!confirm('Отметить задачу как выполненную?')) {
        return;
    }

    try {
        const res = await fetch(`${API_URL}/tasks/${taskId}/mark-complete`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!res.ok) {
            throw new Error('Failed to mark complete');
        }

        // Перезагрузить список
        await loadTasks();
        await loadHistory();
        
        console.log('✅ Задача отмечена как выполненная');
    } catch (error) {
        console.error('Error marking complete:', error);
        alert('Ошибка при отметке задачи');
    }
}

// === Загрузка истории ===
async function loadHistory() {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        const res = await fetch(`${API_URL}/tasks/history?limit=10`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!res.ok) {
            throw new Error('Failed to load history');
        }

        const history = await res.json();

        renderHistory(history);
        console.log('✅ История загружена:', history.length);
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

// === Рендеринг истории ===
function renderHistory(history) {
    const historyList = document.querySelector('.history-list');
    if (!historyList) return;

    if (!history || history.length === 0) {
        historyList.innerHTML = '<li style="color: var(--text-light);">Нет записей в истории</li>';
        return;
    }

    historyList.innerHTML = history.map(h => `
        <li>
            <span class="icon ${h.icon || 'success'}">✔</span> 
            ${h.text}
            <br />
            <small>Автор: ${h.author}, дата: ${h.date}</small>
        </li>
    `).join('');
}

// Глобальные функции для HTML onclick
window.markComplete = markComplete;
