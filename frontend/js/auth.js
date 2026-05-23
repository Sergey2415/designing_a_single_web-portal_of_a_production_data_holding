document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("loginForm");
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const rememberCheckbox = document.getElementById("remember");

    // Автозаполнение логина, если был сохранён
    const savedUser = localStorage.getItem("savedUser");
    if (savedUser) {
        usernameInput.value = savedUser;
        rememberCheckbox.checked = true;
    }

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();

        if (!username || !password) {
            alert("Введите логин и пароль!");
            return;
        }

        try {
            const res = await fetch("http://localhost:8000/api/auth/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ username, password }),
            });

            const data = await res.json();

            if (data.success) {
                // Сохраняем токен и данные пользователя
                localStorage.setItem("token", data.token);
                localStorage.setItem("user", JSON.stringify(data.user));

                // Если отмечено "запомнить"
                if (rememberCheckbox.checked) {
                    localStorage.setItem("savedUser", username);
                } else {
                    localStorage.removeItem("savedUser");
                }

                // Переход на главную страницу
                document.body.classList.add("auth-success");
                setTimeout(() => (window.location.href = "index.html"), 800);
            } else {
                alert(data.message || "Ошибка авторизации");
                passwordInput.value = "";
            }
        } catch (error) {
            console.error("Ошибка при авторизации:", error);
            alert("Ошибка соединения с сервером");
        }
    });
});
