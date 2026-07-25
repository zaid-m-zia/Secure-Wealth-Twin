import { ReactNode } from "react";

import { AppShell } from "@/components/app-shell";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <AppShell
      title="Dashboard"
      description="A polished foundation shell for the future fraud, wealth, and recommendation modules."
    >
      {children}
    </AppShell>
  );
}
