"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api, User } from "@/lib/api";

export function RequireAuth({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    api<User>("/api/auth/me")
      .then(() => setReady(true))
      .catch(() => router.replace("/login"));
  }, [router]);

  if (!ready) return <div className="p-8 text-slate-500">正在检查登录状态...</div>;
  return <>{children}</>;
}
