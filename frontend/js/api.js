import { API_BASE_URL, DEFAULT_HEADERS } from "./config.js";
import { getAuthHeader } from "./auth.js";

async function parseApiError(response) {
  let message = `Request failed with status ${response.status}`;

  try {
    const body = await response.json();
    message = body.detail || body.message || JSON.stringify(body);
  } catch {
    // ignore JSON parse errors
  }

  const error = new Error(message);
  error.status = response.status;
  throw error;
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...DEFAULT_HEADERS,
      ...getAuthHeader(),
      ...(options.headers || {})
    }
  });

  if (!response.ok) {
    await parseApiError(response);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export async function registerUser(payload) {
  return request("/api/auth/create", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
}

export async function login(payload) {
  return request("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
}

export async function getProfile() {
  try {
    return await request("/api/auth/me", { method: "GET" });
  } catch (error) {
    if (error.status === 404) {
      return request("/api/users/me", { method: "GET" });
    }
    throw error;
  }
}

export async function classifyCivilization(file) {
  const formData = new FormData();
  formData.append("file", file);

  return request("/api/civilization/", {
    method: "POST",
    headers: {},
    body: formData
  });
}

export async function getAnalyticsSummary() {
  return request("/api/analytics/summary", { method: "GET" });
}
