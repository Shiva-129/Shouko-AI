"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import type { DailyDigest } from "@/types";

export function useDigest(date?: string) {
  const path = date ? `/digests/${date}` : "/digests/today";
  return useQuery<DailyDigest>({
    queryKey: ["digest", date ?? "today"],
    queryFn: () => apiClient.get<DailyDigest>(path),
    staleTime: 5 * 60 * 1000,
    retry: false,
  });
}
