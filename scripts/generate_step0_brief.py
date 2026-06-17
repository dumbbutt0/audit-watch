#!/usr/bin/env python3
"""
generate_step0_brief.py — Ranked human-readable Step 0 summary.

Reads data/threads/promising_threads.jsonl (and medium_suspicion.json if present),
then writes output/step0_brief.md with:
  - Threads ranked by suspicion_score × severity
  - Grouped by affected function (heatmap)
  - Domain pattern alerts (oracle, DEX/AMM, flash-loan, cross-chain)
  - Watch-list section for soft-flagged score-3 threads

This replaces the raw JSONL as the human review artifact that a human should
read before Step 1 static analysis begins.

Usage:
    python scripts/generate_step0_brief.py
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path, get_audit_meta

ROOT           = Path(__file__).resolve().parent.parent
THREADS_DIR    = audit_path("data/threads")
INVARIANTS_DIR = audit_path("data/invariants")
OUTPUT_DIR     = audit_path("output")
OUT_FILE       = OUTPUT_DIR / "step0_brief.md"

VERDICT_SEVERITY = {
    "CRITICAL_THREAD": "Critical", "HIGH_THREAD": "High", "MEDIUM_THREAD": "Medium",
    "CRITICAL_BACKWARD": "Critical", "HIGH_BACKWARD": "High", "MEDIUM_BACKWARD": "Medium",
    "CRITICAL_MULTITX": "Critical", "HIGH_MULTITX": "High", "MEDIUM_MULTITX": "Medium",
    "NEEDS_MORE_CONTEXT": "Unknown",
}

SEVERITY_ORDER = {"Critical": 4, "High": 3, "Medium": 2, "Unknown": 1}

SCORE_EMOJI = {5: "🔴", 4: "🟠", 3: "🟡", 2: "⚪", 1: "⚪"}

DOMAIN_PATTERNS: dict[str, list[str]] = {
    "Oracle / Price": [
        "latestrounddata", "slot0", "getprice", "oracle", "twap",
        "pricefeed", "chainlink", "priceoracle", "gettwap", "observe",
        "consult", "sqrt", "sqrtpricex96",
    ],
    "DEX / AMM": [
        "swap", "getreserves", "reserve0", "reserve1", "liquidity",
        "amm", "uniswap", "curve", "balancer", "sushiswap",
        "addliquidity", "removeliquidity", "mint", "burn",
    ],
    "Flash Loan": [
        "flashloan", "ierc3156", "flashborrow", "flash_loan", "erc3156",
        "flashswap", "oncredit",
    ],
    "Cross-Chain": [
        "bridge", "relayer", "nonce", "messagehash", "rollup",
        "crosschain", "l2", "layer2", "wormhole", "layerzero",
    ],
}

_FN_RE = re.compile(r"\b([a-zA-Z_]\w*)\s*\(")


def _load_jsonl(path: Path) -> list[dict]:
    out = []
    try:
        for line in path.read_text().splitlines():
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        pass
    return out


def _load_json(path: Path):
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _thread_text(thread: dict) -> str:
    parts = [
        thread.get("title", "") or "",
        thread.get("description", "") or "",
        " ".join(thread.get("hop_trace", []) if isinstance(thread.get("hop_trace"), list) else []),
        " ".join(thread.get("violation_path", []) if isinstance(thread.get("violation_path"), list) else []),
    ]
    return " ".join(parts).lower()


def _detect_domains(thread: dict) -> list[str]:
    text = _thread_text(thread)
    found = []
    for label, keywords in DOMAIN_PATTERNS.items():
        if any(kw in text for kw in keywords):
            # Find which keywords matched for display
            hits = [kw for kw in keywords if kw in text][:3]
            found.append((label, hits))
    return found  # list of (label, matched_keywords)


def _thread_functions(thread: dict) -> list[str]:
    fns: list[str] = []
    seen: set[str] = set()
    for hop in thread.get("hop_traces", []):
        fn = hop.get("function", "")
        if fn and fn not in seen:
            fns.append(fn.split(".")[-1])
            seen.add(fn)
    for step in thread.get("hop_trace", []):
        if isinstance(step, str):
            for m in _FN_RE.findall(step):
                if m not in seen and len(m) > 2:
                    fns.append(m)
                    seen.add(m)
    for step in thread.get("violation_path", []):
        if isinstance(step, str):
            for m in _FN_RE.findall(step):
                if m not in seen and len(m) > 2:
                    fns.append(m)
                    seen.add(m)
    return fns[:5]  # cap to keep brief readable


def _sort_key(thread: dict) -> tuple:
    score = thread.get("suspicion_score", 0)
    verdict = thread.get("verdict", "")
    sev_rank = SEVERITY_ORDER.get(VERDICT_SEVERITY.get(verdict, "Unknown"), 0)
    return (-score, -sev_rank)


def _escalation_angles(thread: dict) -> list[str]:
    return thread.get("escalation_angles", [])[:3]


# ─────────────────────────────────────────────────────────────────────────────
# Markdown generation
# ─────────────────────────────────────────────────────────────────────────────

def generate(threads: list[dict], soft_threads: list[dict], audit_id: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines: list[str] = []

    # ── Header ──────────────────────────────────────────────────────────────
    lines += [
        f"# Step 0 Analysis Brief — {audit_id}",
        f"Generated: {now}",
        "",
    ]

    # ── Summary counts ───────────────────────────────────────────────────────
    by_sev: dict[str, int] = defaultdict(int)
    for t in threads:
        v = t.get("verdict", "")
        s = VERDICT_SEVERITY.get(v, "Unknown")
        by_sev[s] += 1

    needs_ctx = sum(1 for t in threads if t.get("verdict") == "NEEDS_MORE_CONTEXT")
    escalated  = sum(1 for t in threads if t.get("escalate") and not t.get("soft_flag"))

    lines += [
        "## Summary",
        (
            f"Total threads: {len(threads)}  "
            f"(Critical: {by_sev['Critical']} · "
            f"High: {by_sev['High']} · "
            f"Medium: {by_sev['Medium']} · "
            f"NEEDS_MORE_CONTEXT: {needs_ctx})"
        ),
        f"Threads escalated to findings: {escalated}",
        f"Soft-flag threads (score=3 watch list): {len(soft_threads)}",
        "",
    ]

    # ── Priority ranking ─────────────────────────────────────────────────────
    lines.append("## Priority Thread Ranking")
    lines.append("")

    active = [t for t in threads if t.get("verdict") != "NEEDS_MORE_CONTEXT"
              and not t.get("soft_flag")]
    active.sort(key=_sort_key)

    current_score = None
    for thread in active:
        score = thread.get("suspicion_score", 0)
        verdict = thread.get("verdict", "")
        sev = VERDICT_SEVERITY.get(verdict, verdict)
        tid = thread.get("thread_id", "?")
        title = thread.get("title", "(no title)")
        emoji = SCORE_EMOJI.get(score, "⚪")

        if score != current_score:
            current_score = score
            lines.append(f"### {emoji} Score {score}")
            lines.append("")

        lines.append(f"#### [{tid}] {title}  `{verdict}`")

        inv_id = thread.get("invariant_id", "")
        chain_id = thread.get("chain_id", "")
        if inv_id or chain_id:
            lines.append(f"- **Invariant**: {inv_id}  · **Chain**: {chain_id}")

        fns = _thread_functions(thread)
        if fns:
            fn_str = ", ".join(f"`{f}()`" for f in fns)
            lines.append(f"- **Functions**: {fn_str}")

        entry = thread.get("entry_conditions", "")
        if entry:
            lines.append(f"- **Entry conditions**: {entry}")

        domains = _detect_domains(thread)
        for label, kws in domains:
            lines.append(f"- ⚠️ **Domain flag**: {label} — keywords: {', '.join(kws)}")

        angles = _escalation_angles(thread)
        if angles:
            lines.append(f"- **Escalation angles**: {angles[0]}")
            for angle in angles[1:]:
                lines.append(f"  - {angle}")

        lines.append("")

    # ── NEEDS_MORE_CONTEXT section ───────────────────────────────────────────
    ctx_threads = [t for t in threads if t.get("verdict") == "NEEDS_MORE_CONTEXT"]
    if ctx_threads:
        lines += ["## NEEDS_MORE_CONTEXT (Requires Domain Knowledge)", ""]
        for t in ctx_threads:
            tid = t.get("thread_id", "?")
            title = t.get("title", "(no title)")
            inv_id = t.get("invariant_id", "")
            domains = _detect_domains(t)
            dom_str = ", ".join(label for label, _ in domains)
            lines.append(f"- **[{tid}]** {title}")
            if inv_id:
                lines.append(f"  - Invariant: {inv_id}")
            if dom_str:
                lines.append(f"  - Domain flags: {dom_str}")
        lines.append("")

    # ── Function heatmap ─────────────────────────────────────────────────────
    fn_threads: dict[str, list[dict]] = defaultdict(list)
    for t in threads:
        for fn in _thread_functions(t):
            fn_threads[fn].append(t)

    if fn_threads:
        lines += ["## Function Heatmap", ""]
        lines.append("| Function | Threads | Max severity | Domain flags |")
        lines.append("|----------|---------|--------------|--------------|")
        fn_rows = sorted(fn_threads.items(), key=lambda kv: -len(kv[1]))
        for fn, fn_t_list in fn_rows[:20]:
            max_sev = max(
                (SEVERITY_ORDER.get(VERDICT_SEVERITY.get(t.get("verdict", ""), "Unknown"), 0)
                 for t in fn_t_list),
                default=0,
            )
            sev_label = {4: "Critical", 3: "High", 2: "Medium", 1: "Unknown"}.get(max_sev, "-")
            doms: set[str] = set()
            for t in fn_t_list:
                for label, _ in _detect_domains(t):
                    doms.add(label)
            dom_str = ", ".join(sorted(doms)) or "-"
            lines.append(f"| `{fn}()` | {len(fn_t_list)} | {sev_label} | {dom_str} |")
        lines.append("")

    # ── Domain pattern alerts ─────────────────────────────────────────────────
    domain_threads: dict[str, list[tuple[str, list[str]]]] = defaultdict(list)
    for t in threads:
        for label, kws in _detect_domains(t):
            domain_threads[label].append((t.get("thread_id", "?"), kws))

    if domain_threads:
        lines += ["## Domain Pattern Alerts", ""]
        for label, entries in sorted(domain_threads.items()):
            tids = ", ".join(e[0] for e in entries[:8])
            sample_kws = ", ".join(entries[0][1]) if entries else ""
            lines.append(f"- **{label}**: {tids} — keywords: {sample_kws}")
        lines.append("")

    # ── Watch list (soft-flag score-3 threads) ────────────────────────────────
    if soft_threads:
        lines += ["## Watch List (Score = 3, not auto-escalated)", ""]
        lines.append(
            "> These threads were produced by the optional `--include-medium` pass. "
            "They are not escalated to findings automatically. Review manually if a "
            "Step 2 finding covers the same function."
        )
        lines.append("")
        for t in sorted(soft_threads, key=_sort_key):
            tid = t.get("thread_id", "?")
            title = t.get("title", "(no title)")
            verdict = t.get("verdict", "")
            sev = VERDICT_SEVERITY.get(verdict, verdict)
            inv_id = t.get("invariant_id", "")
            fns = _thread_functions(t)
            fn_str = ", ".join(f"`{f}()`" for f in fns) or "-"
            lines.append(f"- **[{tid}]** {title}  `{sev}`")
            if inv_id:
                lines.append(f"  - Invariant: {inv_id}  · Functions: {fn_str}")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    threads_all = _load_jsonl(THREADS_DIR / "promising_threads.jsonl")
    if not threads_all:
        print("generate_step0_brief: no promising_threads.jsonl found — writing empty brief")
        threads_all = []

    hard_threads = [t for t in threads_all if not t.get("soft_flag")]
    soft_threads  = [t for t in threads_all if t.get("soft_flag")]

    try:
        meta = get_audit_meta()
        audit_id = meta.get("audit_id", "unknown")
    except Exception:
        audit_id = "unknown"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    md = generate(hard_threads, soft_threads, audit_id)
    OUT_FILE.write_text(md, encoding="utf-8")

    total = len(hard_threads) + len(soft_threads)
    print(f"generate_step0_brief: wrote {OUT_FILE}  ({total} threads, {len(soft_threads)} soft)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
