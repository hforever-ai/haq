"""Fetch ALL government schemes from MyScheme API across all categories.

Run: python3 scripts/fetch_all_myscheme.py
Output: data/myscheme_all.json
"""
import json, time, urllib.request, urllib.parse
from pathlib import Path

API   = "https://api.myscheme.gov.in/search/v6/schemes"
KEY   = "tYTy5eEhlu9rFjyxuCr7ra7ACp4dv1RH8gWuHTDc"
HEADERS = {
    "x-api-key": KEY,
    "Origin":    "https://www.myscheme.gov.in",
    "Referer":   "https://www.myscheme.gov.in/",
    "User-Agent":"Mozilla/5.0",
    "Accept":    "application/json",
}

CATEGORIES = [
    "women",
    "student",
    "farmer",
    "elderly",
    "disability",
    "bpl",
    "minority",
    "health",
    "housing",
    "employment",
    "entrepreneur",
    "child",
    "maternity",
    "pension",
    "tribal",
]

PAGE_SIZE = 100

OUT = Path(__file__).parent.parent / "data" / "myscheme_all.json"


def fetch_page(keyword, from_=0):
    params = urllib.parse.urlencode({
        "lang": "en", "q": "", "keyword": keyword,
        "sort": "", "from": from_, "size": PAGE_SIZE,
    })
    req = urllib.request.Request(f"{API}?{params}", headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())


def parse_item(item):
    f = item.get("fields", {})
    # tags can be list of strings or list of dicts
    tags = []
    for t in (f.get("tags") or []):
        if isinstance(t, dict):
            tags.append(t.get("en", t.get("label", "")))
        elif isinstance(t, str):
            tags.append(t)

    cats = []
    for c in (f.get("schemeCategory") or []):
        if isinstance(c, dict):
            cats.append(c.get("en", c.get("label", "")))
        elif isinstance(c, str):
            cats.append(c)

    state_list = f.get("beneficiaryState") or []
    state = state_list[0] if state_list else "All"
    if isinstance(state, dict):
        state = state.get("en", state.get("label", "All"))

    return {
        "slug":        f.get("slug", ""),
        "name":        f.get("schemeName", ""),
        "short_title": f.get("schemeShortTitle", ""),
        "level":       f.get("level", ""),
        "state":       state,
        "ministry":    f.get("ministry", ""),
        "description": f.get("briefDescription", ""),
        "category":    [c for c in cats if c],
        "tags":        [t for t in tags if t],
        "url":         f"https://www.myscheme.gov.in/schemes/{f.get('slug','')}",
    }


def fetch_all(keyword):
    schemes = {}
    from_ = 0
    while True:
        data   = fetch_page(keyword, from_)
        hits   = data.get("data", {}).get("hits", {})
        items  = hits.get("items", [])
        page   = hits.get("page", {})
        total  = page.get("total", 0)

        for item in items:
            parsed = parse_item(item)
            if parsed["slug"]:
                schemes[parsed["slug"]] = parsed

        from_ += PAGE_SIZE
        if from_ >= total or not items:
            break
        time.sleep(0.2)

    return list(schemes.values()), total


result = {}
totals = {}

for cat in CATEGORIES:
    print(f"Fetching '{cat}'...", end=" ", flush=True)
    try:
        schemes, total = fetch_all(cat)
        result[cat] = schemes
        totals[cat] = len(schemes)
        print(f"{len(schemes)}/{total}")
    except Exception as e:
        print(f"ERROR: {e}")
        result[cat] = []
    time.sleep(0.4)

OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False))

print(f"\nSaved → {OUT}")
print("Per-category counts:", totals)
all_slugs = {s["slug"] for cat_schemes in result.values() for s in cat_schemes if s.get("slug")}
print(f"Grand total UNIQUE schemes: {len(all_slugs)}")
