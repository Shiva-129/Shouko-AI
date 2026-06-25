export interface Message {
  role: "user" | "assistant";
  content: string;
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
  paper_title: string;
  one_line_summary: string;
  status: string;
  created_at: string;
}

export interface Annotation {
  id: string;
  artifact_id: string;
  user_id: string;
  type: "note" | "highlight" | "experiment" | "task" | "link";
  content: string;
  meta_data: Record<string, unknown>;
  created_at: string;
}
