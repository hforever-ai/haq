"""Aarambha Haq — Government scheme eligibility checker. 22 Indian languages."""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# ── Paths ──────────────────────────────────────────────────────────────────
BASE     = Path(__file__).parent.parent.parent
WEB      = BASE / "web"
I18N_DIR = WEB / "static" / "i18n"
FAQS_FILE = WEB / "data" / "faqs.json"
DATA_DIR  = WEB / "data"

# ── FAQ loader (cached, auto-reloads if file changes) ──────────────────────
_faqs_mtime: float = 0.0
_faqs_data:  dict  = {}

def load_faqs() -> dict:
    global _faqs_mtime, _faqs_data
    if not FAQS_FILE.exists():
        return {}
    mtime = FAQS_FILE.stat().st_mtime
    if mtime != _faqs_mtime:
        _faqs_data  = json.loads(FAQS_FILE.read_text())
        _faqs_mtime = mtime
    return _faqs_data

def get_faqs(category: str, lang: str) -> list:
    faqs = load_faqs()
    cat  = faqs.get(category, {})
    return cat.get(lang) or cat.get("hi") or []

# ── App ────────────────────────────────────────────────────────────────────
app = FastAPI(title="Aarambha Haq", version="0.2.0")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"],
    allow_credentials=False, allow_methods=["*"], allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=str(WEB / "static")), name="static")
templates = Jinja2Templates(directory=str(WEB / "templates"))

# ── i18n ───────────────────────────────────────────────────────────────────
@lru_cache(maxsize=None)
def load_translations(lang: str) -> dict:
    f = I18N_DIR / f"{lang}.json"
    if not f.exists():
        f = I18N_DIR / "hi.json"   # fallback to Hindi
    return json.loads(f.read_text())

@lru_cache(maxsize=1)
def load_languages() -> list[dict]:
    f = I18N_DIR / "_languages.json"
    return json.loads(f.read_text())

VALID_LANGS = {l["code"] for l in load_languages()}
RTL_LANGS   = {"ur", "ks", "sd"}
LANG_META   = {l["code"]: l for l in load_languages()}

_states_i18n_file = I18N_DIR / "states.json"
STATES_I18N: dict = json.loads(_states_i18n_file.read_text()) if _states_i18n_file.exists() else {}

FLAGS = {
    "hi":"🇮🇳","mr":"🇮🇳","ne":"🇳🇵","mai":"🇮🇳","sa":"🇮🇳","doi":"🇮🇳",
    "kok":"🇮🇳","bn":"🇧🇩","as":"🇮🇳","gu":"🇮🇳","pa":"🇮🇳","or":"🇮🇳",
    "ta":"🇮🇳","te":"🇮🇳","kn":"🇮🇳","ml":"🇮🇳","ur":"🇮🇳","ks":"🇮🇳",
    "sd":"🇮🇳","mni":"🇮🇳","brx":"🇮🇳","sat":"🇮🇳","en":"🌐",
}

def make_t(lang: str):
    tr = load_translations(lang)
    def t(key: str, **kwargs) -> str:
        val = tr.get(key, key)
        for k, v in kwargs.items():
            val = val.replace("{" + k + "}", str(v))
        return val
    return t

def ctx(request: Request, lang: str, **extra) -> dict:
    tr   = load_translations(lang)
    meta = LANG_META.get(lang, {"native": lang, "name": lang})
    path = request.url.path
    lp   = "" if lang == "hi" else f"/{lang}"   # URL prefix: "" for Hindi (rootless), "/en" for English, etc.

    # path_base: path without lang prefix, for language-switcher links
    # Hindi is rootless (/yojana/s/slug), others have prefix (/en/yojana/s/slug)
    if lang == "hi":
        path_base = path   # already rootless
    else:
        parts = path.split("/", 2)   # ['', 'en', 'rest/of/path']
        path_base = "/" + parts[2] if len(parts) > 2 else "/"

    return {
        "request":           request,
        "lang_code":         lang,
        "lang_dir":          "rtl" if lang in RTL_LANGS else "ltr",
        "lang_native":       meta["native"],
        "lang_flag":         FLAGS.get(lang, "🌐"),
        "languages":         load_languages(),
        "current_path":      path,
        "current_path_base": path_base,
        "lp":                lp,
        "translations_json": json.dumps(tr),
        "languages_json":    json.dumps(load_languages()),
        "t": make_t(lang),
        "states_i18n":       STATES_I18N.get(lang, {}),
        **extra,
    }

# ── DB ─────────────────────────────────────────────────────────────────────
def db_conn():
    dsn = os.getenv("DATABASE_URL")
    if dsn:
        return psycopg2.connect(dsn)
    # Local dev: socket auth; prod: env vars
    kwargs: dict = {"dbname": os.getenv("DB_NAME", "aarambha_haq")}
    if os.getenv("DB_HOST"):
        kwargs.update({
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "user": os.getenv("DB_USER", "aarambha_haq"),
            "password": os.getenv("DB_PASS", ""),
        })
    return psycopg2.connect(**kwargs)

