#!/usr/bin/env python3
"""
Generate 3-4 English bullet summary per scheme using Gemini.
Sources: name, description, detailed_description_md, benefits_md, eligibility_md
Stores in: schemes.summary_bullets (TEXT — markdown bullet list)
Resumable: skips schemes where summary_bullets is already set.
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

# Each thread gets its own dedicated key (assigned once on first call)
_thread_local = threading.local()
_slot_counter = 0
_slot_lock = threading.Lock()

def get_key() -> str:
    """Returns this thread's dedicated Gemini key — assigned once per thread."""
    global _slot_counter
    if not hasattr(_thread_local, "key"):
        with _slot_lock:
            slot = _slot_counter % len(GEMINI_KEYS)
            _slot_counter += 1
        _thread_local.key = GEMINI_KEYS[slot]
        # Stagger worker starts so 9 don't hit simultaneously
        time.sleep(slot * 0.3)
    return _thread_local.key


SYSTEM = (
    "You are a content writer for an Indian government scheme portal. "
    "Write simple, clear English that low-literacy rural users can understand."
)

def gen_summary_bullets(scheme: dict) -> str | None:
    name = scheme.get("name", "")
    desc = scheme.get("detailed_description_md") or scheme.get("description") or ""
    benefits = scheme.get("benefits_md") or ""
    eligib = scheme.get("eligibility_md") or ""
    benefit_type = scheme.get("benefit_type") or ""
    benefit_amt = scheme.get("benefit_amount_inr")

    prompt = (
        f"Scheme: {name}\n"
        f"Description: {desc[:500]}\n"
        f"Benefits: {benefits[:400]}\n"
        f"Eligibility: {eligib[:300]}\n\n"
        "Write EXACTLY 3 bullet points (each starting with '- ') that summarize:\n"
        "1. What this scheme does (one sentence)\n"
        "2. Who can apply (most important eligibility criteria)\n"
        "3. What you get (main benefit, include amount if available)\n\n"
        "Rules: Plain English. No jargon. Max 15 words per bullet. No numbering — use '-' only."
    )

    if benefit_amt:
        prompt = prompt.replace("include amount if available", f"₹{benefit_amt:,} benefit")

    key = get_key()
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 65536,
    }

    url = f"{BASE_URL}chat/completions"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
    )

    for attempt in range(5):
        try:
            # Rebuild request each attempt (urllib body stream is consumed on first read)
            r = urllib.request.Request(
                url,
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
            )
            with urllib.request.urlopen(r, timeout=45) as resp:
                result = json.loads(resp.read())
                text = result["choices"][0]["message"]["content"].strip()
                bullets = [ln.strip() for ln in text.splitlines() if ln.strip().startswith("-")]
                if len(bullets) >= 2:
                    return "\n".join(bullets[:4])
                return text
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode()[:120]
            except Exception:
                pass
            print(f"  HTTP {e.code} attempt {attempt+1}: {body}", flush=True)
            wait = 10 * (attempt + 1)
            time.sleep(wait)
        except Exception as exc:
            print(f"  Error attempt {attempt+1}: {exc}", flush=True)
            time.sleep(5 * (attempt + 1))
    return None


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--workers", type=int, default=WORKERS)
    args = parser.parse_args()

    conn = psycopg2.connect(dbname="aarambha_haq")
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Get schemes without summary_bullets
    cur.execute(
        """SELECT id, slug, name, description, detailed_description_md,
                  benefits_md, eligibility_md, benefit_type, benefit_amount_inr
           FROM schemes
           WHERE summary_bullets IS NULL
             AND (detailed_description_md IS NOT NULL OR description IS NOT NULL)
           ORDER BY id"""
        + (f" LIMIT {args.limit}" if args.limit else "")
    )
    schemes = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()

    total = len(schemes)
    print(f"Generating summaries for {total} schemes  workers={args.workers}")

    done = 0
    fail = 0

    def process(scheme):
        bullets = gen_summary_bullets(scheme)
        return scheme["id"], scheme["slug"], bullets

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(process, s): s for s in schemes}
        for i, future in enumerate(as_completed(futures), 1):
            scheme_id, slug, bullets = future.result()
            if bullets:
                conn2 = psycopg2.connect(dbname="aarambha_haq")
                cur2 = conn2.cursor()
                cur2.execute("UPDATE schemes SET summary_bullets = %s WHERE id = %s", (bullets, scheme_id))
                conn2.commit()
                cur2.close()
                conn2.close()
                print(f"[{i:4d}/{total}] OK  {slug}")
                done += 1
            else:
                print(f"[{i:4d}/{total}] FAIL  {slug}")
                fail += 1

    print(f"\nDone. OK:{done}  FAIL:{fail}")


if __name__ == "__main__":
    main()
