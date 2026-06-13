"""Gemini parallel batch enrichment for aarambha-haq schemes.

Reads all schemes lacking `enriched_at`, calls gemini-2.5-flash with JSON mode
using a thread pool for parallelism. 13-key rotation with 429/400 handling.

Usage:
    python3 scripts/enrich_schemes.py                    # all unenriched
    python3 scripts/enrich_schemes.py --limit 50         # test run
    python3 scripts/enrich_schemes.py --workers 15       # more parallelism
    python3 scripts/enrich_schemes.py --redo             # re-enrich all
    python3 scripts/enrich_schemes.py --slug pmkisan     # single scheme
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import psycopg2
import psycopg2.extras

# ── Gemini keys (13-key pool) ───────────────────────────────────────────────
GEMINI_KEYS = [
    # 9 verified-working keys (4 invalid keys removed 2026-06-09)
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
MODEL      = "gemini-2.5-flash"
BASE_URL   = "https://generativelanguage.googleapis.com/v1beta/openai/"
CHECKPOINT = Path(__file__).parent.parent / "data" / "enrichment_checkpoint.jsonl"

SYSTEM_PROMPT = """You are a government scheme data extractor for Aarambha Haq.
Extract structured eligibility and benefit data from an Indian government scheme description.
Be precise. Use null for fields not explicitly mentioned. Do NOT infer or hallucinate.
Return ONLY valid JSON matching the schema exactly."""

SCHEMA_DESC = """{
  "age_min": integer or null,
  "age_max": integer or null,
  "income_limit_annual_inr": integer or null,
  "gender": "all"|"male"|"female"|"transgender"|null,
  "caste_categories": ["SC","ST","OBC","General","EWS"],
  "minority_required": boolean,
  "disability_required": boolean,
  "residence_type": "rural"|"urban"|"both"|null,
  "employment_status": "farmer"|"student"|"employed"|"unemployed"|"self_employed"|"any"|null,
  "benefit_type": "cash"|"kind"|"service"|"subsidy"|"loan"|"insurance"|"pension"|"education"|"housing"|"health"|"skill_development"|"food_security"|null,
  "benefit_amount_inr": integer or null,
  "benefit_amount_percent": integer or null,
  "benefit_amount_description": string or null,
  "documents_required": [{"doc_name": "Aadhaar Card", "mandatory": true}],
  "confidence_score": 0.0-1.0,
  "extraction_notes": string or null
}"""


# ── Thread-safe key pool ────────────────────────────────────────────────────
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


# ── Thread-safe counter ─────────────────────────────────────────────────────
class Counter:
    def __init__(self):
        self._v    = 0
        self._lock = threading.Lock()

    def inc(self) -> int:
        with self._lock:
            self._v += 1
            return self._v

    @property
    def value(self) -> int:
        return self._v


# ── Gemini call ─────────────────────────────────────────────────────────────
def call_gemini(pool: KeyPool, scheme: dict) -> dict | None:
    from openai import OpenAI, RateLimitError

    user_msg = (
        f"Extract structured eligibility data for this Indian government scheme:\n\n"
        f"Name: {scheme['name']}\n"
        f"State: {scheme.get('state','All')}\n"
        f"Beneficiary Types: {', '.join(scheme.get('beneficiary_type') or [])}\n"
        f"Tags: {', '.join(scheme.get('tags') or [])}\n\n"
        f"Description:\n{scheme.get('description','')}\n\n"
        f"Output JSON schema:\n{SCHEMA_DESC}"
    )

    for _ in range(len(GEMINI_KEYS) * 2):
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
            return json.loads(resp.choices[0].message.content)
        except RateLimitError:
            pool.mark_dead(key, 90)
        except json.JSONDecodeError:
            return None
        except Exception as e:
            err = str(e)
            if "429" in err or "quota" in err.lower():
                pool.mark_dead(key, 90)
            elif "400" in err and ("API key" in err or "INVALID_ARGUMENT" in err):
                pool.mark_dead(key, 86400)
            else:
                time.sleep(2)
    return None


# ── DB helpers ──────────────────────────────────────────────────────────────
def db_conn():
    kw: dict = {"dbname": os.getenv("DB_NAME", "aarambha_haq")}
    if os.getenv("DB_HOST"):
        kw.update({"host": os.getenv("DB_HOST"), "port": int(os.getenv("DB_PORT", "5432")),
                   "user": os.getenv("DB_USER"), "password": os.getenv("DB_PASS", "")})
    return psycopg2.connect(**kw)


def load_schemes(redo: bool, slug: str | None, limit: int | None) -> list[dict]:
    conn = db_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    parts, params = [], []
    if slug:
        parts.append("slug = %s"); params.append(slug)
    elif not redo:
        parts.append("enriched_at IS NULL")
    where = ("WHERE " + " AND ".join(parts)) if parts else ""
    lim   = f"LIMIT {limit}" if limit else ""
    cur.execute(
        f"SELECT id,slug,name,description,tags,state,beneficiary_type "
        f"FROM schemes {where} ORDER BY id {lim}", params
    )
    rows = [dict(r) for r in cur.fetchall()]
    cur.close(); conn.close()
    return rows


_db_lock = threading.Lock()

def save_enrichment(scheme_id: int, data: dict) -> None:
    conf = data.get("confidence_score")
    if conf is not None:
        conf = round(max(0.0, min(1.0, float(conf))), 2)

    age_min = data.get("age_min")
    age_max = data.get("age_max")
    if age_min is not None and age_max is not None and int(age_min) > int(age_max):
        age_min = age_max = None

    income = data.get("income_limit_annual_inr")
    if income is not None and not (0 < income < 100_000_000):
        income = None

    pct = data.get("benefit_amount_percent")
    if pct is not None and not (0 <= int(pct) <= 100):
        pct = None

    docs = data.get("documents_required") or []
    if not isinstance(docs, list):
        docs = []

    with _db_lock:
        conn = db_conn()
        cur  = conn.cursor()
        cur.execute("""
            UPDATE schemes SET
                age_min                    = %s,
                age_max                    = %s,
                income_limit_annual_inr    = %s,
                gender                     = %s,
                caste_categories           = %s,
                minority_required          = %s,
                disability_required        = %s,
                residence_type             = %s,
                employment_status          = %s,
                benefit_type               = %s,
                benefit_amount_inr         = %s,
                benefit_amount_percent     = %s,
                benefit_amount_description = %s,
                documents_required         = %s,
                enrichment_confidence      = %s,
                enrichment_notes           = %s,
                enriched_at                = NOW()
            WHERE id = %s
        """, (
            age_min, age_max, income,
            data.get("gender"),
            data.get("caste_categories") or [],
            bool(data.get("minority_required", False)),
            bool(data.get("disability_required", False)),
            data.get("residence_type"),
            data.get("employment_status"),
            data.get("benefit_type"),
            data.get("benefit_amount_inr"),
            pct,
            data.get("benefit_amount_description"),
            json.dumps(docs),
            conf,
            data.get("extraction_notes"),
            scheme_id,
        ))
        conn.commit()
        cur.close(); conn.close()


# ── Worker function ─────────────────────────────────────────────────────────
def process_scheme(scheme: dict, pool: KeyPool, counter: Counter,
                   total: int, ckpt_lock: threading.Lock, ckpt_file) -> tuple[str, str]:
    desc = (scheme.get("description") or "").strip()
    idx  = counter.inc()

    if len(desc) < 20:
        return (scheme["slug"], "SKIP")

    t0     = time.time()
    result = call_gemini(pool, scheme)

    if result is None:
        print(f"[{idx:4d}/{total}] FAIL  {scheme['slug']}", flush=True)
        return (scheme["slug"], "FAIL")

    try:
        save_enrichment(scheme["id"], result)
        elapsed = time.time() - t0
        conf    = result.get("confidence_score", 0) or 0
        print(f"[{idx:4d}/{total}] OK  conf={conf:.2f}  {elapsed:.1f}s  {scheme['slug']}", flush=True)

        with ckpt_lock:
            ckpt_file.write(json.dumps({"slug": scheme["slug"], "id": scheme["id"]}) + "\n")
            ckpt_file.flush()

        return (scheme["slug"], "OK")
    except Exception as e:
        print(f"[{idx:4d}/{total}] DB_ERR  {scheme['slug']}  {e}", flush=True)
        return (scheme["slug"], "DB_ERR")


# ── Main ────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit",   type=int, default=None)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--redo",    action="store_true")
    ap.add_argument("--slug",    default=None)
    args = ap.parse_args()

    pool    = KeyPool(GEMINI_KEYS)
    schemes = load_schemes(args.redo, args.slug, args.limit)
    total   = len(schemes)
    counter = Counter()

    print(f"Enriching {total} schemes  workers={args.workers}  model={MODEL}")
    CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)
    ckpt_lock = threading.Lock()
    ckpt_file = open(CHECKPOINT, "a")

    ok = fail = skip = 0

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {
            ex.submit(process_scheme, s, pool, counter, total, ckpt_lock, ckpt_file): s
            for s in schemes
        }
        for fut in as_completed(futs):
            _, status = fut.result()
            if status == "OK":      ok   += 1
            elif status == "FAIL":  fail += 1
            else:                   skip += 1

    ckpt_file.close()

    print(f"\n── Done ─────────────────────────────")
    print(f"  OK:   {ok}")
    print(f"  FAIL: {fail}")
    print(f"  SKIP: {skip}")

    conn = db_conn()
    cur  = conn.cursor()
    cur.execute("""
        SELECT
            COUNT(*) FILTER (WHERE enriched_at IS NOT NULL) enriched,
            COUNT(*) total,
            ROUND(AVG(enrichment_confidence)::numeric, 2) avg_conf,
            COUNT(*) FILTER (WHERE age_min IS NOT NULL) has_age,
            COUNT(*) FILTER (WHERE income_limit_annual_inr IS NOT NULL) has_income,
            COUNT(*) FILTER (WHERE caste_categories != '{}') has_caste,
            COUNT(*) FILTER (WHERE documents_required IS NOT NULL
                             AND documents_required::text != '[]') has_docs
        FROM schemes
    """)
    r = cur.fetchone()
    print(f"\n── DB stats ─────────────────────────")
    print(f"  Enriched:    {r[0]}/{r[1]}")
    print(f"  Avg conf:    {r[2]}")
    print(f"  Has age:     {r[3]}")
    print(f"  Has income:  {r[4]}")
    print(f"  Has caste:   {r[5]}")
    print(f"  Has docs:    {r[6]}")
    cur.close(); conn.close()


if __name__ == "__main__":
    main()
