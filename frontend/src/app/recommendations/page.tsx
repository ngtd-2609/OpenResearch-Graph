"use client";

import AuthGuard from "@/components/auth-guard";
import { api } from "@/lib/api";
import type { Recommendation } from "@/types/api";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

function RecommendationsContent() {
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

  return (
    <main className="container">
      <header className="page-header">
        <div>
          <h1>Đề xuất cá nhân hóa</h1>
          <p className="muted">Kết hợp content, collaborative filtering, citation graph và diversity.</p>
        </div>
      </header>
      {query.isLoading && <div className="card">Đang tính đề xuất…</div>}
      {query.error && <p className="error" role="alert">{query.error.message}</p>}
      {query.data?.map((item) => (
        <article className="card paper" key={item.paper.id}>
          <h2><Link href={`/papers/${item.paper.id}`}>{item.paper.title}</Link></h2>
          <p>{item.explanation}</p>
          <div className="component-bars">
            {Object.entries(item.components).map(([name, value]) => (
              <div key={name}>
                <span>{name}</span>
                <progress max="1" value={Math.max(0, Math.min(1, value))} />
              </div>
            ))}
          </div>
          <div className="row wrap">
            <span className="badge">Score {item.score.toFixed(3)}</span>
            <button className="secondary-button" onClick={() => feedback(item.paper.id, "like")} type="button">Hữu ích</button>
            <button className="secondary-button" onClick={() => feedback(item.paper.id, "dislike")} type="button">Không phù hợp</button>
            <button className="link-button" onClick={() => feedback(item.paper.id, "dismiss")} type="button">Ẩn</button>
          </div>
        </article>
      ))}
    </main>
  );
}

export default function RecommendationsPage() {
  return <AuthGuard><RecommendationsContent /></AuthGuard>;
}
