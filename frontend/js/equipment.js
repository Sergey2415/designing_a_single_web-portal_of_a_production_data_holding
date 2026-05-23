// API_URL определён глобально в permissions.js (window.API_URL)

let currentPage = 1;
let currentFilters = {
    branch: null,
    type: null,
    status: null
};
let equipmentData = [];
let downtimeChart = null;
let equipmentChart = null;

document.addEventListener("DOMContentLoaded", async () => {
    console.log("[Equipment] Страница загружена, начало инициализации");

    // Инициализация RBAC
    try {
        if (typeof initializePermissions !== 'undefined') {
            await initializePermissions();
        } else {
            console.error('[Equipment] initializePermissions не определена!');
        }
    } catch (error) {
        console.error('[Equipment] Ошибка инициализации RBAC:', error);
    }

    // Загружаем данные
    console.log('[Equipment] Загрузка данных...');
    await loadEquipment();
    await loadDowntimeAnalysis();

    // Обработчики фильтров
    const branchFilter = document.getElementById('branchFilter');
    const typeFilter = document.getElementById('typeFilter');
    const statusFilter = document.getElementById('statusFilter');

    if (branchFilter) {
        branchFilter.addEventListener('change', async () => {
            currentFilters.branch = branchFilter.value === 'all' ? null : branchFilter.value;
            currentPage = 1;
            await loadEquipment();
        });
    }

    if (typeFilter) {
        typeFilter.addEventListener('change', async () => {
            currentFilters.type = typeFilter.value === 'all' ? null : typeFilter.value;
            currentPage = 1;
            await loadEquipment();
        });
    }

    if (statusFilter) {
        statusFilter.addEventListener('change', async () => {
            currentFilters.status = statusFilter.value === 'all' ? null : statusFilter.value;
            currentPage = 1;
            await loadEquipment();
        });
    }

    // Кнопка экспорта анализа простоев
    const exportBtn = document.getElementById('exportDowntimeBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', async () => {
            await exportDowntimeAnalysis();
        });
    }

    // Кнопка добавления оборудования
    const addEquipmentBtn = document.getElementById('addEquipmentBtn');
    if (addEquipmentBtn) {
        addEquipmentBtn.addEventListener('click', () => {
            alert('Функция добавления оборудования будет реализована в следующей версии.\n\nДля добавления используйте Swagger UI: http://localhost:8000/docs');
        });
    }
});

// === Загрузка оборудования ===
async function loadEquipment() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'auth.html';
        return;
    }

    try {
        const params = new URLSearchParams({
            page: currentPage,
            limit: 50
        });

        if (currentFilters.branch) params.append('branch', currentFilters.branch);
        if (currentFilters.type) params.append('type', currentFilters.type);
        if (currentFilters.status) params.append('status', currentFilters.status);

        const res = await fetch(`${window.API_URL}/equipment?${params}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!res.ok) throw new Error('Failed to fetch equipment');

        const result = await res.json();

        if (result.success) {
            equipmentData = result.data;
            renderEquipmentTable(result.data);
            renderEquipmentChart(result.data);
        }
    } catch (error) {
        console.error('Error loading equipment:', error);
        // Показываем сообщение в таблице вместо alert
        const tbody = document.querySelector('.table tbody');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 20px; color: red;">Ошибка загрузки оборудования</td></tr>';
        }
    }
}

// === Рендеринг таблицы ===
function renderEquipmentTable(equipment) {
    const tbody = document.querySelector('.table tbody');
    if (!tbody) return;

    if (!equipment || equipment.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 20px;">Оборудование не найдено</td></tr>';
        return;
    }

    tbody.innerHTML = equipment.map(eq => {
        const statusClass = getStatusClass(eq.status);
        const statusText = getStatusText(eq.status);
        const typeText = getTypeText(eq.type);

        return `
            <tr>
                <td>${eq.name}</td>
                <td>${eq.branch}</td>
                <td>${typeText}</td>
                <td><span class="status ${statusClass}">${statusText}</span></td>
                <td>${formatDate(eq.lastCheck)}</td>
                <td>${eq.responsible}</td>
            </tr>
        `;
    }).join('');
}

// === Рендеринг графика состояния ===
function renderEquipmentChart(equipment) {
    const statusCanvas = document.getElementById("equipmentStatusChart");
    if (!statusCanvas || !equipment) return;

    // Уничтожаем старый график если есть
    if (equipmentChart) {
        equipmentChart.destroy();
        equipmentChart = null;
    }

    // Подсчитываем статусы
    const statusCounts = {
        inprogress: 0,
        ready: 0,
        accepted: 0
    };

    equipment.forEach(eq => {
        if (statusCounts.hasOwnProperty(eq.status)) {
            statusCounts[eq.status]++;
        }
    });

    const styles = getComputedStyle(document.documentElement);
    const textColor = styles.getPropertyValue("--text").trim();
    const borderColor = styles.getPropertyValue("--border").trim();

    equipmentChart = new Chart(statusCanvas, {
        type: "doughnut",
        data: {
            labels: ["В работе", "Готов", "Принято"],
            datasets: [
                {
                    data: [statusCounts.inprogress, statusCounts.ready, statusCounts.accepted],
                    backgroundColor: ["#3b82f6", "#ef4444", "#22c55e"],
                    borderColor: borderColor,
                    borderWidth: 2,
                    hoverOffset: 10
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "60%",
            plugins: {
                legend: {
                    position: "bottom",
                    labels: {
                        color: textColor,
                        font: {
                            family: "Geologica",
                            size: 14,
                            weight: "500"
                        },
                        padding: 16,
                        usePointStyle: true,
                    },
                },
                tooltip: {
                    backgroundColor: "rgba(0,0,0,0.7)",
                    titleColor: "#fff",
                    bodyColor: "#fff",
                    titleFont: { family: "Geologica", size: 14 },
                    bodyFont: { family: "Geologica", size: 13 },
                    padding: 10,
                    cornerRadius: 8
                },
            },
            layout: {
                padding: 10
            },
        },
    });
}

// === Загрузка анализа простоев ===
async function loadDowntimeAnalysis() {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        const res = await fetch(`${window.API_URL}/equipment/downtime-analysis?period=last30days`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!res.ok) throw new Error('Failed to fetch downtime analysis');

        const result = await res.json();

        if (result.success) {
            renderDowntimeAnalysis(result.data);
        }
    } catch (error) {
        console.error('Error loading downtime analysis:', error);
    }
}

// === Рендеринг анализа простоев ===
function renderDowntimeAnalysis(data) {
    // Обновляем текст с процентом
    const downtimeText = document.querySelector('.analytics-section p strong');
    if (downtimeText) {
        downtimeText.textContent = `${data.downtimePercentage}%`;
    }

    // Рисуем график
    const downtimeCtx = document.getElementById("downtimeGraph")?.getContext("2d");
    if (!downtimeCtx) return;

    // Уничтожаем старый график если есть
    if (downtimeChart) {
        downtimeChart.destroy();
    }

    const labels = data.history.map(h => {
        const date = new Date(h.date);
        return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' });
    });
    const values = data.history.map(h => h.value);

    downtimeChart = new Chart(downtimeCtx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Простои, ч",
                    data: values,
                    borderColor: "#137fec",
                    backgroundColor: "rgba(19,127,236,0.1)",
                    tension: 0.4,
                    fill: true,
                },
            ],
        },
        options: {
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { display: false } },
                y: { beginAtZero: true },
            },
        },
    });
}

// === Экспорт анализа простоев ===
async function exportDowntimeAnalysis() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'auth.html';
        return;
    }

    try {
        const res = await fetch(`${window.API_URL}/equipment/downtime-analysis/export?format=pdf&period=last30days`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!res.ok) throw new Error('Failed to export');

        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `downtime_analysis_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error exporting downtime analysis:', error);
    }
}

