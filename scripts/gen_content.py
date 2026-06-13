"""
Generate rich page content for Aarambha Haq using Gemini flash-latest.
Generates: scheme detail pages + category hubs + state guides in Hindi & English.

Run: python3 scripts/gen_content.py --lang hi --limit 50
"""
import argparse, json, pathlib, psycopg2, psycopg2.extras
import random, re, sys, time, urllib.request

# ── Keys ───────────────────────────────────────────────────────────────────
env = pathlib.Path("/Users/ajayagrawal/Documents/projects/shrutam-content-pipeline/.env")
KEYS, FLASH_MODEL = [], "gemini-flash-latest"
for line in env.read_text().splitlines():
    if line.startswith("GEMINI_API_KEYS="):
        KEYS = [k.strip() for k in line.split("=",1)[1].split(",") if k.strip()]
    if line.startswith("GEMINI_MODEL_FLASH="):
        FLASH_MODEL = line.split("=",1)[1].strip().split()[0]
random.shuffle(KEYS)
print(f"Model: {FLASH_MODEL} | Keys: {len(KEYS)}", file=sys.stderr)

# ── DB ─────────────────────────────────────────────────────────────────────
def db():
    return psycopg2.connect(dbname="aarambha_haq")

# ── Gemini call ─────────────────────────────────────────────────────────────
_key_idx = 0

def call_gemini(prompt: str, retries: int = 4) -> str:
    global _key_idx
    url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
    for attempt in range(retries):
        key = KEYS[_key_idx % len(KEYS)]
        _key_idx += 1
        body = json.dumps({
            "model": FLASH_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 65536,
            "response_format": {"type": "json_object"},
        }).encode()
        req = urllib.request.Request(url, data=body,
            headers={"Content-Type":"application/json","Authorization":f"Bearer {key}"},
            method="POST")
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                result = json.loads(r.read())
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            err = str(e)
            body_txt = ""
            if hasattr(e, 'read'):
                try: body_txt = e.read().decode()[:200]
                except: pass
            if "400" in err and "INVALID_ARGUMENT" in body_txt:
                continue  # bad key, next
            if "503" in err or "429" in err or "timeout" in err.lower():
                wait = 2 ** attempt
                print(f"  Retry {attempt+1} in {wait}s: {err[:60]}", file=sys.stderr)
                time.sleep(wait)
                continue
            print(f"  Fail: {err[:80]} | {body_txt[:80]}", file=sys.stderr)
    raise RuntimeError(f"All retries failed for prompt[:80]={prompt[:80]}")


# ── Content prompt for a SCHEME page ───────────────────────────────────────
SCHEME_PROMPT = """You are an expert Indian civic-tech content writer. Write a rich, detailed article page for the government scheme below.

SCHEME DATA:
- Name: {name}
- Short title: {short_title}
- Level: {level}
- State: {state}
- Ministry: {ministry}
- Description: {description}
- Tags: {tags}
- Beneficiary types: {beneficiary_type}
- Apply URL: {apply_url}

LANGUAGE: {lang_label} ({lang_code})
Write ALL text content in {lang_label}. Do not mix English words (except scheme names, proper nouns, and abbreviations).

OUTPUT — strict JSON with this exact structure (no extra keys):
{{
  "seo_title": "60-char max SEO title in {lang_label}",
  "seo_desc": "155-char max meta description in {lang_label} — natural, benefit-focused",
  "seo_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "title": "Page H1 title in {lang_label}",
  "subtitle": "One sentence tagline in {lang_label}",
  "hero": {{
    "eyebrow": "category tag · level (e.g. केंद्रीय योजना · महिला)",
    "stat_value": "key number/amount if available, else null",
    "stat_label": "what the stat means"
  }},
  "summary": "3-4 sentence plain-language summary in {lang_label} of what this scheme does and who it helps",
  "eligibility": {{
    "intro": "1 sentence intro",
    "checklist": ["condition 1", "condition 2", "condition 3", "condition 4"],
    "income_limit": "income limit string or null",
    "age_range": "age range string or null",
    "states_covered": "All OR specific states"
  }},
  "benefits": {{
    "intro": "1 sentence intro",
    "items": [
      {{"title": "benefit title", "desc": "benefit description (1-2 sentences)"}},
      {{"title": "benefit title", "desc": "..."}}
    ]
  }},
  "documents_required": ["document 1", "document 2", "document 3", "document 4"],
  "how_to_apply": [
    {{"step": 1, "title": "step title", "desc": "step description"}},
    {{"step": 2, "title": "step title", "desc": "step description"}},
    {{"step": 3, "title": "step title", "desc": "step description"}},
    {{"step": 4, "title": "step title", "desc": "step description"}}
  ],
  "faq": [
    {{"q": "question in {lang_label}", "a": "answer in {lang_label}"}},
    {{"q": "question", "a": "answer"}},
    {{"q": "question", "a": "answer"}}
  ],
  "tips": ["practical tip 1", "practical tip 2", "practical tip 3"],
  "important_dates": "deadline or renewal info or null",
  "helpline": "helpline number if known or null",
  "diagram": {{
    "type": "flow",
    "title": "application process flow title",
    "steps": ["step label 1", "step label 2", "step label 3", "step label 4"]
  }},
  "word_count": 0
}}

Write actual helpful content — not generic filler. Make it the best government scheme guide on the internet for a rural Indian citizen."""


