"use client";

import { useState } from "react";
import { 
  useAnnotations, 
  useCreateAnnotation, 
  useUpdateAnnotation, 
  useDeleteAnnotation 
} from "@/lib/hooks/useAnnotations";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Skeleton } from "@/components/ui/skeleton";
import { 
  FileText, 
  Lightbulb, 
  FlaskConical, 
  CheckSquare, 
  Link as LinkIcon, 
  Plus, 
  Trash2, 
  Edit2, 
  Check, 
  X,
  Tag
} from "lucide-react";
import type { Annotation } from "@/types";

interface AnnotationsTabProps {
  artifactId: string;
}

const TYPE_CONFIG = {
  note: {
    label: "Note",
    icon: FileText,
    color: "text-blue-400 bg-blue-500/10 border-blue-500/20",
    buttonColor: "hover:bg-blue-500/10 hover:text-blue-400 border-blue-500/20",
    activeColor: "bg-blue-500/20 text-blue-400 border-blue-500/40",
  },
  highlight: {
    label: "Highlight",
    icon: Lightbulb,
    color: "text-amber-400 bg-amber-500/10 border-amber-500/20",
    buttonColor: "hover:bg-amber-500/10 hover:text-amber-400 border-amber-500/20",
    activeColor: "bg-amber-500/20 text-amber-400 border-amber-500/40",
  },
  experiment: {
    label: "Experiment",
    icon: FlaskConical,
    color: "text-purple-400 bg-purple-500/10 border-purple-500/20",
    buttonColor: "hover:bg-purple-500/10 hover:text-purple-400 border-purple-500/20",
    activeColor: "bg-purple-500/20 text-purple-400 border-purple-500/40",
  },
  task: {
    label: "Task",
    icon: CheckSquare,
    color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
    buttonColor: "hover:bg-emerald-500/10 hover:text-emerald-400 border-emerald-500/20",
    activeColor: "bg-emerald-500/20 text-emerald-400 border-emerald-500/40",
  },
  link: {
    label: "Link",
    icon: LinkIcon,
    color: "text-pink-400 bg-pink-500/10 border-pink-500/20",
    buttonColor: "hover:bg-pink-500/10 hover:text-pink-400 border-pink-500/20",
    activeColor: "bg-pink-500/20 text-pink-400 border-pink-500/40",
  },
};

type AnnotationType = keyof typeof TYPE_CONFIG;

