"use client";

import { ArrowUpRight, FileText } from "lucide-react";
import type { Document, PageHit } from "../lib/types";

export function EvidenceCard({ hit, index, document }: { hit: PageHit; index: number; document?: Document }) {
  return <article className="hit"><div className="page-preview"><div className="page-grid"><span /><span /><span /><span /><span /><span /></div><b>PAGE {String(hit.page).padStart(2, "0")}</b></div><div className="hit-copy"><div className="hit-top"><span className="hit-type">{index === 0 ? "PRIMARY REGION" : "CROSS-REFERENCE"}</span><span className="score">{Math.round(hit.score * 100)}%</span></div><h3>{hit.title}</h3><p>{hit.excerpt}</p><div className="hit-foot"><span><FileText size={13} /> {hit.document_name || document?.name || "Engineering corpus"}</span><span>Open page <ArrowUpRight size={13} /></span></div></div></article>;
}
