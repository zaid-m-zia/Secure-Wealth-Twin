"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { ArrowRight, ShieldCheck } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { loginUser } from "@/services/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await loginUser({ email, password });
      const nextPath = typeof window === "undefined" ? null : new URLSearchParams(window.location.search).get("next");
      router.push(nextPath?.startsWith("/") ? nextPath : "/dashboard");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to sign in right now.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid min-h-screen lg:grid-cols-[1fr_1fr]">
      <section className="flex items-center justify-center px-4 py-12 sm:px-6 lg:px-10">
        <div className="w-full max-w-md">
          <Link href="/" className="inline-flex items-center gap-2 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground">
            <ShieldCheck className="h-4 w-4 text-primary" />
            SecureWealth AI
          </Link>
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Welcome back</CardTitle>
              <CardDescription>Sign in to continue into the financial intelligence workspace.</CardDescription>
            </CardHeader>
            <CardContent>
              <form className="space-y-5" onSubmit={handleSubmit}>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input id="password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="••••••••" minLength={8} required />
                </div>
                {error ? <p className="text-sm text-destructive">{error}</p> : null}
                <Button type="submit" className="w-full gap-2" disabled={loading}>
                  {loading ? "Signing in..." : "Sign in"}
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </section>
      <section className="hidden bg-gradient-to-br from-primary/15 via-card to-accent/25 p-10 lg:flex lg:flex-col lg:justify-between">
        <div className="max-w-xl">
          <p className="text-xs uppercase tracking-[0.3em] text-muted-foreground">Secure access</p>
          <h1 className="mt-4 text-4xl font-semibold tracking-tight">A calm, premium entry point for the platform.</h1>
          <p className="mt-4 text-sm leading-7 text-muted-foreground">
            The foundation keeps the authentication flow intentionally simple for now while the backend services,
            database model, and security controls continue to evolve in later builds.
          </p>
        </div>
        <div className="rounded-[2rem] border border-border bg-card/80 p-6 shadow-soft backdrop-blur">
          <p className="text-sm font-medium">Built for the next phases</p>
          <p className="mt-2 text-sm leading-7 text-muted-foreground">
            The login surface is fully wired to the foundation backend and can be extended without changing the page layout.
          </p>
        </div>
      </section>
    </div>
  );
}
