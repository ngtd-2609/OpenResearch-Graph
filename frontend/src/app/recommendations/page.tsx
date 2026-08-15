"use client";

import AuthGuard from "@/components/auth-guard";
import { api } from "@/lib/api";
import type { Recommendation } from "@/types/api";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useState } from "react";

const COMPONENT_LABELS: Record<string, string> = {
  content: "Độ tương đồng nội dung",
  collaborative: "Hành vi người dùng tương tự",
  graph: "Vị trí trong đồ thị trích dẫn",
  popularity: "Mức độ ảnh hưởng học thuật",
  recency: "Tính cập nhật thời gian",
  open_access: "Quyền truy cập mở",
  feedback: "Phản hồi tích cực trước đây",
};

function RecommendationsContent() {
  const [saved, setSaved] = useState<Record<string, boolean>>({});
  const query = useQuery({
    queryKey: ["recommendations"],
    queryFn: () => api<Recommendation[]>("/recommendations"),
  });

  async function feedback(paperId: string, interactionType: "like" | "dislike" | "dismiss") {
    await api(`/recommendations/${paperId}/feedback`, {
      method: "POST",
      body: JSON.stringify({ interaction_type: interactionType, value: 1 }),
    });
    await query.refetch();
  }

  async function savePaper(paperId: string) {
    await api("/library", {
      method: "POST",
      body: JSON.stringify({ paper_id: paperId, collection_name: "Saved", tags: ["AI Recommendation"] }),
    });
    setSaved((current) => ({ ...current, [paperId]: true }));
  }

  return (
    <main className="container">
      <header className="page-header">
        <div>
          <h1>Đề xuất Nghiên cứu Cá nhân hóa</h1>
          <p className="muted">
            Thuật toán Hybrid Recommender kết hợp Embeddings, Lọc cộng tác, Personalized PageRank và MMR Diversity.
          </p>
        </div>
      </header>

      {query.isLoading && (
        <div className="card text-center py-12">
          <p className="text-lg font-semibold">Đang tổng hợp đề xuất dựa trên hồ sơ của bạn…</p>
          <p className="muted text-sm mt-1">Tính toán ma trận tương đồng và trích dẫn theo thời gian thực.</p>
        </div>
      )}

      {query.error && <p className="error" role="alert">{query.error.message}</p>}

      {!query.isLoading && query.data?.length === 0 && (
        <div className="card text-center py-12">
          <h3>Chưa có dữ liệu đề xuất</h3>
          <p className="muted text-sm mt-2">
            Hãy bắt đầu bằng cách lưu một vài bài báo vào Thư viện hoặc tìm kiếm các chủ đề bạn quan tâm.
          </p>
          <div className="mt-4">
            <Link className="button" href="/search">Khám phá bài báo ngay</Link>
          </div>
        </div>
      )}

      <div className="stack gap-4">
        {query.data?.map((item) => {
          const matchPercent = Math.min(100, Math.round(item.score * 100));
          return (
            <article className="card rec-card" key={item.paper.id}>
              <div className="rec-card-header">
                <div>
                  <h2 className="rec-title">
                    <Link href={`/papers/${item.paper.id}`}>{item.paper.title}</Link>
                  </h2>
                  <div className="row wrap gap-2 mt-1">
                    <span className="badge">{item.paper.publication_year ?? "N/A"}</span>
                    <span className="badge badge-neutral">
                      {item.paper.cited_by_count.toLocaleString()} citations
                    </span>
                    {item.paper.is_open_access && (
                      <span className="badge badge-success">Open Access</span>
                    )}
                    {item.paper.source_name && (
                      <span className="text-xs muted self-center">{item.paper.source_name}</span>
                    )}
                  </div>
                </div>

                <div className="rec-score-badge">
                  <div className="rec-score-num">{matchPercent}%</div>
                  <div className="rec-score-label">Độ phù hợp</div>
                </div>
              </div>

              <div className="rec-explanation-box">
                <span className="rec-bulb">💡</span>
                <p className="text-sm">{item.explanation}</p>
              </div>

              {/* Component breakdown */}
              <div className="rec-breakdown">
                <div className="text-xs font-semibold muted mb-2">Phân bổ trọng số thuật toán:</div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  {Object.entries(item.components).map(([name, value]) => {
                    const pct = Math.round(Math.max(0, Math.min(1, value)) * 100);
                    return (
                      <div key={name} className="row items-center gap-2">
                        <span className="w-36 truncate muted">{COMPONENT_LABELS[name] || name}:</span>
                        <div className="rec-progress-bar">
                          <div className="rec-progress-fill" style={{ width: `${pct}%` }} />
                        </div>
                        <span className="w-8 text-right font-semibold">{pct}%</span>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="rec-card-actions">
                <div className="row wrap gap-2">
                  <button
                    className="button text-xs"
                    disabled={saved[item.paper.id]}
                    onClick={() => savePaper(item.paper.id)}
                    type="button"
                  >
                    {saved[item.paper.id] ? "✓ Đã lưu vào Thư viện" : "+ Lưu vào Thư viện"}
                  </button>
                  <Link className="secondary-button text-xs" href={`/papers/${item.paper.id}`}>
                    Xem chi tiết bài báo
                  </Link>
                </div>

                <div className="row gap-2">
                  <button
                    className="secondary-button text-xs"
                    onClick={() => feedback(item.paper.id, "like")}
                    title="Gợi ý thêm các bài tương tự"
                    type="button"
                  >
                    👍 Hữu ích
                  </button>
                  <button
                    className="secondary-button text-xs"
                    onClick={() => feedback(item.paper.id, "dislike")}
                    title="Giảm tần suất gợi ý dạng này"
                    type="button"
                  >
                    👎 Không phù hợp
                  </button>
                  <button
                    className="link-button text-xs muted"
                    onClick={() => feedback(item.paper.id, "dismiss")}
                    type="button"
                  >
                    Ẩn bài
                  </button>
                </div>
              </div>
            </article>
          );
        })}
      </div>
    </main>
  );
}

export default function RecommendationsPage() {
  return (
    <AuthGuard>
      <RecommendationsContent />
    </AuthGuard>
  );
}
