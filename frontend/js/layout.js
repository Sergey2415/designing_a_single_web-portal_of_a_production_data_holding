document.addEventListener("DOMContentLoaded", async () => {
  // 🚫 Если на странице авторизации или регистрации — выходим
  const currentPage = window.location.pathname.split("/").pop();
  if (currentPage === "auth.html" || currentPage === "register.html") return;

  const token = localStorage.getItem("token");
  if (!token) {
    window.location.href = "auth.html";
    return;
  }

  try {
    const res = await fetch("http://localhost:8000/api/auth/check", {
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (!res.ok) throw new Error("HTTP error " + res.status);

    const data = await res.json();

    // Если success отсутствует или false — неавторизован
    if (!data.success) {
      throw new Error("Unauthorized");
    }

    // ✅ Только теперь подгружаем header и sidebar
    await loadLayout(data.user);

  } catch (err) {
    console.warn("Auth check failed:", err);
    localStorage.removeItem("token");
    window.location.href = "auth.html";
  }
});


async function loadLayout(user) {
  const headerContainer = document.createElement("div");
  const sidebarContainer = document.createElement("div");

  document.body.prepend(headerContainer);
  document.body.prepend(sidebarContainer);

  try {
    // Загружаем компоненты
    const [headerHtml, sidebarHtml] = await Promise.all([
      fetch("components/header.html").then(r => r.text()),
      fetch("components/sidebar.html").then(r => r.text())
    ]);

    headerContainer.innerHTML = headerHtml;
    sidebarContainer.innerHTML = sidebarHtml;

    // Обновляем имя пользователя (если есть .user-name)
    const userEl = document.querySelector(".user-name");
    if (userEl) userEl.textContent = user.name;

    // Применяем RBAC к элементам меню
    if (typeof window.applyPermissions === 'function') {
      window.applyPermissions();
    }

    // Загружаем аватар пользователя
    await loadUserAvatar();

    // Подсвечиваем текущие ссылки
    const currentPage = location.pathname.split("/").pop();
    document.querySelectorAll(".sidebar-link").forEach(link => {
      const href = link.getAttribute("href");
      link.classList.toggle("active", href && href === currentPage);
    });
    document.querySelectorAll(".nav-link").forEach(link => {
      const href = link.getAttribute("href");
      link.classList.toggle("active", href && href === currentPage);
    });
  } catch (e) {
    console.error("Ошибка при загрузке layout:", e);
  }
}

// Загрузка аватара пользователя
async function loadUserAvatar() {
  const token = localStorage.getItem("token");
  if (!token) return;

  try {
    const res = await fetch("http://localhost:8000/api/user/profile", {
      headers: { "Authorization": `Bearer ${token}` }
    });

    if (res.ok) {
      const profile = await res.json();
      
      // Обновить аватар в header
      const avatarEl = document.querySelector(".user-avatar");
      if (avatarEl && profile.avatarUrl) {
        avatarEl.src = profile.avatarUrl;
      }
    }
  } catch (error) {
    console.error("Error loading user avatar:", error);
  }
}
