"use client";

import { FileText, Upload } from "lucide-react";
import type { Document } from "../lib/types";

export function DocumentList({ documents, onUpload }: { documents: Document[]; onUpload: (file: File) => void }) {
  return <><div className="section-heading"><div><p className="eyebrow">CORPUS</p><h2>Documents <span>{documents.length}</span></h2></div><label className="icon-button" aria-label="Add document"><Upload size={16} /><input style={{ display: "none" }} type="file" accept="application/pdf" onChange={(event) => event.target.files?.[0] && onUpload(event.target.files[0])} /></label></div><div className="doc-list">{documents.map((doc) => <div className="doc" key={doc.id}><div className="doc-icon"><FileText size={17} /></div><div className="doc-info"><strong>{doc.name}</strong><span>{doc.pages ? `${doc.pages} pages` : "Processing"} · {doc.kind}</span></div><div className={`doc-status ${doc.status}`} title={doc.status} /></div>)}</div></>;
}