# URL slug → DB beneficiary_type value
CAT_MAP = {
    "mahila": "women", "student": "student", "kisan": "farmer", "farmer": "farmer",
    "rozgaar": "employment", "employment": "employment", "divyang": "disability",
    "disability": "disability", "pension": "pension", "swasthya": "health",
    "health": "health", "bal": "child", "child": "child", "janjati": "tribal",
    "tribal": "tribal", "bpl": "bpl", "udyami": "entrepreneur",
    "entrepreneur": "entrepreneur", "minority": "minority", "awas": "housing",
    "housing": "housing", "matritva": "maternity", "maternity": "maternity",
    "vridh": "elderly", "elderly": "elderly",
}

def get_schemes(category: str | None = None, state: str | None = None,
                q: str | None = None, level: str | None = None,
                page: int = 1, size: int = 20,
                lang: str | None = None) -> tuple[list, int]:
    conn = db_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    where, params = [], []

    if category:
        db_cat = CAT_MAP.get(category, category)
        where.append("%s = ANY(beneficiary_type)")
        params.append(db_cat)
    if state:
        where.append("(state = %s OR state = 'All')")
        params.append(state)
    if level and level in ("Central","State"):
        where.append("level = %s")
        params.append(level)
    if q:
        where.append("(name ILIKE %s OR description ILIKE %s)")
        params.extend([f"%{q}%", f"%{q}%"])

    wc = "WHERE " + " AND ".join(where) if where else ""
    cur.execute(f"SELECT COUNT(*) FROM schemes {wc}", params)
    total = cur.fetchone()["count"]

    offset = (page - 1) * size
    cur.execute(
        f"SELECT id,slug,name,short_title,level,state,ministry,description,apply_url,"
        f"beneficiary_type,for_married,for_widow,for_pregnant,for_shg,for_girl_child,"
        f"for_sc_st,for_minority,max_income_lakhs,min_class,max_class,streams,genders "
        f"FROM schemes {wc} ORDER BY name LIMIT %s OFFSET %s",
        params + [size, offset]
    )
    rows = [dict(r) for r in cur.fetchall()]

    # Overlay translated name + description for non-English browse pages
    if lang and lang != "en" and rows:
        ids = [r["id"] for r in rows]
        cur.execute(
            "SELECT scheme_id, scheme_name, description FROM scheme_translations "
            "WHERE scheme_id = ANY(%s) AND lang_code = %s",
            (ids, lang)
        )
        tr_map = {r["scheme_id"]: dict(r) for r in cur.fetchall()}
        for row in rows:
            tr = tr_map.get(row["id"])
            if tr:
                if tr.get("scheme_name"): row["name"]        = tr["scheme_name"]
                if tr.get("description"): row["description"] = tr["description"]

    cur.close(); conn.close()
    return rows, total

def get_scheme(slug: str, lang: str | None = None) -> dict | None:
    conn = db_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM schemes WHERE slug = %s", (slug,))
    row = cur.fetchone()
    if not row:
        cur.close(); conn.close()
        return None
    scheme = dict(row)
    scheme["_description_translated"] = False
    # Overlay translated fields if lang requested and translation exists
    if lang and lang != "en":
        cur.execute(
            "SELECT scheme_name, short_title, description, eligibility_text, benefit_text, how_to_apply "
            "FROM scheme_translations WHERE scheme_id = %s AND lang_code = %s",
            (scheme["id"], lang),
        )
        tr = cur.fetchone()
        if tr:
            tr = dict(tr)
            if tr.get("scheme_name"):  scheme["name"]            = tr["scheme_name"]
            if tr.get("short_title"):  scheme["short_title"]      = tr["short_title"]
            if tr.get("description"):
                scheme["description"]             = tr["description"]
                scheme["_description_translated"] = True
            scheme["eligibility_text_translated"] = tr.get("eligibility_text") or ""
            scheme["benefit_text_translated"]     = tr.get("benefit_text") or ""
            scheme["how_to_apply_translated"]     = tr.get("how_to_apply") or ""
    cur.close(); conn.close()

    # Parse documents_required_md into a clean list (prefer over old jsonb)
    docs_md = scheme.get("documents_required_md") or ""
    if docs_md.strip():
        import re as _re
        lines = docs_md.splitlines()
        parsed = []
        for ln in lines:
            ln = ln.strip().lstrip("-*•").strip()
            ln = _re.sub(r"<br\s*/?>", "", ln, flags=_re.IGNORECASE).strip()
            if ln and len(ln) > 3:
                parsed.append(ln)
        if parsed:
            scheme["documents_list"] = parsed
    if "documents_list" not in scheme:
        old = scheme.get("documents_required") or []
        scheme["documents_list"] = old if isinstance(old, list) else []

    # Ensure faqs is a list
    faqs_raw = scheme.get("faqs")
    if isinstance(faqs_raw, list):
        scheme["faqs_list"] = faqs_raw
    else:
        scheme["faqs_list"] = []

    return scheme


