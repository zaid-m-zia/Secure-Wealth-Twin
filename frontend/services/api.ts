import axios from "axios";

import { clearAuthStorage, getAccessToken, getRefreshToken, setAccessToken, setRefreshToken } from "@/utils/storage";

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let refreshRequest: Promise<string | null> | null = null;

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const request = error.config as { _retry?: boolean; url?: string; headers?: Record<string, string> } | undefined;
    const isAuthRequest = request?.url?.startsWith("/auth/");
    if (error.response?.status !== 401 || request?._retry || isAuthRequest) {
      return Promise.reject(error);
    }

    const refreshToken = getRefreshToken();
    if (!refreshToken || !request) {
      clearAuthStorage();
      if (typeof window !== "undefined") window.location.assign("/login");
      return Promise.reject(error);
    }

    request._retry = true;
    refreshRequest ??= apiClient.post("/auth/refresh", { refresh_token: refreshToken })
      .then((response) => {
        setAccessToken(response.data.access_token);
        setRefreshToken(response.data.refresh_token);
        return response.data.access_token as string;
      })
      .catch(() => {
        clearAuthStorage();
        return null;
      })
      .finally(() => { refreshRequest = null; });

    const accessToken = await refreshRequest;
    if (!accessToken) {
      if (typeof window !== "undefined") window.location.assign("/login");
      return Promise.reject(error);
    }
    request.headers = { ...request.headers, Authorization: `Bearer ${accessToken}` };
    return apiClient(request);
  },
);
