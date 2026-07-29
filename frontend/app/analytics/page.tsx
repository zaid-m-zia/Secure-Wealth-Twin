"use client";
import { useEffect, useState } from "react";
import { ErrorState, LoadingState } from "@/components/data-state";
import { SecurePage } from "@/components/secure-page";
import { CustomerPicker } from "@/components/customer-picker";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Customer, getResource, listCustomers } from "@/services/platform";
const sources = [["Behavior", "/analytics/behavior"], ["Fraud", "/analytics/fraud"], ["Wealth", "/analytics/wealth"], ["Transactions", "/analytics/transactions"], ["Recommendations", "/analytics/recommendations"]] as const;
export default function AnalyticsPage() {
  const [customers, setCustomers] = useState<Customer[] | null>(null); const [customerId, setCustomerId] = useState(""); const [data, setData] = useState<Record<string, Record<string, unknown>> | null>(null); const [error, setError] = useState("");
  const loadCustomers = () => { setError(""); listCustomers().then(({ items }) => { setCustomers(items); setCustomerId((current) => current || items[0]?.customer_id || ""); }).catch(() => setError("Unable to load your accounts.")); };
  const load = () => { if (!customerId) return; setError(""); setData(null); Promise.all(sources.map(async ([name, path]) => [name, await getResource<Record<string, unknown>>(`${path}?customer_id=${encodeURIComponent(customerId)}`)] as const)).then((results) => setData(Object.fromEntries(results))).catch(() => setError("Unable to prepare your financial story.")); };
  useEffect(() => { loadCustomers(); }, []);
  useEffect(() => { load(); }, [customerId]);
  useEffect(() => { if (!customerId) return; const refresh = () => load(); window.addEventListener("securewealth:runtime-updated", refresh); return () => window.removeEventListener("securewealth:runtime-updated", refresh); }, [customerId]);
  const retry = () => { if (customers === null) loadCustomers(); else load(); };
  return <SecurePage title="Insights" description="How your financial habits, security, and wellbeing are progressing.">{error ? <ErrorState message={error} onRetry={retry}/> : customers === null ? <LoadingState/> : !customers.length ? <p className="text-sm text-muted-foreground">Create an account and record a money movement to see runtime insights.</p> : !data ? <LoadingState/> : <div className="space-y-6"><CustomerPicker customers={customers} value={customerId} onChange={setCustomerId}/><div className="grid gap-6 lg:grid-cols-2">{Object.entries(data).map(([title, values]) => <Card key={title}><CardHeader><CardTitle>{title}</CardTitle></CardHeader><CardContent>{Object.entries(values).filter(([key]) => key !== "financial_dna").map(([key, item]) => <div key={key} className="flex justify-between border-b border-border py-2 text-sm"><span className="capitalize text-muted-foreground">{key.replaceAll("_", " ")}</span><span>{typeof item === "object" ? "Distribution available" : String(item ?? "—")}</span></div>)}</CardContent></Card>)}</div></div>}</SecurePage>;
}
