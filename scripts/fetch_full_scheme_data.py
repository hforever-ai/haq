#!/usr/bin/env python3
"""
Fetch ALL available data from MyScheme API for every scheme.
Pulls: main details + documents + FAQs.
Resumable via checkpoint at /tmp/haq_full_checkpoint.json.
Incremental DB writes every 50 schemes (so crashes don't lose progress).

Two-step per scheme:
  GET ?slug={slug}&lang=en  →  _id + all content fields
  GET /{_id}/documents      →  documentsRequired_md
  GET /{_id}/faqs           →  faqs list
"""

import json
import re
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

import psycopg2

API_BASE = "https://api.myscheme.gov.in/schemes/v6/public/schemes"
API_KEY = "tYTy5eEhlu9rFjyxuCr7ra7ACp4dv1RH8gWuHTDc"
CHECKPOINT = Path("/tmp/haq_full_checkpoint.json")
DELAY = 0.2  # seconds between each API call
CHECKPOINT_EVERY = 20
DB_FLUSH_EVERY = 50


HEADERS = {
    "x-api-key": API_KEY,
    "accept": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
}


def api_get(url: str, retries: int = 3) -> dict | None:
    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                raw = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", raw)
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 20 * (attempt + 1)
                print(f"\n  Rate limited — sleeping {wait}s", flush=True)
                time.sleep(wait)
            elif e.code == 404:
                return {"statusCode": 404}
            else:
                print(f"\n  HTTP {e.code} for {url}", flush=True)
                return None
        except Exception as exc:
            print(f"\n  Err attempt {attempt+1}: {exc}", flush=True)
            time.sleep(3)
    return None


