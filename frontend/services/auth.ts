import { apiClient } from "@/services/api";
import { LoginRequest, LogoutResponse, RegisterRequest, TokenResponse, UserProfile } from "@/types/auth";
import { clearAuthStorage, setAccessToken, setRefreshToken, setStoredProfile } from "@/utils/storage";

function persistSession(response: TokenResponse): TokenResponse {
  setAccessToken(response.access_token);
  setRefreshToken(response.refresh_token);
  setStoredProfile(response.profile);
  return response;
}

export async function registerUser(payload: RegisterRequest): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>("/auth/register", payload);
  return persistSession(response.data);
}

export async function loginUser(payload: LoginRequest): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>("/auth/login", payload);
  return persistSession(response.data);
}

export async function logoutUser(): Promise<LogoutResponse> {
  const response = await apiClient.post<LogoutResponse>("/auth/logout");
  clearAuthStorage();
  return response.data;
}

export async function fetchProfile(): Promise<UserProfile> {
  const response = await apiClient.get<UserProfile>("/auth/profile");
  return response.data;
}
