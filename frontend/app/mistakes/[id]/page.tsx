"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { RequireAuth } from "@/components/RequireAuth";
import { API_BASE, api, getToken, Mistake } from "@/lib/api";

export default function MistakeDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [item, setItem] = useState<Mistake | null>(null);
  const [imageSrc, setImageSrc] = useState("");
  const [zoom, setZoom] = useState(false);

  async function load() {
    setItem(await api<Mistake>(`/api/mistakes/${params.id}`));
  }

  useEffect(() => {
    load();
  }, [params.id]);

  useEffect(() => {
    if (!item) return;
    if (item.image_url.startsWith("http")) {
      setImageSrc(item.image_url);
      return;
    }
    fetch(`${API_BASE}${item.image_url}`, { headers: { Authorization: `Bearer ${getToken()}` } })
      .then((res) => res.blob())
      .then((blob) => setImageSrc(URL.createObjectURL(blob)));
  }, [item]);

  async function patchStatus(mastery_status: string) {
    await api(`/api/mistakes/${params.id}`, { method: "PATCH", body: JSON.stringify({ mastery_status }) });
    await load();
  }

  async function submit(result: "correct" | "wrong") {
    await api(`/api/review/${params.id}/submit`, { method: "POST", body: JSON.stringify({ result }) });
    await load();
  }

  async function remove() {
    if (!confirm("确定删除这道错题吗？")) return;
    await api(`/api/mistakes/${params.id}`, { method: "DELETE" });
    router.push("/mistakes");
  }

  if (!item) return <RequireAuth><AppShell>加载中...</AppShell></RequireAuth>;

  return (
    <RequireAuth>
      <AppShell>
        <div className="grid gap-4 lg:grid-cols-[360px_1fr]">
          <div className="card">
            {imageSrc ? (
              <button className="block w-full" onClick={() => setZoom(true)}>
                <img src={imageSrc} alt="错题图片" className="w-full rounded-lg border" />
              </button>
            ) : (
              <div className="rounded-lg border p-8 text-center text-slate-500">图片加载中...</div>
            )}
            <div className="mt-4 grid grid-cols-2 gap-2">
              <button className="btn" onClick={() => patchStatus("已订正")}>标记已订正</button>
              <button className="btn btn-primary" onClick={() => submit("correct")}>复习正确</button>
              <button className="btn" onClick={() => submit("wrong")}>复习仍错</button>
              <button className="btn" onClick={() => patchStatus("已掌握")}>标记已掌握</button>
              <button className="btn col-span-2 border-red-200 text-red-600" onClick={remove}>删除错题</button>
            </div>
          </div>

          <div className="grid gap-4">
            <div className="card">
              <h1 className="text-xl font-bold">{item.main_knowledge_point || "错题详情"}</h1>
              <p className="mt-2 text-sm text-slate-500">状态：{item.mastery_status} · 难度：{item.difficulty} · 下次复习：{item.next_review_date}</p>
              <div className="mt-4 grid gap-3">
                <Info label="题目内容" value={item.question_text} />
                <Info label="学生答案" value={item.student_answer} />
                <Info label="正确答案" value={item.correct_answer} />
                <Info label="标准解法" value={item.solution} />
                <Info label="错误步骤" value={item.mistake_step} />
                <Info label="错误原因" value={item.mistake_reason} />
                <Info label="主知识点" value={item.main_knowledge_point} />
                <Info label="前置知识点" value={item.prerequisite_points.join("，")} />
                <Info label="关联知识点" value={item.related_points.join("，")} />
                <Info label="年级学期" value={`${item.grade || ""} ${item.semester || ""}`} />
              </div>
            </div>

            <div className="card">
              <h2 className="mb-3 font-bold">3 道同类题</h2>
              <div className="grid gap-3">
                {item.generated_questions.map((q) => (
                  <div key={q.id} className="rounded-lg bg-slate-50 p-3">
                    <strong>{q.question_type} · {q.difficulty}</strong>
                    <p className="mt-1">{q.question_text}</p>
                    <p className="mt-1 text-sm text-slate-600">答案：{q.answer}</p>
                    <p className="mt-1 text-sm text-slate-600">解析：{q.solution}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="card">
              <h2 className="mb-3 font-bold">复习计划</h2>
              <div className="grid gap-2 text-sm text-slate-600">
                <p>复习次数：{item.review_count} · 连续正确：{item.correct_streak} · 错误次数：{item.wrong_count}</p>
                <p>下次复习日期：{item.next_review_date || "-"}</p>
              </div>
            </div>
          </div>
        </div>
        {zoom && (
          <div className="fixed inset-0 z-50 grid place-items-center bg-black/80 p-4" onClick={() => setZoom(false)}>
            <img src={imageSrc} alt="错题大图" className="max-h-full max-w-full rounded-lg bg-white" />
          </div>
        )}
      </AppShell>
    </RequireAuth>
  );
}

function Info({ label, value }: { label: string; value?: string | null }) {
  return (
    <div className="rounded-lg border bg-white p-3">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-1 whitespace-pre-wrap">{value || "-"}</p>
    </div>
  );
}
