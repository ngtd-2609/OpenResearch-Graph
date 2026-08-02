"use client";

import AuthGuard from "@/components/auth-guard";
import { api } from "@/lib/api";
import type { Paper } from "@/types/api";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

type LibraryItem = {
  id: string;
  paper: Paper;
  collection_name: string;
  notes?: string | null;
  tags: string[];
};

function LibraryContent() {
  const query = useQuery({
    queryKey: ["library"],
    queryFn: () => api<LibraryItem[]>("/library"),
  });

  async function remove(paperId: string) {
    await api(`/library/${paperId}`, { method: "DELETE" });
    await query.refetch();
  }

  return (
    <main className="container">
      <header className="page-header">
        <div>
          <h1>Thư viện nghiên cứu</h1>
          <p className="muted">Các bài đã lưu được dùng để xây dựng hồ sơ recommendation.</p>
        </div>
      </header>
      {query.isLoading && <div className="card">Đang tải thư viện…</div>}
      {query.error && <p className="error" role="alert">{query.error.message}</p>}
      {query.data?.length === 0 && <div className="card">Thư viện đang trống.</div>}
      {query.data?.map((item) => (
        <article className="card paper" key={item.id}>
          <div className="paper-heading">
            <h2><Link href={`/papers/${item.paper.id}`}>{item.paper.title}</Link></h2>
            <button className="secondary-button" onClick={() => remove(item.paper.id)} type="button">Xóa</button>
          </div>
          <p className="muted">Collection: {item.collection_name}</p>
          {item.notes && <p>{item.notes}</p>}
          <div className="row wrap">{item.tags.map((tag) => <span className="badge" key={tag}>{tag}</span>)}</div>
        </article>
      ))}
    </main>
  );
}

export default function LibraryPage() {
  return <AuthGuard><LibraryContent /></AuthGuard>;
}
