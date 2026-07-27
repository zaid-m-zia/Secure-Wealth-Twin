"use client";
import { Customer } from "@/services/platform";
import { Label } from "@/components/ui/label";
export function CustomerPicker({ customers, value, onChange }: { customers: Customer[]; value: string; onChange: (customerId: string) => void }) { return <div className="flex items-center gap-3"><Label htmlFor="customer">Account</Label><select id="customer" className="h-10 rounded-2xl border border-border bg-background px-3 text-sm" value={value} onChange={(event) => onChange(event.target.value)}>{customers.map((customer, index) => <option key={customer.customer_id} value={customer.customer_id}>{index === 0 ? "Primary account" : `Account ${index + 1}`}{customer.location ? ` · ${customer.location}` : ""}</option>)}</select></div>; }
