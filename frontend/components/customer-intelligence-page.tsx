"use client";
import { useEffect, useState } from "react";
import { CustomerPicker } from "@/components/customer-picker";
import { EmptyState, ErrorState, LoadingState } from "@/components/data-state";
import { SecurePage } from "@/components/secure-page";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Customer, getResource, listCustomers } from "@/services/platform";

function display(value: unknown): string { if (value === null || value === undefined) return "—"; if (typeof value === "object") return JSON.stringify(value); return String(value); }

export function CustomerIntelligencePage({ title, description, endpoint, emptyTitle }: { title: string; description: string; endpoint: string; emptyTitle: string }) {
  const [customers, setCustomers] = useState<Customer[]>([]); const [customerId, setCustomerId] = useState(""); const [data, setData] = useState<Record<string, unknown> | null>(null); const [error, setError] = useState("");
  useEffect(() => { listCustomers().then(({ items }) => { setCustomers(items); setCustomerId(items[0]?.customer_id ?? ""); }).catch(() => setError("Unable to load customers.")); }, []);
  useEffect(() => { if (!customerId) return; setData(null); getResource<Record<string, unknown>>(endpoint.replace(":customerId", customerId)).then(setData).catch(() => setError(`Unable to load ${title.toLowerCase()} data.`)); }, [customerId, endpoint, title]);
  return <SecurePage title={title} description={description}>{error ? <ErrorState message={error} /> : !customers.length ? <EmptyState title={emptyTitle} description="Import transaction data or create a customer, then return to this page." /> : !data ? <LoadingState /> : <div className="space-y-6"><CustomerPicker customers={customers} value={customerId} onChange={setCustomerId}/><section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{Object.entries(data).map(([key, value]) => <Card key={key}><CardHeader><CardTitle className="capitalize">{key.replaceAll("_", " ")}</CardTitle></CardHeader><CardContent><p className="break-words text-sm text-muted-foreground">{display(value)}</p></CardContent></Card>)}</section></div>}</SecurePage>;
}
