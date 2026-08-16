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
  const [selectedCollection, setSelectedCollection] = useState<string>("all");
  const [editingItem, setEditingItem] = useState<LibraryItem | null>(null);
  const [editNotes, setEditNotes] = useState("");
  const [editTags, setEditTags] = useState("");
  const [editCollection, setEditCollection] = useState("");
  const [savingEdit, setSavingEdit] = useState(false);

  const query = useQuery({
    queryKey: ["library"],
    queryFn: () => api<LibraryItem[]>("/library"),
  });

  async function remove(paperId: string) {
    if (!confirm("Bạn có chắc chắn muốn xóa bài báo này khỏi thư viện?")) return;
    await api(`/library/${paperId}`, { method: "DELETE" });
    await query.refetch();
  }

  function startEdit(item: LibraryItem) {
    setEditingItem(item);
    setEditNotes(item.notes || "");
    setEditTags(item.tags.join(", "));
    setEditCollection(item.collection_name || "Saved");
  }

  async function saveEdit() {
    if (!editingItem) return;
    setSavingEdit(true);
    try {
      const parsedTags = editTags
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean);
      await api(`/library/${editingItem.paper.id}`, {
        method: "PATCH",
        body: JSON.stringify({
          notes: editNotes,
          tags: parsedTags,
          collection_name: editCollection || "Saved",
        }),
      });
      setEditingItem(null);
      await query.refetch();
    } catch (err: unknown) {
      alert("Lỗi khi lưu chỉnh sửa: " + (err instanceof Error ? err.message : String(err)));
    } finally {
      setSavingEdit(false);
    }
  }

  const items = query.data || [];
  const collections = Array.from(new Set(items.map((i) => i.collection_name || "Saved")));

  const filtered = items.filter((item) => {
    if (selectedCollection !== "all" && item.collection_name !== selectedCollection) {
      return false;
    }
    if (!filterQuery.trim()) return true;
    const term = filterQuery.toLowerCase();
    return (
      item.paper.title.toLowerCase().includes(term) ||
      (item.paper.abstract && item.paper.abstract.toLowerCase().includes(term)) ||
      (item.notes && item.notes.toLowerCase().includes(term)) ||
      item.collection_name.toLowerCase().includes(term) ||
      item.tags.some((t) => t.toLowerCase().includes(term))
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

      {/* Filter and Collection Bar */}
      {items.length > 0 && (
        <div className="card mb-4 stack gap-3">
          <div className="row wrap gap-2 items-center">
            <span className="text-xs font-semibold muted">Bộ sưu tập:</span>
            <button
              type="button"
              className={`badge cursor-pointer ${selectedCollection === "all" ? "badge-primary" : "badge-neutral"}`}
              onClick={() => setSelectedCollection("all")}
            >
              Tất cả ({items.length})
            </button>
            {collections.map((col) => {
              const count = items.filter((i) => i.collection_name === col).length;
              return (
                <button
                  type="button"
                  key={col}
                  className={`badge cursor-pointer ${selectedCollection === col ? "badge-primary" : "badge-neutral"}`}
                  onClick={() => setSelectedCollection(col)}
                >
                  📁 {col} ({count})
                </button>
              );
            })}
          </div>

          <input
            className="input"
            value={filterQuery}
            onChange={(e) => setFilterQuery(e.target.value)}
            placeholder="Lọc nhanh bài báo theo tiêu đề, ghi chú cá nhân, tags (#tag)..."
          />
        </div>
      )}

      {/* Edit Modal / Dialog */}
      {editingItem && (
        <div className="card mb-4" style={{ borderColor: "var(--accent)", background: "rgba(59, 130, 246, 0.05)" }}>
          <h3 className="text-sm font-semibold mb-2">✏️ Chỉnh sửa ghi chú & Thẻ: &ldquo;{editingItem.paper.title}&rdquo;</h3>
          <div className="stack gap-2">
            <div>
              <label className="text-xs font-semibold muted">Tên bộ sưu tập</label>
              <input
                className="input text-sm mt-1"
                value={editCollection}
                onChange={(e) => setEditCollection(e.target.value)}
                placeholder="Ví dụ: Graph Neural Networks, LLM Agent, Saved..."
              />
            </div>
            <div>
              <label className="text-xs font-semibold muted">Ghi chú cá nhân / Ý tưởng nghiên cứu</label>
              <textarea
                className="input text-sm mt-1"
                rows={3}
                value={editNotes}
                onChange={(e) => setEditNotes(e.target.value)}
                placeholder="Nhập nhận xét, câu hỏi hoặc ghi chú phương pháp..."
              />
            </div>
            <div>
              <label className="text-xs font-semibold muted">Tags (phân cách bằng dấu phẩy)</label>
              <input
                className="input text-sm mt-1"
                value={editTags}
                onChange={(e) => setEditTags(e.target.value)}
                placeholder="ví dụ: rag, benchmark, pytorch, survey"
              />
            </div>
            <div className="row gap-2 mt-2">
              <button
                className="button text-xs"
                onClick={saveEdit}
                disabled={savingEdit}
                type="button"
              >
                {savingEdit ? "Đang lưu..." : "💾 Lưu thay đổi"}
              </button>
              <button
                className="secondary-button text-xs"
                onClick={() => setEditingItem(null)}
                type="button"
              >
                Hủy
              </button>
            </div>
          </div>
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
                    📁 {item.collection_name}
                  </span>
                </div>
              </div>

              <div className="row gap-2">
                <button
                  className="secondary-button text-xs"
                  onClick={() => startEdit(item)}
                  type="button"
                >
                  ✏️ Sửa ghi chú/tag
                </button>
                <Link className="secondary-button text-xs" href={`/papers/${item.paper.id}`}>
                  Xem chi tiết
                </Link>
                <button
                  className="secondary-button text-xs"
                  onClick={() => remove(item.paper.id)}
                  type="button"
                >
                  Xóa
                </button>
              </div>
            </div>

            {item.notes && (
              <div className="rec-explanation-box mt-3">
                <span className="rec-bulb">📝</span>
                <p className="text-sm"><strong>Ghi chú:</strong> {item.notes}</p>
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
