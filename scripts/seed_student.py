"""Seed student schemes from myscheme_seed.json into aarambha_haq."""
import json, re
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values

DB   = "aarambha_haq"
SEED = Path(__file__).parent.parent / "data" / "myscheme_seed.json"

GENDER_MAP = {"girl": "female", "women": "female", "woman": "female",
              "boy": "male", "men": "male"}

def income(text):
    m = re.search(r"(\d[\d,]*)\s*(?:lakh|lac|L)\b", text, re.I)
    return float(m.group(1).replace(",","")) if m else None

def class_range(text):
    mn = mx = None
    if re.search(r"\bclass\s*[6-8]\b|\bvi\b|\bvii\b|\bviii\b", text, re.I): mn = 6; mx = 8
    if re.search(r"\bclass\s*9\b|\bix\b", text, re.I): mn = mn or 9
    if re.search(r"\bclass\s*10\b|\bx\b(?![ivx])", text, re.I): mn = mn or 10; mx = 10
    if re.search(r"\bclass\s*11\b|\bxi\b", text, re.I): mn = mn or 11
    if re.search(r"\bclass\s*12\b|\bxii\b", text, re.I): mn = mn or 11; mx = 12
    if re.search(r"\bgraduat|\bug\b|\bb\.tech|\bb\.sc|\bb\.com", text, re.I): mn = mn or 13; mx = 17
    if re.search(r"\bpost.grad|\bpg\b|\bm\.tech|\bm\.sc", text, re.I): mn = mn or 17; mx = 22
    if re.search(r"\bphd\b|\bdoctoral\b", text, re.I): mn = mn or 20; mx = 30
    return mn, mx

conn = psycopg2.connect(dbname=DB)
cur  = conn.cursor()

data    = json.loads(SEED.read_text())
schemes = data.get("student", [])
print(f"Seeding {len(schemes)} student schemes into {DB}...")

rows = []
for s in schemes:
    tags = s.get("tags", [])
    desc = s.get("description", "") or ""
    text = " ".join(tags) + " " + desc
    mn, mx = class_range(text)

    genders = list({GENDER_MAP[k] for k in GENDER_MAP if k in text.lower()})

    streams = []
    if re.search(r"\bengineering|\bb\.tech|\bjee\b", text, re.I): streams.append("engineering")
    if re.search(r"\bmedical|\bmbbs|\bneet\b", text, re.I): streams.append("medical")
    if re.search(r"\barts\b|\bhumanities\b", text, re.I): streams.append("arts")
    if re.search(r"\bcommerce\b|\bb\.com\b", text, re.I): streams.append("commerce")
    if re.search(r"\bscience\b|\bb\.sc\b", text, re.I): streams.append("science")

    rows.append((
        s["slug"], s["name"], s.get("short_title",""),
        s.get("level","Central"), s.get("state","All"),
        s.get("ministry",""), s.get("category",[]), tags, desc,
        s.get("url",""),
        False, False, False, False, False,
        bool(re.search(r"\bsc\b|\bst\b|\bdalit\b|\btribal\b|\bobc\b", text, re.I)),
        bool(re.search(r"\bminority\b|\bmuslim\b|\bsikh\b|\bchristian\b", text, re.I)),
        income(text),
        "{student}", mn, mx, streams or [], genders,
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
        beneficiary_type = EXCLUDED.beneficiary_type
""", rows)

conn.commit(); cur.close(); conn.close()
print(f"Done. {len(rows)} student schemes seeded.")
