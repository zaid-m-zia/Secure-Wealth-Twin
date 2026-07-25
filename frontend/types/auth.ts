export interface RegisterRequest {
  full_name: string;
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface UserProfile {
  subject: string;
  email: string | null;
  full_name: string | null;
  roles: string[];
  issued_at: string | null;
  expires_at: string | null;
  claims: Record<string, unknown>;
}

export interface TokenResponse {
  status: string;
  message: string;
  access_token: string;
  token_type: string;
  expires_in_seconds: number;
  profile: UserProfile;
  request_id: string;
}

export interface LogoutResponse {
  status: string;
  message: string;
  request_id: string;
}
