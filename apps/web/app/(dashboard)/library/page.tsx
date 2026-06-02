"use client";

import { useQuery } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/shared/EmptyState";
import { apiClient } from "@/lib/api";
import { useState } from "react";
import { BookOpen, Search } from "lucide-react";

interface ArtifactListItem {
  id: string;
  title: string;
  status: string;
  created_at: string;
}

export default function LibraryPage() {
  const [search, setSearch] = useState("");
  const { data: artifacts, isLoading } = useQuery<ArtifactListItem[]>({
    queryKey: ["artifacts", search],
    queryFn: () => apiClient.get(`/artifacts?search=${encodeURIComponent(search)}`),
    staleTime: 30 * 1000,
    retry: false,
  });

  return (
    <div className="p-8 max-w-5xl">
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

      {artifacts && artifacts.length === 0 && (
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

      {artifacts && artifacts.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {artifacts.map((artifact) => (
            <Card key={artifact.id} className="bg-card border-border hover:border-lime/20 transition-colors cursor-pointer">
              <CardContent className="p-4">
                <div className="flex items-start justify-between gap-2 mb-2">
                  <h3 className="text-sm font-semibold text-primaryText leading-snug line-clamp-2">
                    {artifact.title}
                  </h3>
                  <Badge
                    variant="outline"
                    className={`shrink-0 text-[10px] px-1.5 py-0.5 uppercase font-mono ${
                      artifact.status === "ready"
                        ? "text-emerald-400 border-emerald-500/30 bg-emerald-500/10"
                        : artifact.status === "processing"
                        ? "text-violet-400 border-violet-500/30 bg-violet-500/10"
                        : "text-amber-400 border-amber-500/30 bg-amber-500/10"
                    }`}
                  >
                    {artifact.status}
                  </Badge>
                </div>
                <p className="text-[10px] text-secondaryText/60 font-mono">
                  {new Date(artifact.created_at).toLocaleDateString()}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
