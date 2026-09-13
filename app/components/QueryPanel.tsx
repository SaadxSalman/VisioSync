"use client";

import { ArrowUpRight, Gauge, Image as ImageIcon, Search, Zap } from "lucide-react";

type QueryPanelProps = { query: string; busy: boolean; onQueryChange: (query: string) => void; onSubmit: () => void };

export function QueryPanel({ query, busy, onQueryChange, onSubmit }: QueryPanelProps) {
  return <section className="query-panel"><div className="query-label"><Search size={15} /> VISUAL QUERY</div><div className="query-row"><input value={query} onChange={(event) => onQueryChange(event.target.value)} onKeyDown={(event) => event.key === "Enter" && onSubmit()} aria-label="Ask about engineering documents" /><button onClick={onSubmit} disabled={busy}>{busy ? "Retrieving..." : "Retrieve & answer"}<ArrowUpRight size={16} /></button></div><div className="query-meta"><span><Zap size={13} /> Late interaction retrieval</span><span><ImageIcon size={13} /> Page-level visual tokens</span><span><Gauge size={13} /> Top 6 regions</span></div></section>;
}
