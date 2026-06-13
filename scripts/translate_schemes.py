"""Phase 3 — Gemini parallel translation of all 2,754 schemes into 22 Indian languages.

One Gemini call per scheme translates all 22 languages simultaneously.
Stores: scheme_name, short_title, description, eligibility_text, benefit_text.

Usage:
    python3 scripts/translate_schemes.py                 # all untranslated
    python3 scripts/translate_schemes.py --limit 20      # test run
    python3 scripts/translate_schemes.py --redo          # re-translate all
    python3 scripts/translate_schemes.py --slug pmkisan  # single scheme
    python3 scripts/translate_schemes.py --workers 10    # more parallelism
"""

from __future__ import annotations

import argparse
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import psycopg2
import psycopg2.extras

# ── 22 Indian languages ─────────────────────────────────────────────────────
TARGET_LANGS = [
    "hi","mr","ne","mai","sa","doi","kok",
    "bn","as","gu","pa","or",
    "ta","te","kn","ml",
    "ur","ks","sd","mni","brx","sat",
]

# ── Gemini keys (9 verified-working) ────────────────────────────────────────
GEMINI_KEYS = [
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
]
MODEL    = "gemini-2.5-flash"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

SYSTEM_PROMPT = """You are a professional government document translator for India.
Translate the given government scheme information into all 22 requested Indian languages.
Keep scheme names accurate; do not transliterate — use proper script for each language.
Keep government terms like 'PM', 'PMKVY', 'Aadhaar', 'CSC' as-is.
Return ONLY valid JSON. No explanation, no extra text."""

LANG_NAMES = {
    "hi":"Hindi","mr":"Marathi","ne":"Nepali","mai":"Maithili","sa":"Sanskrit",
    "doi":"Dogri","kok":"Konkani","bn":"Bengali","as":"Assamese","gu":"Gujarati",
    "pa":"Punjabi","or":"Odia","ta":"Tamil","te":"Telugu","kn":"Kannada",
    "ml":"Malayalam","ur":"Urdu","ks":"Kashmiri","sd":"Sindhi","mni":"Manipuri",
    "brx":"Bodo","sat":"Santali",
}


# ── Key pool ─────────────────────────────────────────────────────────────────
class KeyPool:
    def __init__(self, keys: list[str]):
        self._keys = keys
        self._idx  = 0
        self._dead: dict[str, float] = {}
        self._lock = threading.Lock()

    def next(self) -> str | None:
        with self._lock:
            now = time.time()
            for offset in range(len(self._keys)):
                k = self._keys[(self._idx + offset) % len(self._keys)]
                if self._dead.get(k, 0) < now:
                    self._idx = (self._idx + offset + 1) % len(self._keys)
                    return k
            return None

    def mark_dead(self, key: str, seconds: int):
        with self._lock:
            self._dead[key] = time.time() + seconds


class Counter:
    def __init__(self):
        self._v = 0
        self._lock = threading.Lock()
    def inc(self) -> int:
        with self._lock:
            self._v += 1
            return self._v
    @property
    def value(self) -> int:
        return self._v


# ── Eligibility text builder (from enriched columns) ─────────────────────────
def build_eligibility_en(scheme: dict) -> str:
    parts = []
    if scheme.get("age_min") is not None or scheme.get("age_max") is not None:
        if scheme["age_min"] and scheme["age_max"]:
            parts.append(f"Age {scheme['age_min']}–{scheme['age_max']} years.")
        elif scheme["age_min"]:
            parts.append(f"Age {scheme['age_min']}+ years.")
        else:
            parts.append(f"Age up to {scheme['age_max']} years.")
    if scheme.get("income_limit_annual_inr"):
        inr = scheme["income_limit_annual_inr"]
        lakh = inr / 100_000
        parts.append(f"Annual income up to ₹{lakh:.1f} lakh.")
    cats = scheme.get("caste_categories") or []
    if cats:
        parts.append(f"Open to: {', '.join(cats)}.")
    if scheme.get("gender") and scheme["gender"] not in ("all", None):
        parts.append(f"For {scheme['gender']} applicants.")
    if scheme.get("residence_type"):
        parts.append(f"Applicable in {scheme['residence_type']} areas.")
    if scheme.get("disability_required"):
        parts.append("Persons with disability only.")
    if scheme.get("minority_required"):
        parts.append("Minority communities only.")
    return " ".join(parts) if parts else ""


