const API_URL = 'http://localhost:8000/api';

let currentPage = 1;
let currentFilters = {
    period: null,
    department: null,
    type: null
};

let costDynamicsChart = null;
let budgetEfficiencyChart = null;
let unitCostChart = null;

document.addEventListener('DOMContentLoaded', async () => {
    console.log("✅ finances.js загружен");

    // Загрузка данных
    await loadMetrics();
    await loadCostDynamics();
    await loadCostComparison();
    await loadBudgetEfficiency();

    // Обработчики кнопок динамики затрат
    document.querySelectorAll('[data-period]').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            document.querySelectorAll('[data-period]').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            const period = e.target.dataset.period;
            await loadCostDynamics(period);
        });
    });

    // Обработчики кнопок скачивания отчетов
    document.getElementById('downloadDaily')?.addEventListener('click', () => downloadReport('daily'));
    document.getElementById('downloadMonthly')?.addEventListener('click', () => downloadReport('monthly'));
    document.getElementById('downloadQuarterly')?.addEventListener('click', () => downloadReport('quarterly'));

    // Обработчик обновления отчета
    document.getElementById('updateReportBtn')?.addEventListener('click', openUpdateReportModal);

    // Обработчики фильтров бюджета
    document.getElementById('applyBudgetFilters')?.addEventListener('click', applyBudgetFilters);
    document.getElementById('resetBudgetFilters')?.addEventListener('click', resetBudgetFilters);
});

// === Загрузка метрик ===
async function loadMetrics() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'auth.html';
        return;
    }

    try {
        const res = await fetch(`${API_URL}/finances/metrics`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        const result = await res.json();

        if (result.success && result.data) {
            const data = result.data;
            
            // Обновляем значение
            document.querySelector('.metric-value').textContent = `${data.unitCost.value.toFixed(2)} ₽`;
            
            // Обновляем изменение
            const changeEl = document.querySelector('.metric-change');
            const direction = data.unitCost.changeDirection === 'down' ? '↓' : '↑';
            const changeClass = data.unitCost.changeDirection === 'down' ? 'metric-change--negative' : 'metric-change--positive';
            changeEl.className = `metric-change ${changeClass}`;
            changeEl.textContent = `${direction} ${data.unitCost.changePercentage}% по сравнению с прошлым месяцем`;

            // Обновляем время
            document.querySelector('.update-time').textContent = `Обновлено: ${formatDateTime(data.updatedAt)}`;

            // Рисуем мини-график
            renderUnitCostChart();
        }
    } catch (error) {
        console.error('Error loading metrics:', error);
    }
}

// === Мини-график стоимости за единицу ===
function renderUnitCostChart() {
    const ctx = document.getElementById('unitCostChart');
    if (!ctx) return;

    if (unitCostChart) {
        unitCostChart.destroy();
    }

    unitCostChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Май', 'Июнь', 'Июль', 'Авг', 'Сен', 'Окт'],
            datasets: [{
                label: 'Стоимость за единицу',
                data: [130, 128, 126, 127, 125.5, 125.5],
                borderColor: '#137fec',
                backgroundColor: (context) => {
                    const ctx = context.chart.ctx;
                    const gradient = ctx.createLinearGradient(0, 0, 0, 100);
                    gradient.addColorStop(0, 'rgba(19, 127, 236, 0.3)');
                    gradient.addColorStop(1, 'rgba(19, 127, 236, 0)');
                    return gradient;
                },
                fill: true,
                tension: 0.4,
                borderWidth: 2,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { display: false }
                },
                y: {
                    grid: { display: false },
                    ticks: { display: false },
                    beginAtZero: false
                }
            }
        }
    });
}

// === Загрузка динамики затрат ===
let currentPeriod = 'all';

