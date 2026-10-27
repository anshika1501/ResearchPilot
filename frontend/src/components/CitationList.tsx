import React from "react";
import { BookOpen } from "lucide-react";
import { Citation } from "../types";

interface CitationListProps {
  citations: Citation[];
  onSelectCitation?: (citation: Citation) => void;
}

export const CitationList: React.FC<CitationListProps> = ({
  citations,
  onSelectCitation,
}) => {
  if (!citations || citations.length === 0) {
    return null;
  }

  return (
    <div className="mt-3 pt-3 border-t border-slate-100">
      <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-700 mb-2">
        <BookOpen className="w-3.5 h-3.5 text-teal-600" />
        <span>Source References ({citations.length}):</span>
      </div>
      <div className="flex flex-wrap gap-1.5">
        {citations.map((c, i) => (
          <button
            key={`${c.document_id}-${c.chunk_index}-${i}`}
            onClick={() => onSelectCitation && onSelectCitation(c)}
            type="button"
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium bg-teal-50 text-teal-800 border border-teal-200 hover:bg-teal-100 transition-colors shadow-2xs"
            title={`View evidence from ${c.source_filename}, Page ${c.page_number}`}
          >
            <span className="truncate max-w-[150px] font-semibold">{c.source_filename}</span>
            <span className="text-teal-600 font-bold">· Page {c.page_number}</span>
          </button>
        ))}
      </div>
    </div>
  );
};
