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

  useEffect(() => {
    api<DocumentItem[]>("/documents")
      .then((docs) => {
        setExistingDocs(docs.filter((d) => d.status === "completed"));
      })
      .catch(() => {});
  }, []);

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
      setStatus(`Đã sẵn sàng chat với tài liệu "${doc.filename}"`);
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
          <h1>Trợ lý Nghiên cứu & Deep Research RAG</h1>
          <p className="muted">
            Truy xuất thông minh đa tầng, kiểm chứng dẫn chứng chính xác theo trang PDF.
          </p>
        </div>
      </header>

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
