const API_URL = 'http://localhost:8000/api';

let currentFilters = {
    period: 'К1 2025',
    branch: 'Все',
    type: 'Все'
};

document.addEventListener('DOMContentLoaded', async () => {
    console.log("✅ kpi.js загружен");

    // Загрузка фильтров
    await loadFilters();
    
    // Загрузка данных KPI
    await loadKPIData();

    // Обработчики изменения фильтров
    document.getElementById('periodFilter')?.addEventListener('change', async (e) => {
        currentFilters.period = e.target.value;
        await loadKPIData();
    });

    document.getElementById('branchFilter')?.addEventListener('change', async (e) => {
        currentFilters.branch = e.target.value;
        await loadKPIData();
    });

    document.getElementById('typeFilter')?.addEventListener('change', async (e) => {
        currentFilters.type = e.target.value;
        await loadKPIData();
    });

    // Обработчики экспорта
    document.getElementById('exportPdfBtn')?.addEventListener('click', exportToPDF);
    document.getElementById('exportExcelBtn')?.addEventListener('click', exportToExcel);
});

// === Загрузка фильтров ===
async function loadFilters() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'auth.html';
        return;
    }

    try {
        const res = await fetch(`${API_URL}/kpi/filters`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!res.ok) {
            throw new Error('Failed to load filters');
        }

        const result = await res.json();

        // Заполнить dropdown периодов
        const periodSelect = document.getElementById('periodFilter');
        if (periodSelect && result.periods) {
            periodSelect.innerHTML = result.periods.map(p => 
                `<option value="${p}" ${p === currentFilters.period ? 'selected' : ''}>${p}</option>`
            ).join('');
        }

        // Заполнить dropdown филиалов
        const branchSelect = document.getElementById('branchFilter');
        if (branchSelect && result.branches) {
            branchSelect.innerHTML = result.branches.map(b => 
                `<option value="${b}" ${b === currentFilters.branch ? 'selected' : ''}>${b}</option>`
            ).join('');
        }

        // Заполнить dropdown типов
        const typeSelect = document.getElementById('typeFilter');
        if (typeSelect && result.types) {
            typeSelect.innerHTML = result.types.map(t => 
                `<option value="${t}" ${t === currentFilters.type ? 'selected' : ''}>${t}</option>`
            ).join('');
        }

        console.log('✅ Фильтры загружены');
    } catch (error) {
        console.error('Error loading filters:', error);
        alert('Ошибка загрузки фильтров');
    }
}

// === Загрузка данных KPI ===
async function loadKPIData() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'auth.html';
        return;
    }

    try {
        const params = new URLSearchParams({
            period: currentFilters.period,
            branch: currentFilters.branch,
            type: currentFilters.type
        });

        const res = await fetch(`${API_URL}/kpi/data?${params}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!res.ok) {
            throw new Error('Failed to load KPI data');
        }

        const result = await res.json();

        // Отобразить таблицу
        renderKPITable(result.rows);

        // Отобразить summary
        renderSummary(result.summary);

        console.log('✅ Данные KPI загружены');
    } catch (error) {
        console.error('Error loading KPI data:', error);
        
        const tbody = document.getElementById('kpiTableBody');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" style="text-align: center; color: #ef4444;">Ошибка загрузки данных</td>
                </tr>
            `;
        }
    }
}

// === Рендеринг таблицы KPI ===
function renderKPITable(rows) {
    const tbody = document.getElementById('kpiTableBody');
    if (!tbody) return;

    if (!rows || rows.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; color: var(--text-light);">Нет данных</td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = rows.map(row => {
        const isPositive = row.trend.includes('▲') || row.deviation.includes('+');
        const deviationClass = isPositive ? 'positive' : 'negative';
        const trendClass = isPositive ? 'positive' : 'negative';

        return `
            <tr>
                <td><a href="${row.link}">${row.name}</a></td>
                <td>${row.plan}</td>
                <td>${row.fact}</td>
                <td class="${deviationClass}">${row.deviation}</td>
                <td class="${trendClass}">${row.trend}</td>
            </tr>
        `;
    }).join('');
}

// === Рендеринг summary ===
function renderSummary(summary) {
    if (!summary) return;

    // Тренд KPI
    if (summary.trendKpi) {
        const trendValue = document.getElementById('trendValue');
        const trendSub = document.getElementById('trendSub');
        
        if (trendValue) {
            trendValue.textContent = summary.trendKpi.value;
            trendValue.className = `summary-value ${summary.trendKpi.isPositive ? 'positive' : 'negative'}`;
        }
        
        if (trendSub) {
            trendSub.textContent = summary.trendKpi.sub;
        }
    }

    // Сравнение филиалов
    if (summary.branchCompare) {
        const compareValue = document.getElementById('compareValue');
        const compareSub = document.getElementById('compareSub');
        
        if (compareValue) {
            compareValue.textContent = summary.branchCompare.value;
            compareValue.className = `summary-value ${summary.branchCompare.isPositive ? 'positive' : 'negative'}`;
        }
        
        if (compareSub) {
            compareSub.textContent = summary.branchCompare.sub;
        }
    }
}

// === Экспорт в PDF ===
function exportToPDF() {
    alert('Экспорт в PDF будет реализован');
    // TODO: Реализовать экспорт
}

// === Экспорт в Excel ===
function exportToExcel() {
    alert('Экспорт в Excel будет реализован');
    // TODO: Реализовать экспорт
}

