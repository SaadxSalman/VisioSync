import type { Document, QueryResponse } from "./types";

export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, options);
  if (!response.ok) throw new Error(`API request failed: ${response.status}`);
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string; retrieval: string; documents: number }>("/health"),
  documents: () => request<Document[]>("/documents"),
  query: (query: string, top_k = 6) => request<QueryResponse>("/query", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ query, top_k }) }),
  upload: (file: File) => { const body = new FormData(); body.append("file", file); return request<Document>("/documents", { method: "POST", body }); },
};
