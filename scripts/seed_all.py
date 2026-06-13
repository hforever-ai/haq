"""Seed ALL schemes from myscheme_all.json into aarambha_haq.schemes.

Each scheme gets tagged with its category in beneficiary_type[].
Schemes appearing in multiple categories get multiple tags (array_append).
"""
import json, re
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values

DB   = "aarambha_haq"
SEED = Path(__file__).parent.parent / "data" / "myscheme_all.json"

WIDOW_TAGS    = {"widow","widows","vidhwa","destitute"}
PREGNANT_TAGS = {"pregnant","maternity","matru","prenatal","antenatal","lactating"}
MARRIED_TAGS  = {"married","wife","spouse","vivahit"}
SHG_TAGS      = {"shg","self-help","self help","nrlm","aajeevika"}
GIRL_TAGS     = {"girl","beti","daughter","ladki","kanya"}
SC_ST_TAGS    = {"sc","st","scheduled caste","scheduled tribe","dalit","tribal","obc"}
MINORITY_TAGS = {"minority","muslim","christian","sikh","buddhist","parsi"}

def flag(tags, keywords):
    low = {t.lower() for t in tags}
    return bool(low & keywords)

def income(text):
    m = re.search(r"(\d[\d,]*)\s*(?:lakh|lac|L)\b", text, re.I)
    return float(m.group(1).replace(",","")) if m else None

def class_range(text):
    mn = mx = None
    if re.search(r"\bclass\s*[6-8]\b|\bvi\b|\bvii\b|\bviii\b", text, re.I): mn = 6; mx = 8
    if re.search(r"\bclass\s*9\b|\bix\b", text, re.I): mn = mn or 9
    if re.search(r"\bclass\s*10\b|\bx\b(?![ivx])", text, re.I): mn = mn or 10; mx = 10
    if re.search(r"\bclass\s*12\b|\bxii\b", text, re.I): mn = mn or 11; mx = 12
    if re.search(r"\bgraduat|\bb\.tech|\bb\.sc|\bb\.com", text, re.I): mn = mn or 13; mx = 17
    if re.search(r"\bpost.grad|\bpg\b|\bm\.tech", text, re.I): mn = mn or 17; mx = 22
    if re.search(r"\bphd\b|\bdoctoral\b", text, re.I): mn = mn or 20; mx = 30
    return mn, mx

LEVEL_FIX = {"central": "Central", "state": "State", "": "Central"}

def fix_level(v):
    v = (v or "").strip()
    return LEVEL_FIX.get(v.lower(), v if v in ("Central","State") else "Central")

def main():
    data = json.loads(SEED.read_text())

    # Build slug → {scheme, categories[]}
    by_slug = {}
    for cat, schemes in data.items():
        for s in schemes:
            slug = s.get("slug","").strip()
            if not slug:
                continue
            if slug not in by_slug:
                by_slug[slug] = {"s": s, "cats": set()}
            by_slug[slug]["cats"].add(cat)

    print(f"Total unique schemes: {len(by_slug)}")

    import os as _os
    _kwargs: dict = {"dbname": _os.getenv("DB_NAME", DB)}
    if _os.getenv("DB_HOST"):
        _kwargs.update({"host": _os.getenv("DB_HOST"), "port": int(_os.getenv("DB_PORT", "5432")),
                        "user": _os.getenv("DB_USER"), "password": _os.getenv("DB_PASS", "")})
    conn = psycopg2.connect(**_kwargs)
    cur  = conn.cursor()

    rows = []
    for slug, obj in by_slug.items():
        s    = obj["s"]
        cats = sorted(obj["cats"])
        tags = s.get("tags", [])
        desc = s.get("description", "") or ""
        text = " ".join(tags) + " " + desc
        mn, mx = class_range(text)

        genders = []
        if re.search(r"\bgirl\b|\bwomen\b|\bwoman\b|\bmahila\b", text, re.I): genders.append("female")
        if re.search(r"\bboy\b|\bmen\b|\bmale\b|\bpurush\b", text, re.I): genders.append("male")

        streams = []
        if re.search(r"\bengineering|\bb\.tech|\bjee\b", text, re.I): streams.append("engineering")
        if re.search(r"\bmedical|\bmbbs|\bneet\b", text, re.I): streams.append("medical")
        if re.search(r"\barts\b|\bhumanities\b", text, re.I): streams.append("arts")
        if re.search(r"\bcommerce\b|\bb\.com\b", text, re.I): streams.append("commerce")
        if re.search(r"\bscience\b|\bb\.sc\b", text, re.I): streams.append("science")

        rows.append((
            slug, s.get("name",""), s.get("short_title",""),
            fix_level(s.get("level","")), s.get("state","All") or "All",
            s.get("ministry",""),
            s.get("category",[]), tags, desc, s.get("url",""),
            flag(tags, MARRIED_TAGS),
            flag(tags, WIDOW_TAGS),
            flag(tags, PREGNANT_TAGS),
            flag(tags, SHG_TAGS),
            flag(tags, GIRL_TAGS),
            flag(tags, SC_ST_TAGS),
            flag(tags, MINORITY_TAGS),
            income(text),
            cats,      # beneficiary_type
            mn, mx, streams, genders,
        ))

    execute_values(cur, """
        INSERT INTO schemes
            (slug, name, short_title, level, state, ministry,
             category, tags, description, apply_url,
             for_married, for_widow, for_pregnant, for_shg, for_girl_child,
             for_sc_st, for_minority, max_income_lakhs,
             beneficiary_type, min_class, max_class, streams, genders)
        VALUES %s
        ON CONFLICT (slug) DO UPDATE SET
            name             = EXCLUDED.name,
            description      = EXCLUDED.description,
            tags             = EXCLUDED.tags,
            beneficiary_type = EXCLUDED.beneficiary_type,
            min_class        = EXCLUDED.min_class,
            max_class        = EXCLUDED.max_class,
            streams          = EXCLUDED.streams,
            genders          = EXCLUDED.genders
    """, rows, page_size=500)

    conn.commit()
    cur.close(); conn.close()

    # Summary
    cur2 = psycopg2.connect(**_kwargs).cursor()
    cur2.execute("SELECT unnest(beneficiary_type) AS t, COUNT(*) FROM schemes GROUP BY 1 ORDER BY 2 DESC")
    print("\nDB counts by type:")
    for row in cur2.fetchall():
        print(f"  {row[0]:<20} {row[1]}")
    cur2.execute("SELECT COUNT(*) FROM schemes")
    print(f"\n  TOTAL schemes in DB: {cur2.fetchone()[0]}")
    cur2.connection.close()

if __name__ == "__main__":
    main()
