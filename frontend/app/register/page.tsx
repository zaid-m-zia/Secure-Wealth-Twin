"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { ArrowRight, ShieldPlus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { registerUser } from "@/services/auth";

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await registerUser({ full_name: fullName, email, password });
      router.push("/dashboard");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to create an account right now.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid min-h-screen lg:grid-cols-[1fr_1fr]">
      <section className="flex items-center justify-center px-4 py-12 sm:px-6 lg:px-10">
        <div className="w-full max-w-md">
          <Link href="/" className="inline-flex items-center gap-2 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground">
            <ShieldPlus className="h-4 w-4 text-primary" />
            SecureWealth AI
          </Link>
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Create your account</CardTitle>
              <CardDescription>Set up the foundation workspace and continue into the platform shell.</CardDescription>
            </CardHeader>
            <CardContent>
              <form className="space-y-5" onSubmit={handleSubmit}>
                <div className="space-y-2">
                  <Label htmlFor="fullName">Full name</Label>
                  <Input id="fullName" value={fullName} onChange={(event) => setFullName(event.target.value)} placeholder="Alex Morgan" required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input id="password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Create a strong password" required />
                </div>
                {error ? <p className="text-sm text-destructive">{error}</p> : null}
                <Button type="submit" className="w-full gap-2" disabled={loading}>
                  {loading ? "Creating account..." : "Create account"}
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </section>
      <section className="hidden bg-gradient-to-br from-accent/30 via-card to-primary/15 p-10 lg:flex lg:flex-col lg:justify-between">
        <div className="max-w-xl">
          <p className="text-xs uppercase tracking-[0.3em] text-muted-foreground">Foundation onboarding</p>
          <h1 className="mt-4 text-4xl font-semibold tracking-tight">A registration flow that fits a fintech product.</h1>
          <p className="mt-4 text-sm leading-7 text-muted-foreground">
            The UI is intentionally calm and premium so the future analytics, assistant, and risk workflows can build on top of it cleanly.
          </p>
        </div>
        <div className="rounded-[2rem] border border-border bg-card/80 p-6 shadow-soft backdrop-blur">
          <p className="text-sm font-medium">Next step</p>
          <p className="mt-2 text-sm leading-7 text-muted-foreground">
            Once accounts are persisted in later builds, this same shell can support onboarding, role selection, and policy acceptance.
          </p>
        </div>
      </section>
    </div>
  );
}