// === Вспомогательные функции ===
function getStatusClass(status) {
    const statusMap = {
        'inprogress': 'status--inprogress',
        'ready': 'status--ready',
        'accepted': 'status--accepted'
    };
    return statusMap[status] || 'status--inprogress';
}

function getStatusText(status) {
    const statusMap = {
        'inprogress': 'В работе',
        'ready': 'Готов',
        'accepted': 'Принято'
    };
    return statusMap[status] || status;
}

function formatDate(dateString) {
    if (!dateString) return 'Н/Д';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

function getTypeText(type) {
    const typeMap = {
        'production': 'Производственное',
        'auxiliary': 'Вспомогательное',
        'transport': 'Транспортное'
    };
    return typeMap[type] || type;
}

// === Редактирование оборудования ===
async function editEquipment(id) {
    const equipment = equipmentData.find(eq => eq.id === id);
    if (!equipment) return;

    const newStatus = prompt(
        `Редактирование: ${equipment.name}\n\nВыберите новый статус:\n1 - В работе (inprogress)\n2 - Готов (ready)\n3 - Принято (accepted)\n\nВведите номер:`,
        equipment.status === 'inprogress' ? '1' : equipment.status === 'ready' ? '2' : '3'
    );

    if (!newStatus) return;

    const statusMap = { '1': 'inprogress', '2': 'ready', '3': 'accepted' };
    const status = statusMap[newStatus];

    if (!status) {
        console.error('Неверный статус');
        return;
    }

    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'auth.html';
        return;
    }

    try {
        const res = await fetch(`${window.API_URL}/equipment/${id}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                status: status,
                lastCheck: new Date().toISOString().split('T')[0],
                responsible: equipment.responsible
            })
        });

        const result = await res.json();

        if (result.success) {
            console.log('Оборудование обновлено');
            await loadEquipment(); // Перезагрузка списка
        }
    } catch (error) {
        console.error('Error updating equipment:', error);
    }
}

// === Удаление оборудования ===
async function deleteEquipment(id, name) {
    if (!confirm(`Вы уверены, что хотите удалить "${name}"?\n\nЭто действие нельзя отменить.`)) {
        return;
    }

    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'auth.html';
        return;
    }

    try {
        const res = await fetch(`${window.API_URL}/equipment/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const result = await res.json();

        if (result.success) {
            console.log('Оборудование удалено');
            await loadEquipment(); // Перезагрузка списка
        } else {
            console.error('Ошибка удаления:', result.message);
        }
    } catch (error) {
        console.error('Error deleting equipment:', error);
    }
}

// Делаем функции глобальными для onclick
window.editEquipment = editEquipment;
window.deleteEquipment = deleteEquipment;
