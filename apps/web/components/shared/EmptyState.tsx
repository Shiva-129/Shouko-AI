"use client";

import { Card, CardContent } from "@/components/ui/card";

interface EmptyStateProps {
  title: string;
  description: string;
  action?: React.ReactNode;
}

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <Card className="bg-card border-border">
      <CardContent className="flex flex-col items-center justify-center py-12 text-center">
        <p className="text-base font-semibold text-primaryText mb-1">{title}</p>
        <p className="text-sm text-secondaryText max-w-md mb-4">{description}</p>
        {action}
      </CardContent>
    </Card>
  );
}
