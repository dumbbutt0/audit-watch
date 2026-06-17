#!/usr/bin/env python3
"""
generate_context_pack.py — Build output/context_pack.md for the active audit.

Produces the curated navigation index passed to every Step 2 agent.
Must run at the end of Step 1.5 (after defense_mapper.py).

Sections:
  1. Scope Summary          — protocol type, key contracts, entry points
  2. Top 20 Static Findings — severity × confidence ranked from tool outputs
  3. KB + Immunefi Crossref Gaps — Undefended/Partial patterns (written to kb_crossref.md)
  4. External Dependencies  — off-scope imports, version pins
  5. Compiler Warnings      — shadowing, unused returns, unreachable code
  6. Non-Issues (skip list) — paths confirmed safe; agents must not re-analyze

Usage:
    python scripts/generate_context_pack.py [--contract <path>]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path, get_audit_meta, load_env, write_session

load_env()

SOFT_WARN_LINES = 1200
RETRIEVER   = Path(__file__).resolve().parent / "retriever.py"
IMMUNEFI    = Path(__file__).resolve().parent.parent / "tools" / "immunefi_retriever.py"

# Protocol primitives → query terms for KB + Immunefi lookup
PRIMITIVE_QUERIES: list[tuple[str, str, str]] = [
    ("AMM",           "amm",              "constant product AMM price manipulation"),
    ("Lending",       "logic-error",      "lending protocol bad debt undercollateralized"),
    ("Bridge",        "cross-chain",      "bridge message replay cross-chain mint"),
    ("Staking",       "logic-error",      "staking reward calculation precision loss"),
    ("Oracle",        "oracle-manipulation", "oracle stale price manipulation twap"),
    ("ERC-4626",      "logic-error",      "ERC-4626 vault inflation first depositor"),
    ("Governance",    "flash-loan",       "governance flash loan vote snapshot"),
    ("Reentrancy",    "reentrancy",       "reentrancy CEI external call before state update"),
    ("Access Control","access-control",   "access control missing auth privilege escalation"),
    ("Arithmetic",    "arithmetic",       "integer overflow underflow precision loss"),
    ("Flash Loan",    "flash-loan",       "flash loan price manipulation donation attack"),
    ("Token",         "token-integration","fee on transfer rebasing token accounting"),
]

SEVERITY_RANK = {"Critical": 5, "High": 4, "Medium": 3, "Low": 2, "Info": 1, "Unknown": 0}
CONFIDENCE_RANK = {"Confirmed": 4, "High": 3, "Medium": 2, "Low": 1, "Speculative": 0}


def _run_retriever(cmd: list[str], timeout: int = 25) -> list[dict]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return json.loads(r.stdout or "[]")
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        return []


def _build_scope_summary(static: dict, meta: dict) -> list[str]:
    lines = ["## Scope Summary", ""]
    name = meta.get("name", meta.get("audit_id", "Unknown"))
    lang = meta.get("language", "Solidity")
    lines.append(f"**Protocol:** {name}  **Language:** {lang}")
    lines.append("")

    funcs = static.get("functions", [])
    external_funcs = [f for f in funcs if f.get("visibility") in ("external", "public")]
    lines.append(f"**Entry points ({len(external_funcs)}):**")
    for fn in external_funcs[:15]:
        sig = fn.get("signature") or fn.get("name", "?")
        contract = fn.get("contract", "")
        lines.append(f"  - `{contract}.{sig}`" if contract else f"  - `{sig}`")
    if len(external_funcs) > 15:
        lines.append(f"  - … and {len(external_funcs) - 15} more")

    lines.append("")
    flags = []
    if static.get("is_erc4626"):
        flags.append("ERC-4626 vault")
    if static.get("has_transient_storage"):
        flags.append("transient storage (TSTORE/TLOAD)")
    if static.get("is_proxy"):
        flags.append("proxy/upgradeable")
    if flags:
        lines.append(f"**Detected:** {', '.join(flags)}")
        lines.append("")
    return lines


def _finding_severity(f: dict) -> str:
    """Slither findings carry `impact`; mythril/others carry `severity`."""
    return f.get("severity") or f.get("impact") or "?"


def _finding_file(f: dict) -> str:
    loc = f.get("file") or f.get("source_file") or f.get("location", {}).get("file", "")
    if loc:
        return loc
    m = re.search(r'(contracts/[^\s#)]+\.sol)', f.get("description", ""))
    return m.group(1) if m else ""


def _build_static_findings(static: dict) -> list[str]:
    lines = ["## Top 20 Static Findings", ""]
    raw: list[dict] = static.get("mythril_issues", []) + static.get("slither_findings", [])
    if not raw:
        lines += ["*(no static findings)*", ""]
        return lines

    def score(f: dict) -> int:
        s = SEVERITY_RANK.get(_finding_severity(f), 0)
        c = CONFIDENCE_RANK.get(f.get("confidence", ""), 0)
        return s * 10 + c

    ranked = sorted(raw, key=score, reverse=True)[:20]
    lines.append("| Severity | Confidence | File | Description |")
    lines.append("|---|---|---|---|")
    for f in ranked:
        sev  = _finding_severity(f)
        conf = f.get("confidence", "?")
        loc  = _finding_file(f)
        desc = (f.get("description") or f.get("check", ""))[:80].replace("\n", " ")
        lines.append(f"| {sev} | {conf} | {loc} | {desc} |")
    lines.append("")
    return lines


def _build_priority_clusters(static: dict) -> list[str]:
    """Rank in-scope directories by externally-reachable tainted sinks, then severity.

    Tainted sinks are the strongest pre-filter for attacker reachability, so they dominate
    the ordering. Steers specialist agents at the hotspot instead of the whole tree.
    """
    findings = static.get("slither_findings", [])
    sinks = static.get("tainted_sinks", [])

    # Value-at-risk (VaR) keywords: the price/oracle/AMM/POL machinery where loss-of-funds concentrates.
    # A cluster matching these is ranked at the top EVEN WITH ZERO static sinks (recall-lab coverage fix:
    # oracle/AMM/POL subsystems are frequently sink-free in static analysis yet hold most Highs).
    VAR_KEYWORDS = ("oracle", "price", "twap", "amm", "swap", "liquidity", "pool", "pol", "buyback",
                    "buyandburn", "slipstream", "balancer", "uniswap", "tick", "slippage", "rebalance",
                    "dex", "curve", "vault")

    def _is_var(path: str) -> bool:
        return any(k in (path or "").lower() for k in VAR_KEYWORDS)

    # cluster key = parent directory of the source file
    clusters: dict[str, dict] = {}

    def _bucket(path: str) -> str:
        if not path:
            return "(unknown)"
        p = path.split("#")[0]
        parent = "/".join(p.split("/")[:-1])
        return parent or p

    def _get(path: str) -> dict:
        c = clusters.setdefault(_bucket(path), {"High": 0, "Medium": 0, "Low": 0, "sinks": 0, "var": 0, "files": set()})
        if path:
            fn = path.split("/")[-1].split("#")[0]
            c["files"].add(fn)
            # VaR if the directory OR any file name signals price/oracle/AMM/POL machinery
            if _is_var(path):
                c["var"] = 1
        return c

    for f in findings:
        path = _finding_file(f)
        c = _get(path)
        sev = _finding_severity(f)
        if sev in c:
            c[sev] += 1

    for s in sinks:
        path = s.get("source_file") or _finding_file(s)
        c = _get(path)
        c["sinks"] += 1

    if not clusters:
        return []

    # VaR is the PRIMARY ranking signal (price/oracle/AMM/POL first), then sinks, then severity.
    ranked = sorted(
        clusters.items(),
        key=lambda kv: (kv[1]["var"], kv[1]["sinks"], kv[1]["High"], kv[1]["Medium"]),
        reverse=True,
    )
    hot = [(k, v) for k, v in ranked if v["var"] or v["sinks"] or v["High"] or v["Medium"]]
    cleared = [k for k, v in ranked if not (v["var"] or v["sinks"] or v["High"] or v["Medium"])]

    lines = [
        "## Priority Investigation Clusters",
        "",
        "> Ranked by **VaR** (value-at-risk: price/oracle/AMM/POL machinery), then externally-reachable "
        "tainted **sinks**, then static-analysis severity. **VaR★ clusters come first — investigate them "
        "FIRST even if they have zero sinks**: oracle manipulation, swap slippage, and protocol-owned-"
        "liquidity / buyback accounting are recurring Critical/High classes that static analysis often "
        "misses. This ordering controls DEPTH/ORDER, **not whether a cluster is examined**: every in-scope "
        "cluster below is examined before the review gate can pass. No-signal clusters get a lighter "
        "pass or the mandatory coverage sweep — they are not skipped.",
        "",
        "| Cluster (dir) | VaR | High | Med | Sinks | Representative files |",
        "|---|---|---|---|---|---|",
    ]
    for dirpath, c in hot[:8]:
        files = ", ".join(sorted(c["files"])[:4])
        if len(c["files"]) > 4:
            files += f", +{len(c['files']) - 4}"
        lines.append(f"| `{dirpath}` | {'★' if c['var'] else ''} | {c['High']} | {c['Medium']} | {c['sinks']} | {files} |")
    lines.append("")
    # Every in-scope cluster must be examined. Surface ALL remaining (non-hot) clusters explicitly as the
    # mandatory-sweep set — never drop necessary files to a one-line footnote (they would otherwise be skipped).
    if cleared:
        lines.append("### Remaining in-scope — mandatory sweep")
        lines.append("")
        lines.append(
            "> No High/Med/sink signal, so lower DEPTH priority — but still in scope and **must be examined** "
            "(by a specialist if it touches your specialty, otherwise by the `/coverage-sweep` mandatory pass). "
            "The coverage gate fail-closes until every item here has an evidence-anchored disposition."
        )
        lines.append("")
        lines.append("| Cluster (dir) | Representative files |")
        lines.append("|---|---|")
        for dirpath in cleared:
            c = clusters[dirpath]
            files = ", ".join(sorted(c["files"])[:4])
            if len(c["files"]) > 4:
                files += f", +{len(c['files']) - 4}"
            lines.append(f"| `{dirpath}` | {files} |")
        lines.append("")
    return lines


def _build_crossref(
    primitives_in_scope: list[str],
    static_findings: list[dict],
    defense_map_path: Path,
) -> tuple[list[str], list[str]]:
    """Query KB + Immunefi for each primitive; return (crossref_md_lines, gap_lines)."""
    crossref_rows: list[str] = []
    gap_rows: list[str] = []

    defense_map: dict[str, str] = {}
    if defense_map_path.exists():
        try:
            dm = json.loads(defense_map_path.read_text())
            entries = dm if isinstance(dm, list) else dm.get("entries", [])
            for e in entries:
                defense_map[e.get("function", "")] = e.get("coverage", "Unknown")
        except (json.JSONDecodeError, OSError):
            pass

    for primitive, vuln_type, query in PRIMITIVE_QUERIES:
        if primitives_in_scope and not any(
            p.lower() in primitive.lower() for p in primitives_in_scope
        ):
            continue

        primitive_findings = [
            f for f in static_findings
            if primitive.lower() in f.get("check", "").lower()
            or primitive.lower() in f.get("description", "").lower()
        ]

        if not primitive_findings:
            defense_status = "Unknown"
        elif all(
            defense_map.get(f.get("function", ""), "") == "full"
            for f in primitive_findings
        ):
            defense_status = "Defended"
        elif any(
            defense_map.get(f.get("function", ""), "") == "full"
            for f in primitive_findings
        ):
            defense_status = "Partial"
        else:
            defense_status = "Undefended"

        kb_hits = _run_retriever(["python", str(RETRIEVER), vuln_type, query, "--top-k", "3"])
        immunefi_hits = _run_retriever(
            ["python", str(IMMUNEFI), vuln_type, query, "--top-k", "3"]
        )

        for hit in kb_hits:
            title = hit.get("title", "")[:60]
            row = f"| {primitive} | KB/Solodit | — | {defense_status} | {title} |"
            crossref_rows.append(row)
            if defense_status != "Defended":
                gap_rows.append(row)

        for hit in immunefi_hits:
            title = hit.get("title", "")[:60]
            row = f"| {primitive} | Immunefi | — | {defense_status} | {title} |"
            crossref_rows.append(row)
            if defense_status != "Defended":
                gap_rows.append(row)

    return crossref_rows, gap_rows


def _build_external_deps(static: dict) -> list[str]:
    lines = ["## External Dependencies", ""]
    ext_calls = static.get("external_calls", []) or []
    seen: set[str] = set()
    for call in ext_calls:
        target = call.get("target") or call.get("contract", "")
        if target and target not in seen:
            seen.add(target)
            lines.append(f"  - `{target}`")
    if not seen:
        lines.append("  *(none detected)*")
    lines.append("")
    return lines


def _build_compiler_warnings(static: dict) -> list[str]:
    lines = ["## Compiler Warnings", ""]
    warnings = static.get("compiler_warnings", [])
    if not warnings:
        lines += ["*(none)*", ""]
        return lines
    for w in warnings[:20]:
        msg = w if isinstance(w, str) else w.get("message", str(w))
        lines.append(f"  - {msg[:120]}")
    lines.append("")
    return lines


def _build_skip_list(defense_map_path: Path) -> list[str]:
    lines = ["## Non-Issues (skip list — agents must NOT re-analyze)", ""]
    if not defense_map_path.exists():
        lines += ["*(defense_map.json not found — run defense_mapper.py first)*", ""]
        return lines
    try:
        dm = json.loads(defense_map_path.read_text())
    except (json.JSONDecodeError, OSError):
        lines += ["*(could not parse defense_map.json)*", ""]
        return lines

    safe: list[dict] = [
        e for e in (dm if isinstance(dm, list) else dm.get("entries", []))
        if e.get("coverage") == "full" and not e.get("evasion_path")
    ]
    for e in safe[:20]:
        fn  = e.get("function", "?")
        loc = e.get("file", "")
        lines.append(f"  - `{fn}` `{loc}`")
    if not safe:
        lines.append("  *(no fully-guarded paths identified)*")
    lines.append("")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate context_pack.md for active audit")
    parser.add_argument("--contract", help="Contract path (informational only)")
    args = parser.parse_args()

    meta = get_audit_meta()

    static_path = audit_path("output", "static.json")
    if not static_path.exists():
        print(f"[error] output/static.json not found at {static_path}")
        print("Run: python tools/static_analysis.py <contract_path>")
        sys.exit(1)

    static = json.loads(static_path.read_text())
    defense_map_path = audit_path("output", "defense_map.json")

    primitives_in_scope: list[str] = []
    if static.get("is_erc4626"):
        primitives_in_scope.append("ERC-4626")
    if static.get("is_proxy"):
        primitives_in_scope.append("Governance")

    # Build all sections
    sections: list[str] = []
    sections += [
        "# Context Pack",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Audit: {meta.get('audit_id', 'unknown')}  |  Target: {meta.get('name', args.contract or '?')}",
        "",
        "> Navigation index — table format only. Every line is a file:line pointer; agents fetch depth on demand.",
        "",
        "---",
        "",
    ]
    sections += _build_scope_summary(static, meta)
    sections += ["---", ""]
    cluster_lines = _build_priority_clusters(static)
    if cluster_lines:
        sections += cluster_lines
        sections += ["---", ""]
    sections += _build_static_findings(static)
    sections += ["---", ""]

    # KB + Immunefi crossref
    print("Querying KB and Immunefi MCP for known vulnerability patterns…", flush=True)
    static_findings = (
        static.get("mythril_issues", []) +
        static.get("slither_findings", []) +
        static.get("tainted_sinks", []) +
        static.get("delegatecall_risks", [])
    )
    crossref_rows, gap_rows = _build_crossref(primitives_in_scope, static_findings, defense_map_path)

    kb_crossref_path = audit_path("output", "kb_crossref.md")
    kb_lines = [
        "# KB + Immunefi Crossref",
        "",
        "| Pattern | Source | File(s) in Scope | Defense Status | Notes |",
        "|---|---|---|---|---|",
    ] + crossref_rows
    kb_crossref_path.write_text("\n".join(kb_lines))
    print(f"  Written: {kb_crossref_path}")

    sections += ["## KB + Immunefi Crossref Gaps", ""]
    if gap_rows:
        sections += [
            "| Pattern | Source | File(s) | Defense Status | Notes |",
            "|---|---|---|---|---|",
        ] + gap_rows
    else:
        sections += ["*(no gaps found — all known patterns defended)*"]
    sections += ["", "---", ""]

    sections += _build_external_deps(static)
    sections += ["---", ""]
    sections += _build_compiler_warnings(static)
    sections += ["---", ""]
    sections += _build_skip_list(defense_map_path)

    out_path = audit_path("output", "context_pack.md")
    out_path.write_text("\n".join(sections))
    write_session({"active_step": "1.5-context-pack"})
    if len(sections) > SOFT_WARN_LINES:
        print(f"[warn] context_pack.md is {len(sections)} lines — review section builders for prose creep.")
    print(f"context_pack.md written ({len(sections)} lines): {out_path}")


if __name__ == "__main__":
    main()
