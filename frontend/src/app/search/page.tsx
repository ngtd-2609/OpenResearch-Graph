"use client";

import { api } from "@/lib/api";
import type { PaginatedPapers, Paper } from "@/types/api";
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { FormEvent, useMemo, useState } from "react";

const PER_PAGE = 10;

export default function SearchPage() {
  const [draft, setDraft] = useState("deep learning");
  const [query, setQuery] = useState("deep learning");
  const [page, setPage] = useState(1);
  const [fromYear, setFromYear] = useState("");
  const [toYear, setToYear] = useState("");
  const [openAccess, setOpenAccess] = useState(false);
  const [saved, setSaved] = useState<Record<string, boolean>>({});

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

  async function savePaper(paper: Paper) {
    await api("/library", {
      method: "POST",
      body: JSON.stringify({ paper_id: paper.id, collection_name: "Saved", tags: [] }),
    });
    setSaved((current) => ({ ...current, [paper.id]: true }));
  }

  const totalPages = Math.max(1, Math.ceil((result.data?.total ?? 0) / PER_PAGE));

  return (
    <main className="container">
      <header className="page-header">
        <div>
          <h1>Tìm kiếm bài báo</h1>
          <p className="muted">Hybrid search kết hợp từ khóa, embedding, citation, recency và reranking.</p>
        </div>
      </header>

      <form className="card search-form" onSubmit={submit}>
        <label className="search-query">
          Chủ đề nghiên cứu
          <input
            className="input"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            minLength={2}
            required
          />
        </label>
        <label>
          Từ năm
          <input className="input" type="number" min="1900" value={fromYear} onChange={(event) => setFromYear(event.target.value)} />
        </label>
        <label>
          Đến năm
          <input className="input" type="number" min="1900" value={toYear} onChange={(event) => setToYear(event.target.value)} />
        </label>
        <label className="checkbox-label">
          <input type="checkbox" checked={openAccess} onChange={(event) => setOpenAccess(event.target.checked)} />
          Chỉ Open Access
        </label>
        <button className="button" type="submit">Tìm kiếm</button>
      </form>

      <div className="result-summary" aria-live="polite">
        <span>{result.data?.total ?? 0} kết quả</span>
        {result.isFetching && <span className="muted">Đang cập nhật…</span>}
      </div>
      {result.isLoading && <div className="card">Đang tải kết quả…</div>}
      {result.error && <p className="error" role="alert">{result.error.message}</p>}
      {!result.isLoading && result.data?.items.length === 0 && (
        <div className="card">Không tìm thấy bài phù hợp. Hãy nới bộ lọc hoặc thử cụm từ khác.</div>
      )}
      {result.data?.items.map((paper) => (
        <article className="card paper" key={paper.id}>
          <div className="paper-heading">
            <h2><Link href={`/papers/${paper.id}`}>{paper.title}</Link></h2>
            <button
              className="secondary-button"
              disabled={saved[paper.id]}
              onClick={() => savePaper(paper)}
              type="button"
            >
              {saved[paper.id] ? "Đã lưu" : "Lưu bài"}
            </button>
          </div>
          <p className="muted">
            {paper.publication_year ?? "Không rõ năm"} · {paper.cited_by_count} citations · {paper.is_open_access ? "Open Access" : "Restricted"}
          </p>
          <p>{paper.abstract || "Chưa có abstract trong nguồn dữ liệu."}</p>
        </article>
      ))}

      <nav className="pagination" aria-label="Phân trang kết quả">
        <button className="secondary-button" disabled={page <= 1} onClick={() => setPage((value) => value - 1)} type="button">Trang trước</button>
        <span>Trang {page}/{totalPages}</span>
        <button className="secondary-button" disabled={page >= totalPages} onClick={() => setPage((value) => value + 1)} type="button">Trang sau</button>
      </nav>
    </main>
  );
}
