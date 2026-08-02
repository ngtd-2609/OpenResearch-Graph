export type Paper = {
  id: string;
  openalex_id?: string | null;
  doi?: string | null;
  title: string;
  abstract?: string | null;
  publication_year?: number | null;
  cited_by_count: number;
  is_open_access: boolean;
  open_access_url?: string | null;
  source_name?: string | null;
};

export type PaginatedPapers = {
  query: string;
  total: number;
  page: number;
  per_page: number;
  items: Paper[];
};

export type DocumentStatus = "pending" | "running" | "completed" | "failed" | "canceled";

export type DocumentItem = {
  id: string;
  filename: string;
  status: DocumentStatus;
  pages?: number | null;
  file_size: number;
  error?: string | null;
  created_at: string;
};

export type Citation = {
  document_id: string;
  page: number;
  chunk_id: string;
  quote: string;
  score: number;
};

export type ChatAnswer = {
  answer: string;
  citations: Citation[];
  model: string;
  latency_ms: number;
};

export type Recommendation = {
  paper: Paper;
  score: number;
  explanation: string;
  components: Record<string, number>;
};
