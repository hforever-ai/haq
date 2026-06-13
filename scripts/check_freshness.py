"""Phase 4 — Data freshness monitor for Aarambha Haq schemes.

Scrapes each scheme's apply_url, computes a content hash, compares with
stored source_hash. Schemes that differ or return 4xx/5xx are flagged
for review in the stale_schemes admin queue.

Designed to run nightly via cron:
    0 2 * * * cd /opt/aarambha-haq && python3 scripts/check_freshness.py >> /var/log/haq_freshness.log 2>&1

Usage:
    python3 scripts/check_freshness.py               # check all schemes with apply_url
    python3 scripts/check_freshness.py --limit 50    # test run
    python3 scripts/check_freshness.py --slug pmkisan  # single scheme
    python3 scripts/check_freshness.py --workers 20  # more concurrency
    python3 scripts/check_freshness.py --stats        # print stats only, no scraping
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import psycopg2
import psycopg2.extras
import requests

USER_AGENT = (
    "Mozilla/5.0 (compatible; AarambhaHaqBot/1.0; "
    "+https://haq.aarambhax.in/about)"
)
REQUEST_TIMEOUT = 15
MAX_BODY_BYTES  = 64 * 1024  # first 64KB is enough for hash comparison


# ── DB helpers ────────────────────────────────────────────────────────────────
def db_conn():
    kw: dict = {"dbname": os.getenv("DB_NAME", "aarambha_haq")}
    if os.getenv("DB_HOST"):
        kw.update({
            "host": os.getenv("DB_HOST"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASS", ""),
        })
    return psycopg2.connect(**kw)


def ensure_stale_table():
    conn = db_conn()
    cur  = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stale_schemes (
            id            SERIAL PRIMARY KEY,
            scheme_id     INTEGER NOT NULL REFERENCES schemes(id) ON DELETE CASCADE,
            slug          TEXT    NOT NULL,
            name          TEXT    NOT NULL,
            apply_url     TEXT,
            reason        TEXT    NOT NULL,  -- 'hash_changed'|'404'|'5xx'|'timeout'|'ssl_error'
            old_hash      TEXT,
            new_hash      TEXT,
            http_status   INTEGER,
            checked_at    TIMESTAMPTZ DEFAULT NOW(),
            resolved      BOOLEAN DEFAULT FALSE,
            resolved_at   TIMESTAMPTZ,
            CONSTRAINT uk_stale UNIQUE (scheme_id)
        );
        CREATE INDEX IF NOT EXISTS idx_stale_resolved ON stale_schemes(resolved);
        CREATE INDEX IF NOT EXISTS idx_stale_checked  ON stale_schemes(checked_at);
    """)
    conn.commit()
    cur.close(); conn.close()


def load_schemes(slug: str | None, limit: int | None) -> list[dict]:
    conn = db_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    parts, params = [], []
    parts.append("apply_url IS NOT NULL AND apply_url != ''")
    if slug:
        parts.append("slug = %s"); params.append(slug)
    where = "WHERE " + " AND ".join(parts)
    lim   = f"LIMIT {limit}" if limit else ""
    cur.execute(
        f"SELECT id, slug, name, apply_url, source_hash "
        f"FROM schemes {where} ORDER BY id {lim}",
        params,
    )
    rows = [dict(r) for r in cur.fetchall()]
    cur.close(); conn.close()
    return rows


_db_lock = threading.Lock()

