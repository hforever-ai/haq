#!/usr/bin/env python3
"""
Fetch documents_required for all schemes from MyScheme API.
Two-step: GET ?slug={slug} → get _id → GET /{_id}/documents → get documentsRequired_md
Resumable: saves checkpoint to /tmp/haq_docs_checkpoint.json
"""

import json
import os
import re
import time
import urllib.request
import urllib.error
import psycopg2
from pathlib import Path

API_BASE = "https://api.myscheme.gov.in/schemes/v6/public/schemes"
API_KEY = "tYTy5eEhlu9rFjyxuCr7ra7ACp4dv1RH8gWuHTDc"
CHECKPOINT = Path("/tmp/haq_docs_checkpoint.json")
DELAY = 0.35  # seconds between requests

HEADERS = {
    "x-api-key": API_KEY,
    "accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}


def api_get(url: str) -> dict | None:
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            raw = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", raw)
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print("  Rate limited — sleeping 10s")
            time.sleep(10)
            return None
        print(f"  HTTP {e.code} for {url}")
        return None
    except Exception as e:
        print(f"  Error for {url}: {e}")
        return None


def fetch_documents_for_slug(slug: str) -> str | None:
    """Returns documentsRequired_md string or None if unavailable."""
    # Step 1: get _id
    data = api_get(f"{API_BASE}?slug={slug}&lang=en")
    if not data or data.get("statusCode") != 200:
        return None
    scheme_id = data.get("data", {}).get("_id")
    if not scheme_id:
        return None
    time.sleep(DELAY)

    # Step 2: get documents
    docs_data = api_get(f"{API_BASE}/{scheme_id}/documents?lang=en")
    if not docs_data or docs_data.get("statusCode") != 200:
        return None

    en = docs_data.get("data", {}).get("en", {})
    md = en.get("documentsRequired_md", "").strip()
    return md if md else None


def md_to_list(md: str) -> list[str]:
    """Convert markdown bullet list to clean string list."""
    items = []
    for line in md.splitlines():
        line = line.strip().lstrip("-*• ").strip()
        # Remove markdown formatting
        line = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
        line = re.sub(r"\*(.+?)\*", r"\1", line)
        line = re.sub(r"<br\s*/?>", "", line, flags=re.IGNORECASE)
        line = line.strip()
        if line and len(line) > 3:
            items.append(line)
    return items


def main():
    # Load checkpoint
    checkpoint: dict[str, str | None] = {}
    if CHECKPOINT.exists():
        checkpoint = json.loads(CHECKPOINT.read_text())
        print(f"Loaded checkpoint: {len(checkpoint)} slugs already processed")

    # Get all slugs from DB
    conn = psycopg2.connect(dbname="aarambha_haq")
    cur = conn.cursor()
    cur.execute("SELECT slug FROM schemes ORDER BY id")
    slugs = [row[0] for row in cur.fetchall()]
    print(f"Total schemes: {len(slugs)}")

    pending = [s for s in slugs if s not in checkpoint]
    print(f"Pending: {len(pending)}")

    # Fetch
    for i, slug in enumerate(pending, 1):
        print(f"[{i}/{len(pending)}] {slug}", end=" ... ", flush=True)
        md = fetch_documents_for_slug(slug)
        checkpoint[slug] = md if md else "SKIP"
        print("SKIP" if not md else f"OK ({len(md)} chars)")

        # Save checkpoint every 50
        if i % 50 == 0:
            CHECKPOINT.write_text(json.dumps(checkpoint))
            print(f"  [checkpoint saved: {i} done]")

        time.sleep(DELAY)

    CHECKPOINT.write_text(json.dumps(checkpoint))
    print(f"\nAll fetched. Updating DB...")

    # Update DB
    updated = 0
    for slug, md in checkpoint.items():
        if md == "SKIP" or not md:
            continue
        doc_list = md_to_list(md)
        if not doc_list:
            continue
        doc_json = json.dumps(doc_list, ensure_ascii=False)
        cur.execute(
            "UPDATE schemes SET documents_required = %s::jsonb WHERE slug = %s",
            (doc_json, slug),
        )
        updated += 1

    conn.commit()
    cur.close()
    conn.close()

    print(f"Updated {updated} schemes with documents.")

    # Stats
    skipped = sum(1 for v in checkpoint.values() if v == "SKIP")
    has_docs = sum(1 for v in checkpoint.values() if v and v != "SKIP")
    print(f"Has docs: {has_docs}, No docs: {skipped}")


if __name__ == "__main__":
    main()
