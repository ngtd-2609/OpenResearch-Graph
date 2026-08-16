"use client";

import { api } from "@/lib/api";
import { useEffect, useState } from "react";

export default function VerifyEmailPage() {
  const [token, setToken] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const urlToken = new URLSearchParams(window.location.search).get("token") ?? "";
    setToken(urlToken);

    if (urlToken) {
      verify(urlToken);
    }
  }, []);

  async function verify(verifyToken: string) {
    setLoading(true);
    setError("");
    setMessage("");
    try {
      const data = await api<{ message: string }>("/auth/verify-email", {
        method: "POST",
        body: JSON.stringify({ token: verifyToken }),
      });
      setMessage(data.message);
    } catch (err: unknown) {
      const detail = err instanceof Error ? err.message : "Xác minh email thất bại";
      setError(detail);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container narrow-page">
      <section className="card auth-card">
        <h1>Xác minh email</h1>
        {!token && <p className="error">URL không chứa verification token hợp lệ.</p>}
        {loading && <p>Đang xác minh...</p>}
        {message && <p role="status">{message}</p>}
        {error && <p className="error">{error}</p>}
        {(message || error) && (
          <a className="button" href="/login">Đăng nhập</a>
        )}
      </section>
    </main>
  );
}
