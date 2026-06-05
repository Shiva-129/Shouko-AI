"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/shared/EmptyState";
import { apiClient } from "@/lib/api";
import { useState } from "react";
import { BookOpen, Search, Sparkles, FolderPlus, Loader2, Check } from "lucide-react";

interface ArtifactListItem {
  id: string;
  paper_id: string;
  paper_title?: string;
  one_line_summary?: string;
  status: string;
  created_at: string;
}

interface ArtifactListResponse {
  artifacts: ArtifactListItem[];
  total: number;
}

type Collection = {
  id: string;
  name: string;
  artifact_ids: string[];
};

const STATUS_STYLES: Record<string, { bg: string; text: string }> = {
  queued: { bg: "bg-slate-500/15", text: "text-slate-400" },
  ingesting: { bg: "bg-blue-500/15", text: "text-blue-400" },
  generating: { bg: "bg-violet-500/15", text: "text-violet-400" },
  ready: { bg: "bg-emerald-500/15", text: "text-emerald-400" },
  partial: { bg: "bg-amber-500/15", text: "text-amber-400" },
  failed: { bg: "bg-red-500/15", text: "text-red-400" },
};

export default function LibraryPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [activeArtifactId, setActiveArtifactId] = useState<string | null>(null);

  // Queries
  const { data: response, isLoading } = useQuery<ArtifactListResponse>({
    queryKey: ["artifacts", search],
    queryFn: () => apiClient.get(`/artifacts?search=${encodeURIComponent(search)}`),
    staleTime: 10 * 1000,
    retry: false,
  });

  const { data: collections = [] } = useQuery<Collection[]>({
    queryKey: ["collections"],
    queryFn: () => apiClient.get("/collections"),
  });

  // Mutation
  const addToCollectionMutation = useMutation({
    mutationFn: ({ colId, artId }: { colId: string; artId: string }) =>
      apiClient.post(`/collections/${colId}/artifacts`, { artifact_id: artId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["collections"] });
      setActiveArtifactId(null);
    },
  });

  const artifacts = response?.artifacts || [];

  return (
    <div className="flex-1 bg-workspace flex flex-col min-w-0 p-8 select-none">
      <h1 className="font-syne font-extrabold text-[32px] text-primaryText tracking-tight mb-6">
        My Library
      </h1>

      <div className="relative mb-6 max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondaryText" />
        <Input
          placeholder="Search artifacts..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9 bg-card border-border text-sm text-primaryText placeholder:text-secondaryText"
        />
      </div>

      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-32 bg-card rounded-lg" />
          ))}
        </div>
      )}

      {!isLoading && artifacts.length === 0 && (
        <EmptyState
          title="No artifacts yet"
          description="Ingest a paper and create your first artifact to see it here."
          action={
            <span className="text-xs text-secondaryText/60 flex items-center gap-1.5 mt-2">
              <BookOpen className="h-3.5 w-3.5" />
              Go to Dashboard to get started
            </span>
          }
        />
      )}

      {!isLoading && artifacts.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {artifacts.map((artifact) => {
            const style = STATUS_STYLES[artifact.status] || { bg: "bg-slate-500/15", text: "text-slate-400" };
            const isAdding = activeArtifactId === artifact.id;

            return (
              <Card
                key={artifact.id}
                className="bg-card border-border cursor-pointer hover:border-lime/30 transition-colors flex flex-col justify-between"
                onClick={() => router.push(`/artifact/${artifact.id}`)}
              >
                <CardContent className="p-4 flex-1 flex flex-col justify-between">
                  <div>
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <h3 className="text-sm font-semibold text-primaryText leading-snug line-clamp-2">
                        {artifact.paper_title || "Untitled"}
                      </h3>
                      <Badge
                        variant="outline"
                        className={`font-mono text-[10px] shrink-0 ${style.bg} ${style.text}`}
                      >
                        {artifact.status === "ready" && <Sparkles className="h-2.5 w-2.5 mr-1" />}
                        {artifact.status}
                      </Badge>
                    </div>
                    {artifact.one_line_summary && (
                      <p className="text-[11px] text-secondaryText leading-relaxed line-clamp-2 mb-2">
                        {artifact.one_line_summary}
                      </p>
                    )}
                  </div>
                  
                  <div className="flex items-center justify-between mt-4 pt-3 border-t border-border/40 text-[10px] text-secondaryText/60 font-mono">
                    <span>
                      {artifact.created_at ? new Date(artifact.created_at).toLocaleDateString() : ""}
                    </span>
                    
                    {/* Add to Collection Widget */}
                    <div className="relative" onClick={(e) => e.stopPropagation()}>
                      <button
                        onClick={() => setActiveArtifactId(isAdding ? null : artifact.id)}
                        className="flex items-center gap-1 hover:text-lime transition-colors"
                      >
                        <FolderPlus className="h-3.5 w-3.5" />
                        <span>Organize</span>
                      </button>

                      {isAdding && (
                        <div className="absolute right-0 bottom-6 bg-[#0E1117] border border-border rounded-lg shadow-xl z-20 w-48 p-1.5 space-y-1">
                          <p className="text-[9px] font-bold text-secondaryText/75 px-2 py-1 border-b border-border/40 font-sans">
                            Add to Collection
                          </p>
                          {collections.length === 0 ? (
                            <button
                              onClick={() => router.push("/collections")}
                              className="w-full text-left px-2 py-1 text-[10px] text-secondaryText hover:text-primaryText hover:bg-slate-800 rounded font-sans"
                            >
                              Create a Collection first
                            </button>
                          ) : (
                            collections.map((col) => {
                              const alreadyIn = col.artifact_ids?.includes(artifact.id);
                              return (
                                <button
                                  key={col.id}
                                  disabled={alreadyIn || addToCollectionMutation.isPending}
                                  onClick={() => addToCollectionMutation.mutate({ colId: col.id, artId: artifact.id })}
                                  className="w-full text-left px-2 py-1.5 text-[10px] hover:bg-slate-800/80 rounded font-sans flex items-center justify-between text-primaryText disabled:opacity-50"
                                >
                                  <span className="truncate">{col.name}</span>
                                  {alreadyIn && <Check className="h-3 w-3 text-lime shrink-0" />}
                                </button>
                              );
                            })
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