# ── Content prompt for CATEGORY hub page ───────────────────────────────────
CATEGORY_PROMPT = """Write a comprehensive hub page for the '{category_name}' category of Indian government schemes.

CATEGORY: {category_key}
LANGUAGE: {lang_label} ({lang_code})
TOTAL SCHEMES IN THIS CATEGORY: {count}
TOP SCHEMES: {top_schemes}

Write ALL text in {lang_label}.

OUTPUT — strict JSON:
{{
  "seo_title": "60-char SEO title",
  "seo_desc": "155-char meta description",
  "seo_keywords": ["keyword1", "keyword2", "keyword3", "keyword4"],
  "title": "H1 title",
  "subtitle": "tagline",
  "hero": {{
    "eyebrow": "category context",
    "stat_value": "{count}+",
    "stat_label": "available schemes"
  }},
  "intro": "3-4 sentence introduction about why this category exists and who it serves",
  "highlights": [
    {{"title": "key highlight", "desc": "explanation"}},
    {{"title": "key highlight", "desc": "explanation"}},
    {{"title": "key highlight", "desc": "explanation"}}
  ],
  "eligibility_overview": "paragraph about general eligibility for this category",
  "how_to_find": ["step 1", "step 2", "step 3"],
  "faq": [
    {{"q": "question", "a": "answer"}},
    {{"q": "question", "a": "answer"}},
    {{"q": "question", "a": "answer"}}
  ],
  "tips": ["tip 1", "tip 2", "tip 3"],
  "diagram": {{
    "type": "stat_grid",
    "title": "key statistics title",
    "stats": [
      {{"label": "stat label", "value": "stat value"}},
      {{"label": "stat label", "value": "stat value"}},
      {{"label": "stat label", "value": "stat value"}}
    ]
  }},
  "word_count": 0
}}"""


