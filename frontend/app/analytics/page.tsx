"use client";
import { useEffect, useState } from "react";
import { ErrorState, LoadingState } from "@/components/data-state";
import { SecurePage } from "@/components/secure-page";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getResource } from "@/services/platform";
const sources = [["Behavior", "/analytics/behavior"], ["Fraud", "/analytics/fraud"], ["Wealth", "/analytics/wealth"], ["Transactions", "/analytics/transactions"], ["Recommendations", "/analytics/recommendations"]] as const;
export default function AnalyticsPage() {
  const [data, setData] = useState<Record<string, Record<string, unknown>> | null>(null); const [error, setError] = useState("");
  const load = () => { setError(""); Promise.all(sources.map(async ([name, path]) => [name, await getResource<Record<string, unknown>>(path)] as const)).then((results) => setData(Object.fromEntries(results))).catch(() => setError("Unable to prepare your financial story.")); };
  useEffect(() => { load(); }, []);
  return <SecurePage title="Insights" description="How your financial habits, security, and wellbeing are progressing.">{error ? <ErrorState message={error} onRetry={load}/> : !data ? <LoadingState/> : <div className="grid gap-6 lg:grid-cols-2">{Object.entries(data).map(([title, values]) => <Card key={title}><CardHeader><CardTitle>{title}</CardTitle></CardHeader><CardContent>{Object.entries(values).map(([key, item]) => <div key={key} className="flex justify-between border-b border-border py-2 text-sm"><span className="capitalize text-muted-foreground">{key.replaceAll("_", " ")}</span><span>{typeof item === "object" ? "Distribution available" : String(item)}</span></div>)}</CardContent></Card>)}</div>}</SecurePage>;
}
