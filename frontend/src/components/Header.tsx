import React from "react";
import { Bot, FileText, Menu, RefreshCw, Server, X } from "lucide-react";

interface HeaderProps {
  backendOnline: boolean | null;
  onRefreshHealth: () => void;
  isCheckingHealth: boolean;
  mobileMenuOpen: boolean;
  onToggleMobileMenu: () => void;
  documentCount: number;
}

export const Header: React.FC<HeaderProps> = ({
  backendOnline,
  onRefreshHealth,
  isCheckingHealth,
  mobileMenuOpen,
  onToggleMobileMenu,
  documentCount,
}) => {
  return (
    <header className="bg-white border-b border-slate-200 px-4 sm:px-6 py-3 flex items-center justify-between shrink-0">
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleMobileMenu}
          className="sm:hidden p-1.5 text-slate-600 hover:text-slate-900 rounded-lg hover:bg-slate-100"
          aria-label="Toggle navigation menu"
        >
          {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>

        <div className="w-9 h-9 rounded-xl bg-teal-600 flex items-center justify-center text-white shadow-sm shadow-teal-700/20">
          <Bot className="w-5 h-5" />
        </div>

        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-base font-bold text-slate-900 leading-tight">
              ResearchPilot AI
            </h1>
            <span className="hidden sm:inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-teal-50 text-teal-700 border border-teal-200">
              Stage 2
            </span>
          </div>
          <p className="text-xs text-slate-500 hidden sm:block">
            Evidence-Grounded Document Intelligence Platform
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2 sm:gap-3">
        {/* Document count pill */}
        <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700 text-xs font-medium">
          <FileText className="w-3.5 h-3.5 text-slate-500" />
          <span>
            {documentCount} {documentCount === 1 ? "doc" : "docs"} indexed
          </span>
        </div>

        {/* Backend health status badge */}
        <div className="flex items-center gap-2 px-3 py-1 rounded-lg border border-slate-200 bg-slate-50 text-xs">
          <Server className="w-3.5 h-3.5 text-slate-400" />
          <span className="font-medium text-slate-600 hidden sm:inline">Backend:</span>
          {backendOnline === null ? (
            <span className="flex items-center gap-1.5 text-slate-500 font-medium">
              <span className="w-2 h-2 rounded-full bg-slate-400 animate-pulse"></span>
              Checking
            </span>
          ) : backendOnline ? (
            <span className="flex items-center gap-1.5 text-emerald-600 font-medium">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              Online
            </span>
          ) : (
            <span className="flex items-center gap-1.5 text-rose-600 font-medium">
              <span className="w-2 h-2 rounded-full bg-rose-500"></span>
              Offline
            </span>
          )}

          <button
            onClick={onRefreshHealth}
            disabled={isCheckingHealth}
            title="Check backend connectivity"
            className="p-0.5 text-slate-400 hover:text-slate-600 rounded transition disabled:opacity-50"
          >
            <RefreshCw className={`w-3 h-3 ${isCheckingHealth ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>
    </header>
  );
};