async function loadCostDynamics(period = 'all') {
    const token = localStorage.getItem('token');
    if (!token) return;

    currentPeriod = period;

    try {
        const res = await fetch(`${API_URL}/finances/cost-dynamics?period=${period}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        const result = await res.json();

        if (result.success && result.data) {
            renderCostDynamicsChart(result.data, period);
        }
    } catch (error) {
        console.error('Error loading cost dynamics:', error);
    }
}

// === Рендеринг графика динамики затрат ===
function renderCostDynamicsChart(data, period) {
    const ctx = document.getElementById('costDynamicsChart');
    if (!ctx) return;

    if (costDynamicsChart) {
        costDynamicsChart.destroy();
    }

    // Определяем лейблы в зависимости от периода
    let labels = [];
    if (period === 'all') {
        labels = ['I квартал', 'II квартал', 'III квартал', 'IV квартал'];
    } else if (period === 'q1') {
        labels = ['Январь', 'Февраль', 'Март'];
    } else if (period === 'q2') {
        labels = ['Апрель', 'Май', 'Июнь'];
    } else if (period === 'q3') {
        labels = ['Июль', 'Август', 'Сентябрь'];
    } else if (period === 'q4') {
        labels = ['Октябрь', 'Ноябрь', 'Декабрь'];
    }

    costDynamicsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Затраты (₽)',
                data: [data.q1, data.q2, data.q3, data.q4].slice(0, labels.length),
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59,130,246,0.15)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            plugins: { 
                legend: { display: false },
                title: {
                    display: true,
                    text: period === 'all' ? 'Динамика по кварталам' : `Динамика за ${period.toUpperCase()}`,
                    font: { size: 14, weight: 600 }
                }
            },
            responsive: true,
            scales: { 
                y: { 
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString('ru-RU') + ' ₽';
                        }
                    }
                } 
            }
        }
    });
}

// === Загрузка сравнения затрат ===
async function loadCostComparison() {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        let url = `${API_URL}/finances/cost-comparison?page=${currentPage}&limit=10`;
        
        if (currentFilters.period) url += `&period=${currentFilters.period}`;
        if (currentFilters.department) url += `&department=${currentFilters.department}`;
        if (currentFilters.type) url += `&type=${currentFilters.type}`;

        const res = await fetch(url, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        const result = await res.json();

        if (result.success) {
            renderCostComparisonTable(result.data);
        }
    } catch (error) {
        console.error('Error loading cost comparison:', error);
        const tbody = document.querySelector('.finances-table tbody');
        if (tbody) {
            tbody.innerHTML = `
                <tr><td colspan="6" style="text-align: center; color: var(--text-light);">Нет данных</td></tr>
            `;
        }
    }
}

// === Рендеринг таблицы сравнения затрат ===
function renderCostComparisonTable(data) {
    const tbody = document.querySelector('.finances-table tbody');
    if (!tbody) return;

    if (!data || data.length === 0) {
        tbody.innerHTML = `
            <tr><td colspan="6" style="text-align: center; color: var(--text-light);">Нет данных</td></tr>
        `;
        return;
    }

    tbody.innerHTML = data.map(item => `
        <tr>
            <td>${item.period}</td>
            <td>${item.department}</td>
            <td>${getCostTypeText(item.type)}</td>
            <td>${item.amount.toFixed(2)} ₽</td>
            <td>${item.comment || '—'}</td>
            <td><span class="status ${getStatusClass(item.status)}">${getCostStatusText(item.status)}</span></td>
        </tr>
    `).join('');
}

// === Загрузка бюджета и эффективности ===
async function loadBudgetEfficiency(department = '', period = '') {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        let url = `${API_URL}/finances/budget-efficiency`;
        const params = [];
        
        if (department) params.push(`department=${encodeURIComponent(department)}`);
        if (period) params.push(`period=${encodeURIComponent(period)}`);
        
        if (params.length > 0) {
            url += '?' + params.join('&');
        }

        const res = await fetch(url, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        const result = await res.json();

        if (result.success && result.data) {
            renderBudgetEfficiencyChart(result.data);
        }
    } catch (error) {
        console.error('Error loading budget efficiency:', error);
    }
}

// === Применение фильтров бюджета ===
async function applyBudgetFilters() {
    const department = document.getElementById('budgetDepartment').value;
    const period = document.getElementById('budgetPeriod').value;
    
    await loadBudgetEfficiency(department, period);
}

// === Сброс фильтров бюджета ===
async function resetBudgetFilters() {
    document.getElementById('budgetDepartment').value = '';
    document.getElementById('budgetPeriod').value = '';
    
    await loadBudgetEfficiency();
}

// === Рендеринг графика бюджета и эффективности ===
function renderBudgetEfficiencyChart(data) {
    const ctx = document.getElementById('budgetEfficiencyChart');
    if (!ctx) return;

    if (budgetEfficiencyChart) {
        budgetEfficiencyChart.destroy();
    }

    budgetEfficiencyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: data.datasets.map(ds => ({
                label: ds.label,
                data: ds.data,
                backgroundColor: ds.backgroundColor
            }))
        },
        options: {
            plugins: { legend: { position: 'bottom' } },
            responsive: true,
            scales: { y: { beginAtZero: true } }
        }
    });
}

// === Скачивание отчета ===
async function downloadReport(type) {
    const token = localStorage.getItem('token');
    if (!token) {
        alert('Ошибка аутентификации');
        return;
    }

    try {
        const res = await fetch(`${API_URL}/finances/reports/${type}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!res.ok) {
            const error = await res.json();
            alert('Ошибка: ' + (error.detail || 'Не удалось скачать отчет'));
            return;
        }

        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `financial_report_${type}_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        console.log(`✅ Отчет ${type} скачан`);
    } catch (error) {
        console.error('Error downloading report:', error);
        alert('Ошибка при скачивании отчета');
    }
}

// === Модальное окно обновления отчета ===
let selectedFile = null;

function openUpdateReportModal() {
    const modal = document.getElementById('updateReportModal');
    modal.classList.add('active');
}

function closeUpdateReportModal() {
    const modal = document.getElementById('updateReportModal');
    modal.classList.remove('active');
    // Сброс формы
    document.getElementById('reportType').value = 'daily';
    document.getElementById('reportPeriod').value = '';
    removeFile();
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        if (!file.name.endsWith('.csv')) {
            alert('Пожалуйста, выберите CSV файл');
            event.target.value = '';
            return;
        }
        
        selectedFile = file;
        
        // Показать выбранный файл
        document.querySelector('.file-upload-placeholder').style.display = 'none';
        document.getElementById('fileSelected').style.display = 'flex';
        document.getElementById('fileName').textContent = file.name;
    }
}

function removeFile() {
    selectedFile = null;
    document.getElementById('reportFile').value = '';
    document.querySelector('.file-upload-placeholder').style.display = 'block';
    document.getElementById('fileSelected').style.display = 'none';
    document.getElementById('fileName').textContent = '';
}

async function uploadReport() {
    const token = localStorage.getItem('token');
    if (!token) {
        alert('Ошибка аутентификации');
        return;
    }

    const reportType = document.getElementById('reportType').value;
    const reportPeriod = document.getElementById('reportPeriod').value;

    if (!selectedFile) {
        alert('Пожалуйста, выберите CSV файл');
        return;
    }

    if (!reportPeriod) {
        alert('Пожалуйста, укажите период');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('type', reportType);
        formData.append('period', reportPeriod);

        const res = await fetch(`${API_URL}/finances/reports/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        const result = await res.json();

        if (result.success) {
            alert(`✅ Отчет обновлен успешно!`);
            closeUpdateReportModal();
            // Перезагрузить данные
            await loadCostComparison();
        } else {
            alert('Ошибка: ' + (result.message || 'Не удалось обновить отчет'));
        }
    } catch (error) {
        console.error('Error uploading report:', error);
        alert('Ошибка при загрузке отчета');
    }
}

// Глобальные функции для HTML onclick
window.openUpdateReportModal = openUpdateReportModal;
window.closeUpdateReportModal = closeUpdateReportModal;
window.handleFileSelect = handleFileSelect;
window.removeFile = removeFile;
window.uploadReport = uploadReport;

// === Вспомогательные функции ===
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getStatusClass(status) {
    const map = {
        'В рамках бюджета': 'ok',
        'Превышение стоимости': 'warn',
        'Экономия': 'positive',
        'ok': 'ok',
        'warn': 'warn',
        'positive': 'positive'
    };
    return map[status] || 'ok';
}

// Перевод типов затрат на русский
function getCostTypeText(type) {
    const typeMap = {
        'material': 'Материалы',
        'materials': 'Материалы',
        'labor': 'Труд',
        'equipment': 'Оборудование',
        'overhead': 'Накладные расходы',
        'other': 'Прочее'
    };
    return typeMap[type] || type;
}

// Перевод статусов затрат на русский
function getCostStatusText(status) {
    const statusMap = {
        'ok': 'В рамках бюджета',
        'warn': 'Превышение стоимости',
        'positive': 'Экономия',
        'approved': 'Одобрено',
        'pending': 'Ожидает'
    };
    return statusMap[status] || status;
}
