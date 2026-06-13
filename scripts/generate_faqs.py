"""
Generate rich FAQs for Aarambha Haq using Gemini gemini-3.1-flash-lite.
Phase 1: Generate 5 FAQs per category in Hindi
Phase 2: Translate each category to remaining 21 languages (batches of 7)
Output: web/data/faqs.json
"""
import json, pathlib, time, random, urllib.request, urllib.error, sys, re

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

# ── Languages ──────────────────────────────────────────────────────────────
LANGS = [
    ("hi",  "Hindi",      "Devanagari"),
    ("en",  "English",    "Latin"),
    ("mr",  "Marathi",    "Devanagari"),
    ("bn",  "Bengali",    "Bengali"),
    ("te",  "Telugu",     "Telugu"),
    ("ta",  "Tamil",      "Tamil"),
    ("kn",  "Kannada",    "Kannada"),
    ("ml",  "Malayalam",  "Malayalam"),
    ("gu",  "Gujarati",   "Gujarati"),
    ("pa",  "Punjabi",    "Gurmukhi"),
    ("or",  "Odia",       "Odia"),
    ("ur",  "Urdu",       "Nastaliq"),
    ("ne",  "Nepali",     "Devanagari"),
    ("as",  "Assamese",   "Bengali"),
    ("mai", "Maithili",   "Devanagari"),
    ("kok", "Konkani",    "Devanagari"),
    ("doi", "Dogri",      "Devanagari"),
    ("sa",  "Sanskrit",   "Devanagari"),
    ("ks",  "Kashmiri",   "Perso-Arabic"),
    ("sd",  "Sindhi",     "Perso-Arabic"),
    ("mni", "Meitei",     "Bengali"),
    ("sat", "Santali",    "Latin"),
]

# ── Categories ─────────────────────────────────────────────────────────────
CATEGORIES = [
    ("home",         "General questions about Aarambha Haq — a free platform to check eligibility for 2,754+ Indian government schemes in 22 languages"),
    ("mahila",       "Women's government schemes in India — PM Matru Vandana Yojana, Ujjwala Yojana, Sukanya Samriddhi, widow pension, Beti Bachao Beti Padhao"),
    ("student",      "Student scholarships — National Scholarship Portal (NSP), PM Scholarship, Pre-Matric/Post-Matric for SC/ST/OBC, Central Sector Scholarship"),
    ("farmer",       "Farmer schemes — PM-KISAN (₹6,000/year), Kisan Credit Card, PMFBY crop insurance, Soil Health Card, eNAM market"),
    ("employment",   "Employment and skills — MGNREGA (100 days guaranteed work), PMKVY skill training, PM MUDRA loan, Stand Up India, e-Shram"),
    ("pension",      "Pension schemes — IGNOAPS (old age pension), NPS (National Pension System), APY (Atal Pension Yojana), widow pension, IGNDPS"),
    ("health",       "Health schemes — Ayushman Bharat PM-JAY (₹5 lakh/family), Jan Aushadhi generic medicines, PMSBY accident insurance, Janani Suraksha Yojana"),
    ("disability",   "Disability schemes — IGNDPS pension, UDID card, Divyangjan scholarships, assistive devices, special railway concession"),
    ("housing",      "Housing schemes — PM Awas Yojana Gramin (₹1.2 lakh), PM Awas Urban with interest subsidy, PMGSY rural roads"),
    ("child",        "Child welfare — Anganwadi ICDS nutrition, Sukanya Samriddhi Yojana for daughters, Mid-day meal, POSHAN Abhiyan, PENCIL"),
    ("maternity",    "Maternity schemes — PMMVY (₹5,000 cash), Janani Suraksha Yojana (JSY), maternity leave benefits under Maternity Benefit Act 2017"),
    ("elderly",      "Senior citizen schemes — IGNOAPS pension, PMVVY (LIC 7.4% guaranteed), railway concession, Rashtriya Vayoshri Yojana assistive devices"),
    ("bpl",          "BPL schemes — NFSA PDS ration at ₹2/kg wheat, Ayushman Bharat, Ujjwala free LPG, PM Awas, ONORC One Nation One Ration Card"),
    ("tribal",       "Tribal/ST schemes — Forest Rights Act land titles, ST scholarships on NSP, TRIFED van dhan, PM Jan Man Yojana, Eklavya schools"),
    ("entrepreneur", "Entrepreneur schemes — PM MUDRA (₹50,000 to ₹10 lakh), PMEGP (35% subsidy), Startup India tax benefits, Stand Up India for SC/ST/women"),
    ("minority",     "Minority schemes — Pre/Post Matric scholarships on NSP, Nai Roshni for women leaders, Maulana Azad Fellowship PhD, NMDFC self-employment loans"),
]

MODEL = "gemini-3.1-flash-lite"
API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

def extract_json(text: str) -> dict:
    """Extract first complete JSON object even if Gemini adds text before/after."""
    text = text.strip()
    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found in response")
    # Walk forward tracking depth to find the matching closing brace
    depth, i = 0, start
    in_str, escape = False, False
    while i < len(text):
        ch = text[i]
        if escape:
            escape = False
        elif ch == "\\":
            escape = True
        elif ch == '"' and not escape:
            in_str = not in_str
        elif not in_str:
            if ch == "{": depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    raw = text[start:i+1]
                    # Strip trailing commas before ] or } (Gemini quirk)
                    raw = re.sub(r",\s*([}\]])", r"\1", raw)
                    return json.loads(raw)
        i += 1
    raise ValueError("Unclosed JSON object")

