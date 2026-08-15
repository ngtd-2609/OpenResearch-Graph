"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

const STATS = [
  { value: "600+", label: "Bài báo khoa học đã nạp", desc: "OpenAlex & ArXiv Corpus" },
  { value: "384-dim", label: "Vector Embeddings", desc: "pgvector HNSW Semantic Search" },
  { value: "< 100ms", label: "Thời gian suy luận", desc: "Tối ưu đa luồng SIMD & In-Memory" },
  { value: "100%", label: "Dẫn chứng kiểm chứng", desc: "Grounded Page-level RAG" },
];

const WORKFLOW_STEPS = [
  {
    step: "01",
    title: "Tìm kiếm Đa chiều (Hybrid Search)",
    desc: "Kết hợp Full-Text Search từ khóa chính xác và Vector Embedding ngữ nghĩa, tự động xếp hạng bằng Cross-Encoder.",
    link: "/search",
    action: "Tìm bài báo →",
  },
  {
    step: "02",
    title: "Bảng So sánh Đối chiếu (Matrix)",
    desc: "Chọn nhiều bài báo để đối chiếu song song về phương pháp, số lượt trích dẫn, quyền truy cập và tóm tắt thực nghiệm.",
    link: "/search",
    action: "Mở bảng so sánh →",
  },
  {
    step: "03",
    title: "Mạng lưới Đồ thị Trích dẫn (Graph)",
    desc: "Trực quan hóa quan hệ trích dẫn giữa các công trình khoa học bằng Cytoscape.js và thuật toán Personalized PageRank.",
    link: "/graph",
    action: "Khám phá đồ thị →",
  },
  {
    step: "04",
    title: "Deep Research RAG & Báo cáo Dossier",
    desc: "Tải file PDF lên để AI phân rã câu hỏi, đối chiếu chéo theo trang và xuất báo cáo tổng quan dạng Markdown.",
    link: "/chat",
    action: "Khởi chạy RAG Chat →",
  },
];

const POPULAR_QUERIES = [
  "Attention mechanism in Transformers",
  "Retrieval-Augmented Generation evaluation",
  "Graph Neural Networks for node classification",
  "Deep learning stochastic optimization",
];

export default function HomePage() {
  const router = useRouter();
  const [heroQuery, setHeroQuery] = useState("");

  function handleSearch(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (heroQuery.trim()) {
      router.push(`/search?query=${encodeURIComponent(heroQuery.trim())}`);
    } else {
      router.push("/search");
    }
  }

  return (
    <main className="container home-container">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-badge">
          <span>✨ Nền tảng Trí tuệ Nghiên cứu Khoa học Thông minh</span>
        </div>
        <h1 className="hero-title">
          Khám phá, Đối chiếu & Trích xuất Tri thức Khoa học
        </h1>
        <p className="hero-subtitle">
          Tích hợp Hybrid Semantic Search, Đồ thị trích dẫn học thuật và Trợ lý Deep Research RAG kiểm chứng theo từng trang PDF.
        </p>

        {/* Hero Interactive Search Bar */}
        <form className="hero-search-form" onSubmit={handleSearch}>
          <div className="hero-search-wrapper">
            <span className="hero-search-icon">🔍</span>
            <input
              className="hero-search-input"
              value={heroQuery}
              onChange={(e) => setHeroQuery(e.target.value)}
              placeholder="Nhập chủ đề nghiên cứu (ví dụ: vision transformer, RAG evaluation...)"
            />
            <button className="button hero-search-button" type="submit">
              Khám phá ngay
            </button>
          </div>
        </form>

        <div className="hero-tags">
          <span className="text-xs muted">Gợi ý tra cứu:</span>
          {POPULAR_QUERIES.map((q) => (
            <button
              key={q}
              className="citation-pill text-xs"
              onClick={() => router.push(`/search?query=${encodeURIComponent(q)}`)}
              type="button"
            >
              {q}
            </button>
          ))}
        </div>
      </section>

      {/* Live Metrics Grid */}
      <section className="metrics-grid" aria-label="Chỉ số hiệu năng">
        {STATS.map((s, idx) => (
          <div key={idx} className="metric-card">
            <div className="metric-value">{s.value}</div>
            <div className="metric-label">{s.label}</div>
            <div className="metric-desc muted text-xs">{s.desc}</div>
          </div>
        ))}
      </section>

      {/* Workflow Section */}
      <section className="workflow-section">
        <div className="section-header text-center">
          <h2>Quy trình Nghiên cứu Khoa học Thông minh</h2>
          <p className="muted">
            Từ tìm kiếm tài liệu đến tổng hợp báo cáo đối chiếu chỉ trong vài phút.
          </p>
        </div>

        <div className="grid workflow-grid">
          {WORKFLOW_STEPS.map((step) => (
            <article key={step.step} className="card workflow-card">
              <div className="workflow-number">{step.step}</div>
              <h3>{step.title}</h3>
              <p className="muted text-sm">{step.desc}</p>
              <Link className="workflow-link" href={step.link}>
                {step.action}
              </Link>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
