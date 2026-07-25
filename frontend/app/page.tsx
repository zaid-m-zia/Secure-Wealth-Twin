"use client";

import Link from "next/link";

import { ArrowRight, BadgeCheck, BrainCircuit, ShieldCheck, Sparkles, TrendingUp } from "lucide-react";
import { motion } from "framer-motion";

import { Navigation } from "@/components/navigation";
import { Footer } from "@/components/footer";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const highlights = [
  {
    title: "Behavioral intelligence",
    description: "A clean foundation for customer behavior profiling, transaction context, and future AI orchestration.",
    icon: BrainCircuit,
  },
  {
    title: "Security first",
    description: "JWT structure, password hashing utilities, structured error payloads, and request tracing are in place.",
    icon: ShieldCheck,
  },
  {
    title: "Deployment ready",
    description: "Docker, Compose, environment templates, and app bootstrapping are organized for the next phase.",
    icon: TrendingUp,
  },
];

const metrics = [
  { label: "API shell", value: "FastAPI", detail: "Versioned routing and health checks" },
  { label: "Web shell", value: "Next.js 15", detail: "App router, Tailwind, and motion" },
  { label: "Data layer", value: "PostgreSQL", detail: "Session factory and Alembic scaffold" },
  { label: "Security", value: "JWT + PBKDF2", detail: "Foundation-only auth utilities" },
];

export default function HomePage() {
  return (
    <div className="min-h-screen">
      <Navigation />
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <section className="overflow-hidden rounded-[2rem] border border-border/70 bg-card/80 p-8 shadow-soft backdrop-blur lg:p-12">
          <div className="grid gap-10 lg:grid-cols-[1.2fr_0.8fr] lg:items-center">
            <motion.div
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.55 }}
            >
              <Badge>Enterprise fintech foundation</Badge>
              <h1 className="mt-5 max-w-3xl text-4xl font-semibold tracking-tight text-balance sm:text-5xl lg:text-6xl">
                SecureWealth AI is a premium foundation for financial safety and decision intelligence.
              </h1>
              <p className="mt-6 max-w-2xl text-base leading-7 text-muted-foreground sm:text-lg">
                The current build establishes the production-grade scaffold for authentication, API routing,
                configuration, logging, database connectivity, and a polished frontend shell. Later builds plug
                in ML, AI, recommendation, and wealth-twin engines on top of this base.
              </p>
              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Button asChild>
                  <Link href="/register" className="inline-flex items-center gap-2">
                    Start the foundation
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </Button>
                <Button asChild variant="outline">
                  <Link href="/dashboard">View dashboard shell</Link>
                </Button>
              </div>
              <div className="mt-8 flex flex-wrap gap-3 text-sm text-muted-foreground">
                <span className="inline-flex items-center gap-2 rounded-full border border-border bg-background px-3 py-2">
                  <BadgeCheck className="h-4 w-4 text-success" />
                  Backend starts
                </span>
                <span className="inline-flex items-center gap-2 rounded-full border border-border bg-background px-3 py-2">
                  <BadgeCheck className="h-4 w-4 text-success" />
                  Frontend scaffolded
                </span>
                <span className="inline-flex items-center gap-2 rounded-full border border-border bg-background px-3 py-2">
                  <BadgeCheck className="h-4 w-4 text-success" />
                  Docker ready
                </span>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="relative"
            >
              <div className="absolute -inset-6 rounded-[2rem] bg-gradient-to-br from-primary/20 via-transparent to-accent/30 blur-2xl" />
              <Card className="relative border-white/30 bg-white/85 dark:bg-card/90">
                <CardHeader>
                  <CardTitle>Foundation status</CardTitle>
                  <CardDescription>Current build focuses on platform readiness, not model inference.</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4">
                    {metrics.map((metric) => (
                      <div key={metric.label} className="rounded-2xl border border-border bg-muted/50 p-4">
                        <p className="text-xs uppercase tracking-[0.22em] text-muted-foreground">{metric.label}</p>
                        <p className="mt-2 text-xl font-semibold">{metric.value}</p>
                        <p className="mt-1 text-sm text-muted-foreground">{metric.detail}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </section>

        <section id="overview" className="mt-10 grid gap-6 lg:grid-cols-3">
          {highlights.map((item, index) => {
            const Icon = item.icon;
            return (
              <motion.div
                key={item.title}
                initial={{ opacity: 0, y: 14 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, amount: 0.2 }}
                transition={{ duration: 0.45, delay: index * 0.08 }}
              >
                <Card className="h-full">
                  <CardHeader>
                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
                      <Icon className="h-5 w-5" />
                    </div>
                    <CardTitle>{item.title}</CardTitle>
                    <CardDescription>{item.description}</CardDescription>
                  </CardHeader>
                </Card>
              </motion.div>
            );
          })}
        </section>

        <section id="architecture" className="mt-10 grid gap-6 rounded-[2rem] border border-border/70 bg-card/70 p-6 backdrop-blur lg:grid-cols-[1fr_1fr] lg:p-8">
          <div>
            <Badge>Architecture</Badge>
            <h2 className="mt-4 text-2xl font-semibold tracking-tight">A clean foundation for the future platform.</h2>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-muted-foreground">
              The structure is intentionally modular so later phases can add ML pipelines, agent orchestration,
              report generation, and domain intelligence without disrupting the foundation layer.
            </p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <Card>
              <CardTitle>FastAPI backend</CardTitle>
              <CardDescription className="mt-2">Configuration, middleware, versioned routing, and dependency injection.</CardDescription>
            </Card>
            <Card>
              <CardTitle>Next.js frontend</CardTitle>
              <CardDescription className="mt-2">Landing page, dashboard shell, auth pages, theme support, and responsive layout.</CardDescription>
            </Card>
          </div>
        </section>

        <section id="setup" className="mt-10 rounded-[2rem] border border-border/70 bg-gradient-to-br from-primary/10 via-card/70 to-accent/20 p-6 lg:p-8">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <Badge>Local setup</Badge>
              <h2 className="mt-4 text-2xl font-semibold tracking-tight">Everything needed for the next build phase is organized.</h2>
              <p className="mt-3 max-w-3xl text-sm leading-7 text-muted-foreground">
                Environment templates, Dockerfiles, Compose, Alembic structure, and the base API contract are in place.
                That makes it straightforward to begin persistence and then layer intelligence modules on top.
              </p>
            </div>
            <div className="flex gap-3">
              <Button asChild variant="outline">
                <Link href="/login">Login</Link>
              </Button>
              <Button asChild>
                <Link href="/register">Register</Link>
              </Button>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