def _build_guide_from_scheme(scheme: dict) -> dict | None:
    """Synthesize guide dict from flat rich-content DB columns (how_to_apply_english etc.)."""
    import re as _re
    guide: dict = {}

    # how_to_apply: prefer translated text, fall back to English source
    translated_hta = (scheme.get("how_to_apply_translated") or "").strip()
    raw = (scheme.get("how_to_apply_english") or "").strip()

    def _parse_numbered_steps(text: str) -> list[dict]:
        """Parse numbered steps (newline-separated OR inline) into [{title, detail}]."""
        # Strip docs section (after double newline)
        text = text.split("\n\n")[0].strip()
        # If steps are inline ("1. foo. 2. bar."), split on number boundary
        if _re.search(r"\d+\.\s+.+\d+\.", text):
            parts = _re.split(r"(?=\d+\.\s)", text)
        else:
            parts = text.splitlines()
        steps = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            m = _re.match(r"^(\d+)[.)]\s*(.*)", part, _re.DOTALL)
            if m:
                steps.append({"title": str(m.group(1)), "detail": m.group(2).strip()})
            elif steps:
                steps[-1]["detail"] = (steps[-1]["detail"] + " " + part).strip()
        return steps

    if translated_hta:
        steps = _parse_numbered_steps(translated_hta)
        guide["how_to_apply"] = steps if steps else [{"title": "1", "detail": translated_hta[:300]}]
    elif raw:
        # English: "Step N: ..." format from MyScheme
        parts = _re.split(r"(?=Step\s+\d+[.:)]\s)", raw, flags=_re.IGNORECASE)
        steps = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            m = _re.match(r"^Step\s+(\d+)[.:)]\s*(.*)", part, _re.IGNORECASE | _re.DOTALL)
            if m:
                detail = m.group(2).strip()
                detail = _re.sub(r"\.\s*$", "", detail)
                if detail:
                    steps.append({"title": f"Step {m.group(1)}", "detail": detail})
            elif steps:
                steps[-1]["detail"] = (steps[-1]["detail"] + " " + part).strip()
        guide["how_to_apply"] = steps if steps else [{"title": "Apply", "detail": raw[:300]}]

    # use_case: extract name from start of story text
    raw_story = (scheme.get("use_case_english") or "").strip()
    if raw_story:
        name = "Beneficiary"
        m_name = _re.match(r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", raw_story)
        if m_name:
            name = m_name.group(1)
        age = None
        m_age = _re.search(r"(\d{1,2})[- ]?year[s]?[- ]?old", raw_story, _re.IGNORECASE)
        if m_age:
            age = int(m_age.group(1))
        guide["use_case"] = {"name": name, "age": age, "occupation": None, "state": None, "story": raw_story}

    tips = scheme.get("tips_english") or []
    if isinstance(tips, list) and tips:
        guide["tips"] = tips

    mistakes = scheme.get("common_mistakes_english") or []
    if isinstance(mistakes, list) and mistakes:
        guide["common_mistakes"] = mistakes

    return guide if guide else None


def _inject_translated_guide(guide: dict | None, scheme: dict, lang: str) -> dict | None:
    """Override guide.how_to_apply with DB translation when available (non-hi/en langs)."""
    if lang in ("en", "hi") or not scheme.get("how_to_apply_translated"):
        return guide
    translated = _build_guide_from_scheme(scheme)
    if translated and translated.get("how_to_apply"):
        if guide is None:
            guide = {}
        guide = dict(guide)
        guide["how_to_apply"] = translated["how_to_apply"]
    return guide


def get_eligible_schemes(
    gender: str, age: int, state: str,
    income_annual_inr: int | None,
    caste: str | None,
    residence: str | None,
    has_disability: bool,
    is_minority: bool,
    has_bpl: bool,
) -> list:
    """Match schemes using structured enrichment columns.

    Design principle (Aarambha Haq): only include, never exclude.
    If a scheme has no enriched data for a field (NULL), include it —
    avoid false negatives like Telangana's wrongful welfare exclusions.
    """
    conn = db_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    where, params = [], []

    # ── State ────────────────────────────────────────────────────────────────
    if state and state != "All":
        where.append("(state = %s OR state = 'All')")
        params.append(state)

    # ── Age (NULL on either side = pass through) ─────────────────────────────
    if age:
        where.append("(age_min IS NULL OR age_min <= %s)")
        params.append(age)
        where.append("(age_max IS NULL OR age_max >= %s)")
        params.append(age)

    # ── Gender ───────────────────────────────────────────────────────────────
    # Use enriched 'gender' column; fall back to old genders[] array
    if gender and gender in ("male", "female", "transgender"):
        where.append("""(
            gender IS NULL OR gender = 'all'
            OR gender = %s
            OR (genders = '{}' OR %s = ANY(genders))
        )""")
        params.extend([gender, gender])

    # ── Income ───────────────────────────────────────────────────────────────
    # BPL card = effectively 0 income; use enriched column + old column as fallback
    if has_bpl:
        pass  # BPL users qualify for income-gated schemes — don't filter out
    elif income_annual_inr is not None:
        where.append("""(
            income_limit_annual_inr IS NULL
            OR income_limit_annual_inr >= %s
            OR (max_income_lakhs IS NULL OR max_income_lakhs * 100000 >= %s)
        )""")
        params.extend([income_annual_inr, income_annual_inr])

    # ── Caste ────────────────────────────────────────────────────────────────
    if caste and caste not in ("", "unknown"):
        where.append("""(
            caste_categories = '{}'
            OR %s = ANY(caste_categories)
            OR (for_sc_st IS TRUE AND %s IN ('SC','ST'))
        )""")
        params.extend([caste, caste])

    # ── Residence ────────────────────────────────────────────────────────────
    if residence and residence in ("rural", "urban"):
        where.append("(residence_type IS NULL OR residence_type = 'both' OR residence_type = %s)")
        params.append(residence)

    # ── Disability ───────────────────────────────────────────────────────────
    # If user has disability, include all schemes (disabled users qualify for general ones too)
    # Disability-required schemes only shown to disability users
    if not has_disability:
        where.append("(disability_required IS NULL OR disability_required = FALSE)")

    # ── Minority ─────────────────────────────────────────────────────────────
    if not is_minority:
        where.append("(minority_required IS NULL OR minority_required = FALSE)")

    wc = "WHERE " + " AND ".join(where) if where else ""
    cur.execute(
        f"SELECT id,slug,name,short_title,level,state,ministry,description,apply_url,"
        f"beneficiary_type,age_min,age_max,income_limit_annual_inr,caste_categories,"
        f"benefit_type,benefit_amount_inr,benefit_amount_description,documents_required,"
        f"enrichment_confidence "
        f"FROM schemes {wc} "
        f"ORDER BY enrichment_confidence DESC NULLS LAST, name "
        f"LIMIT 60",
        params,
    )
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [dict(r) for r in rows]


def get_states() -> list[str]:
    conn = db_conn()
    cur  = conn.cursor()
    cur.execute("SELECT DISTINCT state FROM schemes WHERE state != 'All' ORDER BY state")
    rows = [r[0] for r in cur.fetchall()]
    cur.close(); conn.close()
    return rows

# ── Language detection ─────────────────────────────────────────────────────
def detect_lang(request: Request) -> str:
    accept = request.headers.get("accept-language", "")
    for part in accept.split(","):
        code = part.split(";")[0].strip().split("-")[0].lower()
        if code in VALID_LANGS:
            return code
    return "hi"   # default Hindi

# ── Generic 404/422 handlers (return HTML, not JSON) ──────────────────────
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    # Detect lang from URL path prefix (e.g. /ta/...) or Accept-Language
    path_parts = request.url.path.split("/", 2)
    lang = path_parts[1] if len(path_parts) > 1 and path_parts[1] in VALID_LANGS else detect_lang(request)
    return templates.TemplateResponse(request, "404.html",
        ctx(request, lang), status_code=404)

# ── Routes ─────────────────────────────────────────────────────────────────
@app.get("/hi/", include_in_schema=False)
@app.get("/hi/{path:path}", include_in_schema=False)
async def redirect_hi(request: Request, path: str = ""):
    """Redirect all /hi/... URLs to rootless canonical Hindi URLs."""
    qs = str(request.url.query)
    target = ("/" + path if path else "/") + (f"?{qs}" if qs else "")
    return RedirectResponse(target, status_code=301)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "aarambha-haq", "version": "0.2.0"}

