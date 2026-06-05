"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";

type DigestListItem = {
  id: string;
  date: string;
  paper_count: number;
  status: string;
  created_at: string | null;
};

type DigestListResponse = {
  digests: DigestListItem[];
  total: number;
  page: number;
  page_size: number;
};

export function useDigests(page: number = 1, pageSize: number = 10) {
  return useQuery<DigestListResponse>({
    queryKey: ["digests", page, pageSize],
    queryFn: () =>
      apiClient.get<DigestListResponse>(
        `/digests?page=${page}&page_size=${pageSize}`
      ),
    staleTime: 5 * 60 * 1000,
  });
}
