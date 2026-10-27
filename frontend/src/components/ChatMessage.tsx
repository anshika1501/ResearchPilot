import React from "react";
import { AlertTriangle, Bot, CheckCircle2, User } from "lucide-react";
import { ChatMessageItem } from "../types";
import { CitationList } from "./CitationList";
import { EvidenceViewer } from "./EvidenceViewer";

interface ChatMessageProps {
  message: ChatMessageItem;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end mb-4">
        <div className="flex items-start gap-2.5 max-w-[85%] sm:max-w-[75%]">
          <div className="bg-teal-600 text-white rounded-2xl rounded-tr-xs px-4 py-3 shadow-xs">
            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
            <span className="block text-[10px] text-teal-100 text-right mt-1.5 opacity-90">
              {message.timestamp}
            </span>
          </div>
          <div className="w-8 h-8 rounded-full bg-slate-200 text-slate-700 flex items-center justify-center shrink-0 mt-0.5">
            <User className="w-4 h-4" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start mb-6">
      <div className="flex items-start gap-3 max-w-[95%] sm:max-w-[85%]">
        <div className="w-8 h-8 rounded-xl bg-teal-600 text-white flex items-center justify-center shrink-0 shadow-2xs mt-1">
          <Bot className="w-4 h-4" />
        </div>

        <div className="flex-1 bg-white border border-slate-200 rounded-2xl rounded-tl-xs p-4 shadow-xs">
          {/* Header metadata row */}
          <div className="flex flex-wrap items-center justify-between gap-2 pb-2 mb-2 border-b border-slate-100 text-xs">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-slate-800">ResearchPilot</span>
              {message.model && (
                <span className="px-1.5 py-0.5 rounded text-[10px] bg-slate-100 text-slate-600 border border-slate-200">
                  {message.model}
                </span>
              )}
            </div>

            {/* Groundedness status badge */}
            {message.has_sufficient_evidence !== undefined && (
              message.has_sufficient_evidence ? (
                <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                  <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                  Grounded in Evidence
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 text-[11px] font-medium text-amber-800 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">
                  <AlertTriangle className="w-3 h-3 text-amber-600" />
                  Insufficient Evidence
                </span>
              )
            )}
          </div>

          {/* Answer text */}
          <div className="text-slate-800 text-sm leading-relaxed whitespace-pre-wrap">
            {message.content}
          </div>

          {/* Source citations */}
          {message.citations && message.citations.length > 0 && (
            <CitationList citations={message.citations} />
          )}

          {/* Evidence passages inspection */}
          {message.evidence && message.evidence.length > 0 && (
            <EvidenceViewer evidence={message.evidence} />
          )}

          <div className="text-[10px] text-slate-400 text-right mt-2">
            {message.timestamp}
          </div>
        </div>
      </div>
    </div>
  );
};