export function AnnotationsTab({ artifactId }: AnnotationsTabProps) {
  const { data: annotations = [], isLoading } = useAnnotations(artifactId);
  const createMutation = useCreateAnnotation();
  const updateMutation = useUpdateAnnotation();
  const deleteMutation = useDeleteAnnotation();

  const [activeFilter, setActiveFilter] = useState<"all" | AnnotationType>("all");
  const [selectedType, setSelectedType] = useState<AnnotationType>("note");
  const [newContent, setNewContent] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingContent, setEditingContent] = useState("");

  const handleCreate = () => {
    if (!newContent.trim()) return;
    createMutation.mutate({
      artifact_id: artifactId,
      type: selectedType,
      content: newContent.trim(),
    }, {
      onSuccess: () => {
        setNewContent("");
      }
    });
  };

  const handleStartEdit = (ann: Annotation) => {
    setEditingId(ann.id);
    setEditingContent(ann.content);
  };

  const handleSaveEdit = (id: string) => {
    if (!editingContent.trim()) return;
    updateMutation.mutate({
      id,
      artifact_id: artifactId,
      content: editingContent.trim(),
    }, {
      onSuccess: () => {
        setEditingId(null);
      }
    });
  };

  const handleDelete = (id: string) => {
    deleteMutation.mutate({ id, artifact_id: artifactId });
  };

  const filteredAnnotations = annotations.filter(
    (ann) => activeFilter === "all" || ann.type === activeFilter
  );

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-full bg-card" />
        <Skeleton className="h-28 w-full bg-card" />
        <Skeleton className="h-20 w-full bg-card" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Create Annotation Form */}
      <Card className="bg-card border-border">
        <CardContent className="p-4 space-y-3">
          <h3 className="text-xs font-mono font-bold text-secondaryText uppercase tracking-wider">
            Create New Annotation
          </h3>
          <Textarea
            value={newContent}
            onChange={(e) => setNewContent(e.target.value)}
            placeholder="Write a note, task, highlight, link reference..."
            className="bg-background border-border text-sm min-h-[80px]"
          />
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap gap-1.5">
              {(Object.keys(TYPE_CONFIG) as AnnotationType[]).map((type) => {
                const config = TYPE_CONFIG[type];
                const Icon = config.icon;
                const isSelected = selectedType === type;
                return (
                  <button
                    key={type}
                    type="button"
                    onClick={() => setSelectedType(type)}
                    className={`flex items-center gap-1.5 px-2.5 py-1 text-xs border rounded-full transition-all ${
                      isSelected ? config.activeColor : `text-secondaryText bg-transparent ${config.buttonColor}`
                    }`}
                  >
                    <Icon className="h-3.5 w-3.5" />
                    {config.label}
                  </button>
                );
              })}
            </div>
            <Button
              size="sm"
              onClick={handleCreate}
              disabled={!newContent.trim() || createMutation.isPending}
              className="gap-1 bg-lime text-black hover:bg-lime/90"
            >
              <Plus className="h-3.5 w-3.5" />
              Add Annotation
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Filters & Header */}
      <div className="flex items-center justify-between gap-4">
        <h3 className="font-syne font-bold text-sm text-primaryText flex items-center gap-1.5">
          <Tag className="h-4 w-4 text-lime" />
          Annotations ({filteredAnnotations.length})
        </h3>
        <div className="flex items-center gap-1.5 overflow-x-auto">
          <button
            onClick={() => setActiveFilter("all")}
            className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${
              activeFilter === "all"
                ? "bg-lime text-black font-semibold"
                : "text-secondaryText hover:text-primaryText"
            }`}
          >
            All
          </button>
          {(Object.keys(TYPE_CONFIG) as AnnotationType[]).map((type) => {
            const config = TYPE_CONFIG[type];
            return (
              <button
                key={type}
                onClick={() => setActiveFilter(type)}
                className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${
                  activeFilter === type
                    ? "bg-lime text-black font-semibold"
                    : "text-secondaryText hover:text-primaryText"
                }`}
              >
                {config.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Annotations List */}
      <div className="space-y-3">
        {filteredAnnotations.length === 0 ? (
          <div className="text-center py-8 text-secondaryText text-sm font-mono border border-dashed border-border rounded-lg">
            No {activeFilter !== "all" ? `${activeFilter}s` : "annotations"} found.
          </div>
        ) : (
          filteredAnnotations.map((ann) => {
            const config = TYPE_CONFIG[ann.type as AnnotationType] || TYPE_CONFIG.note;
            const Icon = config.icon;
            const isEditing = editingId === ann.id;

            return (
              <Card key={ann.id} className="bg-card border-border hover:border-border-hover transition-colors">
                <CardContent className="p-4">
                  {isEditing ? (
                    <div className="space-y-3">
                      <Textarea
                        value={editingContent}
                        onChange={(e) => setEditingContent(e.target.value)}
                        className="bg-background border-border text-sm min-h-[60px]"
                      />
                      <div className="flex justify-end gap-2">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => setEditingId(null)}
                          className="gap-1 text-secondaryText"
                        >
                          <X className="h-3.5 w-3.5" />
                          Cancel
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => handleSaveEdit(ann.id)}
                          disabled={!editingContent.trim() || updateMutation.isPending}
                          className="gap-1 bg-lime text-black hover:bg-lime/90"
                        >
                          <Check className="h-3.5 w-3.5" />
                          Save
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-start justify-between gap-4">
                      <div className="space-y-2 flex-1">
                        <div className="flex items-center gap-2">
                          <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-semibold uppercase tracking-wider border ${config.color}`}>
                            <Icon className="h-3 w-3" />
                            {config.label}
                          </span>
                          <span className="text-[10px] text-secondaryText font-mono">
                            {new Date(ann.created_at).toLocaleDateString(undefined, {
                              month: "short",
                              day: "numeric",
                              hour: "2-digit",
                              minute: "2-digit"
                            })}
                          </span>
                        </div>
                        <p className="text-sm text-primaryText leading-relaxed whitespace-pre-line">
                          {ann.content}
                        </p>
                      </div>

                      <div className="flex items-center gap-1.5 shrink-0">
                        <Button
                          size="icon"
                          variant="ghost"
                          onClick={() => handleStartEdit(ann)}
                          className="h-7 w-7 text-secondaryText hover:text-primaryText"
                        >
                          <Edit2 className="h-3.5 w-3.5" />
                        </Button>
                        <Button
                          size="icon"
                          variant="ghost"
                          onClick={() => handleDelete(ann.id)}
                          className="h-7 w-7 text-secondaryText hover:text-red-400"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })
        )}
      </div>
    </div>
  );
}
