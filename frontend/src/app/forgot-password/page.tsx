"use client";

import { api } from "@/lib/api";
import { FormEvent, useState } from "react";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = await api<{ message: string }>("/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email }),
    });
    setMessage(data.message);
  }

  return (
    <main className="container narrow-page">
      <section className="card auth-card">
        <h1>Quên mật khẩu</h1>
        <form className="stack" onSubmit={submit}>
          <label>Email<input className="input" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></label>
          <button className="button" type="submit">Tạo liên kết</button>
        </form>
        {message && <p role="status">{message}</p>}
      </section>
    </main>
  );
}
