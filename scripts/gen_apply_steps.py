#!/usr/bin/env python3
"""
Translate how_to_apply + documents_required for ALL 25 languages in ONE Gemini call per scheme.

Strategy: 1 scheme → 1 call → 25 languages → store in scheme_translations.how_to_apply
2492 schemes, parallel key pool, 64K output → ~25 min total.

Usage:
    python3 scripts/gen_apply_steps.py              # all missing
    python3 scripts/gen_apply_steps.py --limit 5    # test
    python3 scripts/gen_apply_steps.py --redo       # regenerate all
"""

from __future__ import annotations
import argparse, json, os, time, threading, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

import psycopg2
import psycopg2.extras

# ── Key pool (round-robin across keys) ────────────────────────────────────
# Load keys from .env file (gitignored — never committed)
def _load_keys() -> list[str]:
    keys = []
    env_file = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_file):
        for line in open(env_file):
            if line.startswith("GEMINI_KEYS="):
                keys = [k.strip() for k in line.split("=", 1)[1].split(",") if k.strip()]
    if not keys:
        k = os.environ.get("GEMINI_KEYS") or os.environ.get("GEMINI_API_KEY")
        if k:
            keys = [x.strip() for x in k.split(",") if x.strip()]
    return keys

GEMINI_KEYS = _load_keys()
if not GEMINI_KEYS:
    raise SystemExit("No keys found. Add GEMINI_KEYS=key1,key2,... to .env file")

MODEL    = "gemini-3.1-flash-lite"
URL      = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
WORKERS  = min(len(GEMINI_KEYS) * 3, 20)

_key_idx  = 0
_key_lock = threading.Lock()

def next_key() -> str:
    global _key_idx
    with _key_lock:
        key = GEMINI_KEYS[_key_idx % len(GEMINI_KEYS)]
        _key_idx += 1
        return key

# ── All 25 languages ───────────────────────────────────────────────────────
LANGS = {
    "hi":  ("Hindi",          "Devanagari", "Standard Hindi — simple, clear"),
    "mr":  ("Marathi",        "Devanagari", "Standard Marathi"),
    "ne":  ("Nepali",         "Devanagari", "Standard Nepali"),
    "mai": ("Maithili",       "Devanagari", "Maithili dialect"),
    "sa":  ("Sanskrit",       "Devanagari", "Simple Sanskrit"),
    "doi": ("Dogri",          "Devanagari", "Dogri dialect"),
    "kok": ("Konkani",        "Devanagari", "Konkani in Devanagari"),
    "bn":  ("Bengali",        "Bengali",    "Standard Bengali"),
    "as":  ("Assamese",       "Bengali",    "Assamese"),
    "gu":  ("Gujarati",       "Gujarati",   "Standard Gujarati"),
    "pa":  ("Punjabi",        "Gurmukhi",   "Punjabi in Gurmukhi"),
    "or":  ("Odia",           "Odia",       "Standard Odia"),
    "ta":  ("Tamil",          "Tamil",      "Standard Tamil"),
    "te":  ("Telugu",         "Telugu",     "Standard Telugu"),
    "kn":  ("Kannada",        "Kannada",    "Standard Kannada"),
    "ml":  ("Malayalam",      "Malayalam",  "Standard Malayalam"),
    "ur":  ("Urdu",           "Nastaliq",   "Urdu in Nastaliq script"),
    "ks":  ("Kashmiri",       "Nastaliq",   "Kashmiri in Nastaliq"),
    "sd":  ("Sindhi",         "Perso-Arabic","Sindhi"),
    "mni": ("Manipuri",       "Meitei Mayek","Manipuri"),
    "brx": ("Bodo",           "Devanagari", "Bodo in Devanagari"),
    "sat": ("Santali",        "Ol Chiki",   "Santali in Ol Chiki script"),
    "raj": ("Rajasthani",     "Devanagari", "Rajasthani — use: राम-राम सा, थारा, आपां, घणो, कोनी"),
    "bho": ("Bhojpuri",       "Devanagari", "Bhojpuri — use: रउवा, बा, भइया, खातिर, होखे"),
    "hne": ("Chhattisgarhi",  "Devanagari", "Chhattisgarhi — use: जय जोहार, हावय, संगवारी, थे, मन"),
}

