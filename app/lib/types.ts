export type BackendStatus = "checking" | "online" | "demo";

export type Document = {
  id: string;
  name: string;
  pages: number;
  status: string;
  indexed_at: string;
  kind: string;
  size_bytes?: number;
};

export type PageHit = {
  page: number;
  score: number;
  title: string;
  excerpt: string;
  document_id: string;
  document_name?: string;
  image_url?: string;
};

export type QueryResponse = {
  answer: string;
  hits: PageHit[];
  model: string;
  retrieval_mode: string;
  query: string;
  latency_ms: number;
};
