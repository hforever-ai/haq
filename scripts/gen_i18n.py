"""
Generate i18n translations for all 22 Indian scheduled languages using Gemini.
Output: web/static/i18n/{lang_code}.json per language
"""
import json, pathlib, sys, time, urllib.request, random

# ── Keys ───────────────────────────────────────────────────────────────────
env = pathlib.Path("/Users/ajayagrawal/Documents/projects/shrutam-content-pipeline/.env")
KEYS = []
for line in env.read_text().splitlines():
    if line.startswith("GEMINI_API_KEYS="):
        KEYS = [k.strip() for k in line.split("=",1)[1].split(",") if k.strip()]
        break
random.shuffle(KEYS)

# ── 22 Scheduled Languages ─────────────────────────────────────────────────
LANGS = [
    {"code":"hi",  "name":"Hindi",      "script":"Devanagari", "native":"हिन्दी"},
    {"code":"mr",  "name":"Marathi",    "script":"Devanagari", "native":"मराठी"},
    {"code":"ne",  "name":"Nepali",     "script":"Devanagari", "native":"नेपाली"},
    {"code":"mai", "name":"Maithili",   "script":"Devanagari", "native":"मैथिली"},
    {"code":"sa",  "name":"Sanskrit",   "script":"Devanagari", "native":"संस्कृतम्"},
    {"code":"doi", "name":"Dogri",      "script":"Devanagari", "native":"डोगरी"},
    {"code":"kok", "name":"Konkani",    "script":"Devanagari", "native":"कोंकणी"},
    {"code":"bn",  "name":"Bengali",    "script":"Bengali",    "native":"বাংলা"},
    {"code":"as",  "name":"Assamese",   "script":"Bengali",    "native":"অসমীয়া"},
    {"code":"gu",  "name":"Gujarati",   "script":"Gujarati",   "native":"ગુજરાતી"},
    {"code":"pa",  "name":"Punjabi",    "script":"Gurmukhi",   "native":"ਪੰਜਾਬੀ"},
    {"code":"or",  "name":"Odia",       "script":"Odia",       "native":"ଓଡ଼ିଆ"},
    {"code":"ta",  "name":"Tamil",      "script":"Tamil",      "native":"தமிழ்"},
    {"code":"te",  "name":"Telugu",     "script":"Telugu",     "native":"తెలుగు"},
    {"code":"kn",  "name":"Kannada",    "script":"Kannada",    "native":"ಕನ್ನಡ"},
    {"code":"ml",  "name":"Malayalam",  "script":"Malayalam",  "native":"മലയാളം"},
    {"code":"ur",  "name":"Urdu",       "script":"Nastaliq",   "native":"اردو"},
    {"code":"ks",  "name":"Kashmiri",   "script":"Nastaliq",   "native":"کٲشُر"},
    {"code":"sd",  "name":"Sindhi",     "script":"Perso-Arabic","native":"سنڌي"},
    {"code":"mni", "name":"Manipuri",   "script":"Meitei Mayek","native":"মৈতৈলোন্"},
    {"code":"brx", "name":"Bodo",       "script":"Devanagari", "native":"बड़ो"},
    {"code":"sat", "name":"Santali",    "script":"Ol Chiki",   "native":"ᱥᱟᱱᱛᱟᱲᱤ"},
]

