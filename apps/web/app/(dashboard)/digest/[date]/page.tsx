"use client";

import { useParams, useRouter } from "next/navigation";
import { useMemo } from "react";
import { ChevronLeft, ChevronRight, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/shared/EmptyState";
import { PaperCard } from "@/components/digest/PaperCard";
import { useDigest } from "@/lib/hooks/useDigest";
import type { ScoredPaper } from "@/types";

function shiftDate(dateStr: string, delta: number): string {
  const d = new Date(dateStr + "T00:00:00");
  d.setDate(d.getDate() + delta);
  return d.toISOString().split("T")[0];
}

export default function DigestDatePage() {
  const params = useParams();
  const router = useRouter();
  const date = params.date as string;
  const { data: digest, isLoading, error } = useDigest(date);

  const prevDate = shiftDate(date, -1);
  const nextDate = shiftDate(date, 1);
  const today = new Date().toISOString().split("T")[0];
  const isToday = date === today;

  const { leftCol, rightCol } = useMemo(() => {
    if (!digest?.papers) return { leftCol: [] as ScoredPaper[], rightCol: [] as ScoredPaper[] };
    const papers = [...digest.papers].sort((a, b) => b.score - a.score);
    return {
      leftCol: papers.filter((_, i) => i % 2 === 0),
      rightCol: papers.filter((_, i) => i % 2 === 1),
    };
  }, [digest]);

  return (
    <div className="flex-1 bg-workspace flex flex-col min-w-0 p-8 select-none">
      <header className="flex flex-col shrink-0 mb-6">
        <div className="flex items-center justify-between">
          <h1 className="font-syne font-extrabold text-[32px] text-primaryText tracking-tight">
            Today's Digest
          </h1>
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => router.push(`/digest/${prevDate}`)}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => router.push(`/digest/${nextDate}`)}
              disabled={isToday}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
        <p className="text-xs text-secondaryText font-mono mt-1">{date}</p>

        {digest && digest.papers.length > 0 && (
          <div className="flex items-center mt-4 border-b border-border pb-4">
            <div className="flex gap-2 items-center">
              <Sparkles className="h-3.5 w-3.5 text-lime" />
              <span className="text-xs text-secondaryText font-mono">
                {digest.paper_count} paper{digest.paper_count !== 1 ? "s" : ""} &middot; {digest.status}
              </span>
            </div>
          </div>
        )}
      </header>

      {isLoading && (
        <div className="grid grid-cols-2 gap-6">
          <div className="flex flex-col gap-6">
            {Array.from({ length: 2 }).map((_, i) => (
              <Skeleton key={i} className="h-48 bg-card rounded-[12px]" />
            ))}
          </div>
          <div className="flex flex-col gap-6">
            {Array.from({ length: 2 }).map((_, i) => (
              <Skeleton key={i} className="h-56 bg-card rounded-[12px]" />
            ))}
          </div>
        </div>
      )}

      {error && (
        <EmptyState
          title="No digest for this date"
          description="The discovery agent hasn't generated recommendations for this date yet. It runs daily at 6 AM UTC."
        />
      )}

      {digest && digest.papers.length === 0 && (
        <EmptyState
          title="No matching papers"
          description="No papers matched your interest profile on this date. Try adding more topics or keywords in Settings."
        />
      )}

      {digest && digest.papers.length > 0 && (
        <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
          <div className="grid grid-cols-2 gap-6 pb-6 items-start">
            <div className="flex flex-col gap-6">
              {leftCol.map((scored) => (
                <PaperCard
                  key={scored.paper_id}
                  paper_id={scored.paper_id}
                  title={scored.title}
                  abstract={scored.abstract ?? ""}
                  category={scored.category ?? "General"}
                  match_score={scored.score}
                  reason={scored.reason}
                />
              ))}
            </div>
            <div className="flex flex-col gap-6">
              {rightCol.map((scored) => (
                <PaperCard
                  key={scored.paper_id}
                  paper_id={scored.paper_id}
                  title={scored.title}
                  abstract={scored.abstract ?? ""}
                  category={scored.category ?? "General"}
                  match_score={scored.score}
                  reason={scored.reason}
                />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
