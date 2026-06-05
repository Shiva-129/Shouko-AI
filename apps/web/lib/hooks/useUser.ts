"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";

type UserProfile = {
  id: string;
  email: string;
  name: string | null;
  avatar_url: string | null;
  plan: string;
  interest_profile: Record<string, unknown>;
  usage: {
    artifact_created_monthly: number;
    artifact_created_limit: number | null;
    question_asked_daily: number;
    question_asked_limit: number | null;
    paper_ingested_monthly: number;
    paper_ingested_limit: number | null;
  } | null;
};

export function useUser() {
  return useQuery<UserProfile>({
    queryKey: ["user"],
    queryFn: () => apiClient.get("/users/me"),
    staleTime: 5 * 60 * 1000,
  });
}
