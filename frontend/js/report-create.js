const API_URL = 'http://localhost:8000/api';

document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('createReportBtn');
  const preview = document.getElementById('reportPreview');
  const titleInput = document.getElementById('reportTitle');
  const contentInput = document.getElementById('reportContent');
  const typeSelect = document.getElementById('reportTypeSelect');
  const statusSelect = document.getElementById('reportStatus');
  const departmentInput = document.getElementById('reportDepartment');
  const authorInput = document.getElementById('reportAuthor');
  const periodInput = document.getElementById('reportPeriod');
  const kpiInput = document.getElementById('reportKpi');

  btn.addEventListener('click', async () => {
    const title = titleInput?.value || 'Новый отчет';
    const content = contentInput?.value || '';
    const type = typeSelect?.value || 'production';
    const status = statusSelect?.value || 'inProgress';
    const department = departmentInput?.value || 'Производственный отдел';
    const author = authorInput?.value || 'Администратор';
    const period = periodInput?.value || 'Q4 2025';
    const kpi = kpiInput?.value || 'Производительность';
    const date = new Date().toISOString().split('T')[0];

    // Показываем предварительный просмотр
    preview.innerHTML = `
      <div class="report-result">
        <h3>📈 Предварительный отчёт</h3>
        <p><b>Название:</b> ${title}</p>
        <p><b>Период:</b> ${period}</p>
        <p><b>Отдел:</b> ${department}</p>
        <p><b>Тип:</b> ${getTypeText(type)}</p>
        <p><b>Автор:</b> ${author}</p>
        <p><b>Статус:</b> ${getStatusText(status)}</p>
        <p><b>KPI:</b> ${kpi}</p>
        <hr style="margin: 16px 0; border: 0; border-top: 1px solid var(--border);" />
        <p><b>Содержание:</b></p>
        <p>${content || 'Не указано'}</p>
        <hr style="margin: 16px 0; border: 0; border-top: 1px solid var(--border);" />
        <button class="btn btn-primary" id="saveReportBtn">Сохранить отчёт</button>
      </div>
    `;

    // Обработчик сохранения
    const saveBtn = document.getElementById('saveReportBtn');
    saveBtn.addEventListener('click', async () => {
      await createReport({
        title,
        content,
        type,
        status,
        department,
        author,
        period,
        kpi,
        date
      });
    });
  });
});

async function createReport(data) {
  const token = localStorage.getItem('token');
  if (!token) {
    window.location.href = 'auth.html';
    return;
  }

  try {
    const res = await fetch(`${API_URL}/reports`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    const result = await res.json();

    if (result.success) {
      alert('Отчёт успешно создан!');
      window.location.href = `report-details.html?id=${result.id}`;
    } else {
      alert('Ошибка создания отчёта: ' + (result.message || 'Неизвестная ошибка'));
    }
  } catch (error) {
    console.error('Error creating report:', error);
    alert('Ошибка создания отчёта');
  }
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

function getStatusText(status) {
  const statusMap = {
    'ready': 'Готов',
    'inProgress': 'В обработке',
    'accepted': 'Принят'
  };
  return statusMap[status] || status;
}
