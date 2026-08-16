"use client";

import AuthGuard from "@/components/auth-guard";
import DeepResearchPanel from "@/components/deep-research-panel";
import { api } from "@/lib/api";
import type { ChatAnswer, DocumentItem } from "@/types/api";
import { useEffect, useState } from "react";

const POLL_INTERVAL_MS = 1_200;
const MAX_POLL_ATTEMPTS = 80;

const SUGGESTED_PROMPTS = [
  "Tóm tắt các đóng góp chính và phương pháp của bài báo",
  "Tập dữ liệu và kết quả thực nghiệm đạt được là gì?",
  "So sánh ưu điểm và nhược điểm của giải pháp trong tài liệu",
  "Các hạn chế (limitations) và hướng nghiên cứu tương lai",
];

type ChatSessionItem = {
  id: string;
  title: string;
  document_id: string;
  updated_at: string;
};

type ChatMessageItem = {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations: Array<{ document_id: string; page: number; chunk_id: string; quote: string; score: number }>;
  created_at: string;
};

function sleep(milliseconds: number) {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}

async function waitForDocument(documentId: string, onStatus: (document: DocumentItem) => void) {
  for (let attempt = 0; attempt < MAX_POLL_ATTEMPTS; attempt += 1) {
    const document = await api<DocumentItem>(`/documents/${documentId}`);
    onStatus(document);
    if (document.status === "completed") return document;
    if (document.status === "failed" || document.status === "canceled") {
      throw new Error(document.error || `Xử lý tài liệu kết thúc với trạng thái ${document.status}`);
    }
    await sleep(POLL_INTERVAL_MS);
  }
  throw new Error("Xử lý PDF quá thời gian chờ. Bạn có thể kiểm tra lại trang sau.");
}

