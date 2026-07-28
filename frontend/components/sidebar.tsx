"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import {
  BarChart3,
  BrainCircuit,
  Building2,
  CircleDollarSign,
  LayoutDashboard,
  ShieldAlert,
  Sparkles,
  WalletCards,
  ReceiptText,
  Settings,
} from "lucide-react";

import { cn } from "@/utils/cn";

const sidebarItems = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Accounts", href: "/customers", icon: Building2 },
  { label: "Money", href: "/transactions", icon: ReceiptText },
  { label: "Security", href: "/fraud", icon: ShieldAlert },
  { label: "Financial Health", href: "/wealth", icon: WalletCards },
  { label: "Recommendations", href: "/recommendations", icon: Sparkles },
  { label: "Assistant", href: "/agentic-ai", icon: BrainCircuit },
  { label: "Analytics", href: "/analytics", icon: BarChart3 },
  { label: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-72 border-r border-border/60 bg-card/70 px-5 py-6 backdrop-blur lg:flex lg:flex-col">
      <div className="mb-8 rounded-3xl border border-border bg-gradient-to-br from-primary/15 via-primary/5 to-accent/20 p-5 shadow-soft">
        <p className="text-xs uppercase tracking-[0.3em] text-muted-foreground">Control Center</p>
        <div className="mt-3 flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-soft">
            <ShieldAlert className="h-5 w-5" />
          </div>
          <div>
            <p className="font-semibold">SecureWealth AI</p>
            <p className="text-sm text-muted-foreground">Financial intelligence</p>
          </div>
        </div>
      </div>
      <nav className="space-y-2">
        {sidebarItems.map((item) => {
          const Icon = item.icon;
          const active = pathname === item.href;
          return (
            <Link
              key={item.label}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition-colors",
                active ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-muted hover:text-foreground",
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="mt-auto rounded-3xl border border-border bg-muted/50 p-5">
        <p className="text-xs uppercase tracking-[0.3em] text-muted-foreground">Secure workspace</p>
        <p className="mt-2 text-sm text-muted-foreground">
          Live platform data is protected by your authenticated session.
        </p>
      </div>
    </aside>
  );
}
