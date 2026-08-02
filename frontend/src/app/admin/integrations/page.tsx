"use client";

import { useQuery } from "@tanstack/react-query";

import AuthGuard from "@/components/auth-guard";
import IntegrationStatusGrid, { type IntegrationStatus } from "@/components/integration-status-grid";
import { api } from "@/lib/api";

function IntegrationPageContent() {
  const query = useQuery({
    queryKey: ["admin-integrations"],
    queryFn: () => api<IntegrationStatus[]>("/admin/integrations"),
  });

  return (
    <main className="container stack">
      <header className="page-header">
        <div>
          <h1>External integrations</h1>
          <p className="muted">Trạng thái kết nối, fallback đang dùng và thời điểm kiểm tra gần nhất.</p>
        </div>
        <button className="secondary-button" disabled={query.isFetching} onClick={() => query.refetch()} type="button">
          {query.isFetching ? "Đang kiểm tra…" : "Refresh"}
        </button>
      </header>
      {query.isLoading && <div className="card">Đang tải…</div>}
      {query.error && <p className="error" role="alert">{query.error.message}</p>}
      {query.data && <IntegrationStatusGrid items={query.data} />}
    </main>
  );
}

export default function IntegrationsPage() {
  return <AuthGuard><IntegrationPageContent /></AuthGuard>;
}
