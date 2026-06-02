"use client";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Beaker } from "lucide-react";
import type { ArtifactExperiment } from "@/lib/hooks/useArtifact";

interface SuggestedExperimentsProps {
  experiments: ArtifactExperiment[];
}

const FEASIBILITY_COLORS: Record<string, string> = {
  EASY: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  MEDIUM: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  HARD: "bg-red-500/15 text-red-400 border-red-500/30",
};

export function SuggestedExperiments({ experiments }: SuggestedExperimentsProps) {
  if (!experiments || experiments.length === 0) {
    return <p className="text-sm text-secondaryText">No suggested experiments available.</p>;
  }

  return (
    <div className="space-y-4">
      {experiments.map((exp, i) => (
        <Card key={i} className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-start justify-between gap-3 mb-2">
              <div className="flex items-center gap-2">
                <Beaker className="h-4 w-4 text-lime" />
                <h3 className="text-sm font-semibold text-primaryText">{exp.title}</h3>
              </div>
              <Badge
                variant="outline"
                className={`shrink-0 font-mono text-[10px] ${FEASIBILITY_COLORS[exp.feasibility] || ""}`}
              >
                {exp.feasibility}
              </Badge>
            </div>
            <p className="text-sm text-secondaryText leading-relaxed">{exp.description}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
