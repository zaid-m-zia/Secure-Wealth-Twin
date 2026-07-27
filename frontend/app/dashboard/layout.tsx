import { ReactNode } from "react";

import { AppShell } from "@/components/app-shell";
import { AuthGuard } from "@/components/auth-guard";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <AuthGuard><AppShell title="Dashboard" description="Your financial safety and decision intelligence overview.">{children}</AppShell></AuthGuard>
  );
}
