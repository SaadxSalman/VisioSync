"use client";

import { Upload } from "lucide-react";

export function WorkspaceHeader({ busy, onUpload }: { busy: boolean; onUpload: (file: File) => void }) {
  return <section className="workspace-head"><div><p className="eyebrow">WORKSPACE / NORTHSTAR MEP</p><h1>Visual knowledge, <em>in context.</em></h1><p className="subhead">Ask across schematics, wiring diagrams, and datasheets without flattening the page.</p></div><label className="upload-button"><Upload size={16} /> {busy ? "Indexing..." : "Add document"}<input type="file" accept="application/pdf" onChange={(event) => event.target.files?.[0] && onUpload(event.target.files[0])} /></label></section>;
}
