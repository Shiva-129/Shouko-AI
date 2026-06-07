"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Sparkles, ArrowRight, FileText, MessageSquare, BookOpen, Loader2 } from "lucide-react";
import { useUser } from "@/lib/hooks/useUser";
import { useDigest } from "@/lib/hooks/useDigest";
import { PaperCard } from "@/components/digest/PaperCard";
import { UsageBanner } from "@/components/billing/UsageBanner";
import { apiClient } from "@/lib/api";

export default function DashboardPage() {
  const router = useRouter();
  const [arxivIdInput, setArxivIdInput] = useState("");
  const [ingesting, setIngesting] = useState(false);
  const [ingestError, setIngestError] = useState<string | null>(null);

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanId = arxivIdInput.trim();
    if (!cleanId) return;

    setIngesting(true);
    setIngestError(null);

    try {
      // 1. Ingest paper using the newly updated endpoint
      const paperRes = await apiClient.post<{ paper_id: string }>("/papers/ingest", {
        arxiv_id: cleanId,
      });

      // 2. Create artifact from the ingested paper
      const artifactRes = await apiClient.post<{ id: string }>("/artifacts", {
        paper_id: paperRes.paper_id,
      });

      // 3. Redirect to the newly generated artifact page
      router.push(`/artifact/${artifactRes.id}`);
    } catch (err: any) {
      console.error("Ingestion failed:", err);
      setIngestError(err.message || "Failed to ingest paper. Check ArXiv ID and try again.");
      setIngesting(false);
    }
  };

  const { data: profile, isLoading: profileLoading } = useUser();
  const today = new Date().toISOString().split("T")[0];
  const { data: digest, isLoading: digestLoading } = useDigest(today);

  const isLoading = profileLoading || digestLoading;

  if (isLoading) {
    return (
      <div className="p-8 space-y-6">
        <Skeleton className="h-8 w-48 bg-card" />
        <div className="grid grid-cols-3 gap-4">
          <Skeleton className="h-24 bg-card rounded-[12px]" />
          <Skeleton className="h-24 bg-card rounded-[12px]" />
          <Skeleton className="h-24 bg-card rounded-[12px]" />
        </div>
      </div>
    );
  }

  const usage = profile?.usage;
  let nearingLimitType = "";
  if (usage) {
    if (usage.artifact_created_limit && (usage.artifact_created_monthly / usage.artifact_created_limit) >= 0.8) {
      nearingLimitType = "Artifact Creation";
    } else if (usage.paper_ingested_limit && (usage.paper_ingested_monthly / usage.paper_ingested_limit) >= 0.8) {
      nearingLimitType = "Paper Ingestion";
    } else if (usage.question_asked_limit && (usage.question_asked_daily / usage.question_asked_limit) >= 0.8) {
      nearingLimitType = "Questions Asked";
    }
  }

  const topPapers = digest?.papers?.slice(0, 3) ?? [];

  return (
    <div className="flex-1 bg-workspace flex flex-col min-w-0 p-8 select-none">
      {nearingLimitType && <UsageBanner limitType={nearingLimitType} />}
      <h1 className="font-syne font-extrabold text-[32px] text-primaryText tracking-tight mb-6">
        Dashboard
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <Card className="bg-card border-border rounded-[12px]">
          <CardHeader className="pb-2 flex flex-row items-center gap-3">
            <FileText className="h-4 w-4 text-lime" />
            <CardTitle className="text-xs font-mono text-secondaryText uppercase tracking-wider">
              Artifacts This Month
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-primaryText">
              {profile?.usage?.artifact_created_monthly ?? 0}
              {profile?.usage?.artifact_created_limit != null && (
                <span className="text-sm text-secondaryText font-normal">
                  {" "}/ {profile.usage.artifact_created_limit}
                </span>
              )}
            </p>
          </CardContent>
        </Card>
        <Card className="bg-card border-border rounded-[12px]">
          <CardHeader className="pb-2 flex flex-row items-center gap-3">
            <MessageSquare className="h-4 w-4 text-lime" />
            <CardTitle className="text-xs font-mono text-secondaryText uppercase tracking-wider">
              Questions Today
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-primaryText">
              {profile?.usage?.question_asked_daily ?? 0}
              {profile?.usage?.question_asked_limit != null && (
                <span className="text-sm text-secondaryText font-normal">
                  {" "}/ {profile.usage.question_asked_limit}
                </span>
              )}
            </p>
          </CardContent>
        </Card>
        <Card className="bg-card border-border rounded-[12px]">
          <CardHeader className="pb-2 flex flex-row items-center gap-3">
            <BookOpen className="h-4 w-4 text-lime" />
            <CardTitle className="text-xs font-mono text-secondaryText uppercase tracking-wider">
              Papers Ingested
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-primaryText">
              {profile?.usage?.paper_ingested_monthly ?? 0}
              {profile?.usage?.paper_ingested_limit != null && (
                <span className="text-sm text-secondaryText font-normal">
                  {" "}/ {profile.usage.paper_ingested_limit}
                </span>
              )}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Ingest Card */}
      <Card className="bg-card border-border rounded-[12px] mb-8 overflow-hidden relative">
        <div className="absolute top-0 right-0 w-64 h-64 bg-lime/5 rounded-full blur-3xl pointer-events-none" />
        <CardHeader className="pb-3">
          <CardTitle className="text-sm text-primaryText font-syne font-bold flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-lime" />
            Ingest ArXiv Paper
          </CardTitle>
          <p className="text-xs text-secondaryText font-mono mt-1">
            Enter an ArXiv ID (e.g. 1706.03762) to download, parse, and generate an AI summary artifact.
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleIngest} className="flex gap-3 max-w-xl">
            <Input
              type="text"
              placeholder="e.g. 1706.03762"
              value={arxivIdInput}
              onChange={(e) => setArxivIdInput(e.target.value)}
              className="bg-canvas border-border text-sm text-primaryText placeholder:text-secondaryText font-mono flex-1 h-9"
              disabled={ingesting}
            />
            <Button
              type="submit"
              disabled={ingesting}
              className="bg-lime text-[#0D0D0D] hover:bg-lime/90 font-bold text-xs h-9 px-4 shrink-0"
            >
              {ingesting ? (
                <>
                  <Loader2 className="h-3 w-3 animate-spin mr-2" />
                  Ingesting...
                </>
              ) : (
                "Ingest & Analyze"
              )}
            </Button>
          </form>
          {ingestError && (
            <p className="text-[11px] text-red-400 font-mono mt-2">{ingestError}</p>
          )}
        </CardContent>
      </Card>

      <header className="flex flex-col shrink-0 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Sparkles className="h-5 w-5 text-lime" />
            <h2 className="font-syne font-bold text-xl text-primaryText tracking-tight">
              Today&apos;s Digest
            </h2>
          </div>
          {digest && (
            <Button
              variant="ghost"
              className="text-xs text-lime font-mono gap-1"
              onClick={() => router.push(`/digest/${today}`)}
            >
              View all <ArrowRight className="h-3 w-3" />
            </Button>
          )}
        </div>
        <div className="mt-4 border-b border-border pb-4" />
      </header>

      {topPapers.length > 0 ? (
        <div className="grid grid-cols-2 gap-6 items-start">
          <div className="flex flex-col gap-6">
            <PaperCard
              paper_id={topPapers[0].paper_id}
              title={topPapers[0].title}
              abstract={topPapers[0].abstract ?? ""}
              category={topPapers[0].category ?? "General"}
              match_score={topPapers[0].score}
              reason={topPapers[0].reason}
            />
            {topPapers.length > 2 && (
              <PaperCard
                paper_id={topPapers[2].paper_id}
                title={topPapers[2].title}
                abstract={topPapers[2].abstract ?? ""}
                category={topPapers[2].category ?? "General"}
                match_score={topPapers[2].score}
                reason={topPapers[2].reason}
              />
            )}
          </div>
          <div className="flex flex-col gap-6">
            {topPapers.length > 1 && (
              <PaperCard
                paper_id={topPapers[1].paper_id}
                title={topPapers[1].title}
                abstract={topPapers[1].abstract ?? ""}
                category={topPapers[1].category ?? "General"}
                match_score={topPapers[1].score}
                reason={topPapers[1].reason}
              />
            )}
          </div>
        </div>
      ) : (
        <Card className="bg-card border-border rounded-[12px]">
          <CardContent className="p-8 text-center">
            <Sparkles className="h-8 w-8 text-secondaryText/40 mx-auto mb-3" />
            <p className="text-secondaryText text-sm">
              Your daily research recommendations will appear here once the
              discovery agent is running.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
