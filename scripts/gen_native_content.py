#!/usr/bin/env python3
"""
Generate NATIVE (not translated) scheme content in 22 Indian languages.

Difference from translate_schemes.py:
  - Does NOT translate English text word-for-word
  - Generates content as a native speaker would explain it to their community
  - Each language gets naturally written content grounded in English source facts
  - Uses Claude Haiku (fast/cheap) when ANTHROPIC_API_KEY is set, else Gemini

Usage:
    python3 scripts/gen_native_content.py                      # all schemes
    python3 scripts/gen_native_content.py --limit 5            # test
    python3 scripts/gen_native_content.py --redo               # regenerate all
    python3 scripts/gen_native_content.py --langs hi,mr,ta     # specific langs only

Stores in scheme_translations (scheme_name, short_title, description,
    eligibility_text, benefit_text) via UPSERT.
"""

from __future__ import annotations
import argparse
import json
import os
import time
import threading
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

import psycopg2
import psycopg2.extras

TARGET_LANGS = [
    "hi", "mr", "ne", "mai", "sa", "doi", "kok",
    "bn", "as", "gu", "pa", "or",
    "ta", "te", "kn", "ml",
    "ur", "ks", "sd", "mni", "brx", "sat",
]

LANG_NAMES = {
    "hi": "Hindi", "mr": "Marathi", "ne": "Nepali", "mai": "Maithili",
    "sa": "Sanskrit", "doi": "Dogri", "kok": "Konkani", "bn": "Bengali",
    "as": "Assamese", "gu": "Gujarati", "pa": "Punjabi", "or": "Odia",
    "ta": "Tamil", "te": "Telugu", "kn": "Kannada", "ml": "Malayalam",
    "ur": "Urdu", "ks": "Kashmiri", "sd": "Sindhi", "mni": "Manipuri",
    "brx": "Bodo", "sat": "Santali",
}

# ── Gemini fallback ──────────────────────────────────────────────────────────
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
GEMINI_MODEL = "gemini-3.1-flash-lite"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

_thread_local = threading.local()
_slot_counter = 0
_slot_lock = threading.Lock()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
USE_CLAUDE = bool(ANTHROPIC_API_KEY)

if USE_CLAUDE:
    import anthropic as _anthropic
    _claude_client = _anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    CLAUDE_MODEL = "claude-haiku-4-5-20251001"
    WORKERS = 12  # Claude is faster, more workers
    print(f"Backend: Claude ({CLAUDE_MODEL}), {WORKERS} workers")
else:
    WORKERS = min(len(GEMINI_KEYS), 9)
    print(f"Backend: Gemini ({GEMINI_MODEL}), {WORKERS} workers (set ANTHROPIC_API_KEY to use Claude)")


def get_gemini_key() -> str:
    global _slot_counter
    if not hasattr(_thread_local, "key"):
        with _slot_lock:
            slot = _slot_counter % len(GEMINI_KEYS)
            _slot_counter += 1
        _thread_local.key = GEMINI_KEYS[slot]
        time.sleep(slot * 0.3)
    return _thread_local.key


# ── Prompt ───────────────────────────────────────────────────────────────────

SYSTEM = """You are a local government scheme officer in India who deeply understands the communities you serve.
Your task: given the English facts about a government scheme, write a NATIVE explanation in each of the 22 Indian languages listed.

Rules:
- Write NATIVELY — as a local speaker would explain this to their neighbor, NOT as a word-for-word translation
- Use simple, everyday spoken language appropriate for that region
- Keep government identifiers (PM, PMKVY, Aadhaar, CSC, scheme names/acronyms) as-is — do not translate them
- Keep dates and numbers in the same format
- Eligibility text: state criteria conversationally (e.g., "18 se 40 saal ki mahila" not a bullet list)
- Benefit text: state the benefit clearly and warmly
- Return ONLY valid JSON. No extra text."""


def build_prompt(s: dict, langs: list[str]) -> str:
    lang_list = ", ".join(f"{LANG_NAMES[l]} ({l})" for l in langs)
    parts = [
        f"Scheme Name (English): {s.get('name', '')}",
        f"Short Title: {s.get('short_title', '') or ''}",
        f"Level: {s.get('level', '')} | State: {s.get('state', '')}",
    ]
    if s.get("description"):
        parts.append(f"Description: {s['description'][:400]}")
    if s.get("detailed_description_md"):
        parts.append(f"Full Description: {s['detailed_description_md'][:500]}")
    if s.get("eligibility_md"):
        parts.append(f"Eligibility: {s['eligibility_md'][:400]}")
    if s.get("benefits_md"):
        parts.append(f"Benefits: {s['benefits_md'][:300]}")
    if s.get("summary_bullets"):
        parts.append(f"Summary: {s['summary_bullets']}")

    parts.append(f"""
Generate a JSON object with one key per language code from: {lang_list}
Each value is an object with:
  - scheme_name: the scheme name adapted/transliterated for that language (keep acronyms)
  - short_title: short title in that language
  - description: 80-120 word native explanation of what this scheme does and who it helps
  - eligibility_text: 2-3 sentence natural eligibility summary in that language
  - benefit_text: 1-2 sentence benefit statement in that language

Example structure:
{{
  "hi": {{
    "scheme_name": "...",
    "short_title": "...",
    "description": "...",
    "eligibility_text": "...",
    "benefit_text": "..."
  }},
  "ta": {{ ... }}
}}""")

    return "\n".join(parts)


# ── LLM calls ────────────────────────────────────────────────────────────────