def clean_md(text: str) -> str:
    if not text:
        return ""
    text = text.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    text = re.sub(r"&amp;amp;", "&", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&quot;", '"', text)
    text = re.sub(r"&#39;", "'", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_scheme_data(slug: str) -> dict | None:
    """Returns a dict with all fields or None on failure."""
    d = api_get(f"{API_BASE}?slug={slug}&lang=en")
    if not d or d.get("statusCode") != 200:
        return None

    raw = d.get("data") or {}
    if not raw:
        return None
    scheme_id = raw.get("_id", "")
    en = raw.get("en") or {}

    bd = en.get("basicDetails", {}) or {}
    sc = en.get("schemeContent", {}) or {}
    ec = en.get("eligibilityCriteria", {}) or {}
    ap = en.get("applicationProcess", []) or []

    ap_md = _extract_application_process_md(ap)

    time.sleep(DELAY)

    docs_md = ""
    if scheme_id:
        docs_d = api_get(f"{API_BASE}/{scheme_id}/documents?lang=en")
        if docs_d and docs_d.get("statusCode") == 200:
            docs_en = (docs_d.get("data") or {}).get("en") or {}
            docs_md = clean_md(docs_en.get("documentsRequired_md", ""))
        time.sleep(DELAY)

    faqs = []
    if scheme_id:
        faqs_d = api_get(f"{API_BASE}/{scheme_id}/faqs?lang=en")
        if faqs_d and faqs_d.get("statusCode") == 200:
            raw_faqs = ((faqs_d.get("data") or {}).get("en") or {}).get("faqs", []) or []
            faqs = [
                {"q": f.get("question", "").strip(), "a": clean_md(f.get("answer_md", ""))}
                for f in raw_faqs
                if f.get("question")
            ]
        time.sleep(DELAY)

    impl_agency = ""
    if isinstance(bd.get("implementingAgency"), str):
        impl_agency = bd["implementingAgency"].strip()

    dept = bd.get("nodalDepartmentName", {})
    nodal_dept = dept.get("label", "").strip() if isinstance(dept, dict) else ""

    # Use nodal_dept as fallback for implementing_agency
    if not impl_agency and nodal_dept:
        impl_agency = nodal_dept

    bt = sc.get("benefitTypes", {})
    benefit_type = bt.get("label", "").strip() if isinstance(bt, dict) else ""

    refs = sc.get("references", []) or []
    clean_refs = [
        {"title": r.get("title", ""), "url": r.get("url", "")}
        for r in refs
        if isinstance(r, dict) and r.get("url")
    ]

    return {
        "myscheme_id": scheme_id,
        "detailed_description_md": clean_md(sc.get("detailedDescription_md", "")),
        "benefits_md": clean_md(sc.get("benefits_md", "")),
        "eligibility_md": clean_md(ec.get("eligibilityDescription_md", "")),
        "exclusions_md": clean_md(sc.get("exclusions_md", "")),
        "application_process_md": ap_md,
        "implementing_agency": impl_agency,
        "nodal_department": nodal_dept,
        "is_dbt": bool(bd.get("dbtScheme", False)),
        "benefit_type": benefit_type,
        "scheme_image_url": sc.get("schemeImageUrl", "") or "",
        "references_json": clean_refs,
        "faqs": faqs,
        "documents_required_md": docs_md,
    }


def _extract_application_process_md(ap_list: list) -> str:
    if not ap_list:
        return ""
    lines = []
    for mode_obj in ap_list:
        if not isinstance(mode_obj, dict):
            continue
        mode = mode_obj.get("mode", "")
        url = mode_obj.get("url", "")
        if mode:
            lines.append(f"**Mode: {mode}**")
        if url:
            lines.append(f"Apply URL: {url}")
        for node in mode_obj.get("process", []) or []:
            lines.extend(_walk_node(node))
    return "\n".join(lines).strip()


def _walk_node(node) -> list[str]:
    if not isinstance(node, dict):
        return []
    ntype = node.get("type", "")
    children = node.get("children", []) or []

    if ntype == "paragraph":
        texts = [c.get("text", "") for c in children if isinstance(c, dict)]
        line = "".join(texts).strip()
        return [line] if line else []
    elif ntype in ("ul_list", "ol_list"):
        result = []
        for child in children:
            result.extend(_walk_node(child))
        return result
    elif ntype == "list_item":
        texts = []
        for c in children:
            if isinstance(c, dict):
                if c.get("text"):
                    texts.append(c["text"])
                else:
                    texts.extend(_walk_node(c))
        line = "- " + " ".join(texts).strip()
        return [line] if line.strip() != "-" else []
    elif ntype in ("align_justify", "align_left", "align_center", "align_right"):
        result = []
        for c in children:
            result.extend(_walk_node(c))
        return result
    elif node.get("text"):
        t = node["text"].strip()
        return [t] if t else []
    else:
        result = []
        for c in children:
            result.extend(_walk_node(c))
        return result


def flush_to_db(batch: dict[str, dict]) -> int:
    """Write a batch of scheme data to DB. Returns count updated."""
    if not batch:
        return 0
    now = datetime.now(timezone.utc)
    conn = psycopg2.connect(dbname="aarambha_haq")
    cur = conn.cursor()
    updated = 0
    for slug, data in batch.items():
        if not isinstance(data, dict):
            continue
        cur.execute(
            """
            UPDATE schemes SET
              myscheme_id             = COALESCE(NULLIF(%s,''), myscheme_id),
              detailed_description_md = COALESCE(NULLIF(%s,''), detailed_description_md),
              benefits_md             = COALESCE(NULLIF(%s,''), benefits_md),
              eligibility_md          = COALESCE(NULLIF(%s,''), eligibility_md),
              exclusions_md           = COALESCE(NULLIF(%s,''), exclusions_md),
              application_process_md  = COALESCE(NULLIF(%s,''), application_process_md),
              implementing_agency     = COALESCE(NULLIF(%s,''), implementing_agency),
              nodal_department        = COALESCE(NULLIF(%s,''), nodal_department),
              is_dbt                  = %s,
              benefit_type            = COALESCE(NULLIF(%s,''), benefit_type),
              scheme_image_url        = COALESCE(NULLIF(%s,''), scheme_image_url),
              references_json         = %s::jsonb,
              faqs                    = %s::jsonb,
              documents_required_md   = COALESCE(NULLIF(%s,''), documents_required_md),
              scraped_at              = %s
            WHERE slug = %s
            """,
            (
                data["myscheme_id"],
                data["detailed_description_md"],
                data["benefits_md"],
                data["eligibility_md"],
                data["exclusions_md"],
                data["application_process_md"],
                data["implementing_agency"],
                data["nodal_department"],
                data["is_dbt"],
                data["benefit_type"],
                data["scheme_image_url"],
                json.dumps(data["references_json"], ensure_ascii=False),
                json.dumps(data["faqs"], ensure_ascii=False),
                data["documents_required_md"],
                now,
                slug,
            ),
        )
        updated += 1
    conn.commit()
    cur.close()
    conn.close()
    return updated


def main():
    checkpoint: dict[str, dict | str] = {}
    if CHECKPOINT.exists():
        checkpoint = json.loads(CHECKPOINT.read_text())
        done = sum(1 for v in checkpoint.values() if v != "SKIP")
        skip = sum(1 for v in checkpoint.values() if v == "SKIP")
        print(f"Checkpoint loaded: {done} fetched, {skip} skipped")

    conn = psycopg2.connect(dbname="aarambha_haq")
    cur = conn.cursor()
    cur.execute("SELECT slug FROM schemes ORDER BY id")
    slugs = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    total = len(slugs)
    print(f"Total schemes: {total}")

    pending = [s for s in slugs if s not in checkpoint]
    print(f"Pending: {len(pending)}")

    db_pending: dict[str, dict] = {}

    for i, slug in enumerate(pending, 1):
        print(f"[{i}/{len(pending)}] {slug}", end=" ", flush=True)
        data = extract_scheme_data(slug)
        if data:
            checkpoint[slug] = data
            db_pending[slug] = data
            parts = []
            if data.get("detailed_description_md"):
                parts.append("desc")
            if data.get("documents_required_md"):
                parts.append("docs")
            if data.get("faqs"):
                parts.append(f"faq:{len(data['faqs'])}")
            if data.get("benefits_md"):
                parts.append("ben")
            print("OK [" + " ".join(parts) + "]", flush=True)
        else:
            checkpoint[slug] = "SKIP"
            print("SKIP", flush=True)

        # Save checkpoint
        if i % CHECKPOINT_EVERY == 0:
            CHECKPOINT.write_text(json.dumps(checkpoint, ensure_ascii=False))

        # Flush to DB
        if len(db_pending) >= DB_FLUSH_EVERY:
            n = flush_to_db(db_pending)
            print(f"  [DB flushed: {n} schemes | total done: {i}]", flush=True)
            db_pending = {}

    # Final flush
    CHECKPOINT.write_text(json.dumps(checkpoint, ensure_ascii=False))
    if db_pending:
        n = flush_to_db(db_pending)
        print(f"  [Final DB flush: {n} schemes]")

    print("\nDone.")

    # Stats
    has = {k: 0 for k in ["detailed_description_md", "documents_required_md", "faqs", "benefits_md", "eligibility_md"]}
    for v in checkpoint.values():
        if not isinstance(v, dict):
            continue
        for k in has:
            val = v.get(k)
            if val and (len(val) > 0 if isinstance(val, (str, list)) else True):
                has[k] += 1

    print("\nCoverage:")
    for k, v in has.items():
        print(f"  {k}: {v}/{total}")


if __name__ == "__main__":
    main()
