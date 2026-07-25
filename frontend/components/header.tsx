"use client";

import { Bell, Search } from "lucide-react";

import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/theme-toggle";

interface HeaderProps {
  title: string;
  description: string;
}

export function Header({ title, description }: HeaderProps) {
  return (
    <header className="flex flex-col gap-4 border-b border-border/60 bg-card/70 px-5 py-5 backdrop-blur sm:flex-row sm:items-center sm:justify-between lg:px-8">
      <div>
        <p className="text-xs uppercase tracking-[0.28em] text-muted-foreground">SecureWealth AI</p>
        <h1 className="mt-1 text-2xl font-semibold tracking-tight">{title}</h1>
        <p className="mt-1 max-w-2xl text-sm text-muted-foreground">{description}</p>
      </div>
      <div className="flex items-center gap-3">
        <Button variant="outline" size="sm" className="hidden gap-2 md:inline-flex">
          <Search className="h-4 w-4" />
          Search
        </Button>
        <Button variant="outline" size="sm" className="gap-2">
          <Bell className="h-4 w-4" />
          Alerts
        </Button>
        <ThemeToggle />
      </div>
    </header>
  );
}
