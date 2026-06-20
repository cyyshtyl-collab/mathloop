"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { RequireAuth } from "@/components/RequireAuth";
import { api, Dashboard } from "@/lib/api";

export default function DashboardPage() {
  const [data, setData] = useState<Dashboard | null>(null);
  useEffect(() => {
    api<Dashboard>("/api/dashboard").then(setData);
  }, []);

  return (
    <RequireAuth>
      <AppShell>
        <div className="grid gap-4">
          <div className="grid gap-3 rounded-xl bg-blue-600 p-5 text-white">
            <h1 className="text-2xl font-bold">今天从一道错题开始</h1>
            <p className="text-sm text-blue-100">拍照上传、生成错题卡，再按计划复习。</p>
            <div className="flex flex-wrap gap-2">
              <a className="btn bg-white text-blue-700" href="/upload">上传错题</a>
              <a className="btn border-blue-200 text-white" href="/review">今日复习</a>
              <a className="btn border-blue-200 text-white" href="/mistakes">错题库</a>
            </div>
          </div>
          <div className="grid gap-4 md:grid-cols-4">
            {[
              ["累计错题", data?.total ?? 0],
              ["本周新增", data?.weekly_new ?? 0],
              ["今日待复习", data?.due_today ?? 0],
              ["高频错题", data?.frequent ?? 0]
            ].map(([label, value]) => (
              <div className="card" key={label}>
                <p className="text-sm text-slate-500">{label}</p>
                <strong className="mt-2 block text-3xl">{value}</strong>
              </div>
            ))}
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <Rank title="薄弱知识点" items={data?.weak_knowledge || []} />
            <Rank title="错因排行" items={data?.mistake_reasons || []} />
          </div>
        </div>
      </AppShell>
    </RequireAuth>
  );
}

function Rank({ title, items }: { title: string; items: Array<{ name: string; count: number }> }) {
  return (
    <div className="card">
      <h2 className="mb-3 font-bold">{title}</h2>
      {!items.length && <p className="text-sm text-slate-500">暂无数据，先上传一道错题吧。</p>}
      <div className="grid gap-2">
        {items.map((item) => (
          <div key={item.name} className="flex justify-between rounded-lg bg-slate-50 p-3">
            <span>{item.name}</span>
            <strong>{item.count}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}
