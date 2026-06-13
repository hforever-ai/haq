#!/usr/bin/env python3
"""
Generate NATIVE scheme content for Rajasthani, Bhojpuri, Chhattisgarhi.

Batches 10 schemes per Gemini call → ~275 calls total (vs 2754 one-by-one).
Rate-limited to 15 RPM (free key limit).

Usage:
    python3 scripts/gen_regional_content.py              # all missing
    python3 scripts/gen_regional_content.py --limit 20   # test
    python3 scripts/gen_regional_content.py --redo        # regenerate all
"""

from __future__ import annotations
import argparse, json, os, time, threading, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

import psycopg2
import psycopg2.extras

# ── Config ─────────────────────────────────────────────────────────────────
FREE_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL     = "gemini-3.1-flash-lite"
URL       = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
BATCH     = 10   # schemes per call → 276 batches for 2754 schemes (< 500 free calls)
WORKERS   = 5    # parallel threads — stay under RPM
RPM_LIMIT = 12   # safe limit (key refresh)

LANGS = {
    "raj": "Rajasthani",
    "bho": "Bhojpuri",
    "hne": "Chhattisgarhi",
}

# ── Rate limiter: sliding-window max RPM_LIMIT calls per 60s ───────────────
_rpm_lock   = threading.Lock()
_call_times: list[float] = []


def rate_limited_call(fn):
    with _rpm_lock:
        now = time.time()
        _call_times[:] = [t for t in _call_times if now - t < 60]
        if len(_call_times) >= RPM_LIMIT:
            sleep_for = 60 - (now - _call_times[0]) + 0.5
            if sleep_for > 0:
                time.sleep(sleep_for)
        _call_times.append(time.time())
    return fn()


# ── Prompts ────────────────────────────────────────────────────────────────
SYSTEM = (
    "You are a trusted village-level government scheme officer fluent in Indian regional dialects.\n"
    "Explain central/state government schemes IN LOCAL DIALECT — the way a neighbor would, not a bureaucrat.\n\n"
    "Rules:\n"
    "1. Write in Devanagari script for all three languages.\n"
    "2. Keep acronyms as-is: PM, BPL, SC, ST, OBC, Aadhaar, CSC, PMAY, MGNREGA, etc.\n"
    "3. Use authentic dialect vocabulary (see examples) — NOT standard Hindi.\n"
    "4. Start description with a native dialect greeting, then explain simply.\n"
    "5. Return ONLY valid JSON — no markdown, no code fences, no explanation.\n\n"
    "DIALECT VOCABULARY GUIDE:\n"
    "Rajasthani (raj):\n"
    "  आपां=हम/हमें, थारा/थांरो=आपका, कोनी=नहीं, घणो/घणी=बहुत, राम-राम सा=नमस्ते\n"
    "  भेळो=साथ, बाई=बहन, म्हारो=हमारा, हां जी=हाँ, सा=सम्मान suffix\n"
    "  Start with: 'राम-राम सा!' or 'हां जी सा!'\n\n"
    "Bhojpuri (bho):\n"
    "  रउवा=आप, हमार=हमारा, बा=है, बाड़न=हैं, होखे=होता है, भइया=भाई\n"
    "  मिली=मिलेगा, देवे=देता है, खातिर=के लिए, जइसन=जैसा, बहुते=बहुत\n"
    "  Start with: 'भइया!' or 'दीदी, का हाल बा?'\n\n"
    "Chhattisgarhi (hne):\n"
    "  संगवारी=दोस्त, जय जोहार=नमस्ते, हावय=है, थे=आप, मन=plural suffix\n"
    "  कइसे=कैसे, बने=अच्छा, ले=से, करे=करता है, जानव=जानते हो\n"
    "  Start with: 'जय जोहार संगवारी!'"
)


