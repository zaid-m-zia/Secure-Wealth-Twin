"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { logoutUser } from "@/services/auth";

export function Footer() {
  const router = useRouter();
  return (
    <footer className="border-t border-border/60 bg-background/80 px-4 py-6 backdrop-blur sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-7xl flex-col gap-3 text-sm text-muted-foreground sm:flex-row sm:items-center sm:justify-between">
        <p>SecureWealth AI · protected financial intelligence</p>
        <div className="flex items-center gap-4">
          <Link href="/settings" className="transition-colors hover:text-foreground">Profile</Link>
          <button onClick={() => logoutUser().finally(() => router.replace("/login"))} className="transition-colors hover:text-foreground">Logout</button>
        </div>
      </div>
    </footer>
  );
}
