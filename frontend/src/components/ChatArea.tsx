import React, { useEffect, useRef, useState } from "react";
import { AlertCircle, Filter, Loader2, Send, Sparkles } from "lucide-react";
import { ChatMessageItem, UploadedDocumentRecord } from "../types";
import { ChatMessage } from "./ChatMessage";

interface ChatAreaProps {
  messages: ChatMessageItem[];
  onSendMessage: (question: string) => void;
  isLoading: boolean;
  selectedDocument: UploadedDocumentRecord | null;
  onClearDocumentFilter: () => void;
  hasDocuments: boolean;
  onOpenUpload: () => void;
  errorMessage: string | null;
  onDismissError: () => void;
}

export const ChatArea: React.FC<ChatAreaProps> = ({
  messages,
  onSendMessage,
  isLoading,
  selectedDocument,
  onClearDocumentFilter,
  hasDocuments,
  onOpenUpload,
  errorMessage,
  onDismissError,
}) => {
  const [inputQuestion, setInputQuestion] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = inputQuestion.trim();
    if (!trimmed || isLoading) return;
    onSendMessage(trimmed);
    setInputQuestion("");
  };

  const handlePromptChipClick = (prompt: string) => {
    if (isLoading) return;
    onSendMessage(prompt);
  };

  return (
    <main className="flex-1 flex flex-col bg-slate-50/50 h-full overflow-hidden min-w-0">
      {/* Active filter banner */}
      {selectedDocument && (
        <div className="bg-teal-50/90 border-b border-teal-200 px-4 py-2 flex items-center justify-between text-xs text-teal-800">
          <div className="flex items-center gap-1.5 truncate">
            <Filter className="w-3.5 h-3.5 text-teal-600 shrink-0" />
            <span className="font-semibold">Scoped Search:</span>
            <span className="truncate">{selectedDocument.filename}</span>
          </div>
          <button
            onClick={onClearDocumentFilter}
            className="text-[11px] font-semibold text-teal-700 hover:text-teal-900 ml-2 underline shrink-0"
          >
            Clear Filter
          </button>
        </div>
      )}

      {/* Messages viewport */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center max-w-xl mx-auto text-center px-4">
            <div className="w-12 h-12 rounded-2xl bg-teal-100 text-teal-700 flex items-center justify-center mb-4 shadow-sm shadow-teal-700/10">
              <Sparkles className="w-6 h-6" />
            </div>

            <h2 className="text-lg font-bold text-slate-800">
              Ask questions grounded in your research documents
            </h2>
            <p className="text-xs text-slate-500 mt-2 leading-relaxed">
              ResearchPilot retrieves semantic passages from ChromaDB and generates verified,
              cited answers using a local Ollama model.
            </p>

            {!hasDocuments ? (
              <div className="mt-6 p-4 rounded-xl bg-white border border-slate-200 shadow-2xs max-w-sm w-full">
                <p className="text-xs font-semibold text-slate-700 mb-2">No documents indexed yet</p>
                <button
                  onClick={onOpenUpload}
                  className="w-full py-2 px-3 rounded-lg bg-teal-600 hover:bg-teal-700 text-white font-medium text-xs shadow-2xs transition"
                >
                  Upload your first PDF
                </button>
              </div>
            ) : (
              <div className="mt-6 w-full text-left">
                <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-2.5 text-center">
                  Suggested Prompts
                </p>
                <div className="flex flex-col gap-2">
                  {[
                    "What are the main research findings and conclusions?",
                    "Summarize the key methodology and evaluation metrics.",
                    "What are the documented limitations or future work?",
                  ].map((chip) => (
                    <button
                      key={chip}
                      onClick={() => handlePromptChipClick(chip)}
                      className="text-left text-xs p-3 rounded-xl bg-white hover:bg-teal-50/60 border border-slate-200 hover:border-teal-300 text-slate-700 transition shadow-2xs group"
                    >
                      <span className="group-hover:text-teal-800">{chip}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}
          </>
        )}

        {/* Loading state indicator */}
        {isLoading && (
          <div className="flex items-start gap-3 mb-6">
            <div className="w-8 h-8 rounded-xl bg-teal-600 text-white flex items-center justify-center shrink-0 shadow-2xs">
              <Loader2 className="w-4 h-4 animate-spin" />
            </div>
            <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-xs p-4 shadow-xs text-xs text-slate-500 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-teal-500 animate-pulse"></span>
              <span>Retrieving relevant chunks & generating grounded answer...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Error alert banner */}
      {errorMessage && (
        <div className="mx-4 sm:mx-6 mb-2 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center justify-between gap-2 shadow-2xs">
          <div className="flex items-center gap-2 min-w-0">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
            <span className="truncate">{errorMessage}</span>
          </div>
          <button
            onClick={onDismissError}
            className="text-rose-500 hover:text-rose-700 font-semibold text-xs shrink-0"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Input area */}
      <div className="p-3 sm:p-4 bg-white border-t border-slate-200 shrink-0">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto flex items-center gap-2">
          <input
            type="text"
            value={inputQuestion}
            onChange={(e) => setInputQuestion(e.target.value)}
            disabled={isLoading || !hasDocuments}
            placeholder={
              !hasDocuments
                ? "Upload a PDF document first to ask questions..."
                : selectedDocument
                ? `Ask about ${selectedDocument.filename}...`
                : "Ask a question across all uploaded documents..."
            }
            className="flex-1 bg-slate-50 border border-slate-300 focus:border-teal-500 focus:bg-white focus:outline-hidden rounded-xl px-4 py-2.5 text-xs sm:text-sm text-slate-800 placeholder:text-slate-400 disabled:opacity-60 disabled:cursor-not-allowed transition"
          />

          <button
            type="submit"
            disabled={!inputQuestion.trim() || isLoading || !hasDocuments}
            className="p-2.5 sm:px-4 sm:py-2.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-medium text-xs sm:text-sm shadow-xs transition disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1.5 shrink-0"
            aria-label="Send message"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span className="hidden sm:inline">Ask</span>
              </>
            )}
          </button>
        </form>

        <p className="text-[10px] text-slate-400 text-center mt-2">
          ResearchPilot answers strictly using retrieved context passages. Sources are cited with filename and page numbers.
        </p>
      </div>
    </main>
  );
};
