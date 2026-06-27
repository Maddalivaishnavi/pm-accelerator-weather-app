const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, options = {}) {
  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new ApiError(
      "Couldn't reach the weather server. Is the backend running?",
      0
    );
  }

  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      /* response wasn't JSON, keep default message */
    }
    throw new ApiError(detail, res.status);
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  lookupWeather: (location, forecastDays = 5) =>
    request(
      `/api/weather/lookup?location=${encodeURIComponent(location)}&forecast_days=${forecastDays}`
    ),

  lookupByCoordinates: (latitude, longitude, forecastDays = 5) =>
    request(
      `/api/weather/by-coordinates?latitude=${latitude}&longitude=${longitude}&forecast_days=${forecastDays}`
    ),

  listRecords: () => request("/api/records"),

  createRecord: (payload) =>
    request("/api/records", { method: "POST", body: JSON.stringify(payload) }),

  updateRecord: (id, payload) =>
    request(`/api/records/${id}`, { method: "PUT", body: JSON.stringify(payload) }),

  deleteRecord: (id) => request(`/api/records/${id}`, { method: "DELETE" }),

  exportRecordUrl: (id, format) =>
    `${API_BASE}/api/records/${id}/export?format=${format}`,

  exportAllUrl: (format) => `${API_BASE}/api/records/export/all?format=${format}`,
};

export { ApiError };
