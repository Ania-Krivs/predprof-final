const canUseLocalStorage = typeof globalThis !== "undefined" && typeof globalThis.localStorage !== "undefined";

export const API_BASE_URL = canUseLocalStorage
  ? globalThis.localStorage.getItem("apiBaseUrl") || "http://localhost:8000"
  : "http://localhost:8000";

export const STORAGE_KEYS = {
  auth: "predprof_auth_state"
};

export const DEFAULT_HEADERS = {
  Accept: "application/json"
};
