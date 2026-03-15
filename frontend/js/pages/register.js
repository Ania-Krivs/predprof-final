import { registerUser } from "../api.js";
import { requireRole, bindLogout } from "../guards.js";
import { setStatus, toggleLoading, setActiveNav } from "../ui.js";

if (requireRole("admin")) {
  bindLogout();
  setActiveNav("register.html");
}

const form = document.querySelector("#registerForm");
const statusEl = document.querySelector("#status");
const submitBtn = document.querySelector("#submitBtn");

form?.addEventListener("submit", async (event) => {
  event.preventDefault();

  const email = document.querySelector("#email").value.trim();
  const username = document.querySelector("#username").value.trim();
  const password = document.querySelector("#password").value;
  const role = document.querySelector("#role").value;

  if (!email || !username || !password) {
    setStatus(statusEl, "Заполните все поля.", "error");
    return;
  }

  toggleLoading(submitBtn, "Создание...", "Создать пользователя", true);
  setStatus(statusEl, "", "");

  try {
    await registerUser({ email, username, password, role });
    form.reset();
    setStatus(statusEl, "Пользователь успешно создан.", "success");
  } catch (error) {
    setStatus(statusEl, error.message, "error");
  } finally {
    toggleLoading(submitBtn, "Создание...", "Создать пользователя", false);
  }
});