SYSTEM = """You are a government scheme expert who can explain application processes
in all Indian languages simply and clearly. Write for rural/semi-urban citizens.
Keep government terms (Aadhaar, CSC, BPL, OBC, SC, ST, PM, SHG) as-is.
For regional dialects (Rajasthani/Bhojpuri/Chhattisgarhi) use authentic local vocabulary.
Return ONLY valid JSON — no markdown, no explanation."""


def build_prompt(scheme: dict) -> str:
    lang_list = "\n".join(
        f'  "{code}": "{name} ({script}) — {hint}"'
        for code, (name, script, hint) in LANGS.items()
    )

    how_to = (scheme.get("how_to_apply_english") or "").strip()
    docs   = (scheme.get("documents_required_md") or "").strip()
    name   = (scheme.get("name") or scheme.get("slug") or "").strip()
    level  = scheme.get("level") or ""
    state  = scheme.get("state") or ""

    return f"""Translate the application steps and documents list for this government scheme into ALL 25 Indian languages.

SCHEME: {name} ({level}{" — " + state if state else ""})

HOW TO APPLY (English source):
{how_to[:800]}

DOCUMENTS REQUIRED (English source):
{docs[:400]}

TARGET LANGUAGES:
{lang_list}

OUTPUT FORMAT — return EXACTLY this JSON:
{{
  "hi":  {{"how_to_apply": "<numbered steps in Hindi, 4-8 steps max, simple language>", "documents": "<bullet list of docs in Hindi>"}},
  "mr":  {{"how_to_apply": "...", "documents": "..."}},
  "ne":  {{"how_to_apply": "...", "documents": "..."}},
  "mai": {{"how_to_apply": "...", "documents": "..."}},
  "sa":  {{"how_to_apply": "...", "documents": "..."}},
  "doi": {{"how_to_apply": "...", "documents": "..."}},
  "kok": {{"how_to_apply": "...", "documents": "..."}},
  "bn":  {{"how_to_apply": "...", "documents": "..."}},
  "as":  {{"how_to_apply": "...", "documents": "..."}},
  "gu":  {{"how_to_apply": "...", "documents": "..."}},
  "pa":  {{"how_to_apply": "...", "documents": "..."}},
  "or":  {{"how_to_apply": "...", "documents": "..."}},
  "ta":  {{"how_to_apply": "...", "documents": "..."}},
  "te":  {{"how_to_apply": "...", "documents": "..."}},
  "kn":  {{"how_to_apply": "...", "documents": "..."}},
  "ml":  {{"how_to_apply": "...", "documents": "..."}},
  "ur":  {{"how_to_apply": "...", "documents": "..."}},
  "ks":  {{"how_to_apply": "...", "documents": "..."}},
  "sd":  {{"how_to_apply": "...", "documents": "..."}},
  "mni": {{"how_to_apply": "...", "documents": "..."}},
  "brx": {{"how_to_apply": "...", "documents": "..."}},
  "sat": {{"how_to_apply": "...", "documents": "..."}},
  "raj": {{"how_to_apply": "...", "documents": "..."}},
  "bho": {{"how_to_apply": "...", "documents": "..."}},
  "hne": {{"how_to_apply": "...", "documents": "..."}}
}}

Rules:
- Keep URLs as-is (don't translate https://... links)
- Keep Aadhaar, CSC, BPL, OBC, SC, ST, PM, SHG unchanged
- Steps should be numbered (1. 2. 3.) in each language
- Documents as bullet list (• or •) in each language
- Write at READING LEVEL of a village resident
- Pure JSON only — no extra text"""


def call_gemini(scheme: dict) -> dict | None:
    key     = next_key()
    prompt  = build_prompt(scheme)
    payload = json.dumps({
        "model":    MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user",   "content": prompt},
        ],
        "max_tokens":      65536,
        "response_format": {"type": "json_object"},
    }).encode()

    for attempt in range(4):
        try:
            req = urllib.request.Request(URL, data=payload, headers={
                "Content-Type":  "application/json",
                "Authorization": f"Bearer {key}",
            })
            with urllib.request.urlopen(req, timeout=120) as r:
                text = json.loads(r.read())["choices"][0]["message"]["content"]
                return json.loads(text)
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:150]
            if e.code == 429:
                key = next_key()   # rotate to fresh key on quota hit
                time.sleep(5 * (attempt + 1))
            else:
                print(f"    HTTP {e.code} attempt {attempt+1}: {body}", flush=True)
                time.sleep(10 * (attempt + 1))
        except json.JSONDecodeError as e:
            print(f"    JSON err attempt {attempt+1}: {e}", flush=True)
            time.sleep(3)
        except Exception as ex:
            print(f"    Err attempt {attempt+1}: {ex}", flush=True)
            time.sleep(8 * (attempt + 1))
    return None


