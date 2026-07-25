export interface MetricCard {
  label: string;
  value: string;
  delta: string;
  tone: "primary" | "success" | "warning" | "muted";
}

export interface TimelineItem {
  title: string;
  detail: string;
  time: string;
}
