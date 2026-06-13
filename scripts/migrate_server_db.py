#!/usr/bin/env python3
"""
Migrate local aarambha_haq DB to server.

Steps:
  1. ALTER TABLE on server — add 21 missing columns
  2. Insert 36 missing schemes (local has 2754, server has 2718)
  3. UPDATE new column data for existing schemes (bulk COPY + UPDATE)
  4. Upsert new scheme_translations rows

Run: python3 scripts/migrate_server_db.py
"""

from __future__ import annotations
import csv
import io
import json
import os
import subprocess
import sys
import tempfile
import time

import psycopg2
import psycopg2.extras

LOCAL_DB  = "aarambha_haq"
SSH_KEY   = os.path.expanduser("~/.ssh/id_ed25519_hostinger")
SERVER    = "saavi@82.25.108.101"


def ssh_run(sql: str, db: str = "aarambha_haq") -> str:
    """Run a SQL statement on the server via sudo -u postgres psql."""
    cmd = ["ssh", "-i", SSH_KEY, SERVER,
           f"sudo -u postgres psql -d {db} -c {json.dumps(sql)}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  SSH error: {r.stderr[:300]}", flush=True)
    return r.stdout + r.stderr


def ssh_pipe_sql(sql_file_path: str, db: str = "aarambha_haq") -> tuple[int, str]:
    """Pipe a .sql file to server postgres and return (returncode, stderr)."""
    cmd = ["ssh", "-i", SSH_KEY, SERVER,
           f"sudo -u postgres psql -d {db} -v ON_ERROR_STOP=1"]
    with open(sql_file_path, "rb") as f:
        r = subprocess.run(cmd, stdin=f, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


# ── Step 1: ALTER TABLE ─────────────────────────────────────────────────────

NEW_COLS = {
    "application_process_md":   "TEXT",
    "benefit_type":             "TEXT",
    "benefits_md":              "TEXT",
    "common_mistakes_english":  "JSONB",
    "detailed_description_md":  "TEXT",
    "documents_required_md":    "TEXT",
    "eligibility_md":           "TEXT",
    "exclusions_md":            "TEXT",
    "faqs":                     "JSONB",
    "how_to_apply_english":     "TEXT",
    "implementing_agency":      "TEXT",
    "is_dbt":                   "BOOLEAN",
    "key_eligibility_questions":"JSONB",
    "myscheme_id":              "TEXT",
    "nodal_department":         "TEXT",
    "references_json":          "JSONB",
    "scheme_image_url":         "TEXT",
    "scraped_at":               "TIMESTAMPTZ",
    "summary_bullets":          "TEXT",
    "tips_english":             "JSONB",
    "use_case_english":         "TEXT",
}


def step1_alter_table():
    print("\n== Step 1: ALTER TABLE ==", flush=True)
    for col, coltype in NEW_COLS.items():
        sql = f"ALTER TABLE schemes ADD COLUMN IF NOT EXISTS {col} {coltype};"
        out = ssh_run(sql)
        status = "OK" if "ALTER TABLE" in out or "already exists" in out or out.strip() == "" else out[:60]
        print(f"  {col}: {status}", flush=True)
    print("  Done.", flush=True)


# ── Step 2: Insert missing schemes ─────────────────────────────────────────

def step2_missing_schemes():
    print("\n== Step 2: Insert missing schemes ==", flush=True)

    # Get slugs on server
    out = ssh_run("SELECT slug FROM schemes ORDER BY slug;")
    server_slugs = set()
    for line in out.splitlines():
        line = line.strip()
        if line and not line.startswith("-") and line not in ("slug", "(", ")") and not line.startswith("("):
            server_slugs.add(line)

    conn = psycopg2.connect(dbname=LOCAL_DB)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT slug FROM schemes ORDER BY slug")
    local_slugs = {r["slug"] for r in cur.fetchall()}
    missing = local_slugs - server_slugs
    print(f"  Missing on server: {len(missing)}", flush=True)

    if not missing:
        print("  Nothing to insert.", flush=True)
        cur.close(); conn.close()
        return

    # Export missing rows as INSERT SQL
    placeholders = ",".join(["%s"] * len(missing))
    cur.execute(f"""
        SELECT id, slug, name, short_title, description, level, state, ministry,
               category, apply_url, beneficiary_type, caste_categories, genders,
               age_min, age_max, income_limit_annual_inr, max_income_lakhs,
               residence_type, disability_required, minority_required,
               employment_status, streams, min_class, max_class, gender,
               for_widow, for_pregnant, for_shg, for_girl_child, for_sc_st,
               for_minority, for_married, benefit_amount_inr, benefit_amount_percent,
               benefit_amount_description, tags, source_hash, enriched_at,
               enrichment_confidence, enrichment_notes, created_at,
               -- new cols too
               application_process_md, benefit_type, benefits_md,
               common_mistakes_english, detailed_description_md,
               documents_required_md, eligibility_md, exclusions_md,
               faqs, how_to_apply_english, implementing_agency, is_dbt,
               key_eligibility_questions, myscheme_id, nodal_department,
               references_json, scheme_image_url, scraped_at, summary_bullets,
               tips_english, use_case_english
        FROM schemes WHERE slug IN ({placeholders})
        ORDER BY id
    """, list(missing))
    rows = cur.fetchall()
    cur.close(); conn.close()

    # Build INSERT SQL
    sql_lines = ["BEGIN;"]
    for row in rows:
        d = dict(row)
        cols_ordered = [k for k in d.keys()]
        vals = []
        for k in cols_ordered:
            v = d[k]
            if v is None:
                vals.append("NULL")
            elif isinstance(v, bool):
                vals.append("TRUE" if v else "FALSE")
            elif isinstance(v, (dict, list)):
                escaped = json.dumps(v, ensure_ascii=False).replace("'", "''")
                vals.append(f"'{escaped}'::jsonb")
            elif isinstance(v, (int, float)):
                vals.append(str(v))
            else:
                escaped = str(v).replace("'", "''")
                vals.append(f"'{escaped}'")
        col_list = ", ".join(cols_ordered)
        val_list = ", ".join(vals)
        sql_lines.append(
            f"INSERT INTO schemes ({col_list}) VALUES ({val_list}) ON CONFLICT (slug) DO NOTHING;"
        )
    sql_lines.append("COMMIT;")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write("\n".join(sql_lines))
        tmpfile = f.name

    rc, out = ssh_pipe_sql(tmpfile)
    os.unlink(tmpfile)
    if rc == 0:
        print(f"  Inserted {len(rows)} missing schemes. OK", flush=True)
    else:
        print(f"  Error rc={rc}: {out[:200]}", flush=True)


# ── Step 3: Update new column data ─────────────────────────────────────────

def step3_update_new_cols():
    print("\n== Step 3: Update new column data (bulk) ==", flush=True)

    JSONB_COLS = {"common_mistakes_english","faqs","key_eligibility_questions",
                  "references_json","tips_english"}
    BOOL_COLS  = {"is_dbt"}
    TSTZ_COLS  = {"scraped_at"}

    conn = psycopg2.connect(dbname=LOCAL_DB)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cols_to_export = ["slug"] + list(NEW_COLS.keys())
    cur.execute(f"SELECT {', '.join(cols_to_export)} FROM schemes ORDER BY id")
    rows = cur.fetchall()
    cur.close(); conn.close()

    print(f"  Exporting {len(rows)} rows...", flush=True)

    # Write to a temp CSV file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False,
                                     encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(cols_to_export)  # header
        for row in rows:
            r = dict(row)
            out_row = []
            for col in cols_to_export:
                v = r[col]
                if v is None:
                    out_row.append("")
                elif col in JSONB_COLS:
                    out_row.append(json.dumps(v, ensure_ascii=False) if v is not None else "")
                elif col in BOOL_COLS:
                    out_row.append("t" if v else "f")
                elif col in TSTZ_COLS:
                    out_row.append(str(v) if v else "")
                else:
                    out_row.append(str(v))
            writer.writerow(out_row)
        csv_path = f.name

    # SCP to server
    scp_cmd = ["scp", "-i", SSH_KEY, csv_path, f"{SERVER}:/tmp/haq_schemes_update.csv"]
    r = subprocess.run(scp_cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  SCP failed: {r.stderr}", flush=True)
        os.unlink(csv_path)
        return
    os.unlink(csv_path)
    print(f"  CSV uploaded to server /tmp/haq_schemes_update.csv", flush=True)

    # Build the UPDATE SQL via temp table
    set_cols = [c for c in NEW_COLS.keys()]
    col_defs = []
    for col, coltype in NEW_COLS.items():
        col_defs.append(f"{col} {coltype}")

    set_clause = ",\n    ".join(
        f"{c} = t.{c}::{NEW_COLS[c]}" if NEW_COLS[c] in ("JSONB",)
        else f"{c} = t.{c}" if NEW_COLS[c] != "TIMESTAMPTZ"
        else f"{c} = CASE WHEN t.{c} = '' THEN NULL ELSE t.{c}::TIMESTAMPTZ END"
        for c in set_cols
    )

    col_list_sql = ", ".join(["slug"] + set_cols)
    col_defs_sql = "slug TEXT,\n  " + ",\n  ".join(col_defs)

    server_sql = f"""
BEGIN;
CREATE TEMP TABLE schemes_upd (
  {col_defs_sql}
);

\\copy schemes_upd ({col_list_sql}) FROM '/tmp/haq_schemes_update.csv' CSV HEADER NULL '';

UPDATE schemes s SET
    {set_clause}
FROM schemes_upd t
WHERE s.slug = t.slug;

DROP TABLE schemes_upd;
COMMIT;
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(server_sql)
        sql_path = f.name

    rc, out = ssh_pipe_sql(sql_path)
    os.unlink(sql_path)

    if rc == 0:
        print(f"  Updated {len(rows)} schemes. OK", flush=True)
    else:
        print(f"  Error rc={rc}:\n{out[:400]}", flush=True)

    # Cleanup server
    ssh_run("SELECT 1;")  # keep connection alive
    subprocess.run(["ssh", "-i", SSH_KEY, SERVER, "rm -f /tmp/haq_schemes_update.csv"],
                   capture_output=True)


# ── Step 4: Sync scheme_translations ───────────────────────────────────────

def step4_sync_translations():
    print("\n== Step 4: Sync scheme_translations ==", flush=True)

    # Get server's existing (scheme_id, lang_code) pairs — slugs easier
    out = ssh_run("""
        SELECT s.slug, t.lang_code
        FROM scheme_translations t
        JOIN schemes s ON s.id = t.scheme_id
        ORDER BY s.slug, t.lang_code;
    """)
    server_pairs = set()
    for line in out.splitlines():
        line = line.strip()
        if "|" in line and not line.startswith("-") and "slug" not in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 2:
                server_pairs.add((parts[0], parts[1]))

    print(f"  Server has {len(server_pairs)} translation pairs", flush=True)

    conn = psycopg2.connect(dbname=LOCAL_DB)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT s.slug, t.lang_code,
               t.scheme_name, t.short_title, t.description,
               t.eligibility_text, t.benefit_text, t.translated_at
        FROM scheme_translations t
        JOIN schemes s ON s.id = t.scheme_id
        ORDER BY s.slug, t.lang_code
    """)
    all_local = cur.fetchall()
    cur.close(); conn.close()

    # Find new rows
    new_rows = [r for r in all_local
                if (dict(r)["slug"], dict(r)["lang_code"]) not in server_pairs]
    print(f"  New translations to add: {len(new_rows)}", flush=True)

    if not new_rows:
        print("  Nothing to add.", flush=True)
        return

    # Build SQL for upsert (batch 500 at a time)
    BATCH = 500
    total_inserted = 0
    for i in range(0, len(new_rows), BATCH):
        batch = new_rows[i : i + BATCH]
        sql_lines = ["BEGIN;"]
        for row in batch:
            d = dict(row)
            slug = d["slug"].replace("'", "''")
            lang = d["lang_code"].replace("'", "''")

            def _esc(v):
                if v is None: return "NULL"
                return "'" + str(v).replace("'", "''") + "'"

            sql_lines.append(f"""
INSERT INTO scheme_translations
  (scheme_id, lang_code, scheme_name, short_title, description, eligibility_text, benefit_text)
SELECT s.id, '{lang}', {_esc(d['scheme_name'])}, {_esc(d['short_title'])},
       {_esc(d['description'])}, {_esc(d['eligibility_text'])}, {_esc(d['benefit_text'])}
FROM schemes s WHERE s.slug = '{slug}'
ON CONFLICT (scheme_id, lang_code) DO NOTHING;""")
        sql_lines.append("COMMIT;")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
            f.write("\n".join(sql_lines))
            tmpfile = f.name

        rc, out = ssh_pipe_sql(tmpfile)
        os.unlink(tmpfile)
        if rc == 0:
            total_inserted += len(batch)
            print(f"  Batch {i//BATCH+1}: {len(batch)} rows  [total {total_inserted}]", flush=True)
        else:
            print(f"  Batch error rc={rc}: {out[:200]}", flush=True)
            break

    print(f"  Done. {total_inserted} translation rows synced.", flush=True)


# ── Step 5: Sync how_to_apply column ───────────────────────────────────────

def step5_sync_how_to_apply():
    print("\n== Step 5: Sync scheme_translations.how_to_apply ==", flush=True)

    # Ensure column exists on server
    ssh_run("ALTER TABLE scheme_translations ADD COLUMN IF NOT EXISTS how_to_apply TEXT;")
    print("  Column ensured on server.", flush=True)

    # Pull all local (slug, lang_code, how_to_apply) where how_to_apply is set
    conn = psycopg2.connect(dbname=LOCAL_DB)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT s.slug, t.lang_code, t.how_to_apply
        FROM scheme_translations t
        JOIN schemes s ON s.id = t.scheme_id
        WHERE t.how_to_apply IS NOT NULL AND t.how_to_apply != ''
        ORDER BY s.slug, t.lang_code
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()

    print(f"  Local rows with how_to_apply: {len(rows)}", flush=True)
    if not rows:
        print("  Nothing to sync.", flush=True)
        return

    def _esc(v):
        if v is None: return "NULL"
        return "'" + str(v).replace("'", "''") + "'"

    BATCH = 500
    total_done = 0
    for i in range(0, len(rows), BATCH):
        batch = [dict(r) for r in rows[i : i + BATCH]]
        sql_lines = ["BEGIN;"]
        for d in batch:
            slug = d["slug"].replace("'", "''")
            lang = d["lang_code"].replace("'", "''")
            sql_lines.append(f"""
UPDATE scheme_translations t SET how_to_apply = {_esc(d['how_to_apply'])}
FROM schemes s
WHERE s.id = t.scheme_id AND s.slug = '{slug}' AND t.lang_code = '{lang}';""")
        sql_lines.append("COMMIT;")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
            f.write("\n".join(sql_lines))
            tmpfile = f.name

        rc, out = ssh_pipe_sql(tmpfile)
        os.unlink(tmpfile)
        if rc == 0:
            total_done += len(batch)
            print(f"  Batch {i//BATCH+1}: {len(batch)} rows updated  [total {total_done}]", flush=True)
        else:
            print(f"  Batch error rc={rc}: {out[:200]}", flush=True)
            break

    print(f"  Done. {total_done} how_to_apply rows synced.", flush=True)


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--only-how-to-apply", action="store_true",
                    help="Skip steps 1-4 and only sync how_to_apply column")
    args = ap.parse_args()

    print("=== Aarambha Haq DB Migration (local → server) ===", flush=True)
    t0 = time.time()

    if args.only_how_to_apply:
        step5_sync_how_to_apply()
    else:
        step1_alter_table()
        step2_missing_schemes()
        step3_update_new_cols()
        step4_sync_translations()
        step5_sync_how_to_apply()

    print(f"\n=== Done in {time.time()-t0:.0f}s ===", flush=True)


if __name__ == "__main__":
    main()