@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots():
    return """User-agent: *
Allow: /
Disallow: /api/
Disallow: /health
Crawl-delay: 1

User-agent: ClaudeBot
Disallow: /

User-agent: GPTBot
Disallow: /

User-agent: Google-Extended
Disallow: /

Sitemap: https://haq.aarambhax.in/sitemap.xml
"""

@app.get("/sitemap.xml")
async def sitemap():
    base   = "https://haq.aarambhax.in"
    langs  = [l["code"] for l in load_languages()]
    cats   = ["mahila","student","farmer","employment","disability","pension",
              "health","child","tribal","bpl","entrepreneur","minority",
              "housing","maternity","elderly"]

    urls: list[str] = []

    def url(loc: str, priority: str = "0.8", freq: str = "weekly") -> str:
        return (f"  <url><loc>{loc}</loc>"
                f"<changefreq>{freq}</changefreq>"
                f"<priority>{priority}</priority></url>")

    # Hindi is rootless (/), all others use /{lang}/ prefix
    non_hi = [l for l in langs if l != "hi"]

    # Homepages
    urls.append(url(f"{base}/", "1.0", "daily"))                    # Hindi (rootless)
    for lang in non_hi:
        urls.append(url(f"{base}/{lang}/", "1.0", "daily"))

    # Browse all
    urls.append(url(f"{base}/yojana", "0.9", "weekly"))             # Hindi
    for lang in non_hi:
        urls.append(url(f"{base}/{lang}/yojana", "0.9", "weekly"))

    # Category pages
    for cat in cats:
        urls.append(url(f"{base}/yojana/{cat}", "0.9", "weekly"))   # Hindi
    for lang in non_hi:
        for cat in cats:
            urls.append(url(f"{base}/{lang}/yojana/{cat}", "0.9", "weekly"))

    # Static pages
    for page in ["check", "haq", "about"]:
        urls.append(url(f"{base}/{page}", "0.7", "monthly"))        # Hindi
    for lang in non_hi:
        for page in ["check", "haq", "about"]:
            urls.append(url(f"{base}/{lang}/{page}", "0.7", "monthly"))

    # Scheme detail pages — Hindi (rootless) + English only (2754×2 = 5508 URLs)
    conn = db_conn(); cur = conn.cursor()
    cur.execute(
        "SELECT slug FROM schemes ORDER BY enrichment_confidence DESC NULLS LAST, name"
    )
    slugs = [r[0] for r in cur.fetchall()]
    cur.close(); conn.close()
    for slug in slugs:
        urls.append(url(f"{base}/yojana/s/{slug}", "0.7", "monthly"))      # Hindi rootless
        urls.append(url(f"{base}/en/yojana/s/{slug}", "0.6", "monthly"))   # English

    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(urls) +
           "\n</urlset>")
    return Response(content=xml, media_type="application/xml")

