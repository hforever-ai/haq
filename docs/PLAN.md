# Aarambha Haq — Implementation Plan
> `haq.aarambhax.in` · Gemini-consulted · 2026-06-09

---

## Product in One Line
Free, Hindi-first government scheme eligibility checker — 2,754 real schemes, no login.

## Pages
| Route | Hindi Name | Priority |
|-------|-----------|----------|
| `/` | होम — हक का दरवाज़ा | P0 |
| `/check` | पात्रता जांचें (5-step wizard) | P0 |
| `/yojana` | सभी योजनाएं (browse + filter) | P0 |
| `/yojana/[category]` | महिला / छात्र / किसान... | P0 |
| `/yojana/[slug]` | योजना विवरण | P1 |
| `/haq` | अपने अधिकार (rights KB) | P1 |
| `/about` | हमारे बारे में | P2 |

---

## Phase 1 — Foundation (Build first)

### Step 1.1: FastAPI + Jinja2 skeleton
**Files:**
- `api/app/main.py` — mount static, add Jinja2 routes
- `web/static/css/theme.css` — full THEME.md → CSS
- `web/static/css/app.css` — imports theme.css, page-specific rules
- `web/templates/base.html` — nav + footer shell, Google Fonts, meta

**FastAPI routes:**
```python
GET /          → templates/index.html
GET /check     → templates/check.html
GET /yojana    → templates/browse.html
GET /yojana/{category}  → templates/browse.html (category pre-filtered)
GET /yojana/s/{slug}    → templates/scheme_detail.html
GET /haq       → templates/rights.html
GET /about     → templates/about.html
```

**API endpoints (JSON, called by frontend JS):**
```
GET /api/schemes?category=&state=&q=&page=&size=20
GET /api/schemes/{slug}
GET /api/categories          → [{key, name_hi, count, icon}]
GET /api/check/results?...   → eligible scheme IDs
GET /api/rights?category=&q=
```

**LOC estimate:** ~200 Python, ~150 HTML (base), ~500 CSS

---

### Step 1.2: Home Page (`/`)
```
┌──────────────────────────────────────┐
│ NAV [Aarambha Haq logo]    [☰]       │
│ ████ tricolor strip ████             │
├──────────────────────────────────────┤
│ HERO — navy gradient bg              │
│ badge: "2,754+ योजनाएं · मुफ़्त"    │
│ H1: अपना हक़ जानिए                   │
│ sub: अपनी पात्रता जांचें...          │
│ [पात्रता जांचें →] saffron btn       │
│ trust bar: govt data · free · mobile │
├──────────────────────────────────────┤
│ CATEGORIES (3-col mobile, 5-col desk)│
│ [👩 महिला 381] [🎓 छात्र 748]        │
│ [🌾 किसान 400] [💼 रोजगार 459]      │
│ [🏠 आवास 69]  [♿ दिव्यांग 289]     │
│ [👴 वृद्ध 24] [🏥 स्वास्थ्य 184]    │
│ [सभी 15 श्रेणियां →]                 │
├──────────────────────────────────────┤
│ HOW IT WORKS (3 steps)               │
│ 1️⃣ अपनी जानकारी दें                │
│ 2️⃣ पात्र योजनाएं देखें              │
│ 3️⃣ सीधे आवेदन करें                  │
├──────────────────────────────────────┤
│ FOOTER [dark navy]                   │
│ ████ tricolor strip ████             │
└──────────────────────────────────────┘
```

---

### Step 1.3: Browse Page (`/yojana`, `/yojana/[category]`)
```
┌──────────────────────────────────────┐
│ PAGE HEADER (navy gradient)          │
│ "महिला योजनाएं" | 381 योजनाएं       │
├──────────────────────────────────────┤
│ FILTER BAR (sticky on scroll)        │
│ Pills: [सभी] [केंद्र] [राज्य]       │
│ Search: [🔍 योजना खोजें...]          │
│ State dropdown: [राज्य चुनें ▼]      │
├──────────────────────────────────────┤
│ RESULTS                              │
│ "381 योजनाएं मिलीं"                  │
│                                      │
│ [Scheme Card] [Scheme Card]          │
│ [Scheme Card] [Scheme Card]          │
│ [और योजनाएं लोड करें]               │
└──────────────────────────────────────┘
```

**`/api/schemes` JSON shape:**
```json
{
  "total": 381,
  "page": 1,
  "schemes": [
    {
      "slug": "wsfw",
      "name": "Welfare Services for Women",
      "short_title": "WSFW",
      "level": "State",
      "state": "Maharashtra",
      "ministry": "Dept. of Women & Child",
      "description": "...(150 chars)...",
      "category": ["mahila"],
      "tags": ["widow","financial-aid"],
      "apply_url": "https://...",
      "beneficiary_type": ["women"]
    }
  ]
}
```

---

### Step 1.4: Scheme Detail (`/yojana/s/[slug]`)
```
┌──────────────────────────────────────┐
│ ← सभी महिला योजनाएं                 │
│ [केंद्र] badge  [महिला] tag          │
│ H1: Welfare Services for Women       │
│ Ministry: Women & Child, Maha govt   │
│                                      │
│ [इस योजना के लिए पात्रता जांचें →]  │
├──────────────────────────────────────┤
│ विवरण                                │
│ (description text)                   │
├──────────────────────────────────────┤
│ पात्रता (eligibility from tags)       │
├──────────────────────────────────────┤
│ [🔗 आधिकारिक वेबसाइट पर जाएं →]     │
│  (opens apply_url in new tab)        │
├──────────────────────────────────────┤
│ संबंधित योजनाएं (same category, 3)  │
└──────────────────────────────────────┘
```

