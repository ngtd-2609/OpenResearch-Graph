"use client";

import AuthGuard from "@/components/auth-guard";
import { api } from "@/lib/api";
import type { Paper } from "@/types/api";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useState } from "react";

type LibraryItem = {
  id: string;
  paper: Paper;
  collection_name: string;
  notes?: string | null;
  tags: string[];
};

function LibraryContent() {
  const [filterQuery, setFilterQuery] = useState("");
  const query = useQuery({
    queryKey: ["library"],
    queryFn: () => api<LibraryItem[]>("/library"),
  });

  async function remove(paperId: string) {
    await api(`/library/${paperId}`, { method: "DELETE" });
    await query.refetch();
  }

  const items = query.data || [];
  const filtered = items.filter((item) => {
    if (!filterQuery.trim()) return true;
    const term = filterQuery.toLowerCase();
    return (
      item.paper.title.toLowerCase().includes(term) ||
      (item.paper.abstract && item.paper.abstract.toLowerCase().includes(term)) ||
      item.collection_name.toLowerCase().includes(term)
    );
  });

  return (
    <main className="container">
      <header className="page-header">
        <div>
          <h1>Thư viện Nghiên cứu Cá nhân</h1>
          <p className="muted">
            Lưu trữ tài liệu và tự động huấn luyện hồ sơ gợi ý AI (Personalized Recommender).
          </p>
        </div>

        <div className="row wrap gap-2">
          <Link className="button text-xs" href="/recommendations">
            ✨ Xem Đề xuất AI theo Thư viện
          </Link>
          <Link className="secondary-button text-xs" href="/search">
            + Thêm bài báo mới
          </Link>
        </div>
      </header>

      {/* Filter bar */}
      {items.length > 0 && (
        <div className="mb-4">
          <input
            className="input"
            value={filterQuery}
            onChange={(e) => setFilterQuery(e.target.value)}
            placeholder="Lọc nhanh bài báo trong thư viện theo tiêu đề, ghi chú hoặc bộ sưu tập..."
          />
        </div>
      )}

      {query.isLoading && (
        <div className="card text-center py-12">
          <p className="font-semibold">Đang tải thư viện nghiên cứu của bạn…</p>
        </div>
      )}

      {query.error && <p className="error" role="alert">{query.error.message}</p>}

      {!query.isLoading && items.length === 0 && (
        <div className="card text-center py-12">
          <h3>Thư viện của bạn đang trống</h3>
          <p className="muted text-sm mt-2">
            Khi bạn bấm &ldquo;Lưu bài&rdquo; tại trang Tìm kiếm hoặc Đề xuất, bài báo sẽ xuất hiện ở đây.
          </p>
          <div className="mt-4">
            <Link className="button" href="/search">Bắt đầu tìm kiếm bài báo</Link>
          </div>
        </div>
      )}

      <div className="stack gap-3">
        {filtered.map((item) => (
          <article className="card paper" key={item.id}>
            <div className="paper-heading">
              <div>
                <h2>
                  <Link href={`/papers/${item.paper.id}`}>{item.paper.title}</Link>
                </h2>
                <div className="row wrap gap-2 mt-1">
                  <span className="badge">{item.paper.publication_year ?? "N/A"}</span>
                  <span className="badge badge-neutral">
                    {item.paper.cited_by_count.toLocaleString()} citations
                  </span>
                  <span className="badge badge-neutral">
                    Bộ sưu tập: {item.collection_name}
                  </span>
                </div>
              </div>

              <div className="row gap-2">
                <Link className="secondary-button text-xs" href={`/papers/${item.paper.id}`}>
                  Xem chi tiết
                </Link>
                <button
                  className="secondary-button text-xs"
                  onClick={() => remove(item.paper.id)}
                  type="button"
                >
                  Xóa khỏi thư viện
                </button>
              </div>
            </div>

            {item.notes && (
              <div className="rec-explanation-box mt-3">
                <span className="rec-bulb">📝</span>
                <p className="text-sm">Ghi chú cá nhân: {item.notes}</p>
              </div>
            )}

            <p className="mt-3 text-sm line-clamp-4">
              {item.paper.abstract || "Chưa có nội dung tóm tắt."}
            </p>

            {item.tags.length > 0 && (
              <div className="row wrap gap-1 mt-3">
                {item.tags.map((tag) => (
                  <span className="badge badge-neutral text-xs" key={tag}>
                    #{tag}
                  </span>
                ))}
              </div>
            )}
          </article>
        ))}
      </div>
    </main>
  );
}

export default function LibraryPage() {
  return (
    <AuthGuard>
      <LibraryContent />
    </AuthGuard>
  );
}
