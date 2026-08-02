"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import AuthGuard from "@/components/auth-guard";
import IntegrationStatusGrid, { type IntegrationStatus } from "@/components/integration-status-grid";
import { api } from "@/lib/api";

function AdminContent() {
  const query = useQuery({
    queryKey: ["admin-integrations"],
    queryFn: () => api<IntegrationStatus[]>("/admin/integrations"),
    refetchInterval: 60_000,
  });

  const unhealthy = query.data?.filter((item) => item.status === "error").length ?? 0;

  return (
    <main className="container stack">
      <header className="page-header">
        <div>
          <h1>Admin overview</h1>
          <p className="muted">Thông tin được redacted; trang này không bao giờ trả secret.</p>
        </div>
        <button className="secondary-button" disabled={query.isFetching} onClick={() => query.refetch()} type="button">
          {query.isFetching ? "Đang kiểm tra…" : "Kiểm tra lại"}
        </button>
      </header>
      <section className="card">
        <strong>{unhealthy === 0 ? "Không phát hiện integration lỗi" : `${unhealthy} integration đang lỗi`}</strong>
        <p><Link href="/admin/integrations">Mở trang tích hợp chi tiết</Link></p>
      </section>
      {query.isLoading && <div className="card">Đang kiểm tra dịch vụ…</div>}
      {query.error && <p className="error" role="alert">{query.error.message}</p>}
      {query.data && <IntegrationStatusGrid items={query.data} />}
    </main>
  );
}

export default function AdminPage() {
  return <AuthGuard><AdminContent /></AuthGuard>;
}
