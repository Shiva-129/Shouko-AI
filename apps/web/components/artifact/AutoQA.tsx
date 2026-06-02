"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { ArtifactQAPair } from "@/lib/hooks/useArtifact";

interface AutoQAProps {
  qaPairs: ArtifactQAPair[];
}

const DIFFICULTY_COLORS: Record<string, string> = {
  EASY: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  MEDIUM: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  HARD: "bg-red-500/15 text-red-400 border-red-500/30",
};

export function AutoQA({ qaPairs }: AutoQAProps) {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  if (!qaPairs || qaPairs.length === 0) {
    return <p className="text-sm text-secondaryText">No Q&A pairs available.</p>;
  }

  return (
    <div className="space-y-2">
      {qaPairs.map((qa, i) => (
        <div key={i} className="bg-card border border-border rounded-lg overflow-hidden">
          <button
            className="w-full flex items-center justify-between p-4 text-left hover:bg-card/80 transition-colors"
            onClick={() => setOpenIndex(openIndex === i ? null : i)}
          >
            <div className="flex items-center gap-2 min-w-0">
              {openIndex === i ? (
                <ChevronDown className="h-4 w-4 shrink-0 text-secondaryText" />
              ) : (
                <ChevronRight className="h-4 w-4 shrink-0 text-secondaryText" />
              )}
              <span className="text-sm text-primaryText font-medium leading-snug">{qa.question}</span>
            </div>
            <Badge
              variant="outline"
              className={`shrink-0 ml-2 font-mono text-[10px] ${DIFFICULTY_COLORS[qa.difficulty] || ""}`}
            >
              {qa.difficulty}
            </Badge>
          </button>
          {openIndex === i && (
            <div className="px-4 pb-4 pt-0 border-t border-border/40">
              <p className="text-sm text-secondaryText leading-relaxed mt-3">{qa.answer}</p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