def build_prompt(schemes: list[dict]) -> str:
    blocks = []
    for i, s in enumerate(schemes):
        lines = [f"[{i}] {(s.get('name') or '').strip()}"]
        if s.get("level"):                   lines.append(f"Level: {s['level']}")
        if s.get("state"):                   lines.append(f"State: {s['state']}")
        if s.get("description"):             lines.append(f"Desc: {s['description'][:250].strip()}")
        if s.get("detailed_description_md"): lines.append(f"Detail: {s['detailed_description_md'][:250].strip()}")
        if s.get("eligibility_md"):          lines.append(f"Eligibility: {s['eligibility_md'][:180].strip()}")
        if s.get("benefits_md"):             lines.append(f"Benefits: {s['benefits_md'][:120].strip()}")
        blocks.append("\n".join(lines))

    n = len(schemes)
    last = n - 1

    return (
        f"Generate NATIVE dialect explanations for {n} government schemes.\n\n"
        "SCHEMES:\n"
        + "\n\n".join(blocks)
        + f"""

OUTPUT — return EXACTLY this JSON (keys "0" to "{last}"):
{{
  "0": {{
    "raj": {{
      "scheme_name": "<Rajasthani name>",
      "description": "<90-110 words in Rajasthani — राम-राम सा greeting + what it does + who benefits>",
      "eligibility_text": "<2-3 sentences: income/caste/age conditions in Rajasthani>",
      "benefit_text": "<1-2 sentences: exact money/benefit in Rajasthani>"
    }},
    "bho": {{
      "scheme_name": "<Bhojpuri name>",
      "description": "<90-110 words in Bhojpuri — भइया/दीदी opening + simple explanation>",
      "eligibility_text": "<2-3 sentences in Bhojpuri>",
      "benefit_text": "<1-2 sentences in Bhojpuri>"
    }},
    "hne": {{
      "scheme_name": "<Chhattisgarhi name>",
      "description": "<90-110 words in Chhattisgarhi — जय जोहार संगवारी opening + हावय/थे/मन>",
      "eligibility_text": "<2-3 sentences in Chhattisgarhi>",
      "benefit_text": "<1-2 sentences in Chhattisgarhi>"
    }}
  }},
  "1": {{ ... }},
  "{last}": {{ ... }}
}}

IMPORTANT: Pure JSON only. No markdown. Use authentic dialect from the guide above."""
    )


# ── Gemini call ────────────────────────────────────────────────────────────
def call_gemini(schemes: list[dict]) -> dict | None:
    prompt  = build_prompt(schemes)
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
            req = urllib.request.Request(
                URL, data=payload,
                headers={
                    "Content-Type":  "application/json",
                    "Authorization": f"Bearer {FREE_KEY}",
                },
            )

            def _do():
                with urllib.request.urlopen(req, timeout=120) as r:
                    return json.loads(r.read())["choices"][0]["message"]["content"]

            text = rate_limited_call(_do)
            return json.loads(text)

        except urllib.error.HTTPError as e:
            body = e.read().decode()[:200]
            print(f"    HTTP {e.code} attempt {attempt+1}: {body}", flush=True)
            time.sleep(15 * (attempt + 1))
        except json.JSONDecodeError as e:
            print(f"    JSON err attempt {attempt+1}: {e}", flush=True)
            time.sleep(5)
        except Exception as ex:
            print(f"    Err attempt {attempt+1}: {ex}", flush=True)
            time.sleep(10 * (attempt + 1))

    return None


