import React, { useState } from "react";
import { ChevronDown, ChevronUp, Eye, FileText } from "lucide-react";
import { EvidencePassage } from "../types";

interface EvidenceViewerProps {
  evidence: EvidencePassage[];
}

export const EvidenceViewer: React.FC<EvidenceViewerProps> = ({ evidence }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!evidence || evidence.length === 0) {
    return null;
  }

  return (
    <div className="mt-3 border border-slate-200 rounded-lg bg-slate-50 overflow-hidden text-xs">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-3 py-2 flex items-center justify-between text-slate-700 font-medium hover:bg-slate-100 transition-colors"
      >
        <span className="flex items-center gap-1.5">
          <Eye className="w-3.5 h-3.5 text-slate-500" />
          <span>Retrieved Evidence Passages ({evidence.length})</span>
        </span>
        {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {isOpen && (
        <div className="p-3 border-t border-slate-200 space-y-2.5 max-h-72 overflow-y-auto">
          {evidence.map((p, idx) => (
            <div
              key={`${p.document_id}-${p.chunk_index}-${idx}`}
              className="p-2.5 bg-white border border-slate-200 rounded-md shadow-2xs"
            >
              <div className="flex items-center justify-between gap-2 mb-1.5 text-slate-600 font-medium">
                <span className="flex items-center gap-1 truncate">
                  <FileText className="w-3 h-3 text-slate-400 shrink-0" />
                  <span className="font-semibold text-slate-800 truncate">{p.source_filename}</span>
                  <span className="text-teal-700">· Page {p.page_number}</span>
                </span>
                <span
                  className="shrink-0 px-1.5 py-0.5 rounded text-[10px] bg-slate-100 text-slate-600 border border-slate-200"
                  title="ChromaDB cosine distance (smaller = closer similarity)"
                >
                  dist: {p.distance.toFixed(3)}
                </span>
              </div>
              <p className="text-slate-700 leading-relaxed font-mono text-[11px] bg-slate-50/70 p-2 rounded border border-slate-100 whitespace-pre-wrap">
                {p.text}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
