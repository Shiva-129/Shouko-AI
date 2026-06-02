"use client";

import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Sparkles, ArrowRight, FileText, MessageSquare, BookOpen } from "lucide-react";
import { useUser } from "@/lib/hooks/useUser";
import { useDigest } from "@/lib/hooks/useDigest";
import { PaperCard } from "@/components/digest/PaperCard";

export default function DashboardPage() {
  const router = useRouter();
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

  const topPapers = digest?.papers?.slice(0, 3) ?? [];

  return (
    <div className="flex-1 bg-workspace flex flex-col min-w-0 p-8 select-none">
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

      <header className="flex flex-col shrink-0 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Sparkles className="h-5 w-5 text-lime" />
            <h2 className="font-syne font-bold text-xl text-primaryText tracking-tight">
              Today's Digest
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
