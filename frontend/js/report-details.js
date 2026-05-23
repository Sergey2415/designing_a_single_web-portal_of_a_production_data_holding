const API_URL = 'http://localhost:8000/api';
let currentReport = null;

document.addEventListener('DOMContentLoaded', async () => {
    // Получаем ID отчёта из URL
    const urlParams = new URLSearchParams(window.location.search);
    const reportId = urlParams.get('id');

    if (!reportId) {
        alert('ID отчёта не указан');
        window.location.href = 'reports.html';
        return;
    }

    // Загружаем данные отчёта
    await loadReportDetails(reportId);

    // Обработчики кнопок
    const downloadPdfBtn = document.getElementById('downloadPdfBtn');
    const downloadCsvBtn = document.getElementById('downloadCsvBtn');
    const sendBtn = document.getElementById('sendBtn');

    if (downloadPdfBtn) {
        downloadPdfBtn.addEventListener('click', () => downloadReport(reportId, 'pdf'));
    }

    if (downloadCsvBtn) {
        downloadCsvBtn.addEventListener('click', () => downloadReport(reportId, 'csv'));
    }

    if (sendBtn) {
        sendBtn.addEventListener('click', () => sendReport(reportId));
    }
});

async function loadReportDetails(reportId) {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'auth.html';
        return;
    }

    try {
        const res = await fetch(`${API_URL}/reports/${reportId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!res.ok) throw new Error('Failed to fetch report');

        const result = await res.json();

        if (result.success) {
            currentReport = result.data;
            renderReportDetails(result.data);
        }
    } catch (error) {
        console.error('Error loading report:', error);
        alert('Ошибка загрузки отчёта');
        window.location.href = 'reports.html';
    }
}

function renderReportDetails(report) {
    // Обновляем заголовок
    const pageTitle = document.querySelector('.page-title');
    if (pageTitle) {
        pageTitle.textContent = report.title;
    }

    // Обновляем breadcrumb
    const breadcrumb = document.querySelector('.breadcrumb span');
    if (breadcrumb) {
        breadcrumb.textContent = report.title;
    }

    // Рендерим таблицу с деталями
    if (report.details && report.details.length > 0) {
        renderDetailsTable(report.details);
    }

    // Рендерим графики
    renderCharts(report);
}

function renderDetailsTable(details) {
    const tbody = document.querySelector('.details-table tbody');
    if (!tbody) return;

    tbody.innerHTML = details.map(item => {
        const deviation = item.deviation > 0 ? `+${item.deviation}%` : `${item.deviation}%`;
        const deviationClass = item.deviation > 0 ? 'positive' : 'negative';
        const statusClass = item.status === 'good' || item.status === 'excellent' ? 'ok' : 'warn';
        const statusText = getStatusText(item.status);

        return `
            <tr>
                <td>${item.parameter}</td>
                <td>${formatNumber(item.target)}</td>
                <td>${formatNumber(item.actual)}</td>
                <td class="${deviationClass}">${deviation}</td>
                <td class="status ${statusClass}">${statusText}</td>
            </tr>
        `;
    }).join('');
}

function renderCharts(report) {
    // График эффективности (если есть данные)
    const efficiencyCanvas = document.getElementById('efficiencyChart');
    if (efficiencyCanvas && report.details) {
        const labels = report.details.slice(0, 3).map(d => d.parameter);
        const data = report.details.slice(0, 3).map(d => d.actual);

        new Chart(efficiencyCanvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Факт',
                    data: data,
                    borderColor: '#137fec',
                    backgroundColor: 'rgba(19, 127, 236, 0.2)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: { responsive: true, plugins: { legend: { display: false } } }
        });
    }

    // График производства
    const productionCanvas = document.getElementById('productionChart');
    if (productionCanvas && report.details) {
        const labels = report.details.slice(0, 3).map(d => d.parameter);
        const planData = report.details.slice(0, 3).map(d => d.target);
        const factData = report.details.slice(0, 3).map(d => d.actual);

        new Chart(productionCanvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'План',
                        data: planData,
                        backgroundColor: '#94a3b8'
                    },
                    {
                        label: 'Факт',
                        data: factData,
                        backgroundColor: '#3b82f6'
                    }
                ]
            },
            options: { responsive: true }
        });
    }

    // График простоев
    const downtimeCanvas = document.getElementById("downtimeChart");
    if (downtimeCanvas && report.downtimeReasons && report.downtimeReasons.length > 0) {
        const styles = getComputedStyle(document.documentElement);
        const textColor = styles.getPropertyValue("--text").trim();
        const borderColor = styles.getPropertyValue("--border").trim();

        const labels = report.downtimeReasons.map(r => r.reason);
        const data = report.downtimeReasons.map(r => r.percentage);

        new Chart(downtimeCanvas, {
            type: "doughnut",
            data: {
                labels: labels,
                datasets: [
                    {
                        data: data,
                        backgroundColor: ["#a3e7bcff", "#e98181ff", "#e8d073ff", "#9fc7ffff"],
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
                            usePointStyle: true
                        },
                    },
                    tooltip: {
                        backgroundColor: "rgba(0,0,0,0.7)",
                        titleColor: "#fff",
                        bodyColor: "#fff",
                        titleFont: { family: "Geologica", size: 14 },
                        bodyFont: { family: "Geologica", size: 13 },
                        padding: 10,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed + '%';
                            }
                        }
                    },
                },
                layout: {
                    padding: 10
                },
            },
        });
    }
}

async function downloadReport(reportId, format) {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'auth.html';
        return;
    }

    try {
        const res = await fetch(`${API_URL}/reports/${reportId}/download?format=${format}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!res.ok) throw new Error('Failed to download');

        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `report_${reportId}.${format}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error downloading report:', error);
        alert('Ошибка скачивания отчёта');
    }
}

async function sendReport(reportId) {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'auth.html';
        return;
    }

    const managerId = prompt('Введите ID менеджера (или оставьте пустым):');

    try {
        const res = await fetch(`${API_URL}/reports/${reportId}/send`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ managerId })
        });

        const result = await res.json();

        if (result.success) {
            alert(result.message);
        } else {
            alert('Ошибка отправки отчёта');
        }
    } catch (error) {
        console.error('Error sending report:', error);
        alert('Ошибка отправки отчёта');
    }
}

function getStatusText(status) {
    const statusMap = {
        'good': 'В норме',
        'excellent': 'Отлично',
        'warning': 'Внимание',
        'normal': 'Нормально'
    };
    return statusMap[status] || status;
}

function formatNumber(num) {
    if (typeof num === 'number') {
        return num.toLocaleString('ru-RU');
    }
    return num;
}