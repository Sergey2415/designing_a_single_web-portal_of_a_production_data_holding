document.addEventListener('DOMContentLoaded', function () {
    const registerForm = document.getElementById('registerForm');
    const phoneInput = document.getElementById('phone');

    // Маска телефона
    phoneInput.addEventListener('input', function (e) {
        let value = e.target.value.replace(/\D/g, '');
        if (value.startsWith('7') || value.startsWith('8')) value = value.substring(1);
        let formattedValue = '+7';
        if (value.length > 0) formattedValue += '(' + value.substring(0, 3);
        if (value.length > 3) formattedValue += ')-' + value.substring(3, 6);
        if (value.length > 6) formattedValue += '-' + value.substring(6, 8);
        if (value.length > 8) formattedValue += '-' + value.substring(8, 10);
        e.target.value = formattedValue;
    });

    registerForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const data = {
            fullName: registerForm.fullName.value.trim(),
            position: registerForm.position.value.trim(),
            email: registerForm.email.value.trim(),
            phone: registerForm.phone.value.trim(),
            organization: registerForm.organization.value,
            role: registerForm.role.value,
            comment: registerForm.comment.value.trim(),
            agreement: registerForm.agreement.checked
        };

        if (!validate(data)) return;

        const submitBtn = registerForm.querySelector('button[type="submit"]');
        submitBtn.textContent = 'Отправка...';
        submitBtn.disabled = true;

        try {
            console.log('📨 Заявка на регистрацию:', data);
            await new Promise(r => setTimeout(r, 2000));
            alert('✅ Заявка отправлена! Ожидайте подтверждения администратора.');
            registerForm.reset();
            setTimeout(() => window.location.href = 'auth.html', 1000);
        } catch (err) {
            alert('Ошибка при отправке заявки. Попробуйте позже.');
        } finally {
            submitBtn.textContent = 'Отправить заявку';
            submitBtn.disabled = false;
        }
    });

    function validate(data) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const phoneDigits = data.phone.replace(/\D/g, '');
        if (!data.fullName || !data.position || !data.email || !data.phone || !data.organization || !data.role) {
            alert('Пожалуйста, заполните все обязательные поля.');
            return false;
        }
        if (!emailRegex.test(data.email)) {
            alert('Введите корректный адрес электронной почты.');
            return false;
        }
        if (phoneDigits.length < 10) {
            alert('Введите корректный номер телефона.');
            return false;
        }
        if (!data.agreement) {
            alert('Необходимо согласие с условиями обслуживания.');
            return false;
        }
        return true;
    }
});
