// API_URL определён глобально в permissions.js (window.API_URL)

let currentPage = 1;
let currentFilters = {
    date: 'all',
    type: 'all',
    status: 'all'
};

document.addEventListener('DOMContentLoaded', async () => {
    console.log('[Reports] Страница загружена, начало инициализации');

    const dateFilter = document.getElementById('dateFilter');
    const typeFilter = document.getElementById('typeFilter');
    const statusFilter = document.getElementById('statusFilter');
    const applyBtn = document.getElementById('applyFiltersBtn');
    const exportBtn = document.getElementById('exportBtn');
    const refreshBtn = document.getElementById('refreshBtn');

    // Инициализация RBAC
    try {
        if (typeof initializePermissions !== 'undefined') {
            await initializePermissions();
        } else {
            console.error('[Reports] initializePermissions не определена!');
        }
    } catch (error) {
        console.error('[Reports] Ошибка инициализации RBAC:', error);
    }

    // Загружаем отчеты при загрузке страницы
    console.log('[Reports] Загрузка отчётов...');
    await loadReports();

    // Обработчик применения фильтров
    if (applyBtn) {
        applyBtn.addEventListener('click', async () => {
            currentFilters.date = dateFilter.value;
            currentFilters.type = typeFilter.value;
            currentFilters.status = statusFilter.value;
            currentPage = 1;
            await loadReports();
        });
    }

    // Экспорт
    if (exportBtn) {
        exportBtn.addEventListener('click', async () => {
            await exportReports();
        });
    }

    // Обновить
    if (refreshBtn) {
        refreshBtn.addEventListener('click', async () => {
            await loadReports();
        });
    }
});

async function loadReports() {
    const token = localStorage.getItem('token');
    if (!token) {
        console.log('[Reports] Нет токена, перенаправление на auth.html');
        window.location.href = 'auth.html';
        return;
    }

    try {
        const params = new URLSearchParams({
            date: currentFilters.date,
            type: currentFilters.type,
            status: currentFilters.status,
            page: currentPage,
            limit: 10
        });

        console.log('[Reports] Отправка запроса:', `${window.API_URL}/reports?${params}`);

        const res = await fetch(`${window.API_URL}/reports?${params}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        console.log('[Reports] Ответ получен, status:', res.status);

        if (!res.ok) throw new Error('Failed to fetch reports');

        const data = await res.json();
        console.log('[Reports] Данные распарсены:', data);

        if (data.success) {
            console.log('[Reports] Рендеринг отчётов, количество:', data.data.length);
            renderReports(data.data);
            renderPagination(data.page, data.pages);
        }
    } catch (error) {
        console.error('[Reports] Ошибка загрузки:', error);
        alert('Ошибка загрузки отчетов');
    }
}

function renderReports(reports) {
    console.log('[Reports] renderReports вызвана, количество отчётов:', reports?.length);

    const tbody = document.getElementById('reportsBody');

    if (!tbody) {
        console.error('[Reports] Элемент reportsBody не найден!');
        return;
    }

    if (!reports || reports.length === 0) {
        console.log('[Reports] Нет отчётов для отображения');
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 20px;">Отчеты не найдены</td></tr>';
        return;
    }

    console.log('[Reports] Проверка isAdmin:', typeof isAdmin !== 'undefined' ? isAdmin() : 'функция не определена');

    tbody.innerHTML = reports.map(report => {
        const statusText = getStatusText(report.status);
        const typeText = getTypeText(report.type);

        // Кнопка удаления только для администраторов
        const deleteButton = (typeof isAdmin !== 'undefined' && isAdmin()) ?
            `<button class="btn btn-sm btn-danger" onclick="event.stopPropagation(); deleteReport('${report.id}')" style="margin-left: 5px;">Удалить</button>` :
            '';

        return `
            <tr onclick="window.location='report-details.html?id=${report.id}'">
                <td>${formatDate(report.date)}</td>
                <td>${typeText}</td>
                <td>${report.author}</td>
                <td><span class="status-badge status-${report.status}">${statusText}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline" onclick="event.stopPropagation(); openReport('${report.id}')">Открыть</button>
                    ${deleteButton}
                </td>
            </tr>
        `;
    }).join('');
}

function renderPagination(currentPage, totalPages) {
    const pagination = document.querySelector('.pagination');
    if (!pagination) return;

    const prevBtn = pagination.querySelector('.pagination-btn:first-child');
    const nextBtn = pagination.querySelector('.pagination-btn:last-child');
    const pagesContainer = pagination.querySelector('.pagination-pages');

    // Кнопки навигации
    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage === totalPages || totalPages === 0;

    prevBtn.onclick = () => {
        if (currentPage > 1) {
            goToPage(currentPage - 1);
        }
    };

    nextBtn.onclick = () => {
        if (currentPage < totalPages) {
            goToPage(currentPage + 1);
        }
    };

    // Страницы
    let pages = [];
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 1 && i <= currentPage + 1)) {
            pages.push(i);
        } else if (pages[pages.length - 1] !== '...') {
            pages.push('...');
        }
    }

    pagesContainer.innerHTML = pages.map(page => {
        if (page === '...') {
            return '<span class="page-ellipsis">...</span>';
        }
        return `<span class="page ${page === currentPage ? 'active' : ''}" onclick="goToPage(${page})">${page}</span>`;
    }).join('');
}

function goToPage(page) {
    currentPage = page;
    loadReports();
}

function openReport(id) {
    window.location.href = `report-details.html?id=${id}`;
}

async function exportReports() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'auth.html';
        return;
    }

    try {
        const params = new URLSearchParams({
            date: currentFilters.date,
            type: currentFilters.type,
            status: currentFilters.status
        });

        const res = await fetch(`${window.API_URL}/reports/export/csv?${params}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!res.ok) throw new Error('Failed to export');

        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `reports_export_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error exporting reports:', error);
        alert('Ошибка экспорта отчетов');
    }
}

function getStatusText(status) {
    const statusMap = {
        'ready': 'Готов',
        'inProgress': 'В обработке',
        'accepted': 'Принят'
    };
    return statusMap[status] || status;
}

function getTypeText(type) {
    const typeMap = {
        'production': 'Производственный',
        'financial': 'Финансовый',
        'equipment': 'Оборудование',
        'analytics': 'Аналитический'
    };
    return typeMap[type] || type;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

async function deleteReport(reportId) {
    if (!isAdmin()) {
        alert('Недостаточно прав для удаления отчетов');
        return;
    }

    if (!confirm('Вы уверены, что хотите удалить этот отчет?')) {
        return;
    }

    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'auth.html';
        return;
    }

    try {
        const res = await fetch(`${window.API_URL}/reports/${reportId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!res.ok) {
            if (res.status === 403) {
                alert('Недостаточно прав для удаления отчетов');
            } else {
                throw new Error('Failed to delete report');
            }
            return;
        }

        const data = await res.json();
        if (data.success) {
            alert('Отчет успешно удален');
            await loadReports();
        }
    } catch (error) {
        console.error('Error deleting report:', error);
        alert('Ошибка при удалении отчета');
    }
}

