"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { clearToken } from "@/lib/api";

const nav = [
  ["/", "首页"],
  ["/upload", "上传"],
  ["/mistakes", "错题库"],
  ["/review", "复习"],
  ["/me", "我的"]
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  return (
    <div className="min-h-screen pb-20 md:grid md:grid-cols-[240px_1fr] md:pb-0">
      <aside className="hidden bg-slate-900 p-5 text-white md:block">
        <div className="mb-6">
          <strong className="text-xl">MathLoop Junior</strong>
          <p className="text-sm text-slate-300">数环错题系统 V1.0</p>
        </div>
        <nav className="grid gap-2">
          {nav.map(([href, label]) => (
            <Link key={href} href={href} className={`rounded-lg px-3 py-2 ${pathname === href ? "bg-slate-700" : "text-slate-300 hover:bg-slate-800"}`}>
              {label}
            </Link>
          ))}
        </nav>
      </aside>
      <main>
        <header className="sticky top-0 z-20 flex flex-wrap items-center justify-between gap-3 border-b bg-white/95 px-4 py-3 backdrop-blur md:px-6 md:py-4">
          <div>
            <h1 className="text-xl font-bold">MathLoop Junior</h1>
            <p className="text-sm text-slate-500">错题到复习的闭环训练</p>
          </div>
          <button
            className="btn hidden md:inline-flex"
            onClick={() => {
              clearToken();
              router.push("/login");
            }}
          >
            退出登录
          </button>
        </header>
        <section className="p-4 md:p-6">{children}</section>
      </main>
      <nav className="fixed inset-x-0 bottom-0 z-30 grid grid-cols-5 border-t bg-white shadow-lg md:hidden">
        {nav.map(([href, label]) => {
          const active = href === "/" ? pathname === "/" || pathname === "/dashboard" : pathname.startsWith(href);
          return (
            <Link key={href} href={href} className={`flex min-h-16 flex-col items-center justify-center text-sm font-medium ${active ? "text-blue-700" : "text-slate-500"}`}>
              <span className={`mb-1 h-1.5 w-1.5 rounded-full ${active ? "bg-blue-600" : "bg-transparent"}`} />
              {label}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