_CATS = [
    ("mahila","cat.women",381),("student","cat.student",748),
    ("farmer","cat.farmer",400),("employment","cat.employment",459),
    ("disability","cat.disability",289),("pension","cat.pension",259),
    ("health","cat.health",184),("child","cat.child",182),
    ("tribal","cat.tribal",157),("bpl","cat.bpl",141),
    ("entrepreneur","cat.entrepreneur",121),("minority","cat.minority",87),
    ("housing","cat.housing",69),("maternity","cat.maternity",40),
    ("elderly","cat.elderly",24),
]

def _qs(request: Request) -> str:
    q = str(request.url.query)
    return f"?{q}" if q else ""

# ── Hindi rootless routes (canonical) ─────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def home_hi(request: Request):
    schemes, _ = get_schemes(size=6, lang="hi")
    return templates.TemplateResponse(request, "index.html", ctx(request, "hi",
        popular_schemes=schemes, home_faqs=get_faqs("home", "hi")))

@app.get("/yojana", response_class=HTMLResponse)
async def browse_hi(request: Request, category: str = "", state: str = "",
                    q: str = "", level: str = "", page: int = 1):
    schemes, total = get_schemes(category or None, state or None, q or None, level or None, page, 24, lang="hi")
    return templates.TemplateResponse(request, "browse.html", ctx(request, "hi",
        schemes=schemes, total=total, category=category, state=state,
        q=q, level=level, page=page, categories=_CATS))

@app.get("/yojana/{category}", response_class=HTMLResponse)
async def browse_cat_hi(request: Request, category: str,
                         state: str = "", q: str = "", level: str = "", page: int = 1):
    schemes, total = get_schemes(category, state or None, q or None, level or None, page, 24, lang="hi")
    return templates.TemplateResponse(request, "browse.html", ctx(request, "hi",
        schemes=schemes, total=total, category=category, state=state,
        q=q, level=level, page=page, cat_faqs=get_faqs(category, "hi"), categories=_CATS))

@app.get("/yojana/s/{slug}", response_class=HTMLResponse)
async def scheme_detail_hi(request: Request, slug: str):
    scheme = get_scheme(slug, "hi")
    if not scheme:
        return templates.TemplateResponse(request, "404.html",
            ctx(request, "hi"), status_code=404)
    related, _ = get_schemes(category=(scheme["beneficiary_type"] or [""])[0] or None, size=3, lang="hi")
    related = [s for s in related if s["slug"] != slug][:3]
    guide_file = DATA_DIR / "guides" / f"{slug}.json"
    guide = json.loads(guide_file.read_text()) if guide_file.exists() else _build_guide_from_scheme(scheme)
    return templates.TemplateResponse(request, "scheme_detail.html", ctx(request, "hi",
        scheme=scheme, related=related, guide=guide))

@app.get("/check", response_class=HTMLResponse)
async def check_hi(request: Request):
    return templates.TemplateResponse(request, "check.html", ctx(request, "hi"))

@app.get("/about", response_class=HTMLResponse)
async def about_hi(request: Request):
    return templates.TemplateResponse(request, "about.html", ctx(request, "hi"))

