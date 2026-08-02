"use client";

import { api, saveSession } from "@/lib/api";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

type LoginResponse = {
  access_token: string;
  refresh_token: string;
};

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("user@openresearch.dev");
  const [password, setPassword] = useState("Student123!");
  const [message, setMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setMessage("");

    try {
      const tokens = await api<LoginResponse>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });

      saveSession(tokens);
      router.push("/search");
      router.refresh();
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "Không thể đăng nhập"
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="container narrow-page">
      <section className="card auth-card">
        <h1>Đăng nhập</h1>

        <form onSubmit={submit} className="stack">
          <label>
            Email
            <input
              className="input"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </label>

          <label>
            Mật khẩu
            <input
              className="input"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>

          <button
            className="button"
            disabled={submitting}
            type="submit"
          >
            {submitting ? "Đang đăng nhập…" : "Đăng nhập"}
          </button>
        </form>

        {message && (
          <p className="error" role="alert">
            {message}
          </p>
        )}

        <p className="muted">
          Demo: user@openresearch.dev / Student123!
        </p>
      </section>
    </main>
  );
}