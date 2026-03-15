import { getProfile } from "../api.js";
import { getAuthState, saveAuthState } from "../auth.js";
import { bindLogout, requireAuth } from "../guards.js";
import { setStatus, setActiveNav } from "../ui.js";

if (requireAuth()) {
  bindLogout();
  setActiveNav("profile.html");
}

const statusEl = document.querySelector("#status");
const auth = getAuthState();

function renderProfile(profile) {
  document.querySelector("#username").textContent = profile.username || "-";
  document.querySelector("#email").textContent = profile.email || "-";
  document.querySelector("#role").textContent = profile.role || "user";
  document.querySelector("#disabled").textContent = profile.disabled ? "Да" : "Нет";
}

(async function init() {
  if (!auth) {
    return;
  }

  renderProfile(auth);

  try {
    const profile = await getProfile();
    const nextAuth = {
      ...auth,
      username: profile.username || auth.username,
      email: profile.email || auth.email,
      role: profile.role || auth.role,
      disabled: profile.disabled ?? auth.disabled
    };
    saveAuthState(nextAuth);
    renderProfile(nextAuth);
  } catch (error) {
    setStatus(statusEl, `Показаны локальные данные профиля: ${error.message}`, "error");
  }
})();
