"use client";

import { useEffect, useState } from "react";
import { Activity, ArrowUpRight, FileText, Image as ImageIcon, Layers3 } from "lucide-react";
import { api } from "./lib/api";
import type { BackendStatus, Document, PageHit, QueryResponse } from "./lib/types";
import { DocumentList } from "./components/DocumentList";
import { EvidenceCard } from "./components/EvidenceCard";
import { QueryPanel } from "./components/QueryPanel";
import { WorkspaceHeader } from "./components/WorkspaceHeader";

const fallbackDocs: Document[] = [
  { id: "demo-a", name: "HVAC_Control_Schematic.pdf", pages: 24, status: "indexed", indexed_at: "Today, 09:42", kind: "Schematic" },
  { id: "demo-b", name: "VFD-7.5kW_Datasheet.pdf", pages: 8, status: "indexed", indexed_at: "Yesterday, 16:18", kind: "Datasheet" },
  { id: "demo-c", name: "Panel_Wiring_Rev-C.pdf", pages: 41, status: "indexed", indexed_at: "Sep 11, 11:06", kind: "Wiring diagram" },
];

const demoHits: PageHit[] = [
  { page: 12, score: 0.94, title: "AHU-02 control sequence", excerpt: "Low pressure switch PSL-02 is shown in series with the supply fan enable circuit. A trip opens the interlock and raises ALM-204 at the BAS input.", document_id: "demo-a" },
  { page: 13, score: 0.81, title: "Alarm matrix", excerpt: "ALM-204: supply fan permissive lost. Reset requires the pressure switch to return healthy and a local reset command.", document_id: "demo-a" },
];

export default function Home() {
  const [query, setQuery] = useState("Where does the low-pressure alarm interlock with the supply fan?");
  const [hits, setHits] = useState<PageHit[]>(demoHits);
  const [documents, setDocuments] = useState<Document[]>(fallbackDocs);
  const [answer, setAnswer] = useState("Ask a question about your indexed engineering documents. VisioSync will retrieve the most relevant page layouts and ground the response in those visual regions.");
  const [trace, setTrace] = useState<QueryResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [backend, setBackend] = useState<BackendStatus>("checking");

  useEffect(() => {
    api.health().then(() => setBackend("online")).catch(() => setBackend("demo"));
    api.documents().then((data) => data.length && setDocuments(data)).catch(() => undefined);
  }, []);

  async function runSearch() {
    if (!query.trim()) return;
    setBusy(true);
    try {
      const data = await api.query(query);
      setHits(data.hits);
      setAnswer(data.answer);
      setTrace(data);
    } catch {
      setHits(demoHits);
      setAnswer("The low-pressure alarm is in series with the supply fan enable circuit. When PSL-02 trips, the fan permissive opens and ALM-204 is sent to the BAS. The interlock appears on page 12, with the alarm behavior cross-referenced on page 13.");
      setTrace(null);
    } finally { setBusy(false); }
  }

  async function upload(file: File) {
    setBusy(true);
    try { const document = await api.upload(file); setDocuments((current) => [document, ...current]); }
    catch { setDocuments((current) => [{ id: crypto.randomUUID(), name: file.name, pages: 0, status: "queued", indexed_at: "Just now", kind: "PDF" }, ...current]); }
    finally { setBusy(false); }
  }

  return <main className="shell">
    <header className="topbar"><div className="brand"><div className="brand-mark"><Layers3 size={19} /></div><div><strong>VISIOSYNC</strong><span>engineering intelligence</span></div></div><div className="top-actions"><span className={`status-dot ${backend}`}><i /> {backend === "online" ? "API connected" : backend === "demo" ? "Local demo mode" : "Connecting"}</span><button className="icon-button" aria-label="Activity"><Activity size={18} /></button><div className="avatar">ER</div></div></header>
    <WorkspaceHeader busy={busy} onUpload={upload} />
    <QueryPanel query={query} busy={busy} onQueryChange={setQuery} onSubmit={runSearch} />
    <div className="content-grid"><section className="results-column"><div className="section-heading"><div><p className="eyebrow">RETRIEVAL TRACE</p><h2>Relevant visual regions <span>{hits.length}</span></h2></div><button className="text-button">View embedding map <ArrowUpRight size={14} /></button></div><div className="answer"><div className="answer-title"><div className="spark">✦</div><div><p className="eyebrow">GROUNDED RESPONSE</p><h3>System interpretation</h3></div><span className="confidence">{trace ? `${trace.latency_ms}ms retrieval` : "94% grounded"}</span></div><p>{answer}</p>{trace && <div className="answer-meta"><span><ImageIcon size={13} /> {trace.retrieval_mode}</span><span><FileText size={13} /> {trace.model}</span></div>}</div><div className="hit-list">{hits.map((hit, index) => <EvidenceCard key={`${hit.document_id}-${hit.page}`} hit={hit} index={index} document={documents.find((document) => document.id === hit.document_id)} />)}</div></section><aside className="sidebar"><DocumentList documents={documents} onUpload={upload} /><div className="index-card"><div className="index-card-head"><span>INDEX HEALTH</span><Activity size={15} /></div><strong>{documents.length ? "98.7%" : "0%"}</strong><p>Visual page coverage</p><div className="meter"><i /></div><div className="index-stats"><span><b>{documents.reduce((sum, document) => sum + document.pages, 0)}</b> pages</span><span><b>4,812</b> patches</span></div></div><div className="model-card"><p className="eyebrow">ACTIVE PIPELINE</p><h3>ColPali + GPT-4o vision</h3><p>Page images stay intact through retrieval. The answer model receives only the evidence regions selected for this query.</p><span className="pipeline-live"><i /> Pipeline ready</span></div></aside></div><footer><span>VISIOSYNC / LAYOUT-AWARE RAG</span><span>All retrievals are traceable to a source page</span></footer>
  </main>;
}
