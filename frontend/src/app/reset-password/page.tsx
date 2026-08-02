"use client";

import { api } from "@/lib/api";
import { FormEvent, useEffect, useState } from "react";

export default function ResetPasswordPage() {
  const [token, setToken] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    setToken(new URLSearchParams(window.location.search).get("token") ?? "");
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = await api<{ message: string }>("/auth/reset-password", {
      method: "POST",
      body: JSON.stringify({ token, new_password: password }),
    });
    setMessage(data.message);
  }

  return (
    <main className="container narrow-page">
      <section className="card auth-card">
        <h1>Đặt lại mật khẩu</h1>
        <form className="stack" onSubmit={submit}>
          <label>Mật khẩu mới<input className="input" type="password" minLength={8} value={password} onChange={(event) => setPassword(event.target.value)} required /></label>
          <button className="button" disabled={!token} type="submit">Xác nhận</button>
        </form>
        {!token && <p className="error">URL không chứa reset token hợp lệ.</p>}
        {message && <p role="status">{message}</p>}
      </section>
    </main>
  );
}
