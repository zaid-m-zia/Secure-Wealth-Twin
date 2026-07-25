"use client";

import { motion } from "framer-motion";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/utils/cn";
import { MetricCard, TimelineItem } from "@/types/dashboard";

const metrics: MetricCard[] = [
  { label: "Financial health", value: "82 / 100", delta: "+4 this month", tone: "success" },
  { label: "Fraud posture", value: "Low risk", delta: "No critical alerts", tone: "primary" },
  { label: "Monthly spend", value: "$12,480", delta: "8% below budget", tone: "warning" },
  { label: "Account balance", value: "$64,290", delta: "+3.8% growth", tone: "muted" },
];

const chartData = [
  { month: "Jan", spending: 12, balance: 56 },
  { month: "Feb", spending: 15, balance: 58 },
  { month: "Mar", spending: 13, balance: 60 },
  { month: "Apr", spending: 17, balance: 59 },
  { month: "May", spending: 14, balance: 62 },
  { month: "Jun", spending: 16, balance: 64 },
];

const timeline: TimelineItem[] = [
  { title: "New salary deposit", detail: "Balance improved after recurring income landed.", time: "08:12" },
  { title: "Travel card swipe", detail: "Normal-sized purchase at a familiar merchant profile.", time: "11:34" },
  { title: "Savings transfer", detail: "Automated transfer preserved the monthly target.", time: "17:45" },
];

export default function DashboardPage() {
  return (
    <div className="space-y-8 pb-8">
      <section id="overview" className="grid gap-4 xl:grid-cols-4">
        {metrics.map((metric, index) => (
          <motion.div
            key={metric.label}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, delay: index * 0.05 }}
          >
            <Card>
              <CardHeader className="space-y-3">
                <div className="flex items-center justify-between gap-3">
                  <CardTitle className="text-base font-medium text-muted-foreground">{metric.label}</CardTitle>
                  <Badge className={cn(
                    metric.tone === "success" && "border-success/30 bg-success/10 text-success",
                    metric.tone === "primary" && "border-primary/30 bg-primary/10 text-primary",
                    metric.tone === "warning" && "border-warning/30 bg-warning/10 text-warning",
                    metric.tone === "muted" && "bg-muted text-muted-foreground",
                  )}>
                    {metric.delta}
                  </Badge>
                </div>
                <p className="text-3xl font-semibold tracking-tight">{metric.value}</p>
              </CardHeader>
            </Card>
          </motion.div>
        ))}
      </section>

      <section id="analytics" className="grid gap-6 lg:grid-cols-[1.4fr_0.8fr]">
        <Card className="min-h-[24rem]">
          <CardHeader>
            <CardTitle>Monthly activity</CardTitle>
            <CardDescription>Placeholder analytics view prepared for future transaction intelligence.</CardDescription>
          </CardHeader>
          <CardContent className="h-[18rem]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="spendingGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.45} />
                    <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.15} />
                <XAxis dataKey="month" tickLine={false} axisLine={false} />
                <YAxis tickLine={false} axisLine={false} />
                <Tooltip />
                <Area type="monotone" dataKey="spending" stroke="hsl(var(--primary))" fill="url(#spendingGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent activity</CardTitle>
            <CardDescription>Representative timeline while the data layer is still being prepared.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {timeline.map((item) => (
              <div key={item.title} className="rounded-2xl border border-border bg-muted/40 p-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-medium">{item.title}</p>
                  <span className="text-xs text-muted-foreground">{item.time}</span>
                </div>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">{item.detail}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <Card id="risk">
          <CardHeader>
            <CardTitle>Risk center</CardTitle>
            <CardDescription>Reserved for fraud and anomaly intelligence in the next build phase.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="rounded-[1.75rem] border border-border bg-gradient-to-br from-primary/10 via-transparent to-accent/20 p-6">
              <p className="text-sm uppercase tracking-[0.25em] text-muted-foreground">Foundation only</p>
              <p className="mt-3 text-lg font-semibold">Fraud, model scoring, and explainability will connect here later.</p>
              <p className="mt-2 text-sm leading-7 text-muted-foreground">
                The layout already reserves space for alert states, risk levels, confidence, and detailed reasoning.
              </p>
            </div>
          </CardContent>
        </Card>

        <Card id="recommendations">
          <CardHeader>
            <CardTitle>Recommendation panel</CardTitle>
            <CardDescription>Future advisor, planner, and goal modules will render into this area.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-border bg-muted/40 p-4">
              <p className="text-sm font-medium">Budget discipline</p>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">Placeholder guidance card for savings, planning, and optimization outputs.</p>
            </div>
            <div className="rounded-2xl border border-border bg-muted/40 p-4">
              <p className="text-sm font-medium">Goal progress</p>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">Reserved for milestone tracking and future financial coaching surfaces.</p>
            </div>
          </CardContent>
        </Card>
      </section>

      <section id="accounts" className="grid gap-6 lg:grid-cols-[1fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>Account summary</CardTitle>
            <CardDescription>Designed for balances, cards, and customer snapshots.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-2xl border border-border bg-muted/40 p-4">
                <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">Primary checking</p>
                <p className="mt-2 text-2xl font-semibold">$42,118</p>
              </div>
              <div className="rounded-2xl border border-border bg-muted/40 p-4">
                <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">Savings reserve</p>
                <p className="mt-2 text-2xl font-semibold">$22,172</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card id="spending">
          <CardHeader>
            <CardTitle>Spending focus</CardTitle>
            <CardDescription>Dedicated section for category breakdowns and trend analysis.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                ["Housing", "41%"],
                ["Transport", "12%"],
                ["Lifestyle", "21%"],
                ["Savings", "26%"],
              ].map(([label, value]) => (
                <div key={label} className="flex items-center justify-between rounded-2xl border border-border bg-muted/40 px-4 py-3">
                  <span className="text-sm font-medium">{label}</span>
                  <span className="text-sm text-muted-foreground">{value}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
