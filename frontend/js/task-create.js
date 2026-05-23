const API_URL = 'http://localhost:8000/api';

document.addEventListener('DOMContentLoaded', async () => {
    console.log("✅ task-create.js загружен");

    // Загрузить список ответственных
    await loadResponsibles();

    // Обработчик выбора файла
    const fileInput = document.getElementById('reportFile');
    const fileNameSpan = document.querySelector('.file-name');
    
    fileInput.addEventListener('change', () => {
        fileNameSpan.textContent = fileInput.files.length
            ? fileInput.files[0].name
            : 'Файл не выбран';
    });

    // Обработчик отправки формы
    const form = document.getElementById('taskForm');
    form.addEventListener('submit', handleSubmit);
});

// === Загрузка списка ответственных ===
async function loadResponsibles() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'auth.html';
        return;
    }

    const select = document.getElementById('responsible');
    if (!select) return;

    try {
        const res = await fetch(`${API_URL}/tasks/responsibles`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!res.ok) {
            throw new Error('Failed to load responsibles');
        }

        const responsibles = await res.json();

        select.innerHTML = '<option value="" disabled selected hidden>Выберите исполнителя</option>' +
            responsibles.map(r => `<option value="${r.value}">${r.label}</option>`).join('');

        console.log('✅ Список ответственных загружен');
    } catch (error) {
        console.error('Error loading responsibles:', error);
        select.innerHTML = '<option value="" disabled selected>Ошибка загрузки</option>';
    }
}

// === Обработка отправки формы ===
async function handleSubmit(e) {
    e.preventDefault();

    const token = localStorage.getItem('token');
    if (!token) {
        alert('Ошибка аутентификации');
        return;
    }

    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;
    submitBtn.textContent = '⏳ Сохранение...';

    try {
        // Собираем данные формы
        const formData = new FormData();
        formData.append('title', document.getElementById('title').value);
        formData.append('description', document.getElementById('description').value || '');
        formData.append('report', document.getElementById('report').value || '');
        formData.append('responsible', document.getElementById('responsible').value);
        formData.append('due', document.getElementById('due').value);
        formData.append('priority', document.getElementById('priority').value);

        // Добавляем файл если выбран
        const fileInput = document.getElementById('reportFile');
        if (fileInput.files.length > 0) {
            formData.append('reportFile', fileInput.files[0]);
        }

        const res = await fetch(`${API_URL}/tasks`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (!res.ok) {
            const error = await res.json();
            throw new Error(error.detail || 'Failed to create task');
        }

        const result = await res.json();

        console.log('✅ Задача создана:', result);
        
        alert('✅ Задача успешно создана!');
        
        // Перенаправляем на список задач
        window.location.href = 'tasks.html';
    } catch (error) {
        console.error('Error creating task:', error);
        alert('Ошибка при создании задачи: ' + error.message);
        
        submitBtn.disabled = false;
        submitBtn.textContent = '💾 Сохранить задачу';
    }
}

