const TOKEN_KEY = "securewealth.access_token";
const REFRESH_TOKEN_KEY = "securewealth.refresh_token";
const PROFILE_KEY = "securewealth.profile";
const THEME_KEY = "securewealth.theme";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setAccessToken(token: string): void {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearAccessToken(): void {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.removeItem(TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function setRefreshToken(token: string): void {
  if (typeof window !== "undefined") window.localStorage.setItem(REFRESH_TOKEN_KEY, token);
}

export function getStoredProfile<T>(): T | null {
  if (typeof window === "undefined") return null;
  const value = window.localStorage.getItem(PROFILE_KEY);
  if (!value) return null;
  try {
    return JSON.parse(value) as T;
  } catch {
    return null;
  }
}

export function setStoredProfile(profile: unknown): void {
  if (typeof window !== "undefined") window.localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
}

export function clearAuthStorage(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(REFRESH_TOKEN_KEY);
  window.localStorage.removeItem(PROFILE_KEY);
}

export function getStoredTheme(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return window.localStorage.getItem(THEME_KEY);
}

export function setStoredTheme(theme: string): void {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.setItem(THEME_KEY, theme);
}