def mark_stale(scheme: dict, reason: str, new_hash: str | None, http_status: int | None):
    with _db_lock:
        conn = db_conn()
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO stale_schemes (scheme_id, slug, name, apply_url, reason, old_hash, new_hash, http_status, checked_at, resolved)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), FALSE)
            ON CONFLICT (scheme_id)
            DO UPDATE SET
                reason       = EXCLUDED.reason,
                old_hash     = EXCLUDED.old_hash,
                new_hash     = EXCLUDED.new_hash,
                http_status  = EXCLUDED.http_status,
                checked_at   = NOW(),
                resolved     = FALSE,
                resolved_at  = NULL
        """, (
            scheme["id"], scheme["slug"], scheme["name"],
            scheme["apply_url"], reason, scheme.get("source_hash"),
            new_hash, http_status,
        ))
        conn.commit()
        cur.close(); conn.close()


def update_hash(scheme_id: int, new_hash: str):
    with _db_lock:
        conn = db_conn()
        cur  = conn.cursor()
        cur.execute(
            "UPDATE schemes SET source_hash = %s WHERE id = %s",
            (new_hash, scheme_id),
        )
        conn.commit()
        cur.close(); conn.close()


def clear_stale(scheme_id: int):
    with _db_lock:
        conn = db_conn()
        cur  = conn.cursor()
        cur.execute(
            "UPDATE stale_schemes SET resolved = TRUE, resolved_at = NOW() WHERE scheme_id = %s",
            (scheme_id,),
        )
        conn.commit()
        cur.close(); conn.close()


# ── Scraper ───────────────────────────────────────────────────────────────────
def scrape_hash(url: str) -> tuple[str | None, int | None, str | None]:
    """Returns (content_hash, http_status, error_reason)."""
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
            stream=True,
        )
        if resp.status_code == 404:
            return None, 404, "404"
        if resp.status_code >= 500:
            return None, resp.status_code, "5xx"
        if resp.status_code >= 400:
            return None, resp.status_code, f"http_{resp.status_code}"

        # Read up to MAX_BODY_BYTES
        body = b""
        for chunk in resp.iter_content(chunk_size=8192):
            body += chunk
            if len(body) >= MAX_BODY_BYTES:
                break

        # Hash the stripped text content (strip whitespace to reduce noise)
        h = hashlib.sha256(body[:MAX_BODY_BYTES]).hexdigest()[:32]
        return h, resp.status_code, None

    except requests.exceptions.SSLError:
        return None, None, "ssl_error"
    except requests.exceptions.Timeout:
        return None, None, "timeout"
    except requests.exceptions.ConnectionError:
        return None, None, "connection_error"
    except Exception as e:
        return None, None, f"error:{str(e)[:60]}"


# ── Worker ────────────────────────────────────────────────────────────────────
class Counter:
    def __init__(self):
        self._v = 0
        self._lock = threading.Lock()
        self.stale = 0
        self.ok = 0
        self.error = 0
    def inc(self) -> int:
        with self._lock:
            self._v += 1
            return self._v


def process_scheme(
    scheme: dict, counter: Counter, total: int
) -> tuple[str, str]:
    idx = counter.inc()
    url = scheme["apply_url"]

    new_hash, status, error_reason = scrape_hash(url)

    slug = scheme["slug"]

    if error_reason:
        mark_stale(scheme, error_reason, None, status)
        print(f"[{idx:4d}/{total}] STALE  {error_reason:20s}  {slug}", flush=True)
        with counter._lock: counter.stale += 1
        return slug, "STALE"

    old_hash = scheme.get("source_hash")

    if old_hash and new_hash and old_hash != new_hash:
        # Content changed
        mark_stale(scheme, "hash_changed", new_hash, status)
        print(f"[{idx:4d}/{total}] CHANGED  {status}  {slug}", flush=True)
        with counter._lock: counter.stale += 1
        return slug, "CHANGED"

    # Fresh — update hash if never set
    if new_hash:
        update_hash(scheme["id"], new_hash)
        if old_hash:
            clear_stale(scheme["id"])  # was stale, now resolved
    print(f"[{idx:4d}/{total}] OK     {status}  {slug}", flush=True)
    with counter._lock: counter.ok += 1
    return slug, "OK"


# ── Stats ─────────────────────────────────────────────────────────────────────
def print_stats():
    conn = db_conn()
    cur  = conn.cursor()
    cur.execute("""
        SELECT
            COUNT(*) FILTER (WHERE resolved = FALSE) unresolved,
            COUNT(*) FILTER (WHERE resolved = TRUE)  resolved,
            COUNT(*) FILTER (WHERE reason = 'hash_changed' AND resolved = FALSE) changed,
            COUNT(*) FILTER (WHERE reason = '404' AND resolved = FALSE)          dead_links,
            COUNT(*) FILTER (WHERE reason LIKE '5%%' AND resolved = FALSE)       server_errors,
            COUNT(*) FILTER (WHERE reason IN ('timeout','ssl_error','connection_error') AND resolved = FALSE) unreachable
        FROM stale_schemes
    """)
    r = cur.fetchone()
    print(f"\n── Stale queue ──────────────────")
    print(f"  Unresolved:    {r[0]}")
    print(f"  Resolved:      {r[1]}")
    print(f"  Changed:       {r[2]}")
    print(f"  Dead links:    {r[3]}")
    print(f"  Server errors: {r[4]}")
    print(f"  Unreachable:   {r[5]}")

    cur.execute("""
        SELECT slug, name, reason, http_status, checked_at
        FROM stale_schemes WHERE resolved = FALSE
        ORDER BY checked_at DESC LIMIT 10
    """)
    rows = cur.fetchall()
    if rows:
        print(f"\n── Most recent stale schemes ────")
        for row in rows:
            print(f"  {row[2]:20s}  {str(row[3] or ''):5s}  {row[0]}")
    cur.close(); conn.close()


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Check scheme URL freshness")
    ap.add_argument("--limit",   type=int,  default=None)
    ap.add_argument("--workers", type=int,  default=20)
    ap.add_argument("--slug",    default=None)
    ap.add_argument("--stats",   action="store_true", help="Print stats only")
    args = ap.parse_args()

    ensure_stale_table()

    if args.stats:
        print_stats()
        return

    schemes = load_schemes(args.slug, args.limit)
    total   = len(schemes)
    counter = Counter()

    print(f"Checking freshness of {total} scheme URLs  workers={args.workers}")
    t0 = time.time()

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(process_scheme, s, counter, total): s for s in schemes}
        for fut in as_completed(futs):
            fut.result()

    elapsed = time.time() - t0
    print(f"\n── Done ({elapsed:.0f}s) ────────────────────────")
    print(f"  OK:     {counter.ok}")
    print(f"  Stale:  {counter.stale}")
    print()
    print_stats()


if __name__ == "__main__":
    main()