def upsert_many(scheme_id: int, translations: dict) -> int:
    """Upsert how_to_apply for all langs in one DB connection."""
    saved = 0
    conn  = psycopg2.connect(dbname="aarambha_haq")
    cur   = conn.cursor()
    for lang_code, data in translations.items():
        how_to = (data.get("how_to_apply") or "").strip()
        docs   = (data.get("documents") or "").strip()
        if not how_to:
            continue
        cur.execute(
            """INSERT INTO scheme_translations
                   (scheme_id, lang_code, how_to_apply)
               VALUES (%s, %s, %s)
               ON CONFLICT (scheme_id, lang_code) DO UPDATE
                   SET how_to_apply = EXCLUDED.how_to_apply,
                       translated_at = now()""",
            (scheme_id, lang_code, how_to + ("\n\n" + docs if docs else "")),
        )
        saved += 1
    conn.commit()
    cur.close()
    conn.close()
    return saved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--redo",  action="store_true")
    args = ap.parse_args()

    conn = psycopg2.connect(dbname="aarambha_haq")
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    if args.redo:
        cur.execute("""
            SELECT id, slug, name, level, state,
                   how_to_apply_english, documents_required_md
            FROM schemes
            WHERE how_to_apply_english IS NOT NULL AND how_to_apply_english != ''
            ORDER BY id
        """ + (f" LIMIT {args.limit}" if args.limit else ""))
    else:
        cur.execute("""
            SELECT s.id, s.slug, s.name, s.level, s.state,
                   s.how_to_apply_english, s.documents_required_md
            FROM schemes s
            WHERE s.how_to_apply_english IS NOT NULL AND s.how_to_apply_english != ''
              AND NOT EXISTS (
                SELECT 1 FROM scheme_translations t
                WHERE t.scheme_id = s.id
                  AND t.lang_code = 'hi'
                  AND t.how_to_apply IS NOT NULL
                  AND t.how_to_apply != ''
              )
            ORDER BY s.id
        """ + (f" LIMIT {args.limit}" if args.limit else ""))

    schemes = [dict(r) for r in cur.fetchall()]
    cur.close(); conn.close()

    total = len(schemes)
    print(f"\n{'─'*65}")
    print(f"  Schemes to process : {total}")
    print(f"  Languages per call : {len(LANGS)} (all 25 in one shot)")
    print(f"  Workers            : {WORKERS}  |  Keys: {len(GEMINI_KEYS)}")
    print(f"  Output             : 64K tokens per call")
    print(f"{'─'*65}\n")

    done = fail = saved = 0
    start = time.time()

    def process(scheme):
        data = call_gemini(scheme)
        return scheme, data

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {ex.submit(process, s): s for s in schemes}
        for future in as_completed(futures):
            scheme, data = future.result()

            if not data:
                fail += 1
                print(f"  ✗ FAIL  {scheme['slug']}", flush=True)
                continue

            n = upsert_many(scheme["id"], data)
            done  += 1
            saved += n
            elapsed = time.time() - start
            pct     = done / total * 100
            eta_s   = (elapsed / done * (total - done)) if done else 0
            bar     = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            print(
                f"  ✓ [{bar}] {pct:5.1f}%  "
                f"{done:4d}/{total}  "
                f"langs={n}  "
                f"ETA {int(eta_s//60)}m{int(eta_s%60):02d}s  "
                f"{scheme['slug']}",
                flush=True,
            )

    print(f"\n{'='*65}")
    print(f"  Done in {int((time.time()-start)//60)}m{int((time.time()-start)%60):02d}s")
    print(f"  Schemes : {done} OK  |  {fail} failed")
    print(f"  Rows    : {saved} total  ({saved // len(LANGS)} schemes × 25 langs)")
    print(f"  Keys used : {len(GEMINI_KEYS)}")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
