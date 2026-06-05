"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useRef } from "react";
import { ArrowLeft, ExternalLink, Sparkles, MessageSquare, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
import { StatusBadge } from "@/components/artifact/StatusBadge";
import { InsightsList } from "@/components/artifact/InsightsList";
import { AutoQA } from "@/components/artifact/AutoQA";
import { SuggestedExperiments } from "@/components/artifact/SuggestedExperiments";
import { AnnotationsTab } from "@/components/artifact/AnnotationsTab";
import { useArtifact } from "@/lib/hooks/useArtifact";
import { useSSEChat } from "@/lib/hooks/useSSEChat";
import { EmptyState } from "@/components/shared/EmptyState";
import { ChatPanel } from "@/components/chat/ChatPanel";

const STATUS_MESSAGES: Record<string, string> = {
  queued: "Queued for processing...",
  ingesting: "Reading and chunking the PDF...",
  generating: "Generating artifact with AI...",
};

export default function ArtifactPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  const { data: artifact, isLoading, error, refetch } = useArtifact(id);
  const { messages, isStreaming, sendMessage } = useSSEChat([]);

  const isProcessing = artifact && ["queued", "ingesting", "generating"].includes(artifact.status);

  useEffect(() => {
    if (isProcessing) {
      const interval = setInterval(() => refetch(), 2000);
      return () => clearInterval(interval);
    }
  }, [isProcessing, refetch]);

  if (error) {
    return (
      <div className="p-8 max-w-5xl">
        <EmptyState
          title="Artifact not found"
          description="This artifact doesn't exist or you don't have access to it."
          action={
            <Button variant="outline" size="sm" onClick={() => router.push("/library")}>
              Go to Library
            </Button>
          }
        />
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="p-8 max-w-5xl space-y-6">
        <Skeleton className="h-8 w-64 bg-card" />
        <Skeleton className="h-4 w-96 bg-card" />
        <div className="flex gap-6 mt-8">
          <div className="flex-1 space-y-4">
            <Skeleton className="h-10 w-80 bg-card" />
            <Skeleton className="h-40 bg-card rounded-lg" />
            <Skeleton className="h-40 bg-card rounded-lg" />
          </div>
          <Skeleton className="w-80 h-96 bg-card rounded-lg" />
        </div>
      </div>
    );
  }

  if (isProcessing) {
    return (
      <div className="p-8 max-w-3xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <Sparkles className="h-5 w-5 text-lime animate-pulse" />
          <div>
            <h1 className="font-syne font-bold text-xl text-primaryText">
              {STATUS_MESSAGES[artifact.status] || "Processing..."}
            </h1>
            <p className="text-xs text-secondaryText font-mono mt-1">
              {artifact.paper_title || "Paper"}
            </p>
          </div>
          <StatusBadge status={artifact.status} />
        </div>
        <Progress value={artifact.status === "queued" ? 10 : artifact.status === "ingesting" ? 40 : 70} className="mb-4" />
        <Card className="bg-card border-border">
          <CardContent className="flex items-center justify-center py-8 text-secondaryText text-sm">
            <Sparkles className="h-4 w-4 mr-2 text-lime animate-spin" />
            This usually takes about 1-2 minutes. The page will update automatically.
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!artifact) return null;

  return (
    <div className="flex h-full">
      <div className="flex-1 overflow-y-auto p-8 pb-4">
        <button
          className="flex items-center gap-1.5 text-xs text-secondaryText hover:text-primaryText mb-4 transition-colors"
          onClick={() => router.back()}
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          Back
        </button>

        <div className="flex items-start justify-between gap-4 mb-1">
          <h1 className="font-syne font-extrabold text-[24px] text-primaryText tracking-tight leading-tight">
            {artifact.paper_title || "Artifact"}
          </h1>
          <StatusBadge status={artifact.status} />
        </div>

        {artifact.one_line_summary && (
          <p className="text-sm text-secondaryText font-mono mt-2 mb-6 italic">
            {artifact.one_line_summary}
          </p>
        )}

        {artifact.error_message && (
          <Card className="bg-red-500/10 border-red-500/30 mb-6">
            <CardContent className="p-4 flex items-center justify-between">
              <p className="text-sm text-red-400">{artifact.error_message}</p>
              <Button
                variant="outline"
                size="sm"
                className="gap-1"
                onClick={() => {
                  fetch(`/api/artifacts/${id}/retry`, { method: "POST" });
                }}
              >
                <RotateCcw className="h-3 w-3" />
                Retry
              </Button>
            </CardContent>
          </Card>
        )}

        <div className="flex gap-6 mt-6">
          <div className="flex-1 min-w-0">
            <Tabs defaultValue="summary">
              <TabsList className="mb-4">
                <TabsTrigger value="summary">Summary</TabsTrigger>
                <TabsTrigger value="insights">Insights</TabsTrigger>
                <TabsTrigger value="qa">Q&A</TabsTrigger>
                <TabsTrigger value="experiments">Experiments</TabsTrigger>
                <TabsTrigger value="annotations">Notes & Highlights</TabsTrigger>
              </TabsList>

              <TabsContent value="summary">
                {artifact.summary ? (
                   <div className="prose prose-sm prose-invert max-w-none">
                    <p className="text-sm text-primaryText leading-relaxed whitespace-pre-line">
                      {artifact.summary}
                    </p>
                  </div>
                ) : (
                  <p className="text-sm text-secondaryText">No summary available.</p>
                )}
              </TabsContent>

              <TabsContent value="insights">
                <InsightsList insights={artifact.key_insights || []} />
              </TabsContent>

              <TabsContent value="qa">
                <AutoQA qaPairs={artifact.auto_qa || []} />
              </TabsContent>

              <TabsContent value="experiments">
                <SuggestedExperiments experiments={artifact.suggested_experiments || []} />
              </TabsContent>

              <TabsContent value="annotations">
                <AnnotationsTab artifactId={id} />
              </TabsContent>
            </Tabs>
          </div>

          <div className="w-80 shrink-0">
            <div className="sticky top-0">
              <ChatPanel
                artifactId={id}
                messages={messages}
                isStreaming={isStreaming}
                sendMessage={sendMessage}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
