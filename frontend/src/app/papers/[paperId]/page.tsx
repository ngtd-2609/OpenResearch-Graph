"use client";

import { api } from "@/lib/api";
import type { Paper } from "@/types/api";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";

type CitationFormat = "bibtex" | "apa" | "ieee";

export default function PaperPage() {
  const { paperId } = useParams<{ paperId: string }>();
  const [saved, setSaved] = useState(false);
  const [citationFormat, setCitationFormat] = useState<CitationFormat>("bibtex");
  const [copied, setCopied] = useState(false);

  const query = useQuery({
    queryKey: ["paper", paperId],
    queryFn: () => api<Paper>(`/papers/${paperId}`),
    enabled: Boolean(paperId),
  });

  async function savePaper() {
    await api("/library", {
      method: "POST",
      body: JSON.stringify({ paper_id: paperId, collection_name: "Saved", tags: [] }),
    });
    setSaved(true);
  }

  function getCitationText(paper: Paper, format: CitationFormat) {
    const year = paper.publication_year || 2024;
    const author = "OpenAlex Research Team";
    const venue = paper.source_name || "Academic Journal";

    if (format === "apa") {
      return `${author} (${year}). ${paper.title}. ${venue}.`;
    }
    if (format === "ieee") {
      return `[1] ${author}, "${paper.title}," in ${venue}, ${year}.`;
    }
    // BibTeX default
    const cleanId = paper.id.replace(/-/g, "").slice(0, 8);
    return `@article{paper_${cleanId},\n  title={${paper.title}},\n  author={${author}},\n  journal={${venue}},\n  year={${year}},\n  publisher={OpenResearch Graph}\n}`;
  }

  function copyCitation(paper: Paper) {
    const text = getCitationText(paper, citationFormat);
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  if (query.isLoading) {
    return (
      <main className="container text-center py-16">
        <p className="text-lg">Đang tải thông tin chi tiết bài báo…</p>
      </main>
    );
  }

  if (query.error) {
    return (
      <main className="container">
        <p className="error">{query.error.message}</p>
      </main>
    );
  }

  if (!query.data) {
    return (
      <main className="container">
        <p className="muted">Không tìm thấy thông tin bài báo.</p>
      </main>
    );
  }

  const paper = query.data;

  return (
    <main className="container">
      {/* Back button */}
      <div className="mb-4">
        <Link className="link-button text-xs text-muted" href="/search">
          ← Quay lại danh sách tìm kiếm
        </Link>
      </div>

      <article className="card paper-detail-card">
        <header className="paper-detail-header">
          <div className="row wrap gap-2 mb-3">
            <span className="badge">{paper.publication_year ?? "N/A"}</span>
            <span className="badge badge-neutral">
              {paper.cited_by_count.toLocaleString()} citations
            </span>
            {paper.is_open_access ? (
              <span className="badge badge-success">Open Access (Miễn phí)</span>
            ) : (
              <span className="badge">Restricted Access</span>
            )}
            {paper.source_name && (
              <span className="badge badge-neutral">{paper.source_name}</span>
            )}
          </div>

          <h1 className="paper-detail-title">{paper.title}</h1>
        </header>

        {/* Abstract Box */}
        <section className="paper-abstract-section mt-6">
          <h2 className="text-base font-semibold mb-2">Tóm tắt nghiên cứu (Abstract)</h2>
          <div className="paper-abstract-body">
            {paper.abstract ? (
              <p className="leading-relaxed">{paper.abstract}</p>
            ) : (
              <p className="italic muted">
                Nguồn dữ liệu OpenAlex chưa cung cấp văn bản tóm tắt đầy đủ cho bài báo này.
              </p>
            )}
          </div>
        </section>

        {/* Citation Box */}
        <section className="paper-citation-export-box mt-6">
          <div className="row justify-between items-center mb-3">
            <h2 className="text-base font-semibold">Trích dẫn học thuật (Cite)</h2>
            <div className="row gap-1">
              <button
                className={`graph-toolbar-btn ${citationFormat === "bibtex" ? "graph-toolbar-btn-active" : ""}`}
                onClick={() => setCitationFormat("bibtex")}
                type="button"
              >
                BibTeX
              </button>
              <button
                className={`graph-toolbar-btn ${citationFormat === "apa" ? "graph-toolbar-btn-active" : ""}`}
                onClick={() => setCitationFormat("apa")}
                type="button"
              >
                APA
              </button>
              <button
                className={`graph-toolbar-btn ${citationFormat === "ieee" ? "graph-toolbar-btn-active" : ""}`}
                onClick={() => setCitationFormat("ieee")}
                type="button"
              >
                IEEE
              </button>
            </div>
          </div>

          <div className="citation-code-wrapper">
            <pre className="citation-code-block">{getCitationText(paper, citationFormat)}</pre>
            <button
              className="button text-xs citation-copy-btn"
              onClick={() => copyCitation(paper)}
              type="button"
            >
              {copied ? "✓ Đã sao chép" : "📋 Sao chép"}
            </button>
          </div>
        </section>

        {/* Action Toolbar */}
        <footer className="paper-detail-footer mt-8 pt-4 border-t">
          <div className="row wrap justify-between items-center gap-3">
            <div className="row wrap gap-2">
              <button
                className="button"
                disabled={saved}
                onClick={savePaper}
                type="button"
              >
                {saved ? "✓ Đã lưu vào Thư viện" : "+ Lưu vào Thư viện"}
              </button>
              {paper.open_access_url && (
                <a
                  className="secondary-button"
                  href={paper.open_access_url}
                  rel="noreferrer"
                  target="_blank"
                >
                  🔗 Đọc PDF Open Access
                </a>
              )}
            </div>

            <Link
              className="secondary-button text-xs"
              href={`/search?query=${encodeURIComponent(paper.title)}`}
            >
              🔍 Tìm các bài báo liên quan
            </Link>
          </div>
        </footer>
      </article>
    </main>
  );
}