@app.get("/haq", response_class=HTMLResponse)
async def rights_hi(request: Request, category: str = "", q: str = ""):
    conn = db_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        conditions: list = []
        params: list = []
        if category:
            conditions.append("category = %s")
            params.append(category)
        if q:
            conditions.append("(title_hi ILIKE %s OR summary_hi ILIKE %s)")
            params.extend([f"%{q}%", f"%{q}%"])
        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        cur.execute(
            f"SELECT id, slug, title_hi, category, summary_hi, detail_hi "
            f"FROM rights_articles {where} ORDER BY category, id",
            params,
        )
        articles = [dict(r) for r in cur.fetchall()]
    except Exception:
        articles = []
    finally:
        cur.close()
        conn.close()
    from collections import defaultdict
    grouped: dict = defaultdict(list)
    for a in articles:
        if len(grouped[a["category"]]) < 3:
            grouped[a["category"]].append(a)
    categories_map = {c["slug"]: c for c in RIGHTS_CATEGORIES}
    return templates.TemplateResponse(request, "rights.html", ctx(request, "hi",
        articles=articles, categories=RIGHTS_CATEGORIES, categories_map=categories_map,
        grouped=dict(grouped), active_category=category, q=q))

# ── Lang-prefixed routes (all non-Hindi langs) ─────────────────────────────
@app.get("/{lang}/", response_class=HTMLResponse)
async def home(request: Request, lang: str):
    if lang not in VALID_LANGS: return RedirectResponse("/")
    schemes, _ = get_schemes(size=6, lang=lang)
    return templates.TemplateResponse(request, "index.html", ctx(request, lang,
        popular_schemes=schemes, home_faqs=get_faqs("home", lang)))

@app.get("/{lang}/yojana", response_class=HTMLResponse)
async def browse(request: Request, lang: str, category: str = "", state: str = "",
                 q: str = "", level: str = "", page: int = 1):
    if lang not in VALID_LANGS: return RedirectResponse(f"/yojana")
    schemes, total = get_schemes(category or None, state or None, q or None, level or None, page, 24, lang)
    return templates.TemplateResponse(request, "browse.html", ctx(request, lang,
        schemes=schemes, total=total, category=category, state=state,
        q=q, level=level, page=page, categories=_CATS))

@app.get("/{lang}/yojana/{category}", response_class=HTMLResponse)
async def browse_category(request: Request, lang: str, category: str,
                           state: str = "", q: str = "", level: str = "", page: int = 1):
    if lang not in VALID_LANGS: return RedirectResponse(f"/yojana/{category}")
    if category.startswith("s/"):
        return RedirectResponse(f"/{lang}/yojana/{category}")
    schemes, total = get_schemes(category, state or None, q or None, level or None, page, 24, lang)
    return templates.TemplateResponse(request, "browse.html", ctx(request, lang,
        schemes=schemes, total=total, category=category, state=state,
        q=q, level=level, page=page, cat_faqs=get_faqs(category, lang), categories=_CATS))

@app.get("/{lang}/yojana/s/{slug}", response_class=HTMLResponse)
async def scheme_detail(request: Request, lang: str, slug: str):
    if lang not in VALID_LANGS: return RedirectResponse(f"/yojana/s/{slug}")
    scheme = get_scheme(slug, lang)
    if not scheme:
        return templates.TemplateResponse(request, "404.html",
            ctx(request, lang), status_code=404)
    related, _ = get_schemes(category=(scheme["beneficiary_type"] or [""])[0] or None, size=3, lang=lang)
    related = [s for s in related if s["slug"] != slug][:3]
    guide_file = DATA_DIR / "guides" / f"{slug}.json"
    guide = json.loads(guide_file.read_text()) if guide_file.exists() else _build_guide_from_scheme(scheme)
    guide = _inject_translated_guide(guide, scheme, lang)
    return templates.TemplateResponse(request, "scheme_detail.html", ctx(request, lang,
        scheme=scheme, related=related, guide=guide))

@app.get("/{lang}/check", response_class=HTMLResponse)
async def check(request: Request, lang: str):
    if lang not in VALID_LANGS: return RedirectResponse("/check")
    return templates.TemplateResponse(request, "check.html", ctx(request, lang))

# Rights KB
RIGHTS_CATEGORIES = [
    {"slug": "women",        "icon": "👩", "label": "महिला हक"},
    {"slug": "domestic",     "icon": "🏠", "label": "घरेलू हिंसा"},
    {"slug": "maternity",    "icon": "🤱", "label": "प्रसूति"},
    {"slug": "divorce",      "icon": "⚖️", "label": "तलाक"},
    {"slug": "property",     "icon": "🏗", "label": "संपत्ति"},
    {"slug": "pension",      "icon": "🏦", "label": "पेंशन"},
    {"slug": "legal_aid",    "icon": "📋", "label": "कानूनी सहायता"},
    {"slug": "education",    "icon": "🎓", "label": "शिक्षा-रोज़गार"},
]

