"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Folder, Plus, ArrowLeft, Trash2, FolderPlus, BookOpen, ExternalLink, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";

type Collection = {
  id: string;
  name: string;
  description: string | null;
  color: string;
  artifact_ids: string[];
  is_default: boolean;
  created_at: string;
};

type CollectionDetail = {
  id: string;
  name: string;
  description: string | null;
  color: string;
  artifacts: Array<{
    id: string;
    paper_id: string;
    paper_title: string | null;
    one_line_summary: string | null;
    status: string;
    created_at: string | null;
  }>;
};

const COLORS = [
  "#3B82F6", // blue
  "#10B981", // green
  "#F59E0B", // amber
  "#EF4444", // red
  "#8B5CF6", // purple
  "#EC4899", // pink
  "#14B8A6", // teal
  "#A3E635", // lime
];

export default function CollectionsPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [newName, setNewName] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [newColor, setNewColor] = useState(COLORS[0]);

  // Queries
  const { data: collections = [], isLoading: isListLoading } = useQuery<Collection[]>({
    queryKey: ["collections"],
    queryFn: () => apiClient.get("/collections"),
  });

  const { data: collectionDetail, isLoading: isDetailLoading } = useQuery<CollectionDetail>({
    queryKey: ["collection", selectedId],
    queryFn: () => apiClient.get(`/collections/${selectedId}`),
    enabled: !!selectedId,
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data: { name: string; description: string; color: string }) =>
      apiClient.post("/collections", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["collections"] });
      setIsCreateOpen(false);
      setNewName("");
      setNewDesc("");
      setNewColor(COLORS[0]);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => apiClient.delete(`/collections/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["collections"] });
      setSelectedId(null);
    },
  });

  const removeArtifactMutation = useMutation({
    mutationFn: ({ colId, artId }: { colId: string; artId: string }) =>
      apiClient.delete(`/collections/${colId}/artifacts/${artId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["collection", selectedId] });
      queryClient.invalidateQueries({ queryKey: ["collections"] });
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) return;
    createMutation.mutate({ name: newName, description: newDesc, color: newColor });
  };

  if (isListLoading) {
    return (
      <div className="p-8 flex justify-center items-center h-96">
        <Loader2 className="h-8 w-8 text-lime animate-spin mr-2" />
        <p className="text-secondaryText font-mono text-sm">Loading collections...</p>
      </div>
    );
  }

  // Detail View Mode
  if (selectedId && collectionDetail) {
    const detail = collectionDetail;
    return (
      <div className="flex-1 bg-workspace flex flex-col min-w-0 p-8 select-none">
        <button
          onClick={() => setSelectedId(null)}
          className="flex items-center gap-1.5 text-xs text-secondaryText hover:text-primaryText mb-4 transition-colors font-mono"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          Back to Collections
        </button>

        <div className="flex justify-between items-start gap-4 mb-6">
          <div>
            <div className="flex items-center gap-3">
              <div 
                className="w-4 h-4 rounded-full" 
                style={{ backgroundColor: detail.color }}
              />
              <h1 className="font-syne font-extrabold text-[32px] text-primaryText tracking-tight">
                {detail.name}
              </h1>
            </div>
            {detail.description && (
              <p className="text-sm text-secondaryText font-mono mt-1 italic">
                {detail.description}
              </p>
            )}
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              if (confirm("Delete this collection? This will not delete the papers/artifacts inside.")) {
                deleteMutation.mutate(detail.id);
              }
            }}
            className="text-red-400 hover:text-red-300 hover:bg-red-500/10 font-mono text-xs"
          >
            <Trash2 className="h-3.5 w-3.5 mr-1" />
            Delete Collection
          </Button>
        </div>

        {isDetailLoading ? (
          <div className="flex justify-center items-center h-48">
            <Loader2 className="h-6 w-6 text-lime animate-spin" />
          </div>
        ) : detail.artifacts.length === 0 ? (
          <Card className="bg-card border-border">
            <CardContent className="py-12 text-center text-secondaryText font-mono text-sm">
              <BookOpen className="h-8 w-8 mx-auto mb-2 text-secondaryText/40" />
              No papers inside this collection yet.
              <p className="text-xs text-secondaryText/50 mt-1">
                Go to the library to add artifacts to this folder.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-3">
            {detail.artifacts.map((a) => (
              <Card 
                key={a.id} 
                className="bg-card border-border hover:border-lime/30 transition-all cursor-pointer"
                onClick={() => router.push(`/artifact/${a.id}`)}
              >
                <CardContent className="p-4 flex items-center justify-between gap-4">
                  <div className="min-w-0 flex-1">
                    <h3 className="font-bold text-sm text-primaryText truncate">
                      {a.paper_title || "Untitled Paper"}
                    </h3>
                    {a.one_line_summary && (
                      <p className="text-xs text-secondaryText font-mono truncate mt-1">
                        {a.one_line_summary}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        removeArtifactMutation.mutate({ colId: detail.id, artId: a.id });
                      }}
                      className="text-secondaryText hover:text-red-400 font-mono text-[10px]"
                    >
                      Remove
                    </Button>
                    <ExternalLink className="h-4 w-4 text-secondaryText/60" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="flex-1 bg-workspace flex flex-col min-w-0 p-8 select-none">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="font-syne font-extrabold text-[32px] text-primaryText tracking-tight">
            Collections
          </h1>
          <p className="text-xs text-secondaryText font-mono mt-1">
            Organize research papers and artifacts into structured workspaces.
          </p>
        </div>

        <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
          <DialogTrigger asChild>
            <Button className="bg-lime text-[#0D0D0D] hover:bg-lime/90 font-bold text-xs gap-1.5">
              <FolderPlus className="h-4 w-4" />
              New Collection
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-[#0E1117] border-border text-primaryText max-w-md">
            <DialogHeader>
              <DialogTitle className="font-syne font-bold text-lg">Create Collection</DialogTitle>
              <DialogDescription className="text-secondaryText text-xs font-mono">
                Group relevant papers together.
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4 pt-2">
              <div className="space-y-1">
                <label className="text-xs font-mono text-secondaryText font-semibold">Name</label>
                <Input
                  required
                  placeholder="e.g. LLM Reasoning, Vector DBs"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className="bg-slate-900 border-border text-xs focus:border-lime/50"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-mono text-secondaryText font-semibold">Description</label>
                <Input
                  placeholder="Brief summary (optional)"
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  className="bg-slate-900 border-border text-xs focus:border-lime/50"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-mono text-secondaryText font-semibold">Color Tag</label>
                <div className="flex flex-wrap gap-2">
                  {COLORS.map((c) => (
                    <button
                      key={c}
                      type="button"
                      onClick={() => setNewColor(c)}
                      className={`w-6 h-6 rounded-full border-2 transition-transform ${
                        newColor === c ? "border-lime scale-110" : "border-transparent hover:scale-105"
                      }`}
                      style={{ backgroundColor: c }}
                    />
                  ))}
                </div>
              </div>

              <Button
                type="submit"
                className="w-full bg-lime text-[#0D0D0D] hover:bg-lime/90 font-bold text-xs"
              >
                Create Folder
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {collections.length === 0 ? (
        <Card className="bg-card border-border py-12 text-center">
          <CardContent className="font-mono text-sm text-secondaryText">
            <Folder className="h-10 w-10 mx-auto mb-2 text-secondaryText/40" />
            No collections found.
            <p className="text-xs text-secondaryText/50 mt-1">
              Create a new folder to start organizing your research.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4">
          {collections.map((c) => (
            <Card
              key={c.id}
              onClick={() => setSelectedId(c.id)}
              className="bg-card border-border hover:border-lime/30 transition-all cursor-pointer relative overflow-hidden group"
            >
              <div 
                className="absolute top-0 left-0 bottom-0 w-1.5" 
                style={{ backgroundColor: c.color }}
              />
              <CardHeader className="pb-2 pl-5">
                <CardTitle className="text-sm font-syne font-bold text-primaryText group-hover:text-lime transition-colors">
                  {c.name}
                </CardTitle>
                {c.description && (
                  <CardDescription className="text-xs text-secondaryText font-mono line-clamp-2">
                    {c.description}
                  </CardDescription>
                )}
              </CardHeader>
              <CardContent className="pt-2 pl-5 flex items-center justify-between text-xs font-mono text-secondaryText/80">
                <span>{c.artifact_ids?.length || 0} papers</span>
                <Folder className="h-4 w-4 text-secondaryText/40 group-hover:text-lime/60 transition-colors" />
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
