import { ReactNode } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
export function LoadingState({ label = "Loading data…" }: { label?: string }) { return <Card><CardContent className="py-12 text-center text-sm text-muted-foreground">{label}</CardContent></Card>; }
export function EmptyState({ title, description, action }: { title: string; description: string; action?: ReactNode }) { return <Card><CardHeader><CardTitle>{title}</CardTitle><CardDescription>{description}</CardDescription></CardHeader>{action ? <CardContent>{action}</CardContent> : null}</Card>; }
export function ErrorState({ message }: { message: string }) { return <Card className="border-destructive/30"><CardContent className="py-8 text-sm text-destructive">{message}</CardContent></Card>; }
