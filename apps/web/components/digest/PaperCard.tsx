"use client";

import { useRouter } from "next/navigation";
import { FileText, Sparkles, Building2, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";

interface PaperCardProps {
  paper_id?: string;
  title: string;
  abstract: string;
  category: string;
  match_score: number;
  reason?: string;
}

function getScoreBadge(score: number): { bg: string; text: string } {
  if (score >= 85) return { bg: "bg-emerald-500/15 border-emerald-500/30", text: "text-emerald-400" };
  if (score >= 70) return { bg: "bg-blue-500/15 border-blue-500/30", text: "text-blue-400" };
  if (score >= 60) return { bg: "bg-amber-500/15 border-amber-500/30", text: "text-amber-400" };
  return { bg: "bg-slate-500/15 border-slate-500/30", text: "text-slate-400" };
}

const CATEGORY_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  "cs.AI": { bg: "bg-[#0D1525]", text: "text-blue", border: "border-blue/20" },
  "cs.CL": { bg: "bg-[#1A142D]", text: "text-violet", border: "border-violet/20" },
  "cs.LG": { bg: "bg-[#1A2400]", text: "text-lime", border: "border-lime/20" },
  "cs.CV": { bg: "bg-[#2D0D0D]", text: "text-coral", border: "border-coral/20" },
};

function getCategoryStyle(cat: string) {
  return CATEGORY_COLORS[cat] || { bg: "bg-[#141414]", text: "text-secondaryText", border: "border-border" };
}

export function PaperCard({ paper_id, title, abstract, category, match_score, reason }: PaperCardProps) {
  const router = useRouter();
  const score = getScoreBadge(match_score);
  const catStyle = getCategoryStyle(category);

  return (
    <div className="bg-card border border-border p-6 rounded-[12px] transition-all flex flex-col justify-between group hover:border-lime/30 select-none">
      <div>
        <div className="flex justify-end items-start mb-3">
          <span className={`font-mono text-[8px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider border ${score.bg} ${score.text} ${score.bg}`}>
            {match_score}% Match
          </span>
        </div>

        <h2 className="font-syne font-bold text-[15px] text-primaryText tracking-tight mb-2 group-hover:text-lime transition-colors leading-tight line-clamp-2">
          {title}
        </h2>

        <div className="flex flex-wrap gap-1.5 mb-4">
          <span className={`font-mono text-[8px] font-semibold px-2 py-0.5 rounded-md border uppercase tracking-wider ${catStyle.bg} ${catStyle.text} ${catStyle.border}`}>
            {category}
          </span>
          {reason && (
            <span className="font-mono text-[8px] text-secondaryText/60 px-2 py-0.5">
              {reason}
            </span>
          )}
        </div>

        {abstract && (
          <p className="text-[12.5px] text-secondaryText leading-relaxed mb-6 font-sans line-clamp-3">
            {abstract}
          </p>
        )}
      </div>

      <div className="flex items-center justify-between pt-4 border-t border-border/40 font-mono text-[10px] text-secondaryText tracking-wide">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5">
            <FileText className="h-3.5 w-3.5 text-secondaryText/80" />
            <span>{category}</span>
          </span>
        </div>

        <div className="flex items-center gap-2 select-none">
          <Button
            variant="ghost"
            className="font-mono text-[10px] text-secondaryText hover:text-white h-auto px-2 py-1"
            onClick={(e) => {
              e.stopPropagation();
            }}
          >
            <Sparkles className="h-3 w-3 mr-1" />
            Analyze
          </Button>
          {paper_id && (
            <Button
              className="font-mono text-[10px] bg-lime text-[#0D0D0D] hover:bg-lime/90 h-auto px-3 py-1 font-bold"
              onClick={(e) => {
                e.stopPropagation();
                router.push(`/artifact/${paper_id}`);
              }}
            >
              Create Artifact
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
