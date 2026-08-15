"use client";

import type { Citation } from "@/types/api";
import { useState } from "react";
import ReactMarkdown from "react-markdown";

interface DeepResearchStep {
  title: string;
  detail: string;
  done: boolean;
}

interface DeepResearchPanelProps {
  query: string;
  answer: string | null;
  citations: Citation[];
  model: string;
  latencyMs: number;
  isDeepResearch: boolean;
  onToggleDeepResearch: (active: boolean) => void;
  onCitationClick?: (citation: Citation) => void;
}

export default function DeepResearchPanel({
  query,
  answer,
  citations,
  model,
  latencyMs,
  isDeepResearch,
  onToggleDeepResearch,
  onCitationClick,
}: DeepResearchPanelProps) {
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);

  const steps: DeepResearchStep[] = [
    {
      title: "1. Phân rã câu hỏi nghiên cứu",
      detail: `Chia nhỏ chủ đề "${query || "..."}" thành các truy vấn thành phần: lý thuyết, phương pháp, thực nghiệm.`,
      done: Boolean(answer),
    },
    {
      title: "2. Truy xuất đa chiều & Reranking",
      detail: `Tìm kiếm vector 384 chiều, lọc FTS và xếp hạng lại bằng Cross-Encoder trên toàn bộ tài liệu.`,
      done: Boolean(answer),
    },
    {
      title: "3. Tổng hợp Báo cáo Toàn diện (Dossier)",
      detail: `Mô hình ${model || "LLM"} lập luận chặt chẽ và gắn dẫn chứng trang chính xác (Grounding).`,
      done: Boolean(answer),
    },
  ];

  function handleCitationClick(citation: Citation) {
    setSelectedCitation(citation);
    if (onCitationClick) onCitationClick(citation);
  }

  function exportDossier() {
    if (!answer) return;
    const content = `# Báo cáo Nghiên cứu Chuyên sâu (Deep Research Dossier)\n\n**Chủ đề:** ${query}\n**Thời gian:** ${new Date().toLocaleString("vi-VN")}\n**Mô hình:** ${model} (${latencyMs} ms)\n\n---\n\n## 1. Kết quả Tổng hợp\n\n${answer}\n\n---\n\n## 2. Danh mục Dẫn chứng Nguồn (Citations)\n\n${citations.map((c) => `- **Trang ${c.page}** (Score: ${c.score.toFixed(3)}):\n  > "${c.quote}"`).join("\n\n")}\n`;
    const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `Deep_Research_Dossier_${Date.now()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="deep-research-container">
      <div className="card research-mode-toggle-card">
        <div className="row wrap justify-between items-center">
          <div>
            <div className="row items-center gap-2">
              <span className={`status-indicator ${isDeepResearch ? "status-active" : "status-idle"}`} />
              <strong>Chế độ Deep Research Multi-step Agent</strong>
            </div>
            <p className="muted text-sm mt-1">
              {isDeepResearch
                ? "Bật: Tự động phân rã câu hỏi, đối chiếu chéo nhiều trang và tổng hợp báo cáo chi tiết."
                : "Tắt: Hỏi đáp nhanh đơn lẻ."}
            </p>
          </div>
          <button
            className={isDeepResearch ? "button" : "secondary-button"}
            onClick={() => onToggleDeepResearch(!isDeepResearch)}
            type="button"
          >
            {isDeepResearch ? "Đang bật Deep Mode" : "Bật Deep Mode"}
          </button>
        </div>

        {isDeepResearch && (
          <div className="research-stepper mt-4">
            {steps.map((step, idx) => (
              <div key={idx} className={`stepper-item ${step.done ? "step-done" : "step-pending"}`}>
                <div className="stepper-circle">{step.done ? "✓" : idx + 1}</div>
                <div className="stepper-content">
                  <div className="stepper-title">{step.title}</div>
                  <div className="stepper-detail muted text-xs">{step.detail}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {answer && (
        <article className="card answer-dossier-card mt-4">
          <div className="row wrap justify-between items-center pb-3 border-b">
            <div className="answer-meta text-xs">
              <span className="badge">Mô hình: {model}</span>
              <span className="badge">Thời gian: {latencyMs} ms</span>
              <span className="badge badge-success">{citations.length} Dẫn chứng gốc</span>
            </div>
            <button className="secondary-button text-xs" onClick={exportDossier} type="button">
              📥 Xuất Báo cáo Markdown
            </button>
          </div>

          <div className="answer-prose mt-4">
            <ReactMarkdown>{answer}</ReactMarkdown>
          </div>

          <div className="citations-section mt-6">
            <h3 className="text-sm font-semibold mb-3">Dẫn chứng Trang Đã Được Kiểm Chứng:</h3>
            <div className="citation-pills-row">
              {citations.map((c, idx) => (
                <button
                  key={c.chunk_id || idx}
                  className={`citation-pill ${selectedCitation?.chunk_id === c.chunk_id ? "citation-pill-active" : ""}`}
                  onClick={() => handleCitationClick(c)}
                  type="button"
                >
                  📄 Trang {c.page} (Score {c.score.toFixed(2)})
                </button>
              ))}
            </div>

            {selectedCitation && (
              <div className="citation-quote-box mt-3">
                <div className="row justify-between text-xs text-muted mb-1">
                  <span>Trích dẫn từ trang {selectedCitation.page}:</span>
                  <span>Độ tin cậy: {(selectedCitation.score * 100).toFixed(1)}%</span>
                </div>
                <blockquote>&ldquo;{selectedCitation.quote}&rdquo;</blockquote>
              </div>
            )}
          </div>
        </article>
      )}
    </div>
  );
}
