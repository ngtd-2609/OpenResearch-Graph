"use client";

import AuthGuard from "@/components/auth-guard";
import { api } from "@/lib/api";
import type { ChatAnswer, DocumentItem } from "@/types/api";
import ReactMarkdown from "react-markdown";
import { useState } from "react";

const POLL_INTERVAL_MS = 1_500;
const MAX_POLL_ATTEMPTS = 80;

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
  const [question, setQuestion] = useState("Tài liệu này giải quyết vấn đề gì?");
  const [answer, setAnswer] = useState<ChatAnswer | null>(null);
  const [status, setStatus] = useState("Chưa có tài liệu được tải lên.");
  const [busy, setBusy] = useState(false);

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
      setStatus(`Đã tải ${uploaded.filename}. Đang chờ worker xử lý…`);
      const document = await waitForDocument(uploaded.id, (current) => {
        const pageText = current.pages ? ` · ${current.pages} trang` : "";
        setStatus(`Trạng thái: ${current.status}${pageText}`);
      });
      const session = await api<{ id: string }>("/chat/sessions", {
        method: "POST",
        body: JSON.stringify({ document_id: document.id, title: document.filename }),
      });
      setSessionId(session.id);
      setStatus("Tài liệu đã sẵn sàng để đặt câu hỏi.");
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
          <h1>Chatbot đọc PDF</h1>
          <p className="muted">Hybrid retrieval, reranking và trích dẫn theo đúng trang tài liệu.</p>
        </div>
      </header>
      <div className="grid two-columns">
        <section className="card stack">
          <h2>1. Tải tài liệu</h2>
          <input type="file" accept="application/pdf" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
          <button className="button" disabled={!file || busy} onClick={upload} type="button">
            {busy && !sessionId ? "Đang xử lý…" : "Tải và xử lý PDF"}
          </button>
          <p className="muted" role="status">{status}</p>
        </section>
        <section className="card stack">
          <h2>2. Đặt câu hỏi</h2>
          <label>
            Câu hỏi
            <textarea className="input" value={question} onChange={(event) => setQuestion(event.target.value)} />
          </label>
          <button className="button" disabled={!sessionId || busy} onClick={ask} type="button">
            {busy && sessionId ? "Đang truy xuất…" : "Hỏi tài liệu"}
          </button>
          {answer && (
            <div className="answer-panel">
              <div className="answer-meta">Model: {answer.model} · {answer.latency_ms} ms</div>
              <ReactMarkdown>{answer.answer}</ReactMarkdown>
              <h3>Nguồn được truy xuất</h3>
              <ol className="citation-list">
                {answer.citations.map((citation) => (
                  <li key={citation.chunk_id}>
                    <strong>Trang {citation.page}</strong> · score {citation.score.toFixed(3)}
                    <blockquote>{citation.quote}</blockquote>
                  </li>
                ))}
              </ol>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}

export default function ChatPage() {
  return <AuthGuard><ChatContent /></AuthGuard>;
}
