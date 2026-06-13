"""Seed aarambha_haq DB with women schemes from MyScheme API data."""
import json, re, sys
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values

DB   = "aarambha_haq"
SEED = Path(__file__).parent.parent / "data" / "myscheme_seed.json"

WIDOW_TAGS    = {"widow","widows","vidhwa","destitute"}
PREGNANT_TAGS = {"pregnant","maternity","matru","prenatal","antenatal","lactating"}
MARRIED_TAGS  = {"married","wife","spouse","vivahit"}
SHG_TAGS      = {"shg","self-help","self help","nrlm","aajeevika"}
GIRL_TAGS     = {"girl","beti","daughter","ladki","kanya"}
SC_ST_TAGS    = {"sc","st","scheduled caste","scheduled tribe","dalit","tribal","obc"}
MINORITY_TAGS = {"minority","muslim","christian","sikh","buddhist","jain","parsi"}

def flag(tags: list[str], keywords: set[str]) -> bool:
    low = {t.lower() for t in tags}
    return bool(low & keywords)

def income_from_tags(tags: list[str], desc: str) -> float | None:
    text = " ".join(tags) + " " + (desc or "")
    m = re.search(r"(?:income|salary|earning)[^\d]*(\d[\d,]*)\s*(?:lakh|lac|L)", text, re.I)
    if m:
        return float(m.group(1).replace(",", ""))
    m = re.search(r"(\d[\d,]*)\s*(?:lakh|lac|L)\s*(?:per annum|pa|p\.a\.|annual)", text, re.I)
    if m:
        return float(m.group(1).replace(",", ""))
    return None

def main():
    data   = json.loads(SEED.read_text())
    women  = data["women"]
    print(f"Seeding {len(women)} women schemes into {DB}...")

    conn = psycopg2.connect(dbname=DB)
    cur  = conn.cursor()

    rows = []
    for s in women:
        tags = s.get("tags", [])
        desc = s.get("description", "")
        rows.append((
            s["slug"], s["name"], s.get("short_title",""),
            s.get("level","State"), s.get("state","All"),
            s.get("ministry",""),
            s.get("category",[]), tags, desc,
            s.get("url",""),
            flag(tags, MARRIED_TAGS),
            flag(tags, WIDOW_TAGS),
            flag(tags, PREGNANT_TAGS),
            flag(tags, SHG_TAGS),
            flag(tags, GIRL_TAGS),
            flag(tags, SC_ST_TAGS),
            flag(tags, MINORITY_TAGS),
            income_from_tags(tags, desc),
        ))

    execute_values(cur, """
        INSERT INTO schemes
            (slug, name, short_title, level, state, ministry,
             category, tags, description, apply_url,
             for_married, for_widow, for_pregnant, for_shg,
             for_girl_child, for_sc_st, for_minority, max_income_lakhs)
        VALUES %s
        ON CONFLICT (slug) DO UPDATE SET
            name        = EXCLUDED.name,
            tags        = EXCLUDED.tags,
            description = EXCLUDED.description
    """, rows)

    conn.commit()
    cur.close(); conn.close()
    print(f"Done. {len(rows)} women schemes seeded.")

if __name__ == "__main__":
    main()
