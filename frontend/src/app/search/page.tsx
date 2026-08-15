"use client";

import PaperComparisonMatrix from "@/components/paper-comparison-matrix";
import { api } from "@/lib/api";
import type { PaginatedPapers, Paper } from "@/types/api";
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { FormEvent, useMemo, useState } from "react";

const PER_PAGE = 10;

const QUICK_TOPICS = [
  "Deep Learning",
  "Transformer",
  "Retrieval-Augmented Generation",
  "Graph Neural Networks",
  "Explainable AI",
  "Recommender Systems",
];

export default function SearchPage() {
  const [draft, setDraft] = useState("deep learning");
  const [query, setQuery] = useState("deep learning");
  const [page, setPage] = useState(1);
  const [fromYear, setFromYear] = useState("");
  const [toYear, setToYear] = useState("");
  const [openAccess, setOpenAccess] = useState(false);
  const [saved, setSaved] = useState<Record<string, boolean>>({});
  const [selectedForCompare, setSelectedForCompare] = useState<Paper[]>([]);

  const searchPath = useMemo(() => {
    const parameters = new URLSearchParams({
      query,
      page: String(page),
      per_page: String(PER_PAGE),
    });
    if (fromYear) parameters.set("from_year", fromYear);
    if (toYear) parameters.set("to_year", toYear);
    if (openAccess) parameters.set("open_access", "true");
    return `/search/papers?${parameters.toString()}`;
  }, [fromYear, openAccess, page, query, toYear]);

  const result = useQuery({
    queryKey: ["papers", searchPath],
    queryFn: () => api<PaginatedPapers>(searchPath),
    placeholderData: keepPreviousData,
    enabled: query.trim().length >= 2,
  });

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPage(1);
    setQuery(draft.trim());
  }

  function applyQuickTopic(topic: string) {
    setDraft(topic);
    setQuery(topic);
    setPage(1);
  }

  async function savePaper(paper: Paper) {
    await api("/library", {
      method: "POST",
      body: JSON.stringify({ paper_id: paper.id, collection_name: "Saved", tags: [] }),
    });
    setSaved((current) => ({ ...current, [paper.id]: true }));
  }

  function toggleCompare(paper: Paper) {
    setSelectedForCompare((prev) => {
      const exists = prev.some((p) => p.id === paper.id);
      if (exists) return prev.filter((p) => p.id !== paper.id);
      if (prev.length >= 4) {
        alert("Bạn có thể so sánh tối đa 4 bài báo cùng lúc.");
        return prev;
      }
      return [...prev, paper];
    });
  }

  function removeCompare(paperId: string) {
    setSelectedForCompare((prev) => prev.filter((p) => p.id !== paperId));
  }

  const totalPages = Math.max(1, Math.ceil((result.data?.total ?? 0) / PER_PAGE));

  return (
    <main className="container">
      <header className="page-header">
        <div>
          <h1>Tìm kiếm & Phân tích Bài báo Khoa học</h1>
          <p className="muted">
            Hybrid Search đa chiều (pgvector + FTS + Reranking) & Bảng so sánh tương tác.
          </p>
        </div>
      </header>

      <form className="card search-form" onSubmit={submit}>
        <label className="search-query">
          Chủ đề / Từ khóa nghiên cứu
          <input
            className="input"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            minLength={2}
            placeholder="Ví dụ: attention mechanism, graph neural network..."
            required
          />
        </label>
        <label>
          Từ năm
          <input
            className="input"
            type="number"
            min="1900"
            value={fromYear}
            onChange={(event) => setFromYear(event.target.value)}
          />
        </label>
        <label>
          Đến năm
          <input
            className="input"
            type="number"
            min="1900"
            value={toYear}
            onChange={(event) => setToYear(event.target.value)}
          />
        </label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={openAccess}
            onChange={(event) => setOpenAccess(event.target.checked)}
          />
          Chỉ Open Access
        </label>
        <button className="button" type="submit">Tìm kiếm</button>
      </form>

      <div className="row wrap gap-2 mt-3">
        <span className="text-xs muted self-center">Chủ đề gợi ý nhanh:</span>
        {QUICK_TOPICS.map((topic) => (
          <button
            key={topic}
            className="citation-pill text-xs"
            onClick={() => applyQuickTopic(topic)}
            type="button"
          >
            {topic}
          </button>
        ))}
      </div>

      {selectedForCompare.length > 0 && (
        <PaperComparisonMatrix
          papers={selectedForCompare}
          onRemove={removeCompare}
          onClear={() => setSelectedForCompare([])}
        />
      )}

      <div className="result-summary" aria-live="polite">
        <span>
          <strong>{result.data?.total ?? 0}</strong> bài báo được tìm thấy
          {selectedForCompare.length > 0 && ` · Đã chọn ${selectedForCompare.length} bài để so sánh`}
        </span>
        {result.isFetching && <span className="muted">Đang cập nhật…</span>}
      </div>

      {result.isLoading && <div className="card">Đang tải kết quả…</div>}
      {result.error && <p className="error" role="alert">{result.error.message}</p>}
      {!result.isLoading && result.data?.items.length === 0 && (
        <div className="card">Không tìm thấy bài phù hợp. Hãy nới bộ lọc hoặc thử cụm từ khác.</div>
      )}

      {result.data?.items.map((paper) => {
        const isCompared = selectedForCompare.some((p) => p.id === paper.id);
        return (
          <article className="card paper" key={paper.id}>
            <div className="paper-heading">
              <div>
                <h2>
                  <Link href={`/papers/${paper.id}`}>{paper.title}</Link>
                </h2>
                <div className="row wrap gap-2 mt-1">
                  <span className="badge">{paper.publication_year ?? "N/A"}</span>
                  <span className="badge badge-neutral">
                    {paper.cited_by_count.toLocaleString()} citations
                  </span>
                  {paper.is_open_access ? (
                    <span className="badge badge-success">Open Access</span>
                  ) : (
                    <span className="badge">Restricted</span>
                  )}
                  {paper.source_name && (
                    <span className="text-xs muted self-center">{paper.source_name}</span>
                  )}
                </div>
              </div>
              <div className="row wrap gap-2">
                <button
                  className={isCompared ? "button text-xs" : "secondary-button text-xs"}
                  onClick={() => toggleCompare(paper)}
                  type="button"
                >
                  {isCompared ? "✓ Đang so sánh" : "+ So sánh"}
                </button>
                <button
                  className="secondary-button text-xs"
                  disabled={saved[paper.id]}
                  onClick={() => savePaper(paper)}
                  type="button"
                >
                  {saved[paper.id] ? "Đã lưu" : "Lưu bài"}
                </button>
              </div>
            </div>
            <p className="mt-3 text-sm">{paper.abstract || "Chưa có abstract trong nguồn dữ liệu."}</p>
          </article>
        );
      })}

      <nav className="pagination" aria-label="Phân trang kết quả">
        <button
          className="secondary-button"
          disabled={page <= 1}
          onClick={() => setPage((value) => value - 1)}
          type="button"
        >
          Trang trước
        </button>
        <span>Trang {page}/{totalPages}</span>
        <button
          className="secondary-button"
          disabled={page >= totalPages}
          onClick={() => setPage((value) => value + 1)}
          type="button"
        >
          Trang sau
        </button>
      </nav>
    </main>
  );
}
