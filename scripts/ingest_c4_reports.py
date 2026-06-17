#!/usr/bin/env python3
"""
ingest_c4_reports.py — Ingest Code4rena and Sherlock contest findings into Chroma KB.

Sources:
  - Code4rena: public findings API (https://code4rena.com/reports)
  - Sherlock: public GitHub repo (github.com/sherlock-audit/audits)

Adds a `source` metadata field ("code4rena" or "sherlock") to each document,
allowing retriever.py to surface provenance to specialist agents.

Usage:
    python scripts/ingest_c4_reports.py                 # ingest both sources
    python scripts/ingest_c4_reports.py --source c4      # Code4rena only
    python scripts/ingest_c4_reports.py --source sherlock # Sherlock only
    python scripts/ingest_c4_reports.py --limit 200      # cap at 200 findings per source
    python scripts/ingest_c4_reports.py --dry-run        # show counts without writing

Environment:
    ANTHROPIC_API_KEY — optional, used to improve vuln_type classification
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Iterator

import requests
import chromadb
from sentence_transformers import SentenceTransformer

KB_DIR     = Path("kb")
CHROMA_DIR = KB_DIR / "chroma"

VALID_VULN_TYPES = [
    "reentrancy", "access-control", "arithmetic", "oracle-manipulation",
    "flash-loan", "logic-error", "gas-griefing", "dos", "signature-replay",
    "storage-collision", "proxy-upgrade", "front-running", "other",
]

KEYWORD_TO_VULN = {
    "reentran": "reentrancy",
    "reentr": "reentrancy",
    "access control": "access-control",
    "authorization": "access-control",
    "unauthorized": "access-control",
    "overflow": "arithmetic",
    "underflow": "arithmetic",
    "precision": "arithmetic",
    "rounding": "arithmetic",
    "oracle": "oracle-manipulation",
    "price manipulation": "oracle-manipulation",
    "flash loan": "flash-loan",
    "flashloan": "flash-loan",
    "flash-loan": "flash-loan",
    "sandwich": "flash-loan",
    "dos": "dos",
    "denial of service": "dos",
    "griefing": "gas-griefing",
    "signature": "signature-replay",
    "replay": "signature-replay",
    "storage collision": "storage-collision",
    "proxy": "proxy-upgrade",
    "upgrade": "proxy-upgrade",
    "front.run": "front-running",
    "mev": "front-running",
    "frontrun": "front-running",
}


def _classify_vuln_type(text: str) -> str:
    low = text.lower()
    for kw, vt in KEYWORD_TO_VULN.items():
        if kw in low:
            return vt
    return "other"


def _normalize_severity(raw: str) -> str:
    raw = raw.lower().strip()
    if raw in ("critical", "high", "medium", "low", "informational", "gas"):
        return raw.capitalize()
    if "critical" in raw:
        return "Critical"
    if "high" in raw:
        return "High"
    if "medium" in raw or "med" in raw:
        return "Medium"
    if "low" in raw:
        return "Low"
    return "Informational"


# ─────────────────────────────────────────────────────────────────────────────
# Code4rena ingestion
# ─────────────────────────────────────────────────────────────────────────────

C4_FINDINGS_URL = "https://code4rena.com/findings/json"

def _fetch_c4_findings(limit: int) -> Iterator[dict]:
    """
    Fetch findings from Code4rena's public JSON endpoint.
    Falls back to scraping report pages if the JSON endpoint is unavailable.
    """
    try:
        resp = requests.get(C4_FINDINGS_URL, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            for item in data[:limit]:
                yield _normalize_c4_item(item)
            return
    except Exception as e:
        print(f"  C4 JSON endpoint unavailable ({e}), trying report index …")

    # Fallback: parse the public reports index
    try:
        index_resp = requests.get("https://code4rena.com/reports", timeout=30)
        index_resp.raise_for_status()
        # Extract report slugs from href="/reports/<slug>"
        slugs = list(dict.fromkeys(re.findall(r'/reports/([\w-]+)', index_resp.text)))[:50]
        fetched = 0
        for slug in slugs:
            if fetched >= limit:
                break
            try:
                r = requests.get(f"https://code4rena.com/reports/{slug}.json", timeout=20)
                if r.status_code == 200:
                    report = r.json()
                    for finding in report.get("findings", [])[:20]:
                        if fetched >= limit:
                            break
                        yield _normalize_c4_item(finding, contest=slug)
                        fetched += 1
                time.sleep(1)
            except Exception:
                continue
    except Exception as e:
        print(f"  C4 fallback also failed: {e}")


def _normalize_c4_item(item: dict, contest: str = "") -> dict:
    title = item.get("title", item.get("name", ""))
    body = item.get("body", item.get("content", item.get("description", "")))
    severity = _normalize_severity(item.get("severity", item.get("risk", "Medium")))
    return {
        "title": title,
        "severity": severity,
        "vuln_type": _classify_vuln_type(f"{title} {body}"),
        "protocol": item.get("contest", contest),
        "audit_firm": "Code4rena",
        "source": "code4rena",
        "description": body[:1000] if body else "",
        "code_snippet": item.get("snippet", "")[:500],
        "fix": item.get("recommendation", "")[:400],
        "url": item.get("url", f"https://code4rena.com/reports/{contest}"),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Sherlock ingestion
# ─────────────────────────────────────────────────────────────────────────────

SHERLOCK_API = "https://api.github.com/repos/sherlock-audit/audits/contents"
SHERLOCK_RAW = "https://raw.githubusercontent.com/sherlock-audit/audits/main"


def _fetch_sherlock_findings(limit: int) -> Iterator[dict]:
    """Fetch Sherlock audit findings from their public GitHub repository."""
    try:
        headers = {"Accept": "application/vnd.github.v3+json"}
        gh_token = os.environ.get("GITHUB_TOKEN")
        if gh_token:
            headers["Authorization"] = f"token {gh_token}"

        resp = requests.get(SHERLOCK_API, headers=headers, timeout=30)
        resp.raise_for_status()
        contest_dirs = [
            item["name"] for item in resp.json()
            if item.get("type") == "dir" and not item["name"].startswith(".")
        ]
    except Exception as e:
        print(f"  Sherlock GitHub API failed: {e}")
        return

    fetched = 0
    for contest in contest_dirs[:30]:
        if fetched >= limit:
            break
        try:
            report_url = f"{SHERLOCK_RAW}/{contest}/report.md"
            r = requests.get(report_url, timeout=20)
            if r.status_code != 200:
                continue
            for finding in _parse_sherlock_report(r.text, contest):
                if fetched >= limit:
                    break
                yield finding
                fetched += 1
            time.sleep(0.5)
        except Exception:
            continue


def _parse_sherlock_report(markdown: str, contest: str) -> list[dict]:
    """Extract individual findings from a Sherlock markdown report."""
    findings = []
    # Match ## H-NNN or ## M-NNN heading blocks
    sections = re.split(r'\n(?=## [HML]-\d+)', markdown)
    for section in sections:
        match = re.match(r'## ([HML]-\d+)\s+\*\*([^*]+)\*\*', section)
        if not match:
            match = re.match(r'## ([HML]-\d+)\s+(.+)\n', section)
        if not match:
            continue
        finding_id = match.group(1)
        title = match.group(2).strip()
        severity_char = finding_id[0]
        severity = {"H": "High", "M": "Medium", "L": "Low"}.get(severity_char, "Medium")
        body = section[match.end():].strip()
        # Extract summary and recommendation
        summary_match = re.search(r'## Summary\n+(.*?)(?=\n## |\Z)', body, re.DOTALL)
        rec_match = re.search(r'## Recommendation\n+(.*?)(?=\n## |\Z)', body, re.DOTALL)
        summary = summary_match.group(1).strip()[:800] if summary_match else body[:800]
        recommendation = rec_match.group(1).strip()[:400] if rec_match else ""
        findings.append({
            "title": title,
            "severity": severity,
            "vuln_type": _classify_vuln_type(f"{title} {summary}"),
            "protocol": contest,
            "audit_firm": "Sherlock",
            "source": "sherlock",
            "description": summary,
            "code_snippet": "",
            "fix": recommendation,
            "url": f"https://github.com/sherlock-audit/audits/blob/main/{contest}/report.md",
        })
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# Chroma ingestion
# ─────────────────────────────────────────────────────────────────────────────

def _ingest_to_chroma(findings: list[dict], dry_run: bool) -> int:
    if dry_run:
        print(f"  [dry-run] Would ingest {len(findings)} finding(s)")
        return len(findings)

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    try:
        collection = client.get_collection("solodit_findings")
    except Exception:
        collection = client.create_collection(
            "solodit_findings",
            metadata={"hnsw:space": "cosine"},
        )

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    ingested = 0

    for i, f in enumerate(findings):
        doc_text = json.dumps({
            "description": f.get("description", ""),
            "code_snippet": f.get("code_snippet", ""),
            "fix": f.get("fix", ""),
            "title": f.get("title", ""),
        })
        embedding = model.encode([doc_text])[0].tolist()
        doc_id = f"{f['source']}_{f['protocol']}_{i}_{hash(f['title']) & 0xFFFFFF:06x}"
        meta = {
            "title":      f.get("title", "")[:200],
            "severity":   f.get("severity", ""),
            "vuln_type":  f.get("vuln_type", "other"),
            "protocol":   f.get("protocol", ""),
            "audit_firm": f.get("audit_firm", ""),
            "source":     f.get("source", ""),
            "url":        f.get("url", ""),
        }
        try:
            collection.upsert(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[doc_text],
                metadatas=[meta],
            )
            ingested += 1
        except Exception as e:
            print(f"  Warning: failed to ingest '{f['title'][:40]}': {e}")

    return ingested


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ingest Code4rena and Sherlock findings into the Chroma knowledge base"
    )
    parser.add_argument("--source", choices=["c4", "sherlock", "both"], default="both")
    parser.add_argument("--limit", type=int, default=500, help="Max findings per source")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("Knowledge Base Expansion — C4 + Sherlock Ingestion")
    total = 0

    if args.source in ("c4", "both"):
        print("\nFetching Code4rena findings …")
        c4_findings = list(_fetch_c4_findings(args.limit))
        print(f"  Fetched {len(c4_findings)} finding(s)")
        if c4_findings:
            n = _ingest_to_chroma(c4_findings, args.dry_run)
            print(f"  Ingested {n} finding(s) from Code4rena")
            total += n

    if args.source in ("sherlock", "both"):
        print("\nFetching Sherlock findings …")
        sherlock_findings = list(_fetch_sherlock_findings(args.limit))
        print(f"  Fetched {len(sherlock_findings)} finding(s)")
        if sherlock_findings:
            n = _ingest_to_chroma(sherlock_findings, args.dry_run)
            print(f"  Ingested {n} finding(s) from Sherlock")
            total += n

    print(f"\nTotal ingested: {total} finding(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
