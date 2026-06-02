"use client";

import { Badge } from "@/components/ui/badge";

interface StatusBadgeProps {
  status: string;
}

const STATUS_STYLES: Record<string, { variant: "default" | "secondary" | "destructive" | "outline"; label: string }> = {
  queued: { variant: "outline", label: "Queued" },
  ingesting: { variant: "secondary", label: "Ingesting" },
  generating: { variant: "secondary", label: "Generating" },
  ready: { variant: "default", label: "Ready" },
  partial: { variant: "default", label: "Partial" },
  failed: { variant: "destructive", label: "Failed" },
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const style = STATUS_STYLES[status] || { variant: "outline" as const, label: status };
  return <Badge variant={style.variant}>{style.label}</Badge>;
}
