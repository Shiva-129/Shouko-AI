import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import type { ArtifactListItem } from "@/types";

export interface Artifact {
  id: string;
  paper_id: string;
  paper_title: string | null;
  one_line_summary: string | null;
  summary: string | null;
  key_insights: ArtifactInsight[];
  auto_qa: ArtifactQAPair[];
  suggested_experiments: ArtifactExperiment[];
  status: string;
  error_message: string | null;
  generation_cost_usd: number | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface ArtifactInsight {
  insight: string;
  importance_score: number;
  section: string | null;
}

export interface ArtifactQAPair {
  question: string;
  answer: string;
  difficulty: string;
}

export interface ArtifactExperiment {
  title: string;
  description: string;
  feasibility: string;
}

interface ArtifactListResponse {
  artifacts: ArtifactListItem[];
  total: number;
}

export function useArtifact(id: string | undefined) {
  return useQuery<Artifact>({
    queryKey: ["artifact", id],
    queryFn: () => apiClient.get(`/artifacts/${id}`),
    staleTime: 5 * 60 * 1000,
    enabled: !!id,
    retry: false,
  });
}

export function useArtifacts(search?: string) {
  return useQuery<ArtifactListResponse>({
    queryKey: ["artifacts", search],
    queryFn: () =>
      apiClient.get(
        `/artifacts?search=${encodeURIComponent(search || "")}`
      ),
    staleTime: 30 * 1000,
  });
}

export function useCreateArtifact() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (paperId: string) =>
      apiClient.post<Artifact>("/artifacts", { paper_id: paperId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["artifacts"] });
      queryClient.invalidateQueries({ queryKey: ["user"] });
    },
  });
}

export function useDeleteArtifact() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => apiClient.delete(`/artifacts/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["artifacts"] });
      queryClient.invalidateQueries({ queryKey: ["user"] });
    },
  });
}