def build_benefit_en(scheme: dict) -> str:
    if scheme.get("benefit_amount_description"):
        return scheme["benefit_amount_description"]
    if scheme.get("benefit_amount_inr"):
        inr = scheme["benefit_amount_inr"]
        if inr >= 1_00_000:
            return f"₹{inr/1_00_000:.1f} lakh benefit."
        return f"₹{inr:,} benefit."
    if scheme.get("benefit_amount_percent"):
        return f"{scheme['benefit_amount_percent']}% subsidy."
    return ""


# ── Gemini call ───────────────────────────────────────────────────────────────
def call_gemini(pool: KeyPool, scheme: dict) -> dict | None:
    from openai import OpenAI, RateLimitError

    desc      = (scheme.get("description") or "")[:600]
    elig_en   = build_eligibility_en(scheme)
    benefit_en = build_benefit_en(scheme)

    lang_list = "\n".join(
        f'  "{code}": {{"scheme_name":"...", "short_title":"...", "description":"...", "eligibility_text":"...", "benefit_text":"..."}}'
        for code in TARGET_LANGS
    )

    user_msg = f"""Translate this Indian government scheme into {len(TARGET_LANGS)} languages.

Name: {scheme["name"]}
Short title: {scheme.get("short_title") or scheme["name"][:60]}
Description: {desc}
Eligibility (English): {elig_en or "See description."}
Benefit (English): {benefit_en or "See description."}

Return EXACTLY this JSON structure (fill all values, keep scheme name accurate):
{{
{lang_list}
}}

Rules:
- description: 1-2 sentences max, natural in each language
- eligibility_text: plain language, no markdown
- benefit_text: plain language, no markdown
- short_title: brief name (4-8 words max)
- Use proper script for each language (not transliteration)
- Keep 'Aadhaar', 'PM', scheme acronyms as-is"""

    for _attempt in range(len(GEMINI_KEYS) * 2):
        key = pool.next()
        if key is None:
            time.sleep(30)
            key = pool.next()
            if key is None:
                return None
        try:
            client = OpenAI(api_key=key, base_url=BASE_URL)
            resp = client.chat.completions.create(
                model=MODEL,
                temperature=0.1,
                max_tokens=65536,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": user_msg},
                ],
            )
            data = json.loads(resp.choices[0].message.content)
            # Validate structure — must have at least one lang key
            if not any(k in data for k in TARGET_LANGS):
                return None
            return data
        except RateLimitError:
            pool.mark_dead(key, 90)
        except json.JSONDecodeError:
            return None
        except Exception as e:
            err = str(e)
            if "429" in err or "quota" in err.lower():
                pool.mark_dead(key, 90)
            elif "400" in err and "API key" in err:
                pool.mark_dead(key, 86400)
            else:
                time.sleep(2)
    return None


