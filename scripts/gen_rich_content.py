#!/usr/bin/env python3
"""
Generate 5 rich English content fields per scheme in ONE Gemini call.

Fields:
  how_to_apply_english   TEXT      — step-by-step application guide
  use_case_english       TEXT      — 50-100 word real-life beneficiary story
  tips_english           JSONB     — 3-5 practical tips as JSON array of strings
  common_mistakes_english JSONB    — 3-4 mistakes to avoid as JSON array of strings
  key_eligibility_questions JSONB  — [{q, a}] eligibility as Q&A pairs

Resumable: skips schemes where ALL 5 fields are already populated.
Per-thread dedicated keys: each of 9 workers owns one key exclusively.
"""

from __future__ import annotations
import json
import os
import time
import threading
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

import psycopg2
import psycopg2.extras

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
MODEL = "gemini-3.1-flash-lite"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
WORKERS = min(len(GEMINI_KEYS), 9)

_thread_local = threading.local()
_slot_counter = 0
_slot_lock = threading.Lock()


def get_key() -> str:
    global _slot_counter
    if not hasattr(_thread_local, "key"):
        with _slot_lock:
            slot = _slot_counter % len(GEMINI_KEYS)
            _slot_counter += 1
        _thread_local.key = GEMINI_KEYS[slot]
        time.sleep(slot * 0.4)
    return _thread_local.key


SYSTEM = (
    "You are a content writer for a government scheme portal. "
    "All content must be factually derived from the provided scheme data. "
    "Never invent facts not present in the source data. "
    "Write for low-literacy rural Indian users — simple, clear, actionable English."
)


def build_prompt(s: dict) -> str:
    parts = [f"Scheme Name: {s.get('name', '')}"]
    if s.get("state") and s["state"] != "All":
        parts.append(f"State: {s['state']}")
    if s.get("ministry"):
        parts.append(f"Ministry: {s['ministry']}")
    if s.get("benefit_type"):
        parts.append(f"Benefit Type: {s['benefit_type']}")
    if s.get("benefit_amount_inr"):
        parts.append(f"Benefit Amount: ₹{s['benefit_amount_inr']:,}")
    if s.get("beneficiary_type"):
        parts.append(f"Beneficiary Types: {', '.join(s['beneficiary_type'])}")
    if s.get("detailed_description_md"):
        parts.append(f"\n--- Description ---\n{s['detailed_description_md'][:800]}")
    if s.get("eligibility_md"):
        parts.append(f"\n--- Eligibility ---\n{s['eligibility_md'][:500]}")
    if s.get("documents_required_md"):
        parts.append(f"\n--- Documents Required ---\n{s['documents_required_md'][:400]}")
    if s.get("application_process_md"):
        parts.append(f"\n--- Application Process ---\n{s['application_process_md'][:500]}")
    if s.get("benefits_md"):
        parts.append(f"\n--- Benefits ---\n{s['benefits_md'][:400]}")
    if s.get("apply_url"):
        parts.append(f"Apply URL: {s['apply_url']}")

    return "\n".join(parts)


