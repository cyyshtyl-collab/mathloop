"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import type { FormEvent } from "react";
import { useState } from "react";
import { api, setToken } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [error, setError] = useState("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    const formData = new FormData(event.currentTarget);
    try {
      const result = await api<{ access_token: string }>("/api/auth/register", {
        method: "POST",
        body: JSON.stringify(Object.fromEntries(formData.entries()))
      });
      setToken(result.access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "注册失败");
    }
  }

  return (
    <main className="grid min-h-screen place-items-center p-6">
      <form onSubmit={onSubmit} className="card grid w-full max-w-md gap-4">
        <div>
          <h1 className="text-2xl font-bold">注册家长账号</h1>
          <p className="mt-2 text-sm text-slate-500">V1.0 支持简单账号密码登录。</p>
        </div>
        <div className="field">
          <label>姓名</label>
          <input name="name" required />
        </div>
        <div className="field">
          <label>邮箱</label>
          <input name="email" type="email" required />
        </div>
        <div className="field">
          <label>密码</label>
          <input name="password" type="password" minLength={6} required />
        </div>
        {error && <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
        <button className="btn btn-primary">注册并登录</button>
        <p className="text-center text-sm text-slate-500">
          已有账号？<Link href="/login" className="text-blue-600">去登录</Link>
        </p>
      </form>
    </main>
  );
}