function ChatContent() {
  const [file, setFile] = useState<File | null>(null);
  const [sessionId, setSessionId] = useState("");
  const [documentName, setDocumentName] = useState("");
  const [question, setQuestion] = useState("Tóm tắt các đóng góp chính và phương pháp của bài báo");
  const [answer, setAnswer] = useState<ChatAnswer | null>(null);
  const [status, setStatus] = useState("Chưa có tài liệu được tải lên.");
  const [busy, setBusy] = useState(false);
  const [isDeepResearch, setIsDeepResearch] = useState(true);
  const [existingDocs, setExistingDocs] = useState<DocumentItem[]>([]);
  const [chatSessions, setChatSessions] = useState<ChatSessionItem[]>([]);
  const [sessionMessages, setSessionMessages] = useState<ChatMessageItem[]>([]);
  const [showSessions, setShowSessions] = useState(false);

  useEffect(() => {
    api<DocumentItem[]>("/documents")
      .then((docs) => {
        setExistingDocs(docs.filter((d) => d.status === "completed"));
      })
      .catch(() => {});
    api<ChatSessionItem[]>("/chat/sessions")
      .then((sessions) => {
        setChatSessions(sessions);
      })
      .catch(() => {});
  }, []);

  async function loadSession(session: ChatSessionItem) {
    setBusy(true);
    setAnswer(null);
    setSessionMessages([]);
    try {
      const data = await api<{
        id: string;
        title: string;
        document_id: string;
        messages: ChatMessageItem[];
      }>(`/chat/sessions/${session.id}`);
      setSessionId(data.id);
      setDocumentName(data.title);
      setSessionMessages(data.messages);
      setStatus(`Đã mở phiên chat: "${data.title}"`);
      // Show the last assistant answer if available
      const lastAssistant = [...data.messages].reverse().find((m) => m.role === "assistant");
      if (lastAssistant) {
        setAnswer({
          answer: lastAssistant.content,
          citations: lastAssistant.citations,
          model: "qwen3:4b (Ollama)",
          latency_ms: 0,
        });
      }
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Không thể mở phiên chat");
    } finally {
      setBusy(false);
    }
  }

  async function deleteSession(sessionIdToDelete: string) {
    try {
      await api(`/chat/sessions/${sessionIdToDelete}`, { method: "DELETE" });
      setChatSessions((prev) => prev.filter((s) => s.id !== sessionIdToDelete));
      if (sessionId === sessionIdToDelete) {
        setSessionId("");
        setDocumentName("");
        setAnswer(null);
        setSessionMessages([]);
        setStatus("Phiên chat đã bị xóa.");
      }
    } catch (error) {
      alert(error instanceof Error ? error.message : "Không thể xóa phiên chat");
    }
  }

  async function selectExistingDoc(doc: DocumentItem) {
    setBusy(true);
    setStatus(`Đang mở tài liệu: ${doc.filename}...`);
    try {
      const session = await api<{ id: string }>("/chat/sessions", {
        method: "POST",
        body: JSON.stringify({ document_id: doc.id, title: doc.filename }),
      });
      setSessionId(session.id);
      setDocumentName(doc.filename);
      setSessionMessages([]);
      setAnswer(null);
      setStatus(`Đã sẵn sàng chat với tài liệu "${doc.filename}"`);
      // Refresh session list
      setChatSessions((prev) => [
        { id: session.id, title: doc.filename, document_id: doc.id, updated_at: new Date().toISOString() },
        ...prev,
      ]);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Không thể chọn tài liệu");
    } finally {
      setBusy(false);
    }
  }

  async function upload() {
    if (!file) return;
    setBusy(true);
    setAnswer(null);
    setSessionMessages([]);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const uploaded = await api<{ id: string; filename: string; status: string }>("/documents/upload", {
        method: "POST",
        body: formData,
      });
      setStatus(`Đã tải ${uploaded.filename}. Đang tách chunk và trích xuất vector...`);
      const document = await waitForDocument(uploaded.id, (current) => {
        const pageText = current.pages ? ` · ${current.pages} trang` : "";
        setStatus(`Trạng thái xử lý: ${current.status}${pageText}`);
      });
      const session = await api<{ id: string }>("/chat/sessions", {
        method: "POST",
        body: JSON.stringify({ document_id: document.id, title: document.filename }),
      });
      setSessionId(session.id);
      setDocumentName(document.filename);
      setStatus("Tài liệu đã sẵn sàng để đối thoại chuyên sâu.");
      // Refresh session list
      setChatSessions((prev) => [
        { id: session.id, title: document.filename, document_id: document.id, updated_at: new Date().toISOString() },
        ...prev,
      ]);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Không thể xử lý tài liệu");
    } finally {
      setBusy(false);
    }
  }

  async function ask() {
    if (!sessionId || !question.trim()) return;
    setBusy(true);
    try {
      const response = await api<ChatAnswer>(`/chat/sessions/${sessionId}/messages`, {
        method: "POST",
        body: JSON.stringify({ question: question.trim() }),
      });
      setAnswer(response);
      // Append new messages to session history
      const now = new Date().toISOString();
      setSessionMessages((prev) => [
        ...prev,
        { id: `user-${Date.now()}`, role: "user", content: question.trim(), citations: [], created_at: now },
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: response.answer,
          citations: response.citations,
          created_at: now,
        },
      ]);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Không thể gửi câu hỏi");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="container">
      <header className="page-header">
        <div>
          <h1>Trợ lý Nghiên cứu &amp; Deep Research RAG</h1>
          <p className="muted">
            Truy xuất thông minh đa tầng, kiểm chứng dẫn chứng chính xác theo trang PDF.
          </p>
        </div>
        <button
          className="secondary-button"
          onClick={() => setShowSessions((v) => !v)}
          type="button"
        >
          {showSessions ? "Ẩn lịch sử" : `📋 Lịch sử (${chatSessions.length})`}
        </button>
      </header>

      {showSessions && chatSessions.length > 0 && (
        <section className="card mb-4">
          <h2 className="text-sm font-semibold mb-2">Các phiên chat trước đó</h2>
          <div className="stack gap-2" style={{ maxHeight: "300px", overflowY: "auto" }}>
            {chatSessions.map((session) => (
              <div
                key={session.id}
                className="row gap-2"
                style={{ alignItems: "center", justifyContent: "space-between" }}
              >
                <button
                  className={`secondary-button text-xs text-left flex-1 ${sessionId === session.id ? "border-primary" : ""}`}
                  onClick={() => loadSession(session)}
                  type="button"
                  style={{ minWidth: 0 }}
                >
                  <span style={{ fontWeight: 500 }}>💬 {session.title}</span>
                  <span className="muted" style={{ marginLeft: "8px", fontSize: "0.7rem" }}>
                    {new Date(session.updated_at).toLocaleDateString("vi-VN", {
                      day: "2-digit",
                      month: "2-digit",
                      year: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                </button>
                <button
                  className="secondary-button text-xs"
                  onClick={() => deleteSession(session.id)}
                  title="Xóa phiên chat"
                  type="button"
                  style={{ flexShrink: 0 }}
                >
                  🗑️
                </button>
              </div>
            ))}
          </div>
        </section>
      )}

      {showSessions && chatSessions.length === 0 && (
        <section className="card mb-4">
          <p className="muted text-sm">Chưa có phiên chat nào.</p>
        </section>
      )}

      <div className="grid two-columns">
        <section className="card stack">
          <h2>1. Tải hoặc Chọn Tài liệu PDF</h2>
          <input
            type="file"
            accept="application/pdf"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
          <button className="button" disabled={!file || busy} onClick={upload} type="button">
            {busy && !sessionId ? "Đang xử lý & Vector hóa…" : "Tải lên & Phân tích PDF"}
          </button>

          {existingDocs.length > 0 && (
            <div className="mt-4 border-t pt-3">
              <label className="text-xs font-semibold muted block mb-2">
                Hoặc chọn tài liệu đã tải lên trước đó:
              </label>
              <div className="stack gap-2">
                {existingDocs.map((doc) => (
                  <button
                    key={doc.id}
                    className={`secondary-button text-xs text-left ${documentName === doc.filename ? "border-primary" : ""}`}
                    onClick={() => selectExistingDoc(doc)}
                    type="button"
                  >
                    📄 {doc.filename} ({doc.pages ?? 1} trang)
                  </button>
                ))}
              </div>
            </div>
          )}

          <p className="muted text-sm" role="status">{status}</p>
        </section>

        <section className="card stack">
          <h2>2. Đặt Câu hỏi Nghiên cứu</h2>
          {documentName && (
            <div className="text-xs muted">
              Đang làm việc với: <strong className="text-primary">{documentName}</strong>
            </div>
          )}

          <label>
            Nội dung cần phân tích / tóm tắt
            <textarea
              className="input"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Nhập câu hỏi nghiên cứu..."
            />
          </label>

          <div className="row wrap gap-2 mt-1">
            <span className="text-xs muted">Gợi ý nhanh:</span>
            {SUGGESTED_PROMPTS.map((prompt, idx) => (
              <button
                key={idx}
                className="citation-pill text-xs"
                onClick={() => setQuestion(prompt)}
                type="button"
              >
                {prompt.slice(0, 32)}...
              </button>
            ))}
          </div>

          <button
            className="button"
            disabled={!sessionId || busy}
            onClick={ask}
            type="button"
          >
            {busy && sessionId ? "Đang suy luận & đối chiếu nguồn…" : "Phân tích & Trả lời"}
          </button>
        </section>
      </div>

      {sessionMessages.length > 0 && (
        <section className="card mt-4">
          <h2 className="text-sm font-semibold mb-2">Lịch sử hội thoại</h2>
          <div className="stack gap-3" style={{ maxHeight: "400px", overflowY: "auto" }}>
            {sessionMessages.map((msg) => (
              <div
                key={msg.id}
                style={{
                  padding: "8px 12px",
                  borderRadius: "8px",
                  background: msg.role === "user" ? "var(--surface-alt, #f0f4ff)" : "var(--surface, #fff)",
                  borderLeft: msg.role === "assistant" ? "3px solid var(--primary, #3b82f6)" : "none",
                }}
              >
                <div className="text-xs muted mb-1" style={{ fontWeight: 600 }}>
                  {msg.role === "user" ? "🧑 Bạn" : "🤖 Trợ lý"}
                  <span style={{ marginLeft: "8px", fontWeight: 400 }}>
                    {new Date(msg.created_at).toLocaleTimeString("vi-VN")}
                  </span>
                </div>
                <div className="text-sm" style={{ whiteSpace: "pre-wrap" }}>{msg.content}</div>
              </div>
            ))}
          </div>
        </section>
      )}

      <DeepResearchPanel
        query={question}
        answer={answer ? answer.answer : null}
        citations={answer ? answer.citations : []}
        model={answer ? answer.model : "qwen3:4b (Ollama)"}
        latencyMs={answer ? answer.latency_ms : 0}
        isDeepResearch={isDeepResearch}
        onToggleDeepResearch={setIsDeepResearch}
      />
    </main>
  );
}

export default function ChatPage() {
  return (
    <AuthGuard>
      <ChatContent />
    </AuthGuard>
  );
}
