import React, { useEffect, useState } from "react";
import { Header } from "./components/Header";
import { Sidebar } from "./components/Sidebar";
import { ChatArea } from "./components/ChatArea";
import { DocumentUploadModal } from "./components/DocumentUploadModal";
import { api } from "./services/api";
import {
  ChatMessageItem,
  DocumentUploadResponse,
  UploadedDocumentRecord,
} from "./types";

const STORAGE_KEY_DOCS = "researchpilot_documents";

export const App: React.FC = () => {
  const [documents, setDocuments] = useState<UploadedDocumentRecord[]>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_DOCS);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessageItem[]>([]);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);
  const [isCheckingHealth, setIsCheckingHealth] = useState(false);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Sync documents to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY_DOCS, JSON.stringify(documents));
    } catch {
      // Ignore storage errors
    }
  }, [documents]);

  const checkHealth = async () => {
    setIsCheckingHealth(true);
    try {
      await api.checkHealth();
      setBackendOnline(true);
    } catch {
      setBackendOnline(false);
    } finally {
      setIsCheckingHealth(false);
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleUploadSuccess = (result: DocumentUploadResponse) => {
    const newDoc: UploadedDocumentRecord = {
      document_id: result.document_id,
      filename: result.filename,
      file_size_bytes: result.file_size_bytes,
      page_count: result.page_count,
      total_chunks: result.total_chunks,
      uploaded_at: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setDocuments((prev) => [newDoc, ...prev.filter((d) => d.document_id !== newDoc.document_id)]);
    setSelectedDocumentId(newDoc.document_id);

    // Add notification in chat thread
    setMessages((prev) => [
      ...prev,
      {
        id: `sys-${Date.now()}`,
        role: "assistant",
        content: `Document **${newDoc.filename}** (${newDoc.page_count} pages, ${newDoc.total_chunks} chunks) was successfully uploaded and indexed into ChromaDB. You can now ask questions about it!`,
        has_sufficient_evidence: true,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      },
    ]);
  };

  const handleDeleteDocument = async (docId: string) => {
    const docToDelete = documents.find((d) => d.document_id === docId);
    if (!docToDelete) return;

    if (!window.confirm(`Delete "${docToDelete.filename}" and its vector embeddings?`)) {
      return;
    }

    try {
      await api.deleteDocument(docId);
      setDocuments((prev) => prev.filter((d) => d.document_id !== docId));
      if (selectedDocumentId === docId) {
        setSelectedDocumentId(null);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to delete document";
      setErrorMessage(msg);
    }
  };

  const handleSendMessage = async (question: string) => {
    const userMessage: ChatMessageItem = {
      id: `user-${Date.now()}`,
      role: "user",
      content: question,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsChatLoading(true);
    setErrorMessage(null);

    try {
      const response = await api.askQuestion({
        question,
        document_id: selectedDocumentId || undefined,
        top_k: 5,
      });

      const assistantMessage: ChatMessageItem = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: response.answer,
        citations: response.citations,
        evidence: response.evidence,
        has_sufficient_evidence: response.has_sufficient_evidence,
        model: response.model,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: unknown) {
      const errorText =
        err instanceof Error
          ? err.message
          : "An unexpected error occurred while communicating with the backend.";
      setErrorMessage(errorText);

      // Also append error message to chat
      setMessages((prev) => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          role: "assistant",
          content: `⚠️ Error: ${errorText}`,
          has_sufficient_evidence: false,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } finally {
      setIsChatLoading(false);
    }
  };

  const selectedDocObj = documents.find((d) => d.document_id === selectedDocumentId) || null;

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-slate-50 font-sans">
      <Header
        backendOnline={backendOnline}
        onRefreshHealth={checkHealth}
        isCheckingHealth={isCheckingHealth}
        mobileMenuOpen={mobileMenuOpen}
        onToggleMobileMenu={() => setMobileMenuOpen(!mobileMenuOpen)}
        documentCount={documents.length}
      />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          documents={documents}
          selectedDocumentId={selectedDocumentId}
          onSelectDocument={(id) => {
            setSelectedDocumentId(id);
            setMobileMenuOpen(false);
          }}
          onDeleteDocument={handleDeleteDocument}
          onOpenUpload={() => {
            setIsUploadModalOpen(true);
            setMobileMenuOpen(false);
          }}
          isOpenMobile={mobileMenuOpen}
          onCloseMobile={() => setMobileMenuOpen(false)}
        />

        <ChatArea
          messages={messages}
          onSendMessage={handleSendMessage}
          isLoading={isChatLoading}
          selectedDocument={selectedDocObj}
          onClearDocumentFilter={() => setSelectedDocumentId(null)}
          hasDocuments={documents.length > 0}
          onOpenUpload={() => setIsUploadModalOpen(true)}
          errorMessage={errorMessage}
          onDismissError={() => setErrorMessage(null)}
        />
      </div>

      <DocumentUploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onUploadSuccess={handleUploadSuccess}
      />
    </div>
  );
};
export default App;