def call_claude(prompt: str) -> dict | None:
    for attempt in range(4):
        try:
            msg = _claude_client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=65536,
                system=SYSTEM,
                messages=[{"role": "user", "content": prompt}],
            )
            text = msg.content[0].text.strip()
            # Strip markdown code fences if present
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"  Claude JSON error attempt {attempt+1}: {e}", flush=True)
            time.sleep(3)
        except Exception as e:
            print(f"  Claude error attempt {attempt+1}: {type(e).__name__}: {str(e)[:100]}", flush=True)
            time.sleep(10 * (attempt + 1))
    return None


def call_gemini(prompt: str) -> dict | None:
    key = get_gemini_key()
    payload = {
        "model": GEMINI_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 65536,
        "response_format": {"type": "json_object"},
    }
    url = f"{GEMINI_BASE_URL}chat/completions"

    for attempt in range(5):
        try:
            r = urllib.request.Request(
                url,
                data=json.dumps(payload).encode(),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {key}",
                },
            )
            with urllib.request.urlopen(r, timeout=90) as resp:
                result = json.loads(resp.read())
                text = result["choices"][0]["message"]["content"].strip()
                return json.loads(text)
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode()[:120]
            except Exception:
                pass
            print(f"  Gemini HTTP {e.code} attempt {attempt+1}: {body}", flush=True)
            time.sleep(15 * (attempt + 1))
        except json.JSONDecodeError as e:
            print(f"  Gemini JSON error attempt {attempt+1}: {e}", flush=True)
            time.sleep(5)
        except Exception as exc:
            print(f"  Gemini error attempt {attempt+1}: {exc}", flush=True)
            time.sleep(10 * (attempt + 1))
    return None


def gen_native(scheme: dict, langs: list[str]) -> dict | None:
    prompt = build_prompt(scheme, langs)
    if USE_CLAUDE:
        return call_claude(prompt)
    return call_gemini(prompt)


# ── DB ────────────────────────────────────────────────────────────────────────

def upsert_translations(scheme_id: int, data: dict, langs: list[str]) -> int:
    saved = 0
    conn = psycopg2.connect(dbname="aarambha_haq")
    cur = conn.cursor()
    for lang in langs:
        row = data.get(lang)
        if not isinstance(row, dict):
            continue
        cur.execute(
            """INSERT INTO scheme_translations
               (scheme_id, lang_code, scheme_name, short_title, description, eligibility_text, benefit_text)
               VALUES (%s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (scheme_id, lang_code) DO UPDATE SET
                 scheme_name      = EXCLUDED.scheme_name,
                 short_title      = EXCLUDED.short_title,
                 description      = EXCLUDED.description,
                 eligibility_text = EXCLUDED.eligibility_text,
                 benefit_text     = EXCLUDED.benefit_text,
                 translated_at    = now()""",
            (
                scheme_id,
                lang,
                row.get("scheme_name", ""),
                row.get("short_title", ""),
                row.get("description", ""),
                row.get("eligibility_text", ""),
                row.get("benefit_text", ""),
            ),
        )
        saved += 1
    conn.commit()
    cur.close()
    conn.close()
    return saved


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--workers", type=int, default=WORKERS)
    parser.add_argument("--redo", action="store_true", help="Regenerate all, including already done")
    parser.add_argument("--langs", type=str, default=None, help="Comma-separated lang codes, e.g. hi,mr,ta")
    parser.add_argument("--slug", type=str, default=None)
    args = parser.parse_args()

    langs = TARGET_LANGS
    if args.langs:
        langs = [l.strip() for l in args.langs.split(",") if l.strip() in TARGET_LANGS]

    conn = psycopg2.connect(dbname="aarambha_haq")
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    if args.slug:
        cur.execute(
            """SELECT s.id, s.slug, s.name, s.short_title, s.level, s.state,
                      s.description, s.detailed_description_md, s.eligibility_md,
                      s.benefits_md, s.summary_bullets
               FROM schemes s WHERE s.slug = %s""",
            (args.slug,),
        )
    elif args.redo:
        cur.execute(
            """SELECT s.id, s.slug, s.name, s.short_title, s.level, s.state,
                      s.description, s.detailed_description_md, s.eligibility_md,
                      s.benefits_md, s.summary_bullets
               FROM schemes s
               ORDER BY s.id"""
            + (f" LIMIT {args.limit}" if args.limit else "")
        )
    else:
        # Only schemes missing at least one language
        placeholders = ",".join(["%s"] * len(langs))
        cur.execute(
            f"""SELECT DISTINCT s.id, s.slug, s.name, s.short_title, s.level, s.state,
                      s.description, s.detailed_description_md, s.eligibility_md,
                      s.benefits_md, s.summary_bullets
               FROM schemes s
               WHERE (
                 SELECT COUNT(*) FROM scheme_translations t
                 WHERE t.scheme_id = s.id AND t.lang_code IN ({placeholders})
               ) < %s
               ORDER BY s.id"""
            + (f" LIMIT {args.limit}" if args.limit else ""),
            (*langs, len(langs)),
        )

    schemes = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()

    total = len(schemes)
    print(f"Native content for {total} schemes, {len(langs)} langs, {args.workers} workers")

    done = 0
    fail = 0

    def process(s):
        data = gen_native(s, langs)
        return s["id"], s["slug"], data

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(process, s): s for s in schemes}
        for i, future in enumerate(as_completed(futures), 1):
            sid, slug, data = future.result()
            if data:
                n = upsert_translations(sid, data, langs)
                print(f"[{i:4d}/{total}] OK  {slug}  ({n}/{len(langs)} langs)", flush=True)
                done += 1
            else:
                print(f"[{i:4d}/{total}] FAIL  {slug}", flush=True)
                fail += 1

    print(f"\nDone. OK:{done}  FAIL:{fail}")


if __name__ == "__main__":
    main()
