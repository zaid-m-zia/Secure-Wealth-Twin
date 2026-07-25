import { apiClient } from "@/services/api";
import { LoginRequest, LogoutResponse, RegisterRequest, TokenResponse, UserProfile } from "@/types/auth";
import { clearAccessToken, setAccessToken } from "@/utils/storage";

export async function registerUser(payload: RegisterRequest): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>("/auth/register", payload);
  setAccessToken(response.data.access_token);
  return response.data;
}

export async function loginUser(payload: LoginRequest): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>("/auth/login", payload);
  setAccessToken(response.data.access_token);
  return response.data;
}

export async function logoutUser(): Promise<LogoutResponse> {
  const response = await apiClient.post<LogoutResponse>("/auth/logout");
  clearAccessToken();
  return response.data;
}

export async function fetchProfile(): Promise<UserProfile> {
  const response = await apiClient.get<UserProfile>("/auth/profile");
  return response.data;
}
