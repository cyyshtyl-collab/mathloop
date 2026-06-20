export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "";

export type User = {
  id: string;
  email: string;
  name: string;
  role: string;
};

export type Mistake = {
  id: string;
  image_url: string;
  image_storage_key: string;
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
  mastery_status: string;
  review_count: number;
  correct_streak: number;
  wrong_count: number;
  next_review_date?: string;
  created_at: string;
  generated_questions: Array<{
    id: string;
    question_type: string;
    question_text: string;
    answer?: string;
    solution?: string;
    knowledge_point?: string;
    difficulty?: string;
  }>;
};

export type Dashboard = {
  total: number;
  weekly_new: number;
  due_today: number;
  frequent: number;
  weak_knowledge: Array<{ name: string; count: number }>;
  mistake_reasons: Array<{ name: string; count: number }>;
};

export function getToken() {
  if (typeof window === "undefined") return "";
  return localStorage.getItem("mathloop_token") || "";
}

export function setToken(token: string) {
  localStorage.setItem("mathloop_token", token);
}

export function clearToken() {
  localStorage.removeItem("mathloop_token");
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  if (!API_BASE) {
    throw new Error("缺少 NEXT_PUBLIC_API_BASE_URL，请先配置后端 API 地址");
  }
  const headers = new Headers(options.headers);
  if (!(options.body instanceof FormData)) headers.set("Content-Type", "application/json");
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(data?.detail || data?.message || "请求失败");
  }
  return data as T;
}
