#!/usr/bin/env python3
"""
Fix for migrate_server_db.py steps 2 and 3.
Handles TEXT[] array columns + postgres file permission for COPY.
"""

from __future__ import annotations
import csv
import json
import os
import subprocess
import sys
import tempfile
import time

import psycopg2
import psycopg2.extras

LOCAL_DB = "aarambha_haq"
SSH_KEY  = os.path.expanduser("~/.ssh/id_ed25519_hostinger")
SERVER   = "saavi@82.25.108.101"

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

ARRAY_COLS = {"category", "beneficiary_type", "caste_categories", "genders", "streams", "tags"}
JSONB_COLS = {"common_mistakes_english", "faqs", "key_eligibility_questions",
              "references_json", "tips_english"}
BOOL_COLS  = {"is_dbt"}


def ssh_run(sql: str) -> str:
    cmd = ["ssh", "-i", SSH_KEY, SERVER,
           f"sudo -u postgres psql -d {LOCAL_DB} -c {json.dumps(sql)}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout + r.stderr


def ssh_pipe_sql(sql_file_path: str) -> tuple[int, str]:
    cmd = ["ssh", "-i", SSH_KEY, SERVER,
           f"sudo -u postgres psql -d {LOCAL_DB} -v ON_ERROR_STOP=1"]
    with open(sql_file_path, "rb") as f:
        r = subprocess.run(cmd, stdin=f, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def pg_literal(col: str, v) -> str:
    """Convert Python value to PostgreSQL literal, handling arrays correctly."""
    if v is None:
        return "NULL"
    if col in BOOL_COLS:
        return "TRUE" if v else "FALSE"
    if col in ARRAY_COLS:
        if isinstance(v, list):
            # PostgreSQL array literal: '{"val1","val2"}'::text[]
            items = []
            for x in v:
                s = str(x).replace("\\", "\\\\").replace('"', '\\"')
                items.append(f'"{s}"')
            return "'{" + ",".join(items) + "}'::text[]"
        return "NULL"
    if col in JSONB_COLS:
        if isinstance(v, (dict, list)):
            escaped = json.dumps(v, ensure_ascii=False).replace("'", "''")
            return f"'{escaped}'::jsonb"
        return "NULL"
    if isinstance(v, (int, float)):
        return str(v)
    escaped = str(v).replace("'", "''")
    return f"'{escaped}'"


# ── Step 2: Insert missing schemes ─────────────────────────────────────────

def step2_missing_schemes():
    print("\n== Step 2: Insert missing schemes ==", flush=True)

    # Get server slugs
    out = ssh_run("SELECT slug FROM schemes ORDER BY slug;")
    server_slugs = set()
    for line in out.splitlines():
        line = line.strip()
        if line and "|" not in line and not line.startswith("-") and line != "slug" and "row" not in line:
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

    placeholders = ",".join(["%s"] * len(missing))
    cur.execute(f"""
        SELECT *
        FROM schemes
        WHERE slug IN ({placeholders})
        ORDER BY id
    """, list(missing))
    rows = [dict(r) for r in cur.fetchall()]
    cur.close(); conn.close()

    # Get column order from first row
    if not rows:
        print("  No rows to insert.", flush=True)
        return

    col_names = list(rows[0].keys())
    # Skip the 'id' (serial) column to let server assign new ids
    col_names = [c for c in col_names if c != "id"]

    sql_lines = ["BEGIN;"]
    for row in rows:
        vals = [pg_literal(col, row[col]) for col in col_names]
        col_list = ", ".join(col_names)
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
        print(f"  Error rc={rc}: {out[:400]}", flush=True)


# ── Step 3: Update new column data (via Python batch UPDATEs) ──────────────

def step3_update_new_cols():
    print("\n== Step 3: Update new column data ==", flush=True)

    conn = psycopg2.connect(dbname=LOCAL_DB)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cols = ["slug"] + list(NEW_COLS.keys())
    cur.execute(f"SELECT {', '.join(cols)} FROM schemes ORDER BY id")
    rows = [dict(r) for r in cur.fetchall()]
    cur.close(); conn.close()

    total = len(rows)
    print(f"  {total} rows to update", flush=True)

    BATCH = 200
    done = 0
    for i in range(0, total, BATCH):
        batch = rows[i : i + BATCH]
        sql_lines = ["BEGIN;"]

        for row in batch:
            slug = row["slug"].replace("'", "''")
            set_parts = []
            for col in NEW_COLS.keys():
                val = pg_literal(col, row[col])
                set_parts.append(f"{col} = {val}")
            set_clause = ", ".join(set_parts)
            sql_lines.append(f"UPDATE schemes SET {set_clause} WHERE slug = '{slug}';")

        sql_lines.append("COMMIT;")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
            f.write("\n".join(sql_lines))
            tmpfile = f.name

        rc, out = ssh_pipe_sql(tmpfile)
        os.unlink(tmpfile)

        if rc == 0:
            done += len(batch)
            print(f"  Batch {i//BATCH+1}: {len(batch)} rows  [total {done}/{total}]", flush=True)
        else:
            print(f"  Batch error rc={rc}: {out[:300]}", flush=True)
            # Don't abort — continue with next batch
        time.sleep(0.2)

    print(f"  Done. {done}/{total} schemes updated.", flush=True)


def main():
    print("=== Aarambha Haq Migration — Steps 2 & 3 ===", flush=True)
    t0 = time.time()
    step2_missing_schemes()
    step3_update_new_cols()
    print(f"\n=== Done in {time.time()-t0:.0f}s ===", flush=True)


if __name__ == "__main__":
    main()