# ── DB helpers ────────────────────────────────────────────────────────────────
def db_conn():
    kw: dict = {"dbname": os.getenv("DB_NAME", "aarambha_haq")}
    if os.getenv("DB_HOST"):
        kw.update({
            "host": os.getenv("DB_HOST"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASS", ""),
        })
    return psycopg2.connect(**kw)


def load_schemes(redo: bool, slug: str | None, limit: int | None) -> list[dict]:
    conn = db_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    if slug:
        cur.execute(
            "SELECT id,slug,name,short_title,description,"
            "age_min,age_max,income_limit_annual_inr,gender,caste_categories,"
            "residence_type,disability_required,minority_required,"
            "benefit_amount_inr,benefit_amount_percent,benefit_amount_description "
            "FROM schemes WHERE slug = %s", (slug,)
        )
    elif redo:
        lim = f"LIMIT {limit}" if limit else ""
        cur.execute(
            "SELECT id,slug,name,short_title,description,"
            "age_min,age_max,income_limit_annual_inr,gender,caste_categories,"
            "residence_type,disability_required,minority_required,"
            "benefit_amount_inr,benefit_amount_percent,benefit_amount_description "
            f"FROM schemes ORDER BY id {lim}"
        )
    else:
        # Only schemes that don't have translations yet
        lim = f"LIMIT {limit}" if limit else ""
        cur.execute(
            "SELECT s.id,s.slug,s.name,s.short_title,s.description,"
            "s.age_min,s.age_max,s.income_limit_annual_inr,s.gender,s.caste_categories,"
            "s.residence_type,s.disability_required,s.minority_required,"
            "s.benefit_amount_inr,s.benefit_amount_percent,s.benefit_amount_description "
            "FROM schemes s "
            "WHERE NOT EXISTS (SELECT 1 FROM scheme_translations t WHERE t.scheme_id = s.id) "
            f"ORDER BY s.id {lim}"
        )

    rows = [dict(r) for r in cur.fetchall()]
    cur.close(); conn.close()
    return rows


_db_lock = threading.Lock()

def save_translations(scheme_id: int, translations: dict) -> int:
    """Upsert all language rows for a scheme. Returns count saved."""
    rows = []
    for lang in TARGET_LANGS:
        data = translations.get(lang)
        if not data or not isinstance(data, dict):
            continue
        rows.append((
            scheme_id, lang,
            (data.get("scheme_name") or "")[:500],
            (data.get("short_title") or "")[:200],
            (data.get("description") or "")[:2000],
            (data.get("eligibility_text") or "")[:1000],
            (data.get("benefit_text") or "")[:500],
        ))

    if not rows:
        return 0

    with _db_lock:
        conn = db_conn()
        cur  = conn.cursor()
        cur.executemany(
            """INSERT INTO scheme_translations
               (scheme_id, lang_code, scheme_name, short_title, description, eligibility_text, benefit_text, translated_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
               ON CONFLICT (scheme_id, lang_code)
               DO UPDATE SET
                   scheme_name      = EXCLUDED.scheme_name,
                   short_title      = EXCLUDED.short_title,
                   description      = EXCLUDED.description,
                   eligibility_text = EXCLUDED.eligibility_text,
                   benefit_text     = EXCLUDED.benefit_text,
                   translated_at    = NOW()
            """,
            rows,
        )
        conn.commit()
        cur.close(); conn.close()
    return len(rows)


# ── Worker ────────────────────────────────────────────────────────────────────
def process_scheme(
    scheme: dict, pool: KeyPool, counter: Counter, total: int
) -> tuple[str, str]:
    idx = counter.inc()
    t0  = time.time()

    data = call_gemini(pool, scheme)
    if data is None:
        print(f"[{idx:4d}/{total}] FAIL  {scheme['slug']}", flush=True)
        return (scheme["slug"], "FAIL")

    try:
        saved = save_translations(scheme["id"], data)
        elapsed = time.time() - t0
        print(f"[{idx:4d}/{total}] OK  langs={saved}  {elapsed:.1f}s  {scheme['slug']}", flush=True)
        return (scheme["slug"], "OK")
    except Exception as e:
        print(f"[{idx:4d}/{total}] DB_ERR  {scheme['slug']}  {e}", flush=True)
        return (scheme["slug"], "DB_ERR")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Translate schemes into 22 Indian languages")
    ap.add_argument("--limit",   type=int, default=None,  help="Max schemes to process")
    ap.add_argument("--workers", type=int, default=8,     help="Thread pool size")
    ap.add_argument("--redo",    action="store_true",     help="Re-translate already done")
    ap.add_argument("--slug",    default=None,            help="Single scheme slug")
    args = ap.parse_args()

    pool    = KeyPool(GEMINI_KEYS)
    schemes = load_schemes(args.redo, args.slug, args.limit)
    total   = len(schemes)
    counter = Counter()

    print(f"Translating {total} schemes  workers={args.workers}  langs={len(TARGET_LANGS)}")

    ok = fail = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {
            ex.submit(process_scheme, s, pool, counter, total): s
            for s in schemes
        }
        for fut in as_completed(futs):
            _, status = fut.result()
            if status == "OK": ok   += 1
            else:              fail += 1

    print(f"\n── Done ────────────────────────")
    print(f"  OK:   {ok}")
    print(f"  FAIL: {fail}")

    conn = db_conn()
    cur  = conn.cursor()
    cur.execute("""
        SELECT
            COUNT(DISTINCT scheme_id) schemes_done,
            COUNT(*) total_rows,
            COUNT(DISTINCT lang_code) langs
        FROM scheme_translations
    """)
    r = cur.fetchone()
    print(f"\n── DB stats ────────────────────")
    print(f"  Schemes translated: {r[0]}/{total}")
    print(f"  Total rows:         {r[1]}")
    print(f"  Languages:          {r[2]}")
    cur.close(); conn.close()


if __name__ == "__main__":
    main()
