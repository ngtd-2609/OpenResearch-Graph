"use client";

import { hasSession, logout, SESSION_EVENT } from "@/lib/api";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function NavBar() {
  const router = useRouter();
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    const synchronize = () => setAuthenticated(hasSession());
    synchronize();
    window.addEventListener(SESSION_EVENT, synchronize);
    window.addEventListener("storage", synchronize);
    return () => {
      window.removeEventListener(SESSION_EVENT, synchronize);
      window.removeEventListener("storage", synchronize);
    };
  }, []);

  async function signOut() {
    await logout();
    setAuthenticated(false);
    router.push("/login");
    router.refresh();
  }

  return (
    <nav className="nav" aria-label="Điều hướng chính">
      <Link className="brand" href="/">
        OpenResearch Graph
      </Link>
      <Link href="/search">Tìm kiếm</Link>
      <Link href="/analytics">Phân tích</Link>
      <Link href="/graph">Citation Graph</Link>
      <Link href="/chat">PDF Chat</Link>
      <Link href="/recommendations">Đề xuất</Link>
      {authenticated ? (
        <button className="link-button" onClick={signOut} type="button">
          Đăng xuất
        </button>
      ) : (
        <Link href="/login">Đăng nhập</Link>
      )}
    </nav>
  );
}