def gemini_call(prompt: str, retries: int = 4) -> str:
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 65536,
            "temperature": 0.3,
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
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read())
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"  HTTP {e.code} attempt {attempt+1}: {body[:150]}", file=sys.stderr)
            time.sleep(5 * (attempt + 1))
        except Exception as ex:
            print(f"  Error attempt {attempt+1}: {ex}", file=sys.stderr)
            time.sleep(3)
    raise RuntimeError(f"All {retries} retries failed")

# ─────────────────────────────────────────────────────────────────────────
# Phase 1: Generate Hindi FAQs per category
# ─────────────────────────────────────────────────────────────────────────
HINDI_PROMPT = """You are an expert on Indian government welfare schemes.

Generate EXACTLY 5 FAQ entries about: {desc}

Each FAQ must be:
- Practically useful to an Indian citizen
- Mention specific scheme names, amounts in ₹, eligibility, and how to apply
- Answer in 2-4 clear sentences

Return ONLY this JSON (no other text):
[
  {{"q": "question 1 in Hindi", "a": "detailed answer in Hindi"}},
  {{"q": "question 2 in Hindi", "a": "detailed answer in Hindi"}},
  {{"q": "question 3 in Hindi", "a": "detailed answer in Hindi"}},
  {{"q": "question 4 in Hindi", "a": "detailed answer in Hindi"}},
  {{"q": "question 5 in Hindi", "a": "detailed answer in Hindi"}}
]"""

def gen_hindi(cat_key: str, cat_desc: str) -> list:
    prompt = HINDI_PROMPT.format(desc=cat_desc)
    raw = gemini_call(prompt)
    raw = raw.strip()
    start = raw.find("[")
    end   = raw.rfind("]") + 1
    if start == -1:
        raise ValueError("No array in response")
    parsed = json.loads(raw[start:end])
    assert len(parsed) >= 3, f"Only {len(parsed)} FAQs returned"
    return parsed[:5]

# ─────────────────────────────────────────────────────────────────────────
# Phase 2: Translate a batch of languages
# ─────────────────────────────────────────────────────────────────────────
TRANSLATE_PROMPT = """Translate these 5 FAQ pairs about Indian government schemes into the languages listed.

Source (Hindi):
{hindi_json}

Translate into these languages and return ONLY valid JSON:
{lang_targets}

Return format:
{{
  "{lang1_code}": [{{"q":"...","a":"..."}}, ... 5 items],
  "{lang2_code}": [...],
  ...
}}

Rules:
- Translate naturally in each language's native script
- Keep scheme names (PM-KISAN, MGNREGA, Ayushman Bharat etc.) in English/original
- Keep ₹ amounts as-is
- NO extra text outside JSON"""

def translate_batch(hindi_faqs: list, lang_batch: list) -> dict:
    """Translate to a batch of languages. lang_batch = [(code, name, script), ...]"""
    hindi_json = json.dumps(hindi_faqs, ensure_ascii=False, indent=2)
    lang_targets = "\n".join(
        f'  - {code}: {name} ({script})'
        for code, name, script in lang_batch
        if code != "hi"
    )
    # Build the placeholder codes for return format hint
    first_code = lang_batch[0][0] if lang_batch[0][0] != "hi" else lang_batch[1][0]
    last_code  = lang_batch[-1][0]

    prompt = TRANSLATE_PROMPT.format(
        hindi_json=hindi_json,
        lang_targets=lang_targets,
        lang1_code=lang_batch[0][0],
        lang2_code=last_code,
    )
    raw = gemini_call(prompt)
    return extract_json(raw)

# ─────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────
def main():
    out_path = pathlib.Path(__file__).parent.parent / "web" / "data" / "faqs.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    result = {}
    if out_path.exists():
        result = json.loads(out_path.read_text())
        print(f"Resuming — {len(result)} categories done")

    # Non-Hindi languages in batches of 7
    non_hi = [l for l in LANGS if l[0] != "hi"]
    batches = [non_hi[i:i+7] for i in range(0, len(non_hi), 7)]

    for cat_key, cat_desc in CATEGORIES:
        if cat_key in result and "hi" in result[cat_key] and len(result[cat_key]) >= 22:
            print(f"  skip {cat_key}")
            continue

        print(f"\n→ {cat_key}")
        cat_data = result.get(cat_key, {})

        # Phase 1: Hindi
        if "hi" not in cat_data:
            print(f"  phase 1: Hindi...")
            try:
                cat_data["hi"] = gen_hindi(cat_key, cat_desc)
                print(f"  ✓ Hindi ({len(cat_data['hi'])} FAQs)")
            except Exception as ex:
                print(f"  ✗ Hindi failed: {ex}", file=sys.stderr)
                continue
            result[cat_key] = cat_data
            out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))

        hindi_faqs = cat_data["hi"]

        # Phase 2: Translate in batches
        for i, batch in enumerate(batches):
            batch_codes = [l[0] for l in batch]
            # Skip if all in batch already done
            if all(c in cat_data for c in batch_codes):
                print(f"  skip batch {i+1}")
                continue

            print(f"  batch {i+1}/{len(batches)}: {', '.join(batch_codes)}")
            try:
                translated = translate_batch(hindi_faqs, batch)
                for code in batch_codes:
                    if code in translated and len(translated[code]) >= 3:
                        cat_data[code] = translated[code]
                    else:
                        print(f"    missing/short: {code}", file=sys.stderr)
                result[cat_key] = cat_data
                out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
                print(f"  ✓ batch {i+1} done ({len(translated)} langs)")
            except Exception as ex:
                print(f"  ✗ batch {i+1} failed: {ex}", file=sys.stderr)

            time.sleep(1)

    print(f"\nDone — {out_path}")
    for k, v in result.items():
        print(f"  {k}: {len(v)} languages")

if __name__ == "__main__":
    main()
