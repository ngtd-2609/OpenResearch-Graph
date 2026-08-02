"use client";

import { useState } from "react";

import { api, hasSession } from "@/lib/api";

type CheckoutResponse = { mode: "mock" | "stripe"; checkout_url: string };

export default function PricingPage() {
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  async function startCheckout() {
    if (!hasSession()) {
      window.location.assign("/login");
      return;
    }
    setBusy(true);
    setMessage("");
    try {
      const result = await api<CheckoutResponse>("/subscriptions/checkout", { method: "POST" });
      window.location.assign(result.checkout_url);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Không thể tạo checkout");
      setBusy(false);
    }
  }

  return (
    <main className="container">
      <header className="page-header">
        <div>
          <h1>Gói sử dụng</h1>
          <p className="muted">Development mặc định dùng mock billing; production dùng Stripe webhook.</p>
        </div>
      </header>
      <div className="grid pricing-grid">
        <section className="card stack">
          <h2>Free</h2>
          <strong>0 đ</strong>
          <ul>
            <li>Search và analytics với giới hạn cấu hình</li>
            <li>3 PDF trong development</li>
            <li>RAG và recommendation tiêu chuẩn</li>
          </ul>
        </section>
        <section className="card stack featured-plan">
          <span className="badge">Khuyến nghị cho demo</span>
          <h2>Premium</h2>
          <strong>Giá cấu hình trong Stripe</strong>
          <ul>
            <li>Quota cao hơn</li>
            <li>Reranking và analytics nâng cao</li>
            <li>Nhiều PDF và export</li>
          </ul>
          <button className="button" disabled={busy} onClick={startCheckout} type="button">
            {busy ? "Đang mở checkout…" : "Chọn Premium"}
          </button>
          {message && <p className="error" role="alert">{message}</p>}
        </section>
      </div>
    </main>
  );
}