@app.get("/{lang}/haq", response_class=HTMLResponse)
async def rights(request: Request, lang: str, category: str = "", q: str = ""):
    if lang not in VALID_LANGS: return RedirectResponse("/haq")
    conn = db_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        conditions: list = []
        params: list = []
        if category:
            conditions.append("category = %s")
            params.append(category)
        if q:
            conditions.append("(title_hi ILIKE %s OR summary_hi ILIKE %s)")
            params.extend([f"%{q}%", f"%{q}%"])
        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        cur.execute(
            f"SELECT id, slug, title_hi, category, summary_hi, detail_hi "
            f"FROM rights_articles {where} ORDER BY category, id",
            params,
        )
        articles = [dict(r) for r in cur.fetchall()]
    except Exception:
        articles = []
    finally:
        cur.close()
        conn.close()

    # grouped view: category_slug → first 3 articles
    from collections import defaultdict
    grouped: dict = defaultdict(list)
    for a in articles:
        if len(grouped[a["category"]]) < 3:
            grouped[a["category"]].append(a)

    categories_map = {c["slug"]: c for c in RIGHTS_CATEGORIES}
    return templates.TemplateResponse(request, "rights.html", ctx(request, lang,
        articles=articles,
        categories=RIGHTS_CATEGORIES,
        categories_map=categories_map,
        grouped=dict(grouped),
        active_category=category,
        q=q,
    ))

# About
@app.get("/{lang}/about", response_class=HTMLResponse)
async def about(request: Request, lang: str):
    if lang not in VALID_LANGS: return RedirectResponse("/about")
    return templates.TemplateResponse(request, "about.html", ctx(request, lang))

# ── API endpoints ──────────────────────────────────────────────────────────
@app.get("/api/schemes")
async def api_schemes(category: str = "", state: str = "", q: str = "",
                      level: str = "", page: int = 1, size: int = 20):
    schemes, total = get_schemes(
        category or None, state or None, q or None, level or None, page, min(size, 50)
    )
    return {"total": total, "page": page, "schemes": schemes}

@app.get("/api/schemes/{slug}")
async def api_scheme(slug: str, lang: str = ""):
    s = get_scheme(slug, lang or None)
    if not s: return JSONResponse({"error": "not found"}, status_code=404)
    return s

@app.get("/api/guide/{slug}")
async def api_guide(slug: str):
    """Serve pre-generated rich guide JSON for a scheme (static file, no DB hit)."""
    guide_path = DATA_DIR / "guides" / f"{slug}.json"
    if not guide_path.exists():
        return JSONResponse({"error": "no_guide"}, status_code=404)
    return JSONResponse(json.loads(guide_path.read_text()))

@app.get("/api/categories")
async def api_categories():
    return [
        {"key":"mahila",      "name_hi":"महिला",      "count":381, "icon":"👩"},
        {"key":"student",     "name_hi":"छात्र",       "count":748, "icon":"🎓"},
        {"key":"farmer",      "name_hi":"किसान",       "count":400, "icon":"🌾"},
        {"key":"employment",  "name_hi":"रोजगार",      "count":459, "icon":"💼"},
        {"key":"disability",  "name_hi":"दिव्यांग",    "count":289, "icon":"♿"},
        {"key":"pension",     "name_hi":"पेंशन",       "count":259, "icon":"🏦"},
        {"key":"health",      "name_hi":"स्वास्थ्य",   "count":184, "icon":"🏥"},
        {"key":"child",       "name_hi":"बाल",         "count":182, "icon":"👶"},
        {"key":"tribal",      "name_hi":"जनजाति",      "count":157, "icon":"🌿"},
        {"key":"bpl",         "name_hi":"BPL",         "count":141, "icon":"🏠"},
        {"key":"entrepreneur","name_hi":"उद्यमी",      "count":121, "icon":"💡"},
        {"key":"minority",    "name_hi":"अल्पसंख्यक",  "count":87,  "icon":"🕌"},
        {"key":"housing",     "name_hi":"आवास",        "count":69,  "icon":"🏗"},
        {"key":"maternity",   "name_hi":"मातृत्व",     "count":40,  "icon":"🤱"},
        {"key":"elderly",     "name_hi":"वृद्ध",       "count":24,  "icon":"👴"},
    ]

@app.get("/api/check/results")
async def api_check(
    gender: str   = "female",
    age: int      = 30,
    state: str    = "All",
    income: int   = 0,         # annual income in INR (0 = not specified)
    caste: str    = "",        # SC|ST|OBC|General|EWS|unknown
    residence: str = "",       # rural|urban
    has_disability: int = 0,   # 0/1
    is_minority: int    = 0,   # 0/1
    has_bpl: int        = 0,   # 0/1
):
    schemes = get_eligible_schemes(
        gender=gender,
        age=age,
        state=state,
        income_annual_inr=income if income > 0 else None,
        caste=caste or None,
        residence=residence or None,
        has_disability=bool(has_disability),
        is_minority=bool(is_minority),
        has_bpl=bool(has_bpl),
    )
    return {"count": len(schemes), "schemes": schemes}


@app.get("/api/states")
async def api_states():
    return {"states": get_states()}


