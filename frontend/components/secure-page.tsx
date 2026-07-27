"use client";
import { ReactNode } from "react";
import { AppShell } from "@/components/app-shell";
import { AuthGuard } from "@/components/auth-guard";
export function SecurePage({ title, description, children }: { title: string; description: string; children: ReactNode }) { return <AuthGuard><AppShell title={title} description={description}>{children}</AppShell></AuthGuard>; }
