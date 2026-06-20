"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { AppShell } from "@/components/AppShell";
import { RequireAuth } from "@/components/RequireAuth";
import { api } from "@/lib/api";

type Analysis = {
  recognition_status?: string;
  question_text: string;
  student_answer?: string;
  correct_answer?: string;
  solution?: string;
  mistake_step?: string;
  mistake_reason?: string;
  mistake_type?: string;
  main_knowledge_point?: string;
  prerequisite_points: string[];
  related_points: string[];
  grade?: string;
  semester?: string;
  difficulty?: string;
  generated_questions?: unknown[];
};

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState("");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [upload, setUpload] = useState<any>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function chooseFile(nextFile?: File) {
    if (!nextFile) return;
    setFile(nextFile);
    setPreview(URL.createObjectURL(nextFile));
    setAnalysis(null);
    setUpload(null);
  }

  async function analyze() {
    if (!file) return;
    setError("");
    setLoading(true);
    try {
      const form = new FormData();
      form.append("file", file);
      const uploaded = await api("/api/upload", { method: "POST", body: form });
      setUpload(uploaded);
      const result = await api<Analysis>("/api/analyze", { method: "POST", body: JSON.stringify(uploaded) });
      setAnalysis(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "上传失败");
    } finally {
      setLoading(false);
    }
  }

  function updateField(name: keyof Analysis, value: string) {
    if (!analysis) return;
    if (name === "prerequisite_points" || name === "related_points") {
      setAnalysis({ ...analysis, [name]: value.split(/[，,]/).map((item) => item.trim()).filter(Boolean) });
      return;
    }
    setAnalysis({ ...analysis, [name]: value } as Analysis);
  }

  async function save() {
    if (!analysis || !upload) return;
    const mistake = await api<{ id: string }>("/api/mistakes", {
      method: "POST",
      body: JSON.stringify({ ...analysis, ...upload })
    });
    router.push(`/mistakes/${mistake.id}`);
  }

  return (
    <RequireAuth>
      <AppShell>
        <div className="grid gap-4 lg:grid-cols-[420px_1fr]">
          <div className="card grid gap-4">
            <div>
              <h1 className="text-xl font-bold">拍照上传错题</h1>
              <p className="mt-1 text-sm text-slate-500">手机可直接拍照，也可以从相册选择。</p>
            </div>
            <label className="grid cursor-pointer place-items-center rounded-xl border-2 border-dashed border-blue-200 bg-blue-50 p-6 text-center">
              <input
                type="file"
                accept="image/*"
                capture="environment"
                className="hidden"
                onChange={(e) => chooseFile(e.target.files?.[0])}
              />
              <span className="text-lg font-bold text-blue-700">拍照或选择图片</span>
              <span className="mt-1 text-sm text-blue-600">jpg / png / webp，最大 10MB</span>
            </label>
            {preview && <img src={preview} alt="错题预览" className="max-h-[420px] w-full rounded-xl border object-contain" />}
            {error && <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
            <button className="btn btn-primary min-h-12 text-base" onClick={analyze} disabled={!file || loading}>
              {loading ? "识别中..." : "开始识别"}
            </button>
          </div>

          <div className="card grid gap-3">
            <h2 className="text-lg font-bold">确认识别结果</h2>
            {!analysis && <p className="text-sm text-slate-500">识别后可修改题目、答案、错因和知识点。</p>}
            {analysis && (
              <div className="grid gap-3">
                <Field label="题目内容" value={analysis.question_text} onChange={(v) => updateField("question_text", v)} textarea />
                <Field label="学生答案" value={analysis.student_answer || ""} onChange={(v) => updateField("student_answer", v)} />
                <Field label="正确答案" value={analysis.correct_answer || ""} onChange={(v) => updateField("correct_answer", v)} />
                <Field label="标准解法" value={analysis.solution || ""} onChange={(v) => updateField("solution", v)} textarea />
                <Field label="错误步骤" value={analysis.mistake_step || ""} onChange={(v) => updateField("mistake_step", v)} textarea />
                <div className="grid gap-3 md:grid-cols-2">
                  <Field label="错因" value={analysis.mistake_reason || ""} onChange={(v) => updateField("mistake_reason", v)} />
                  <Field label="知识点" value={analysis.main_knowledge_point || ""} onChange={(v) => updateField("main_knowledge_point", v)} />
                  <Field label="年级" value={analysis.grade || ""} onChange={(v) => updateField("grade", v)} />
                  <Field label="难度" value={analysis.difficulty || ""} onChange={(v) => updateField("difficulty", v)} />
                </div>
                <Field label="前置知识点（逗号分隔）" value={analysis.prerequisite_points.join("，")} onChange={(v) => updateField("prerequisite_points", v)} />
                <Field label="关联知识点（逗号分隔）" value={analysis.related_points.join("，")} onChange={(v) => updateField("related_points", v)} />
                <button className="btn btn-primary min-h-12 text-base" onClick={save}>生成错题卡</button>
              </div>
            )}
          </div>
        </div>
      </AppShell>
    </RequireAuth>
  );
}

function Field({ label, value, onChange, textarea = false }: { label: string; value: string; onChange: (value: string) => void; textarea?: boolean }) {
  return (
    <label className="field">
      <span>{label}</span>
      {textarea ? (
        <textarea value={value} onChange={(e) => onChange(e.target.value)} rows={3} />
      ) : (
        <input value={value} onChange={(e) => onChange(e.target.value)} />
      )}
    </label>
  );
}
