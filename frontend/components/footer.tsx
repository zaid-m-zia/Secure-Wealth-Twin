"use client";

import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t border-border/60 bg-background/80 px-4 py-6 backdrop-blur sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-7xl flex-col gap-3 text-sm text-muted-foreground sm:flex-row sm:items-center sm:justify-between">
        <p>SecureWealth AI foundation scaffold</p>
        <div className="flex items-center gap-4">
          <Link href="/login" className="transition-colors hover:text-foreground">
            Login
          </Link>
          <Link href="/register" className="transition-colors hover:text-foreground">
            Register
          </Link>
        </div>
      </div>
    </footer>
  );
}
