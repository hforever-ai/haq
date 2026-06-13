"""
Generate rich scheme guide content (how-to-apply + use case story + tips) for all schemes.
Reads from local aarambha_haq Postgres DB.
Saves to web/data/guides/{slug}.json — served as static files, no server Gemini key needed.
"""
import json, pathlib, time, random, sys, re, urllib.request, urllib.error, os
import psycopg2, psycopg2.extras

# ── Keys ───────────────────────────────────────────────────────────────────
env = pathlib.Path("/Users/ajayagrawal/Documents/projects/shrutam-content-pipeline/.env")
KEYS = []
for line in env.read_text().splitlines():
    if line.startswith("GEMINI_API_KEYS="):
        KEYS = [k.strip() for k in line.split("=", 1)[1].split(",") if k.strip()]
        break
random.shuffle(KEYS)
_key_idx = 0

def next_key():
    global _key_idx
    k = KEYS[_key_idx % len(KEYS)]
    _key_idx += 1
    return k

MODEL    = "gemini-3.1-flash-lite"
API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

def extract_json(text: str) -> dict:
    text = text.strip()
    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found")
    depth, i, in_str, escape = 0, start, False, False
    while i < len(text):
        ch = text[i]
        if escape: escape = False
        elif ch == "\\": escape = True
        elif ch == '"' and not escape: in_str = not in_str
        elif not in_str:
            if ch == "{": depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    raw = re.sub(r",\s*([}\]])", r"\1", text[start:i+1])
                    return json.loads(raw)
        i += 1
    raise ValueError("Unclosed JSON")

def gemini_call(prompt: str, retries: int = 4) -> str:
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 65536,
            "temperature": 0.4,
            "responseMimeType": "application/json",
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }).encode()
    for attempt in range(retries):
        key = next_key()
        url = f"{API_BASE}/{MODEL}:generateContent?key={key}"
        req = urllib.request.Request(url, data=payload,
                                     headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"  HTTP {e.code} attempt {attempt+1}: {body[:120]}", file=sys.stderr)
            time.sleep(4 * (attempt + 1))
        except Exception as ex:
            print(f"  Error attempt {attempt+1}: {ex}", file=sys.stderr)
            time.sleep(3)
    raise RuntimeError("All retries failed")

GUIDE_PROMPT = """You are an expert on Indian government welfare schemes. Generate a rich, practical guide for citizens who want to apply for this scheme.

Scheme details:
- Name: {name}
- Level: {level} ({state})
- Ministry: {ministry}
- Description: {description}
- Who benefits: {beneficiary_type}
- Benefit: {benefit}
- Documents typically required: {documents}

Generate a practical guide in HINDI. Return ONLY this JSON:
{{
  "how_to_apply": [
    {{"step": 1, "title": "पहला कदम", "detail": "..."}},
    {{"step": 2, "title": "दूसरा कदम", "detail": "..."}},
    {{"step": 3, "title": "तीसरा कदम", "detail": "..."}},
    {{"step": 4, "title": "चौथा कदम", "detail": "..."}},
    {{"step": 5, "title": "पाँचवाँ कदम", "detail": "..."}}
  ],
  "use_case": {{
    "name": "Indian first name appropriate for target beneficiary",
    "age": 30,
    "occupation": "relevant occupation",
    "state": "relevant Indian state",
    "story": "2-3 sentence story: how this person learned about the scheme, what they did, what benefit they received. Make it feel real and specific with ₹ amounts."
  }},
  "tips": [
    "Practical tip 1 in Hindi",
    "Practical tip 2 in Hindi",
    "Practical tip 3 in Hindi"
  ],
  "common_mistakes": [
    "Common mistake 1 to avoid in Hindi",
    "Common mistake 2 to avoid in Hindi"
  ]
}}

Rules:
- All text in Hindi Devanagari script
- Steps must be actionable (what exactly to do, where to go, what to bring)
- Use_case must feel like a real person — specific amounts, specific state
- Tips must be truly useful (not generic)
- Keep scheme name in English within Hindi text
"""

def build_prompt(s: dict) -> str:
    benefit = s.get("benefit_amount_description") or ""
    if s.get("benefit_amount_inr"):
        benefit = f"₹{s['benefit_amount_inr']:,} — " + benefit
    elif s.get("benefit_amount_percent"):
        benefit = f"{s['benefit_amount_percent']}% — " + benefit
    docs = ", ".join(s.get("documents_required") or []) or "आधार, निवास, आय प्रमाण"
    btype = ", ".join(s.get("beneficiary_type") or []) or "सामान्य नागरिक"
    return GUIDE_PROMPT.format(
        name=s["name"],
        level=s["level"],
        state=s["state"] or "All India",
        ministry=s.get("ministry") or "Government of India",
        description=(s.get("description") or "")[:500],
        beneficiary_type=btype,
        benefit=benefit or s.get("benefit_type") or "सरकारी सहायता",
        documents=docs,
    )

def main():
    out_dir = pathlib.Path(__file__).parent.parent / "web" / "data" / "guides"
    out_dir.mkdir(parents=True, exist_ok=True)

    conn = psycopg2.connect(database="aarambha_haq")
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "SELECT slug, name, level, state, ministry, description, beneficiary_type, "
        "benefit_type, benefit_amount_inr, benefit_amount_percent, benefit_amount_description, "
        "documents_required "
        "FROM schemes ORDER BY enrichment_confidence DESC NULLS LAST"
    )
    schemes = [dict(r) for r in cur.fetchall()]
    cur.close(); conn.close()

    print(f"Total schemes: {len(schemes)}")
    done = {p.stem for p in out_dir.glob("*.json")}
    todo = [s for s in schemes if s["slug"] not in done]
    print(f"Already done: {len(done)}  |  Remaining: {len(todo)}")

    ok, fail = 0, 0
    for i, s in enumerate(todo):
        slug = s["slug"]
        print(f"[{i+1}/{len(todo)}] {slug[:30]:<30}  {s['name'][:50]}", end="  ")
        try:
            prompt = build_prompt(s)
            raw    = gemini_call(prompt)
            guide  = extract_json(raw)
            (out_dir / f"{slug}.json").write_text(
                json.dumps(guide, ensure_ascii=False, indent=2)
            )
            print("✓")
            ok += 1
        except Exception as ex:
            print(f"✗ {ex}", file=sys.stderr)
            fail += 1

        # Rate limit: ~3 req/sec per key, we have multiple keys
        if (i + 1) % 10 == 0:
            time.sleep(1)

    print(f"\nDone. ✓ {ok}  ✗ {fail}")

if __name__ == "__main__":
    main()