---

## Phase 2 — Eligibility Wizard (`/check`)

5-step wizard, pure JS state machine, API call only at final step.

```
Step 1: आप कौन हैं?
  → radio: महिला / पुरुष / अन्य

Step 2: आपकी उम्र?
  → number input (1-120)

Step 3: आपका राज्य?
  → select: 28 states + UTs

Step 4: पारिवारिक आय (सालाना)?
  → radio: 1L से कम / 1-3L / 3-6L / 6L से ज़्यादा

Step 5: और जानकारी (optional — skip करें)
  → checkboxes: विधवा · गर्भवती · SHG सदस्य · SC/ST/OBC · अल्पसंख्यक · दिव्यांग

→ RESULTS: "आप X योजनाओं के लिए पात्र हैं"
  → scheme cards with apply buttons
```

**`/api/check/results` query params:**
```
?gender=female&age=32&state=UP&income=2&flags=widow,sc_st
```

**Backend filter logic (rule-based, no LLM):**
```python
# in api/app/routes/check.py
def get_eligible(gender, age, state, income_lakhs, flags):
    q = db.query(Scheme)
    if gender == "female":
        q = q.filter(Scheme.beneficiary_type.overlap(["women","child"]))
    if "widow" in flags:
        q = q.filter(Scheme.for_widow == True)
    if state:
        q = q.filter(or_(Scheme.state == state, Scheme.state == "All"))
    if income_lakhs:
        q = q.filter(or_(Scheme.max_income_lakhs >= income_lakhs,
                          Scheme.max_income_lakhs == None))
    return q.limit(30).all()
```

---

## Phase 3 — Rights KB (`/haq`) and About

### Rights Articles (seed manually, ~20 articles)
Categories: mahila-haq · sampatti · gharelu-hinsa · prasuti · talak · pension · legal-aid

Each article: `slug, title_hi, category, summary_hi (3 lines), detail_hi`

Seed script: `scripts/seed_rights.py` (manual content, not from API)

---

## File Structure

```
aarambha-haq/
├── api/
│   └── app/
│       ├── main.py           ← FastAPI app + Jinja2 + static mount
│       ├── db.py             ← postgres connection
│       ├── models.py         ← SQLAlchemy Scheme + Rights models
│       └── routes/
│           ├── pages.py      ← GET / /check /yojana /haq /about
│           ├── schemes.py    ← GET /api/schemes GET /api/categories
│           ├── check.py      ← GET /api/check/results
│           └── rights.py     ← GET /api/rights
├── web/
│   ├── THEME.md              ← ✅ DONE
│   ├── static/
│   │   ├── css/
│   │   │   ├── theme.css     ← CSS vars from THEME.md
│   │   │   └── app.css       ← page styles (imports theme)
│   │   ├── js/
│   │   │   ├── nav.js        ← hamburger toggle
│   │   │   ├── browse.js     ← scheme fetch + filter + pagination
│   │   │   └── wizard.js     ← 5-step eligibility wizard
│   │   └── icons/            ← SVG icons (categories + UI)
│   └── templates/
│       ├── base.html         ← nav + footer shell
│       ├── index.html        ← home
│       ├── check.html        ← wizard
│       ├── browse.html       ← category + all schemes
│       ├── scheme_detail.html
│       ├── rights.html
│       └── about.html
├── db/
│   └── migrations/
│       ├── 001_init.sql      ← ✅ DONE
│       └── 002_add_fields.sql ← ✅ DONE (beneficiary_type etc)
├── data/
│   ├── myscheme_seed.json    ← ✅ DONE (old 332)
│   └── myscheme_all.json     ← ✅ DONE (2,718 schemes)
├── scripts/
│   ├── fetch_all_myscheme.py ← ✅ DONE
│   ├── seed_schemes.py       ← ✅ DONE (mahila)
│   ├── seed_student.py       ← ✅ DONE
│   ├── seed_all.py           ← ✅ DONE (2,754 total)
│   └── seed_rights.py        ← TODO
└── docs/
    ├── PLAN.md               ← this file
    └── gemini_design_consult.md ← ✅ DONE
```

---

## Build Order (start → ship)

```
[✅] DB + schema
[✅] Data seeded (2,754 schemes)
[✅] THEME.md
[ ] theme.css (CSS from THEME.md)
[ ] base.html (nav + footer)
[ ] index.html (home)
[ ] browse.html + /api/schemes (category page, filterable)
[ ] scheme_detail.html + /api/schemes/{slug}
[ ] check.html + wizard.js + /api/check/results
[ ] rights.html + seed_rights.py
[ ] about.html
[ ] Deploy to haq.aarambhax.in
```

---

## Deployment Target

- **Server:** Independent VPS (NOT shared with Shrutam or Jansampark)
- **Domain:** `haq.aarambhax.in` → Cloudflare DNS → VPS IP
- **Stack:** FastAPI + Uvicorn, PM2 process manager, Nginx reverse proxy
- **DB:** Local Postgres `aarambha_haq` (already seeded)
- **Port:** 8097 (clear of Jansampark :8095, Saavi :8080)
- **Deploy:** `rsync` from local (same pattern as Hisaab)

---

*Consulted: Gemini 2.5 Flash · 2026-06-09 · gemini_design_consult.md*
