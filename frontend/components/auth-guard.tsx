"use client";

import { usePathname, useRouter } from "next/navigation";
import { ReactNode, useEffect, useState } from "react";

import { fetchProfile } from "@/services/auth";
import { clearAuthStorage, getAccessToken } from "@/utils/storage";

export function AuthGuard({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!getAccessToken()) {
      router.replace(`/login?next=${encodeURIComponent(pathname)}`);
      return;
    }
    fetchProfile().then(() => setReady(true)).catch(() => {
      clearAuthStorage();
      router.replace(`/login?next=${encodeURIComponent(pathname)}`);
    });
  }, [pathname, router]);

  if (!ready) return <div className="flex min-h-screen items-center justify-center text-sm text-muted-foreground">Restoring your secure session…</div>;
  return <>{children}</>;
}
