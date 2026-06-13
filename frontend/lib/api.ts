// Server-side API calls to FastAPI backend
// All functions run in RSC — zero client bundle cost

const API_BASE =
  process.env.API_BASE_URL ?? "http://localhost:8097";

export interface Scheme {
  id: number;
  slug: string;
  name: string;
  short_title: string;
  level: "Central" | "State";
  state: string;
  ministry: string;
  description: string;
  apply_url: string;
  beneficiary_type: string[];
  for_married: boolean;
  for_widow: boolean;
  for_pregnant: boolean;
  for_shg: boolean;
  for_girl_child: boolean;
  for_sc_st: boolean;
  for_minority: boolean;
  max_income_lakhs: number | null;
  min_class: number | null;
  max_class: number | null;
  streams: string[];
  genders: string[];
  // Enriched fields (Gemini-extracted)
  age_min: number | null;
  age_max: number | null;
  income_limit_annual_inr: number | null;
  gender: string | null;
  caste_categories: string[];
  minority_required: boolean;
  disability_required: boolean;
  residence_type: string | null;
  employment_status: string | null;
  benefit_type: string | null;
  benefit_amount_inr: number | null;
  benefit_amount_percent: number | null;
  benefit_amount_description: string | null;
  documents_required: Array<{ doc_name: string; mandatory: boolean }> | null;
  enrichment_confidence: number | null;
  enriched_at: string | null;
  // Translation overlay (present when lang param was used and translation exists)
  eligibility_text_translated?: string;
  benefit_text_translated?: string;
}

export interface PageContent {
  page_type: string;
  slug: string;
  lang: string;
  title: string;
  subtitle: string;
  seo_title: string;
  seo_desc: string;
  seo_keywords: string[];
  content_json: Record<string, unknown>;
  schema_json: Record<string, unknown> | null;
  word_count: number;
  updated_at: string;
}

export interface SchemesResponse {
  total: number;
  page: number;
  schemes: Scheme[];
}

export interface Category {
  key: string;
  name_hi: string;
  count: number;
}

async function apiFetch<T>(
  path: string,
  opts?: RequestInit & { next?: { revalidate?: number; tags?: string[] } }
): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    ...opts,
    next: { revalidate: 3600, ...opts?.next }, // 1hr cache default
  });
  if (!res.ok) throw new Error(`API ${path} → ${res.status}`);
  return res.json();
}

export async function getSchemes(params?: {
  category?: string;
  state?: string;
  q?: string;
  level?: string;
  page?: number;
  size?: number;
}): Promise<SchemesResponse> {
  const qp = new URLSearchParams();
  if (params?.category) qp.set("category", params.category);
  if (params?.state) qp.set("state", params.state);
  if (params?.q) qp.set("q", params.q);
  if (params?.level) qp.set("level", params.level);
  if (params?.page) qp.set("page", String(params.page));
  if (params?.size) qp.set("size", String(params.size ?? 24));
  return apiFetch<SchemesResponse>(`/api/schemes?${qp}`);
}

export async function getScheme(slug: string, lang?: string): Promise<Scheme | null> {
  try {
    const qp = lang ? `?lang=${lang}` : "";
    return await apiFetch<Scheme>(`/api/schemes/${slug}${qp}`);
  } catch {
    return null;
  }
}

export async function getCategories(): Promise<Category[]> {
  return apiFetch<Category[]>("/api/categories");
}

export async function getEligibleSchemes(params: {
  gender: string;
  age: number;
  state: string;
  income: number;        // annual INR (0 = not specified)
  caste?: string;        // SC|ST|OBC|EWS|General|unknown
  residence?: string;    // rural|urban
  has_disability?: boolean;
  is_minority?: boolean;
  has_bpl?: boolean;
}): Promise<{ count: number; schemes: Scheme[] }> {
  const qp = new URLSearchParams({
    gender:         params.gender,
    age:            String(params.age),
    state:          params.state,
    income:         String(params.income),
    caste:          params.caste || "",
    residence:      params.residence || "",
    has_disability: params.has_disability ? "1" : "0",
    is_minority:    params.is_minority   ? "1" : "0",
    has_bpl:        params.has_bpl       ? "1" : "0",
  });
  return apiFetch(`/api/check/results?${qp}`, { next: { revalidate: 0 } });
}
