const TOKEN_KEY = "securewealth.access_token";
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
