"use client";

import { hasSession, logout, SESSION_EVENT } from "@/lib/api";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

const NAV_LINKS = [
  { href: "/search", label: "Tìm kiếm" },
  { href: "/graph", label: "Đồ thị Trích dẫn" },
  { href: "/chat", label: "Deep RAG Chat" },
  { href: "/recommendations", label: "Đề xuất AI" },
  { href: "/analytics", label: "Phân tích Xu hướng" },
  { href: "/library", label: "Thư viện" },
];

export default function NavBar() {
  const router = useRouter();
  const pathname = usePathname();
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
    <header className="nav-header">
      <nav className="nav" aria-label="Điều hướng chính">
        <Link className="brand" href="/">
          <span className="brand-icon">🔬</span>
          <span className="brand-name">OpenResearch</span>
          <span className="brand-badge">v2</span>
        </Link>

        <div className="nav-links">
          {NAV_LINKS.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                className={`nav-link ${isActive ? "nav-link-active" : ""}`}
                href={link.href}
              >
                {link.label}
              </Link>
            );
          })}
        </div>

        <div className="nav-actions">
          {authenticated ? (
            <div className="row gap-2 items-center">
              <Link className="secondary-button text-xs" href="/account">
                👤 Tài khoản
              </Link>
              <button className="link-button text-xs muted" onClick={signOut} type="button">
                Đăng xuất
              </button>
            </div>
          ) : (
            <div className="row gap-2 items-center">
              <Link className="secondary-button text-xs" href="/login">
                Đăng nhập
              </Link>
              <Link className="button text-xs" href="/register">
                Đăng ký
              </Link>
            </div>
          )}
        </div>
      </nav>
    </header>
  );
}
