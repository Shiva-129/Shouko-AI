import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import type { Annotation } from "@/types";

export function useAnnotations(artifactId?: string) {
  return useQuery<Annotation[]>({
    queryKey: ["annotations", artifactId],
    queryFn: () =>
      apiClient.get(
        artifactId ? `/annotations?artifact_id=${artifactId}` : "/annotations"
      ),
    staleTime: 10 * 1000, // 10 seconds
  });
}

export function useCreateAnnotation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: {
      artifact_id: string;
      type: string;
      content: string;
      meta_data?: Record<string, any>;
    }) => apiClient.post<Annotation>("/annotations", payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ["annotations", variables.artifact_id],
      });
    },
  });
}

export function useUpdateAnnotation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: {
      id: string;
      artifact_id: string;
      content?: string;
      meta_data?: Record<string, any>;
    }) =>
      apiClient.put<Annotation>(`/annotations/${payload.id}`, {
        content: payload.content,
        meta_data: payload.meta_data,
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ["annotations", variables.artifact_id],
      });
    },
  });
}

export function useDeleteAnnotation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: { id: string; artifact_id: string }) =>
      apiClient.delete(`/annotations/${payload.id}`),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ["annotations", variables.artifact_id],
      });
    },
  });
}
