import React from "react";
import { FileText, Filter, Layers, Plus, Trash2, X } from "lucide-react";
import { UploadedDocumentRecord } from "../types";

interface SidebarProps {
  documents: UploadedDocumentRecord[];
  selectedDocumentId: string | null;
  onSelectDocument: (docId: string | null) => void;
  onDeleteDocument: (docId: string) => void;
  onOpenUpload: () => void;
  isOpenMobile: boolean;
  onCloseMobile: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  documents,
  selectedDocumentId,
  onSelectDocument,
  onDeleteDocument,
  onOpenUpload,
  isOpenMobile,
  onCloseMobile,
}) => {
  const formatBytes = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <>
      {/* Mobile backdrop */}
      {isOpenMobile && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-2xs sm:hidden"
          onClick={onCloseMobile}
        />
      )}

      <aside
        className={`fixed sm:static inset-y-0 left-0 z-40 w-72 sm:w-80 bg-white border-r border-slate-200 flex flex-col shrink-0 transition-transform duration-200 ease-in-out ${
          isOpenMobile ? "translate-x-0" : "-translate-x-full sm:translate-x-0"
        }`}
      >
        {/* Sidebar Header & Upload Button */}
        <div className="p-4 border-b border-slate-200">
          <div className="flex items-center justify-between mb-3 sm:hidden">
            <span className="font-semibold text-sm text-slate-800">Navigation</span>
            <button
              onClick={onCloseMobile}
              className="p-1 text-slate-400 hover:text-slate-600 rounded"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <button
            onClick={onOpenUpload}
            className="w-full py-2.5 px-3 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-medium text-xs shadow-xs transition flex items-center justify-center gap-1.5"
          >
            <Plus className="w-4 h-4" />
            <span>Upload Document</span>
          </button>
        </div>

        {/* Filter scope bar */}
        <div className="px-4 py-2.5 bg-slate-50/70 border-b border-slate-200 flex items-center justify-between text-xs">
          <div className="flex items-center gap-1.5 font-medium text-slate-600">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <span>Scope Filter</span>
          </div>
          {selectedDocumentId ? (
            <button
              onClick={() => onSelectDocument(null)}
              className="text-[11px] font-semibold text-teal-700 hover:text-teal-900"
            >
              Reset to All
            </button>
          ) : (
            <span className="text-[11px] text-slate-400 font-medium">All Documents</span>
          )}
        </div>

        {/* Document List */}
        <div className="flex-1 overflow-y-auto p-3 space-y-1.5">
          {documents.length === 0 ? (
            <div className="p-6 text-center text-slate-400">
              <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-xs font-medium">No documents uploaded yet</p>
              <p className="text-[11px] text-slate-400 mt-1">
                Upload PDF files to build your grounded research knowledge base.
              </p>
            </div>
          ) : (
            documents.map((doc) => {
              const isSelected = selectedDocumentId === doc.document_id;
              return (
                <div
                  key={doc.document_id}
                  onClick={() => onSelectDocument(isSelected ? null : doc.document_id)}
                  className={`p-3 rounded-xl border text-xs cursor-pointer transition-all group ${
                    isSelected
                      ? "border-teal-500 bg-teal-50/60 shadow-2xs"
                      : "border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50/80"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-start gap-2 min-w-0">
                      <div
                        className={`p-1.5 rounded-lg shrink-0 mt-0.5 ${
                          isSelected ? "bg-teal-600 text-white" : "bg-slate-100 text-slate-600"
                        }`}
                      >
                        <FileText className="w-3.5 h-3.5" />
                      </div>
                      <div className="min-w-0">
                        <p className="font-semibold text-slate-800 truncate" title={doc.filename}>
                          {doc.filename}
                        </p>
                        <div className="flex items-center gap-2 text-[11px] text-slate-500 mt-1">
                          <span>{doc.page_count} {doc.page_count === 1 ? "page" : "pages"}</span>
                          <span>•</span>
                          <span className="flex items-center gap-0.5">
                            <Layers className="w-3 h-3 text-slate-400" />
                            {doc.total_chunks} chunks
                          </span>
                        </div>
                      </div>
                    </div>

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDeleteDocument(doc.document_id);
                      }}
                      title="Delete from vector store"
                      className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded transition shrink-0"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  <div className="mt-2 pt-2 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-400">
                    <span>{formatBytes(doc.file_size_bytes)}</span>
                    {isSelected ? (
                      <span className="font-semibold text-teal-700">Active Scope</span>
                    ) : (
                      <span>Click to filter</span>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer info */}
        <div className="p-3 border-t border-slate-200 text-center text-[11px] text-slate-400 bg-slate-50/50">
          ChromaDB Vector Store · all-MiniLM-L6-v2
        </div>
      </aside>
    </>
  );
};