def gen_rich_content(scheme: dict) -> dict | None:
    prompt = build_prompt(scheme)
    key = get_key()

    instruction = (
        "\n\nGenerate a JSON object with EXACTLY these 5 keys:\n"
        "- how_to_apply_english (string): step-by-step guide to apply\n"
        "- use_case_english (string): 50-80 word real-life beneficiary story\n"
        "- tips_english (array of strings): 3-5 practical tips for applicants\n"
        "- common_mistakes_english (array of strings): 3-4 mistakes to avoid\n"
        "- key_eligibility_questions (array of {q, a} objects): 3-5 eligibility Q&A pairs\n"
    )

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt + instruction},
        ],
        "max_tokens": 65536,
        "response_format": {"type": "json_object"},
    }

    url = f"{BASE_URL}chat/completions"

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
            with urllib.request.urlopen(r, timeout=60) as resp:
                result = json.loads(resp.read())
                text = result["choices"][0]["message"]["content"].strip()
                data = json.loads(text)

                # Validate required fields
                out = {}
                if isinstance(data.get("how_to_apply_english"), str):
                    out["how_to_apply_english"] = data["how_to_apply_english"].strip()
                if isinstance(data.get("use_case_english"), str):
                    out["use_case_english"] = data["use_case_english"].strip()
                if isinstance(data.get("tips_english"), list):
                    out["tips_english"] = [t for t in data["tips_english"] if isinstance(t, str)]
                if isinstance(data.get("common_mistakes_english"), list):
                    out["common_mistakes_english"] = [t for t in data["common_mistakes_english"] if isinstance(t, str)]
                if isinstance(data.get("key_eligibility_questions"), list):
                    out["key_eligibility_questions"] = [
                        q for q in data["key_eligibility_questions"]
                        if isinstance(q, dict) and q.get("q") and q.get("a")
                    ]

                if len(out) >= 3:
                    return out
                print(f"  Partial response (only {len(out)} fields), retrying...", flush=True)

        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode()[:120]
            except Exception:
                pass
            print(f"  HTTP {e.code} attempt {attempt+1}: {body}", flush=True)
            time.sleep(12 * (attempt + 1))
        except json.JSONDecodeError as e:
            print(f"  JSON parse error attempt {attempt+1}: {e}", flush=True)
            time.sleep(5)
        except Exception as exc:
            print(f"  Error attempt {attempt+1}: {exc}", flush=True)
            time.sleep(8 * (attempt + 1))

    return None


def save_to_db(scheme_id: int, data: dict) -> None:
    conn = psycopg2.connect(dbname="aarambha_haq")
    cur = conn.cursor()
    cur.execute(
        """UPDATE schemes SET
             how_to_apply_english       = COALESCE(%s, how_to_apply_english),
             use_case_english           = COALESCE(%s, use_case_english),
             tips_english               = COALESCE(%s::jsonb, tips_english),
             common_mistakes_english    = COALESCE(%s::jsonb, common_mistakes_english),
             key_eligibility_questions  = COALESCE(%s::jsonb, key_eligibility_questions)
           WHERE id = %s""",
        (
            data.get("how_to_apply_english"),
            data.get("use_case_english"),
            json.dumps(data.get("tips_english", [])),
            json.dumps(data.get("common_mistakes_english", [])),
            json.dumps(data.get("key_eligibility_questions", [])),
            scheme_id,
        ),
    )
    conn.commit()
    cur.close()
    conn.close()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--workers", type=int, default=WORKERS)
    args = parser.parse_args()

    conn = psycopg2.connect(dbname="aarambha_haq")
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """SELECT id, slug, name, state, ministry, benefit_type, benefit_amount_inr,
                  beneficiary_type, detailed_description_md, description,
                  eligibility_md, documents_required_md, application_process_md,
                  benefits_md, apply_url
           FROM schemes
           WHERE how_to_apply_english IS NULL
              OR use_case_english IS NULL
              OR tips_english IS NULL
              OR key_eligibility_questions IS NULL
           ORDER BY id"""
        + (f" LIMIT {args.limit}" if args.limit else "")
    )
    schemes = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()

    total = len(schemes)
    print(f"Rich content generation for {total} schemes  workers={args.workers}")

    done = 0
    fail = 0

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(gen_rich_content, s): s for s in schemes}
        for i, future in enumerate(as_completed(futures), 1):
            s = futures[future]
            try:
                data = future.result()
            except Exception as exc:
                print(f"[{i:4d}/{total}] FAIL  {s['slug']}  exception: {exc}", flush=True)
                fail += 1
                continue

            if data:
                save_to_db(s["id"], data)
                fields = " ".join(k[:6] for k in data)
                print(f"[{i:4d}/{total}] OK  {s['slug']}  [{fields}]", flush=True)
                done += 1
            else:
                print(f"[{i:4d}/{total}] FAIL  {s['slug']}", flush=True)
                fail += 1

    print(f"\nDone. OK:{done}  FAIL:{fail}")


if __name__ == "__main__":
    main()
