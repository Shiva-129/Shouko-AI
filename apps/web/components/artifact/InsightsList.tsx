"use client";

import { Badge } from "@/components/ui/badge";
import type { ArtifactInsight } from "@/lib/hooks/useArtifact";

interface InsightsListProps {
  insights: ArtifactInsight[];
}

function getScoreColor(score: number): string {
  if (score >= 8) return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
  if (score >= 5) return "bg-blue-500/15 text-blue-400 border-blue-500/30";
  return "bg-slate-500/15 text-slate-400 border-slate-500/30";
}

export function InsightsList({ insights }: InsightsListProps) {
  if (!insights || insights.length === 0) {
    return <p className="text-sm text-secondaryText">No insights available.</p>;
  }

  return (
    <div className="space-y-3">
      {insights.map((insight, i) => (
        <div key={i} className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-start justify-between gap-3 mb-2">
            <p className="text-sm text-primaryText leading-relaxed">{insight.insight}</p>
            <span
              className={`shrink-0 font-mono text-[10px] font-bold px-2 py-0.5 rounded-full border ${getScoreColor(insight.importance_score)}`}
            >
              {insight.importance_score}/10
            </span>
          </div>
          {insight.section && (
            <Badge variant="outline" className="text-[10px] font-mono text-secondaryText">
              {insight.section}
            </Badge>
          )}
        </div>
      ))}
    </div>
  );
}
