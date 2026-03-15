import { clearAuthState, getAuthState, isAuthenticated } from "./auth.js";

export function requireAuth() {
  if (!isAuthenticated()) {
    window.location.href = "./login.html";
    return false;
  }
  return true;
}

export function requireRole(role) {
  const auth = getAuthState();
  if (!auth || !auth.token) {
    window.location.href = "./login.html";
    return false;
  }

  if (auth.role !== role) {
    window.location.href = "./profile.html";
    return false;
  }

  return true;
}

export function bindLogout(buttonSelector = "#logoutBtn") {
  const button = document.querySelector(buttonSelector);
  if (!button) {
    return;
  }

  button.addEventListener("click", () => {
    clearAuthState();
    window.location.href = "./login.html";
  });
}
