import { apiClient } from "@/services/api";
import { ApiEnvelope } from "@/types/api";

export interface Customer { customer_id: string; dob: string | null; gender: string | null; location: string | null; account_balance: number; }
export interface Transaction { transaction_id: string; customer_id: string; transaction_date: string; transaction_time: string; transaction_amount: number; }
export interface PageResult<T> { items: T[]; meta: { total: number; page: number; page_size: number; total_pages: number }; }

function unwrap<T>(response: { data: ApiEnvelope<T> }): T { return response.data.data; }

export async function listCustomers(): Promise<PageResult<Customer>> { return unwrap(await apiClient.get<ApiEnvelope<PageResult<Customer>>>("/customers", { params: { page_size: 100 } })); }
export async function listTransactions(params: Record<string, string | number | undefined> = {}): Promise<PageResult<Transaction>> { return unwrap(await apiClient.get<ApiEnvelope<PageResult<Transaction>>>("/transactions", { params: { page_size: 20, ...params } })); }
export async function getResource<T>(path: string): Promise<T> { return unwrap(await apiClient.get<ApiEnvelope<T>>(path)); }
export async function uploadTransactions(file: File): Promise<{ rows_processed: number; transactions_created: number; transactions_skipped: number }> {
  const form = new FormData(); form.append("file", file);
  const response = await apiClient.post("/transactions/upload", form, { headers: { "Content-Type": "multipart/form-data" } });
  return response.data.data;
}
