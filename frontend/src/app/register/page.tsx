"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { api } from "@/lib/api";
import { registerSchema, type RegisterValues } from "@/lib/schemas";

export default function RegisterPage() {
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { email: "", username: "", full_name: "", password: "", passwordConfirmation: "" },
  });

  async function submit(values: RegisterValues) {
    setMessage("");
    setIsError(false);
    const payload = {
      email: values.email,
      username: values.username,
      full_name: values.full_name,
      password: values.password,
    };
    try {
      await api("/auth/register", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setMessage("Đăng ký thành công. Bạn có thể đăng nhập ngay.");
    } catch (error) {
      setIsError(true);
      setMessage(error instanceof Error ? error.message : "Không thể đăng ký");
    }
  }

  return (
    <main className="container narrow-page">
      <section className="card auth-card">
        <h1>Tạo tài khoản</h1>
        <form className="stack" onSubmit={handleSubmit(submit)} noValidate>
          <label>
            Email
            <input className="input" type="email" autoComplete="email" {...register("email")} />
            {errors.email && <small className="error">{errors.email.message}</small>}
          </label>
          <label>
            Username
            <input className="input" autoComplete="username" {...register("username")} />
            {errors.username && <small className="error">{errors.username.message}</small>}
          </label>
          <label>
            Họ tên
            <input className="input" autoComplete="name" {...register("full_name")} />
          </label>
          <label>
            Mật khẩu
            <input className="input" type="password" autoComplete="new-password" {...register("password")} />
            {errors.password && <small className="error">{errors.password.message}</small>}
          </label>
          <label>
            Nhập lại mật khẩu
            <input className="input" type="password" autoComplete="new-password" {...register("passwordConfirmation")} />
            {errors.passwordConfirmation && (
              <small className="error">{errors.passwordConfirmation.message}</small>
            )}
          </label>
          <button className="button" disabled={isSubmitting} type="submit">
            {isSubmitting ? "Đang tạo…" : "Đăng ký"}
          </button>
        </form>
        {message && <p className={isError ? "error" : "success"} role={isError ? "alert" : "status"}>{message}</p>}
        <p className="muted">Đã có tài khoản? <Link href="/login">Đăng nhập</Link></p>
      </section>
    </main>
  );
}
