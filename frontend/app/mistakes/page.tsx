"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { RequireAuth } from "@/components/RequireAuth";
import { api, Mistake } from "@/lib/api";

export default function MistakesPage() {
  const [items, setItems] = useState<Mistake[]>([]);
  const [query, setQuery] = useState("");
  const [grade, setGrade] = useState("");
  const [knowledge, setKnowledge] = useState("");
  const [reason, setReason] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const [status, setStatus] = useState("");

  useEffect(() => {
    api<Mistake[]>("/api/mistakes").then(setItems);
  }, []);

  const filtered = useMemo(() => {
    return items.filter((item) => {
      const text = `${item.question_text} ${item.main_knowledge_point} ${item.mistake_reason}`.toLowerCase();
      return (!query || text.includes(query.toLowerCase()))
        && (!grade || item.grade === grade)
        && (!knowledge || item.main_knowledge_point === knowledge)
        && (!reason || item.mistake_reason === reason)
        && (!difficulty || item.difficulty === difficulty)
        && (!status || item.mastery_status === status);
    });
  }, [items, query, grade, knowledge, reason, difficulty, status]);

  const uniq = (values: Array<string | undefined>) => [...new Set(values.filter(Boolean) as string[])];

  return (
    <RequireAuth>
      <AppShell>
        <div className="grid gap-4">
          <div className="card">
            <h1 className="mb-4 text-xl font-bold">错题库</h1>
            <div className="grid gap-3 md:grid-cols-3">
              <input className="rounded-lg border px-3 py-2" placeholder="搜索题目 / 知识点 / 错因" value={query} onChange={(e) => setQuery(e.target.value)} />
              <Select value={grade} onChange={setGrade} label="全部年级" options={uniq(items.map((i) => i.grade))} />
              <Select value={knowledge} onChange={setKnowledge} label="全部知识点" options={uniq(items.map((i) => i.main_knowledge_point))} />
              <Select value={reason} onChange={setReason} label="全部错因" options={uniq(items.map((i) => i.mistake_reason))} />
              <Select value={difficulty} onChange={setDifficulty} label="全部难度" options={uniq(items.map((i) => i.difficulty))} />
              <Select value={status} onChange={setStatus} label="全部状态" options={uniq(items.map((i) => i.mastery_status))} />
            </div>
          </div>
          <div className="grid gap-3">
            {filtered.map((item) => (
              <Link key={item.id} href={`/mistakes/${item.id}`} className="card block hover:bg-slate-50">
                <strong className="line-clamp-2">{item.question_text}</strong>
                <p className="mt-2 text-sm text-slate-500">{item.grade} · {item.main_knowledge_point} · {item.mistake_reason} · {item.difficulty}</p>
                <p className="mt-1 text-sm text-blue-700">状态：{item.mastery_status} · 下次复习：{item.next_review_date || "-"}</p>
              </Link>
            ))}
            {!filtered.length && <div className="card text-sm text-slate-500">暂无符合条件的错题。</div>}
          </div>
        </div>
      </AppShell>
    </RequireAuth>
  );
}

function Select({ value, onChange, label, options }: { value: string; onChange: (value: string) => void; label: string; options: string[] }) {
  return (
    <select className="rounded-lg border px-3 py-2" value={value} onChange={(e) => onChange(e.target.value)}>
      <option value="">{label}</option>
      {options.map((option) => <option key={option} value={option}>{option}</option>)}
    </select>
  );
}
