"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { RequireAuth } from "@/components/RequireAuth";
import { api, Mistake } from "@/lib/api";

export default function ReviewPage() {
  const [items, setItems] = useState<Mistake[]>([]);
  const [index, setIndex] = useState(0);

  async function load() {
    const data = await api<Mistake[]>("/api/review/today");
    setItems(data);
    setIndex(0);
  }
  useEffect(() => { load(); }, []);

  async function submit(id: string, result: "correct" | "wrong" | "later") {
    await api(`/api/review/${id}/submit`, { method: "POST", body: JSON.stringify({ result }) });
    await load();
  }

  const item = items[index];

  return (
    <RequireAuth>
      <AppShell>
        <div className="grid gap-4">
          <div>
            <h1 className="text-xl font-bold">今日复习</h1>
            <p className="mt-1 text-sm text-slate-500">{items.length ? `第 ${index + 1} / ${items.length} 题` : "今天没有必须复习的错题"}</p>
          </div>
          {!item && <div className="card text-slate-500">今天没有必须复习的错题。</div>}
          {item && (
            <div className="card grid gap-4">
              <Link href={`/mistakes/${item.id}`} className="text-lg font-bold text-blue-700">{item.question_text}</Link>
              <p className="text-sm text-slate-500">{item.main_knowledge_point} · {item.mistake_reason} · {item.difficulty}</p>
              <div className="rounded-lg bg-slate-50 p-3">
                <p className="text-sm text-slate-500">正确做法</p>
                <p className="mt-1">{item.solution}</p>
              </div>
              <div>
                <h2 className="mb-2 font-bold">同类题</h2>
                <div className="grid gap-2">
                  {item.generated_questions.map((q) => (
                    <div key={q.id} className="rounded-lg border p-3">
                      <p className="font-medium">{q.question_type}：{q.question_text}</p>
                      <p className="mt-1 text-sm text-slate-500">答案：{q.answer}</p>
                    </div>
                  ))}
                </div>
              </div>
              <div className="grid gap-2 sm:grid-cols-3">
                <button className="btn btn-primary min-h-12" onClick={() => submit(item.id, "correct")}>做对了</button>
                <button className="btn min-h-12" onClick={() => submit(item.id, "wrong")}>做错了</button>
                <button className="btn min-h-12" onClick={() => submit(item.id, "later")}>稍后复习</button>
              </div>
              {items.length > 1 && (
                <div className="flex gap-2">
                  <button className="btn" disabled={index === 0} onClick={() => setIndex((i) => Math.max(0, i - 1))}>上一题</button>
                  <button className="btn" disabled={index === items.length - 1} onClick={() => setIndex((i) => Math.min(items.length - 1, i + 1))}>下一题</button>
                </div>
              )}
            </div>
          )}
        </div>
      </AppShell>
    </RequireAuth>
  );
}
