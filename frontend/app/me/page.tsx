"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { RequireAuth } from "@/components/RequireAuth";
import { api, clearToken, Dashboard, User } from "@/lib/api";
import { useRouter } from "next/navigation";

export default function MePage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [stats, setStats] = useState<Dashboard | null>(null);
  const [installable, setInstallable] = useState(false);
  const [promptEvent, setPromptEvent] = useState<any>(null);

  useEffect(() => {
    api<User>("/api/auth/me").then(setUser);
    api<Dashboard>("/api/dashboard").then(setStats);
    const onPrompt = (event: Event) => {
      event.preventDefault();
      setPromptEvent(event);
      setInstallable(true);
    };
    window.addEventListener("beforeinstallprompt", onPrompt);
    return () => window.removeEventListener("beforeinstallprompt", onPrompt);
  }, []);

  return (
    <RequireAuth>
      <AppShell>
        <div className="grid gap-4">
          <div className="card">
            <h1 className="text-xl font-bold">我的</h1>
            <p className="mt-2 text-slate-600">{user?.name} · {user?.email}</p>
            <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-lg bg-slate-50 p-3">累计错题 <strong className="block text-2xl">{stats?.total ?? 0}</strong></div>
              <div className="rounded-lg bg-slate-50 p-3">今日复习 <strong className="block text-2xl">{stats?.due_today ?? 0}</strong></div>
            </div>
          </div>
          <div className="card">
            <h2 className="font-bold">安装到手机桌面</h2>
            <p className="mt-2 text-sm text-slate-500">安装后可以像 App 一样从桌面打开，适合孩子每天复习。</p>
            <button
              className="btn btn-primary mt-4"
              onClick={async () => {
                if (promptEvent) {
                  await promptEvent.prompt();
                  setInstallable(false);
                }
              }}
            >
              {installable ? "立即安装" : "浏览器菜单中选择添加到主屏幕"}
            </button>
          </div>
          <button
            className="btn"
            onClick={() => {
              clearToken();
              router.push("/login");
            }}
          >
            退出登录
          </button>
        </div>
      </AppShell>
    </RequireAuth>
  );
}