@app.get("/api/rights")
async def api_rights(category: str = "", q: str = ""):
    conn = db_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        conditions = []
        params: list = []
        if category:
            conditions.append("category = %s")
            params.append(category)
        if q:
            conditions.append("(title_hi ILIKE %s OR summary_hi ILIKE %s OR %s = ANY(keywords))")
            params.extend([f"%{q}%", f"%{q}%", q])
        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        cur.execute(
            f"SELECT id, slug, title_hi, title_en, category, summary_hi, keywords "
            f"FROM rights_articles {where} ORDER BY category, id",
            params,
        )
        articles = [dict(r) for r in cur.fetchall()]
        return {"count": len(articles), "articles": articles}
    finally:
        cur.close()
        conn.close()


@app.get("/api/rights/{slug}")
async def api_rights_detail(slug: str):
    conn = db_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute(
            "SELECT id, slug, title_hi, title_en, category, summary_hi, detail_hi, keywords "
            "FROM rights_articles WHERE slug = %s",
            (slug,),
        )
        row = cur.fetchone()
        if not row:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Article not found")
        return dict(row)
    finally:
        cur.close()
        conn.close()


@app.get("/api/admin/stale")
async def api_admin_stale(resolved: int = 0, limit: int = 50):
    """Admin endpoint: schemes flagged as stale by the freshness checker."""
    conn = db_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT
                ss.id, ss.scheme_id, ss.slug, ss.name, ss.apply_url,
                ss.reason, ss.http_status, ss.checked_at,
                ss.old_hash, ss.new_hash, ss.resolved, ss.resolved_at
            FROM stale_schemes ss
            WHERE ss.resolved = %s
            ORDER BY ss.checked_at DESC
            LIMIT %s
        """, (bool(resolved), min(limit, 200)))
        rows = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT COUNT(*) FROM stale_schemes WHERE resolved = FALSE")
        total_unresolved = cur.fetchone()["count"]
    except Exception as e:
        # Table may not exist yet if freshness script hasn't run
        rows = []
        total_unresolved = 0
    finally:
        cur.close(); conn.close()
    return {"total_unresolved": total_unresolved, "schemes": rows}


@app.post("/api/admin/stale/{scheme_id}/resolve")
async def api_admin_resolve(scheme_id: int):
    """Mark a stale scheme as manually reviewed/resolved."""
    conn = db_conn()
    cur  = conn.cursor()
    try:
        cur.execute(
            "UPDATE stale_schemes SET resolved = TRUE, resolved_at = NOW() WHERE scheme_id = %s",
            (scheme_id,),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        return JSONResponse({"error": "update failed"}, status_code=500)
    finally:
        cur.close(); conn.close()
    return {"ok": True, "scheme_id": scheme_id}


@app.get("/api/admin/stats")
async def api_admin_stats():
    """High-level platform health stats."""
    conn = db_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT
            COUNT(*)                                               total_schemes,
            COUNT(*) FILTER (WHERE enriched_at IS NOT NULL)       enriched,
            ROUND(AVG(enrichment_confidence)::numeric, 2)         avg_confidence
        FROM schemes
    """)
    scheme_stats = dict(cur.fetchone())

    try:
        cur.execute("""
            SELECT
                COUNT(DISTINCT scheme_id) translated_schemes,
                COUNT(DISTINCT lang_code) languages
            FROM scheme_translations
        """)
        tr = dict(cur.fetchone())
    except Exception:
        tr = {"translated_schemes": 0, "languages": 0}

    try:
        cur.execute("SELECT COUNT(*) FROM stale_schemes WHERE resolved = FALSE")
        stale_count = cur.fetchone()["count"]
    except Exception:
        stale_count = 0

    cur.close(); conn.close()
    return {
        **scheme_stats,
        **tr,
        "stale_count": stale_count,
    }


# ── Telegram Bot User State ───────────────────────────────────────────────────
@app.get("/api/bot/user/{chat_id}")
async def bot_get_user(chat_id: int):
    conn = db_conn(); cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("SELECT * FROM telegram_users WHERE chat_id = %s", (chat_id,))
        row = cur.fetchone()
        return dict(row) if row else {}
    finally:
        cur.close(); conn.close()


@app.post("/api/bot/user/{chat_id}")
async def bot_save_user(chat_id: int, body: dict):
    conn = db_conn(); cur = conn.cursor()
    try:
        cols = list(body.keys())
        vals = list(body.values())
        set_clause = ", ".join(f"{c} = %s" for c in cols)
        cur.execute(
            f"""INSERT INTO telegram_users (chat_id, {', '.join(cols)})
                VALUES (%s, {', '.join(['%s']*len(vals))})
                ON CONFLICT (chat_id) DO UPDATE SET {set_clause}, updated_at = NOW()""",
            [chat_id, *vals, *vals],
        )
        conn.commit()
        return {"ok": True}
    finally:
        cur.close(); conn.close()