# ── UI Strings to translate ────────────────────────────────────────────────
STRINGS = {
    # Nav
    "nav.check_eligibility": "Check Eligibility",
    "nav.all_schemes": "All Schemes",
    "nav.your_rights": "Your Rights",
    "nav.about": "About Us",
    "nav.tagline": "Know Your Rights",

    # Hero
    "hero.headline": "Know Your Rights",
    "hero.sub": "Check eligibility for 2,754+ government schemes — free",
    "hero.cta": "Check Eligibility →",
    "hero.badge": "2,754+ Government Schemes · Free",

    # Trust bar
    "trust.govt_data": "Official Govt Data",
    "trust.schemes_count": "2,754+ Schemes",
    "trust.free": "Free · No Registration",
    "trust.mobile": "Mobile Friendly",

    # Categories (Hindi names for categories)
    "cat.women": "Women",
    "cat.student": "Students",
    "cat.farmer": "Farmer",
    "cat.employment": "Employment",
    "cat.disability": "Disability",
    "cat.pension": "Pension",
    "cat.health": "Health",
    "cat.child": "Child",
    "cat.tribal": "Tribal",
    "cat.bpl": "BPL",
    "cat.entrepreneur": "Entrepreneur",
    "cat.minority": "Minority",
    "cat.housing": "Housing",
    "cat.maternity": "Maternity",
    "cat.elderly": "Elderly",
    "cat.view_all": "View All {n} Categories →",

    # How it works
    "how.title": "How It Works",
    "how.step1": "Enter Your Details",
    "how.step2": "See Eligible Schemes",
    "how.step3": "Apply Directly",

    # Browse page
    "browse.all_schemes": "All Government Schemes",
    "browse.search_placeholder": "Search scheme by name...",
    "browse.filter": "Filter",
    "browse.level_all": "All",
    "browse.central": "Central",
    "browse.state": "State",
    "browse.select_state": "Select State",
    "browse.results": "{n} schemes found",
    "browse.load_more": "Load More Schemes",
    "browse.no_results": "No schemes found.",

    # Scheme card
    "scheme.apply": "Apply →",
    "scheme.view": "View Scheme",
    "scheme.check_eligibility": "Check Eligibility for This Scheme →",

    # Wizard
    "wizard.title": "Check Eligibility",
    "wizard.step": "Step {n} of {total}",
    "wizard.next": "Next →",
    "wizard.prev": "← Previous",
    "wizard.submit": "View Results →",
    "wizard.q1": "Who are you?",
    "wizard.q1.female": "Woman",
    "wizard.q1.male": "Man",
    "wizard.q1.other": "Other",
    "wizard.q2": "What is your age?",
    "wizard.q2.placeholder": "E.g. 32",
    "wizard.q3": "Your state?",
    "wizard.q3.placeholder": "Select your state",
    "wizard.q4": "Annual family income?",
    "wizard.q4.opt1": "Less than ₹1 lakh",
    "wizard.q4.opt2": "₹1 – 3 lakh",
    "wizard.q4.opt3": "₹3 – 6 lakh",
    "wizard.q4.opt4": "More than ₹6 lakh",
    "wizard.q5": "Any of these apply to you? (optional)",
    "wizard.q5.widow": "Widow",
    "wizard.q5.pregnant": "Pregnant / Lactating",
    "wizard.q5.shg": "SHG Member",
    "wizard.q5.sc_st": "SC / ST / OBC",
    "wizard.q5.minority": "Minority",
    "wizard.q5.disability": "Disability",
    "wizard.q5.skip": "Skip",
    "wizard.results.title": "You are eligible for {n} schemes!",
    "wizard.results.none": "No matching schemes found. Try changing your details.",
    "wizard.results.view_all": "View All →",

    # Rights KB
    "rights.title": "Your Rights",
    "rights.sub": "Know your legal rights and how to get what you deserve",
    "rights.search": "Search rights articles...",
    "rights.read_more": "Read →",
    "rights.cats.all": "All",
    "rights.cats.women": "Women's Rights",
    "rights.cats.property": "Property Rights",
    "rights.cats.maternity": "Maternity Rights",
    "rights.cats.legal_aid": "Legal Aid",
    "rights.cats.pension": "Pension & Benefits",

    # About
    "about.title": "About Us",
    "about.mission.title": "Our Mission",
    "about.mission.text": "Reach every Indian citizen with information about government schemes they deserve.",
    "about.data_source": "Data Source: MyScheme.gov.in (Official Government Portal)",
    "about.contact": "Contact Us",

    # Footer
    "footer.tagline": "Know Your Rights. Claim What's Yours.",
    "footer.data_note": "Data sourced from MyScheme.gov.in · Official Government Portal",
    "footer.free_note": "Free · No Registration · No Personal Data Stored",
    "footer.links.schemes": "Schemes",
    "footer.links.check": "Check Eligibility",
    "footer.links.rights": "Your Rights",
    "footer.links.about": "About",
    "footer.copyright": "© 2026 Aarambha Haq · Aarambhax.in",

    # General
    "general.loading": "Loading...",
    "general.error": "Something went wrong. Please try again.",
    "general.official_site": "Official Website →",
    "general.scheme_count": "{n} Schemes",
    "general.back": "← Back",
    "general.share": "Share",
    "general.central_scheme": "Central Scheme",
    "general.state_scheme": "State Scheme",
}

