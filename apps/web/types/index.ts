export interface Paper {
  id: string;
  title: string;
  subTagline: string;
  institution: string;
  difficulty: "EASY" | "MEDIUM" | "HARD";
  readingTime: string;
  relevance: string;
  isHot: boolean;
  category: "Agents" | "Multi-Agent" | "Safety" | "Reasoning";
  tags: string[];
  summary: string;
  body: string;
  citations: string[];
  notes: string[];
  initialAssistantMessage: string;
  mockQueries: string[];
  mockQAs: { question: string; answer: string }[];
  borderAccent?: string;
}

export interface Message {
  role: "user" | "assistant";
  content: string;
}

export interface NodePosition {
  id: string;
  label: string;
  desc: string;
  type: "root" | "branch" | "child";
  parentId?: string;
  x: number;
  y: number;
}

export interface UserProfile {
  id: string;
  email: string;
  name: string | null;
  avatar_url: string | null;
  plan: string;
  interest_profile: Record<string, unknown>;
  onboarded_at: string | null;
  created_at: string;
  usage: UsageStats | null;
}

export interface UsageStats {
  artifact_created_monthly: number;
  artifact_created_limit: number | null;
  question_asked_daily: number;
  question_asked_limit: number | null;
  paper_ingested_monthly: number;
  paper_ingested_limit: number | null;
}

export interface ScoredPaper {
  paper_id: string;
  score: number;
  reason: string;
  title: string;
  abstract: string | null;
  category: string | null;
  authors: string[] | null;
}

export interface DailyDigest {
  id: string;
  date: string;
  paper_count: number;
  status: string;
  papers: ScoredPaper[];
  created_at: string | null;
  email_sent_at: string | null;
}

export interface ArtifactListItem {
  id: string;
  title: string;
  paper_title: string;
  one_line_summary: string;
  status: string;
  created_at: string;
}
