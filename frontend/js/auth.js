import { STORAGE_KEYS } from "./config.js";

export function saveAuthState(state, storage = localStorage) {
  storage.setItem(STORAGE_KEYS.auth, JSON.stringify(state));
}

export function getAuthState(storage = localStorage) {
  const raw = storage.getItem(STORAGE_KEYS.auth);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function clearAuthState(storage = localStorage) {
  storage.removeItem(STORAGE_KEYS.auth);
}

export function isAuthenticated(storage = localStorage) {
  const auth = getAuthState(storage);
  return Boolean(auth && auth.token);
}

export function hasRole(role, storage = localStorage) {
  const auth = getAuthState(storage);
  return Boolean(auth && auth.role === role);
}

export function getAuthHeader(storage = localStorage) {
  const auth = getAuthState(storage);
  if (!auth || !auth.token) {
    return {};
  }

  return { Authorization: `Bearer ${auth.token}` };
}