OUT_DIR = pathlib.Path("/Users/ajayagrawal/Documents/projects/aarambha-haq/web/static/i18n")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def call_gemini(key, prompt):
    url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
    body = json.dumps({
        "model": "gemini-2.5-flash",
        "messages": [{"role":"user","content": prompt}],
        "max_tokens": 65536,
        "response_format": {"type": "json_object"},
    }).encode()
    req = urllib.request.Request(url, data=body,
        headers={"Content-Type":"application/json","Authorization":f"Bearer {key}"},
        method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        result = json.loads(r.read())
    return result["choices"][0]["message"]["content"]

def translate_batch(langs_batch, key):
    lang_list = "\n".join(
        f'- "{l["code"]}": {l["name"]} ({l["native"]}, script: {l["script"]})'
        for l in langs_batch
    )
    strings_json = json.dumps(STRINGS, ensure_ascii=False, indent=2)

    prompt = f"""You are a professional Indian multilingual translator.
Translate the following UI strings into MULTIPLE Indian languages.

## Source strings (English keys → English values):
{strings_json}

## Target languages:
{lang_list}

## RULES:
1. Return ONLY valid JSON — no markdown, no explanation.
2. JSON structure: {{ "hi": {{ "nav.check_eligibility": "...", ... }}, "mr": {{ ... }}, ... }}
3. For EACH language, translate ALL {len(STRINGS)} keys.
4. Keep placeholders like {{n}}, {{total}} exactly as-is.
5. Keep "→" and "←" arrows as-is.
6. Keep "₹" rupee symbol as-is.
7. For Urdu/Kashmiri/Sindhi: use appropriate script (Nastaliq/Perso-Arabic).
8. For Santali: use Ol Chiki script where possible, Roman fallback acceptable.
9. Translations must be natural and simple — low-literacy audience.
10. Category names (cat.*) should use the standard term used in that language for govt schemes.
11. Do NOT translate proper nouns: "Aarambha Haq", "MyScheme.gov.in", "SC", "ST", "OBC", "SHG".

Return ONLY the JSON object with language codes as keys."""

    return json.loads(call_gemini(key, prompt))

# ── Run translation in batches of 5-6 languages ───────────────────────────
BATCHES = [
    LANGS[0:6],   # hi, mr, ne, mai, sa, doi  (all Devanagari)
    LANGS[6:12],  # kok, bn, as, gu, pa, or
    LANGS[12:17], # ta, te, kn, ml, ur
    LANGS[17:22], # ks, sd, mni, brx, sat
]

all_translations = {}
key_idx = 0

for i, batch in enumerate(BATCHES):
    batch_codes = [l["code"] for l in batch]
    print(f"\nBatch {i+1}/4: {batch_codes}", flush=True)

    success = False
    for attempt in range(3):
        key = KEYS[key_idx % len(KEYS)]
        key_idx += 1
        try:
            print(f"  Key ...{key[-8:]} attempt {attempt+1}", flush=True)
            result = translate_batch(batch, key)
            for code, translations in result.items():
                all_translations[code] = translations
            print(f"  ✓ Got {len(result)} languages", flush=True)
            success = True
            break
        except Exception as e:
            print(f"  ✗ {e}", flush=True)
            if hasattr(e,'read'):
                try: print("   ", e.read().decode()[:150])
                except: pass
            time.sleep(2)

    if not success:
        print(f"  FAILED batch {i+1} — using English fallback", flush=True)
        for l in batch:
            all_translations[l["code"]] = STRINGS.copy()

    time.sleep(1)

# ── Save one file per language ─────────────────────────────────────────────
for lang in LANGS:
    code = lang["code"]
    if code in all_translations:
        out = OUT_DIR / f"{code}.json"
        data = {
            "_meta": {
                "code": code,
                "name": lang["name"],
                "native": lang["native"],
                "script": lang["script"],
                "dir": "rtl" if code in ("ur","ks","sd") else "ltr",
            },
            **all_translations[code]
        }
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        print(f"  Saved {code}.json ({len(all_translations[code])} keys)")

# ── Save master strings (English source) ──────────────────────────────────
(OUT_DIR / "en.json").write_text(json.dumps({
    "_meta": {"code":"en","name":"English","native":"English","script":"Latin","dir":"ltr"},
    **STRINGS
}, ensure_ascii=False, indent=2))

# ── Save languages index ───────────────────────────────────────────────────
(OUT_DIR / "_languages.json").write_text(json.dumps(LANGS, ensure_ascii=False, indent=2))

print(f"\nDone. {len(all_translations)+1} language files in {OUT_DIR}")
