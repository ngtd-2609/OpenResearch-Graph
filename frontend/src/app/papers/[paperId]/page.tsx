"use client";

import { api } from "@/lib/api";
import type { Paper } from "@/types/api";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { useState } from "react";

export default function PaperPage() {
  const { paperId } = useParams<{ paperId: string }>();
  const [saved, setSaved] = useState(false);
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

  if (query.isLoading) return <main className="container">Đang tải paper…</main>;
  if (query.error) return <main className="container"><p className="error">{query.error.message}</p></main>;
  if (!query.data) return <main className="container">Không tìm thấy paper.</main>;
  const paper = query.data;

  return (
    <main className="container">
      <article className="card stack">
        <div className="row wrap">
          <span className="badge">{paper.publication_year ?? "Không rõ năm"}</span>
          {paper.is_open_access && <span className="badge">Open Access</span>}
        </div>
        <h1>{paper.title}</h1>
        <p className="muted">{paper.cited_by_count} citations · {paper.source_name || "Không rõ nguồn"}</p>
        <p>{paper.abstract || "Nguồn dữ liệu chưa cung cấp abstract."}</p>
        <div className="row wrap">
          <button className="secondary-button" disabled={saved} onClick={savePaper} type="button">{saved ? "Đã lưu" : "Lưu vào thư viện"}</button>
          {paper.open_access_url && <a className="button" href={paper.open_access_url} rel="noreferrer" target="_blank">Mở bản truy cập</a>}
        </div>
      </article>
    </main>
  );
}
