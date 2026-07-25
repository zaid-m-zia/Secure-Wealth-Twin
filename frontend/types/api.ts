export interface ApiEnvelope<T> {
  status: string;
  message: string;
  data: T;
  timestamp: string;
  request_id: string;
}

export interface ApiErrorEnvelope {
  timestamp: string;
  request_id: string;
  error_code: string;
  description: string;
  possible_solution: string;
}