# ── DB upsert ──────────────────────────────────────────────────────────────
def upsert(scheme_id: int, lang: str, row: dict) -> None:
    conn = psycopg2.connect(dbname="aarambha_haq")
    cur  = conn.cursor()
    cur.execute(
        """INSERT INTO scheme_translations
               (scheme_id, lang_code, scheme_name, short_title, description,
                eligibility_text, benefit_text)
           VALUES (%s,%s,%s,%s,%s,%s,%s)
           ON CONFLICT (scheme_id, lang_code) DO UPDATE SET
             scheme_name     = EXCLUDED.scheme_name,
             short_title     = EXCLUDED.short_title,
             description     = EXCLUDED.description,
             eligibility_text= EXCLUDED.eligibility_text,
             benefit_text    = EXCLUDED.benefit_text,
             translated_at   = now()""",
        (
            scheme_id, lang,
            row.get("scheme_name", ""),
            row.get("short_title",  ""),
            row.get("description",  ""),
            row.get("eligibility_text", ""),
            row.get("benefit_text", ""),
        ),
    )
    conn.commit()
    cur.close()
    conn.close()


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Process N schemes (test mode)")
    parser.add_argument("--redo",  action="store_true",    help="Regenerate even existing translations")
    args = parser.parse_args()

    target_langs = list(LANGS.keys())

    conn = psycopg2.connect(dbname="aarambha_haq")
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    if args.redo:
        query = """
            SELECT s.id, s.slug, s.name, s.short_title, s.level, s.state,
                   s.description, s.detailed_description_md,
                   s.eligibility_md, s.benefits_md
            FROM schemes s ORDER BY s.id
        """
        params = ()
    else:
        placeholders = ",".join(["%s"] * len(target_langs))
        query = f"""
            SELECT DISTINCT s.id, s.slug, s.name, s.short_title, s.level, s.state,
                   s.description, s.detailed_description_md,
                   s.eligibility_md, s.benefits_md
            FROM schemes s
            WHERE (SELECT COUNT(*) FROM scheme_translations t
                   WHERE t.scheme_id = s.id
                     AND t.lang_code IN ({placeholders})) < %s
            ORDER BY s.id
        """
        params = (*target_langs, len(target_langs))

    if args.limit:
        query += f" LIMIT {args.limit}"

    cur.execute(query, params)
    schemes = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()

    total     = len(schemes)
    n_batches = (total + BATCH - 1) // BATCH

    print(f"\n{'─'*60}")
    print(f"  Schemes to process : {total}")
    print(f"  Batches (10/call)  : {n_batches}")
    print(f"  Workers            : {WORKERS}  |  RPM limit: {RPM_LIMIT}")
    print(f"  Languages          : {', '.join(f'{k} ({v})' for k, v in LANGS.items())}")
    print(f"  Free calls budget  : 500  (need {n_batches})")
    print(f"{'─'*60}\n")

    done = fail = saved = 0
    start_time = time.time()

    batches = [schemes[i : i + BATCH] for i in range(0, total, BATCH)]

    def process_batch(batch_schemes, batch_idx):
        data = call_gemini(batch_schemes)
        return batch_idx, batch_schemes, data

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {ex.submit(process_batch, b, i): i for i, b in enumerate(batches)}
        for future in as_completed(futures):
            batch_idx, batch_schemes, data = future.result()

            if not data:
                fail += len(batch_schemes)
                slugs = [s["slug"] for s in batch_schemes]
                print(f"  ✗ Batch {batch_idx+1:3d}/{n_batches}  FAILED  slugs={slugs}", flush=True)
                continue

            batch_saved = 0
            for j, scheme in enumerate(batch_schemes):
                scheme_data = data.get(str(j))
                if not isinstance(scheme_data, dict):
                    continue
                for lang in target_langs:
                    row = scheme_data.get(lang)
                    if isinstance(row, dict) and row.get("description"):
                        upsert(scheme["id"], lang, row)
                        batch_saved += 1

            done   += len(batch_schemes)
            saved  += batch_saved
            elapsed = time.time() - start_time
            pct     = done / total * 100
            eta_s   = (elapsed / done * (total - done)) if done else 0
            eta_m   = int(eta_s // 60)
            eta_ss  = int(eta_s % 60)
            bar     = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            print(
                f"  ✓ [{bar}] {pct:5.1f}%  "
                f"batch {batch_idx+1:3d}/{n_batches}  "
                f"schemes {done:4d}/{total}  "
                f"rows +{batch_saved}  "
                f"ETA {eta_m}m{eta_ss:02d}s",
                flush=True,
            )

    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"  Completed in {int(elapsed//60)}m{int(elapsed%60):02d}s")
    print(f"  Schemes  : {done} OK  |  {fail} failed")
    print(f"  Rows saved : {saved}  ({saved // max(len(target_langs), 1)} schemes fully done)")
    print(f"  API calls  : ~{n_batches - (fail // BATCH if fail else 0)} used")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
