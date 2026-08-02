"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useRef, useState } from "react";

import AuthGuard from "@/components/auth-guard";
import StatusBadge from "@/components/status-badge";
import { api, clearSession } from "@/lib/api";

type Subscription = {
  plan: "free" | "premium";
  status: string;
  current_period_end: string | null;
  cancel_at_period_end?: boolean;
};

function AccountContent() {
  const queryClient = useQueryClient();
  const searchParams = useSearchParams();
  const mockUpgradeStarted = useRef(false);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const subscription = useQuery({
    queryKey: ["subscription"],
    queryFn: () => api<Subscription>("/subscriptions/me"),
  });

  useEffect(() => {
    if (searchParams.get("mock_upgrade") !== "1" || mockUpgradeStarted.current) return;
    mockUpgradeStarted.current = true;
    setBusy(true);
    api<{ message: string }>("/subscriptions/mock-upgrade", { method: "POST" })
      .then(async (data) => {
        setMessage(data.message);
        await queryClient.invalidateQueries({ queryKey: ["subscription"] });
        window.history.replaceState({}, "", "/account");
      })
      .catch((error: unknown) => {
        setMessage(error instanceof Error ? error.message : "Không thể cập nhật gói");
      })
      .finally(() => setBusy(false));
  }, [queryClient, searchParams]);

  async function upgradeMock() {
    setBusy(true);
    setMessage("");
    try {
      const data = await api<{ message: string }>("/subscriptions/mock-upgrade", { method: "POST" });
      setMessage(data.message);
      await queryClient.invalidateQueries({ queryKey: ["subscription"] });
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Không thể cập nhật gói");
    } finally {
      setBusy(false);
    }
  }

  async function openPortal() {
    setBusy(true);
    try {
      const data = await api<{ portal_url: string }>("/subscriptions/portal", { method: "POST" });
      window.location.assign(data.portal_url);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Không thể mở customer portal");
      setBusy(false);
    }
  }

  async function logoutAll() {
    setBusy(true);
    try {
      const data = await api<{ message: string }>("/auth/logout-all", { method: "POST" });
      clearSession();
      setMessage(data.message);
      window.location.assign("/login");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Không thể thu hồi phiên");
      setBusy(false);
    }
  }

  return (
    <main className="container">
      <h1>Tài khoản</h1>
      <section className="card stack">
        <div className="row wrap">
          <h2>Subscription</h2>
          {subscription.data && (
            <StatusBadge tone={subscription.data.plan === "premium" ? "success" : "neutral"}>
              {subscription.data.plan} / {subscription.data.status}
            </StatusBadge>
          )}
        </div>
        {subscription.data?.current_period_end && (
          <p className="muted">Chu kỳ hiện tại kết thúc: {new Date(subscription.data.current_period_end).toLocaleString("vi-VN")}</p>
        )}
        <div className="row wrap">
          <button className="button" disabled={busy} onClick={upgradeMock} type="button">Nâng cấp mock</button>
          <button className="secondary-button" disabled={busy} onClick={openPortal} type="button">Customer portal</button>
          <button className="secondary-button" disabled={busy} onClick={logoutAll} type="button">Đăng xuất mọi thiết bị</button>
        </div>
        {subscription.error && <p className="error" role="alert">{subscription.error.message}</p>}
        {message && <p role="status">{message}</p>}
      </section>
    </main>
  );
}

export default function AccountPage() {
  return (
    <AuthGuard>
      <Suspense fallback={<main className="container">Đang tải tài khoản…</main>}>
        <AccountContent />
      </Suspense>
    </AuthGuard>
  );
}