# ── Upsert to DB ────────────────────────────────────────────────────────────
def upsert(conn, page_type, slug, lang, content: dict):
    word_count = sum(
        len(str(v).split())
        for v in json.dumps(content, ensure_ascii=False).split()
    ) // 2   # rough estimate

    # Build JSON-LD for scheme pages
    schema = None
    if page_type == "scheme":
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "name": content.get("title",""),
            "description": content.get("seo_desc",""),
            "inLanguage": lang,
            "publisher": {"@type":"Organization","name":"Aarambha Haq","url":"https://haq.aarambhax.in"},
        }

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO page_content
            (page_type, slug, lang, title, subtitle, seo_title, seo_desc, seo_keywords,
             content_json, schema_json, word_count, generated_at, updated_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW(),NOW())
        ON CONFLICT (slug, lang) DO UPDATE SET
            title       = EXCLUDED.title,
            subtitle    = EXCLUDED.subtitle,
            seo_title   = EXCLUDED.seo_title,
            seo_desc    = EXCLUDED.seo_desc,
            seo_keywords= EXCLUDED.seo_keywords,
            content_json= EXCLUDED.content_json,
            schema_json = EXCLUDED.schema_json,
            word_count  = EXCLUDED.word_count,
            updated_at  = NOW()
    """, (
        page_type, slug, lang,
        content.get("title", slug),
        content.get("subtitle",""),
        content.get("seo_title",""),
        content.get("seo_desc",""),
        content.get("seo_keywords",[]),
        json.dumps(content, ensure_ascii=False),
        json.dumps(schema, ensure_ascii=False) if schema else None,
        word_count,
    ))
    conn.commit()
    cur.close()


# ── Main ────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="hi", help="Language code (hi or en)")
    ap.add_argument("--limit", type=int, default=50, help="Max scheme pages to generate")
    ap.add_argument("--type", default="scheme", choices=["scheme","category","all"])
    args = ap.parse_args()

    lang_code = args.lang
    lang_label = "Hindi" if lang_code == "hi" else "English"

    conn = db()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # ── Category pages ──────────────────────────────────────────────────────
    if args.type in ("category", "all"):
        CAT_INFO = {
            "women":      ("महिला" if lang_code=="hi" else "Women", 381),
            "student":    ("छात्र" if lang_code=="hi" else "Students", 748),
            "farmer":     ("किसान" if lang_code=="hi" else "Farmer", 400),
            "employment": ("रोजगार" if lang_code=="hi" else "Employment", 459),
            "disability": ("दिव्यांग" if lang_code=="hi" else "Disability", 289),
            "pension":    ("पेंशन" if lang_code=="hi" else "Pension", 259),
            "health":     ("स्वास्थ्य" if lang_code=="hi" else "Health", 184),
            "child":      ("बाल" if lang_code=="hi" else "Child", 182),
            "tribal":     ("जनजातीय" if lang_code=="hi" else "Tribal", 157),
            "bpl":        ("BPL/गरीबी रेखा" if lang_code=="hi" else "BPL", 141),
            "entrepreneur":("उद्यमी" if lang_code=="hi" else "Entrepreneur", 121),
            "minority":   ("अल्पसंख्यक" if lang_code=="hi" else "Minority", 87),
            "housing":    ("आवास" if lang_code=="hi" else "Housing", 69),
            "maternity":  ("मातृत्व" if lang_code=="hi" else "Maternity", 40),
            "elderly":    ("वृद्ध" if lang_code=="hi" else "Elderly", 24),
        }
        for cat_key, (cat_name, count) in CAT_INFO.items():
            slug = f"category/{cat_key}"
            # check if exists
            cur.execute("SELECT 1 FROM page_content WHERE slug=%s AND lang=%s", (slug, lang_code))
            if cur.fetchone():
                print(f"  SKIP (exists): {slug}/{lang_code}")
                continue

            # Get top 5 scheme names for this category
            cur.execute(
                "SELECT name FROM schemes WHERE %s = ANY(beneficiary_type) ORDER BY name LIMIT 5",
                (cat_key,)
            )
            top = [r["name"] for r in cur.fetchall()]
            top_str = ", ".join(top)

            print(f"  Generating category: {cat_key} ({lang_label})", flush=True)
            prompt = CATEGORY_PROMPT.format(
                category_key=cat_key, category_name=cat_name,
                lang_code=lang_code, lang_label=lang_label,
                count=count, top_schemes=top_str,
            )
            try:
                raw = call_gemini(prompt)
                content = json.loads(raw)
                upsert(conn, "category", slug, lang_code, content)
                print(f"  ✓ {cat_key} ({lang_label}) — {content.get('title','')[:50]}")
            except Exception as e:
                print(f"  ✗ {cat_key}: {e}", file=sys.stderr)
            time.sleep(0.5)

    # ── Scheme pages ────────────────────────────────────────────────────────
    if args.type in ("scheme", "all"):
        # Priority order: 20 women, 20 student, 15 farmer, 10 employment, 5 disability, 5 pension, rest
        priority_cats = [
            ("women", 20), ("student", 20), ("farmer", 15),
            ("employment", 10), ("disability", 5), ("pension", 5),
            ("health", 5), ("child", 5), ("tribal", 5), ("housing", 5),
        ]
        scheme_ids_done = set()
        all_schemes = []

        for cat, n in priority_cats:
            cur.execute(
                "SELECT * FROM schemes WHERE %s = ANY(beneficiary_type) ORDER BY name LIMIT %s",
                (cat, n)
            )
            for row in cur.fetchall():
                if row["id"] not in scheme_ids_done:
                    scheme_ids_done.add(row["id"])
                    all_schemes.append(dict(row))

        all_schemes = all_schemes[:args.limit]
        print(f"\nGenerating {len(all_schemes)} scheme pages in {lang_label}...", flush=True)

        for i, s in enumerate(all_schemes):
            slug = f"yojana/s/{s['slug']}"
            cur.execute("SELECT 1 FROM page_content WHERE slug=%s AND lang=%s", (slug, lang_code))
            if cur.fetchone():
                print(f"  [{i+1}/{len(all_schemes)}] SKIP: {s['slug']}")
                continue

            print(f"  [{i+1}/{len(all_schemes)}] {s['name'][:45]}...", end=" ", flush=True)
            prompt = SCHEME_PROMPT.format(
                name=s["name"], short_title=s.get("short_title",""),
                level=s.get("level",""), state=s.get("state",""),
                ministry=s.get("ministry",""), description=(s.get("description","") or "")[:500],
                tags=", ".join((s.get("tags") or [])[:8]),
                beneficiary_type=", ".join((s.get("beneficiary_type") or [])),
                apply_url=s.get("apply_url",""),
                lang_code=lang_code, lang_label=lang_label,
            )
            try:
                raw = call_gemini(prompt)
                content = json.loads(raw)
                upsert(conn, "scheme", slug, lang_code, content)
                print(f"✓ {content.get('title','')[:40]}")
            except Exception as e:
                print(f"✗ {str(e)[:60]}", file=sys.stderr)
            time.sleep(0.3)

    cur.close(); conn.close()

    # Summary
    conn2 = db()
    cur2  = conn2.cursor()
    cur2.execute("SELECT page_type, lang, COUNT(*) FROM page_content GROUP BY 1,2 ORDER BY 1,2")
    print("\n── page_content DB summary ──")
    for row in cur2.fetchall():
        print(f"  {row[0]:<15} {row[1]:<6} {row[2]} pages")
    cur2.close(); conn2.close()


if __name__ == "__main__":
    main()
