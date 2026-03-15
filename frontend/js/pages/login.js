import { login, getProfile } from "../api.js";
import { saveAuthState } from "../auth.js";
import { setStatus, toggleLoading } from "../ui.js";

const form = document.querySelector("#loginForm");
const statusEl = document.querySelector("#status");
const submitBtn = document.querySelector("#submitBtn");

form?.addEventListener("submit", async (event) => {
  event.preventDefault();

  const email = document.querySelector("#email").value.trim();
  const password = document.querySelector("#password").value;

  if (!email || !password) {
    setStatus(statusEl, "Заполните email и пароль.", "error");
    return;
  }

  toggleLoading(submitBtn, "Вход...", "Войти", true);
  setStatus(statusEl, "", "");

  try {
    const authResponse = await login({ email, password });
    const token = authResponse.user_token;

    if (!token) {
      throw new Error("Сервер не вернул user_token.");
    }

    let profile = null;
    try {
      profile = await getProfile();
    } catch {
      profile = null;
    }

    saveAuthState({
      token,
      role: authResponse.role || profile?.role || "user",
      username: authResponse.username || profile?.username || "",
      email: authResponse.email || profile?.email || email,
      disabled: profile?.disabled || false
    });

    window.location.href = "./profile.html";
  } catch (error) {
    setStatus(statusEl, error.message, "error");
  } finally {
    toggleLoading(submitBtn, "Вход...", "Войти", false);
  }
});
