#!/usr/bin/env python3
"""
report_generator.py

Reads all output/findings_*.json files, deduplicates overlapping findings,
scores severity, and produces output/merged_findings.json for the synthesis agent.

Run after all specialist agents complete:
    python tools/report_generator.py
"""

import json
import glob
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from audit_context import audit_path

OUTPUT_DIR = audit_path("output")

# Similarity threshold for semantic deduplication (0.0–1.0; higher = stricter)
SEMANTIC_DEDUP_THRESHOLD = 0.85

SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Informational": 4}

ID_PREFIXES = {
    "reentrancy":            "RE",
    "access_control":        "AC",
    "arithmetic":            "AR",
    "oracle":                "OR",
    "flash_loan":            "FL",
    "logic":                 "LG",
    "protocol_context":      "PC",
    "dos":                   "DS",
    "snapshot":              "SN",
    "deep_trace":            "DT",
    "economic_attack":       "EA",
    "cross_chain":           "XC",   # XC- to avoid conflict with compound CC- prefix
    "reference_diff":        "RD",
    "smt":                   "SMT",
    "token_integration":     "TI",
    "upgrade_storage":       "UP",
    "compound_synthesis":    "CC",   # CC- reserved for compound findings
}


def load_all_findings() -> list[dict]:
    """Load and flatten all findings from specialist agent output files."""
    all_findings = []
    pattern = str(OUTPUT_DIR / "findings_*.json")
    files = sorted(glob.glob(pattern))

    if not files:
        print("No findings files found. Run all specialist agents first.")
        return []

    for filepath in files:
        try:
            with open(filepath) as f:
                data = json.load(f)
            findings = data.get("findings", [])
            agent = data.get("agent", "unknown")
            contract = data.get("contract", "unknown")

            # protocol_context findings are included like any other agent
            if agent == "unknown":
                continue

            for finding in findings:
                finding["_source_agent"] = agent
                finding["_contract"] = contract
                all_findings.append(finding)

            print(f"  {filepath}: {len(findings)} findings from {agent}")
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"  Warning: could not load {filepath} — {e}")

    return all_findings


def semantic_deduplicate(findings: list[dict]) -> list[dict]:
    """
    Embedding-based pre-deduplication pass.
    Clusters findings with cosine similarity > SEMANTIC_DEDUP_THRESHOLD and
    keeps the highest-confidence finding in each cluster.
    Falls back gracefully if sentence-transformers is not available.
    """
    if len(findings) < 2:
        return findings

    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np
    except ImportError:
        return findings

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    texts = [
        f"{f.get('title', '')} {f.get('description', '')[:300]}"
        for f in findings
    ]
    embeddings = model.encode(texts, normalize_embeddings=True)

    # Greedy clustering: assign each finding to first cluster whose centroid is similar
    cluster_members: list[list[int]] = []
    cluster_rep: list[int] = []

    for i, emb in enumerate(embeddings):
        assigned = False
        for c_idx, rep_idx in enumerate(cluster_rep):
            sim = float(np.dot(emb, embeddings[rep_idx]))
            if sim >= SEMANTIC_DEDUP_THRESHOLD:
                cluster_members[c_idx].append(i)
                assigned = True
                break
        if not assigned:
            cluster_members.append([i])
            cluster_rep.append(i)

    CONFIDENCE_ORDER = {"High": 0, "Medium": 1, "Low": 2}
    result = []
    removed_count = 0

    for members in cluster_members:
        if len(members) == 1:
            result.append(findings[members[0]])
            continue
        # Keep finding with highest confidence; mark others as duplicates of it
        best_idx = min(
            members,
            key=lambda i: (
                CONFIDENCE_ORDER.get(findings[i].get("confidence", "Low"), 2),
                SEVERITY_ORDER.get(findings[i].get("severity", "Informational"), 99),
            ),
        )
        best = findings[best_idx]
        for m in members:
            if m != best_idx:
                findings[m]["duplicate_of"] = best.get("id", "")
                findings[m]["_semantic_duplicate"] = True
                removed_count += 1
        result.append(best)

    if removed_count:
        print(f"  Semantic dedup: removed {removed_count} near-duplicate finding(s) (threshold={SEMANTIC_DEDUP_THRESHOLD})")

    return result


def deduplicate(findings: list[dict]) -> list[dict]:
    """
    Remove or merge duplicate findings.
    Two findings are duplicates if they:
    - Reference the same function AND
    - Have the same vuln_type AND
    - Have duplicate_of pointing at each other
    """
    seen = {}
    deduplicated = []

    for finding in findings:
        duplicate_of = finding.get("duplicate_of")
        if duplicate_of and duplicate_of in seen:
            # Merge: keep the higher severity version, append references
            existing = seen[duplicate_of]
            if SEVERITY_ORDER.get(finding["severity"], 99) < SEVERITY_ORDER.get(existing["severity"], 99):
                existing["severity"] = finding["severity"]
            existing.setdefault("_also_found_by", []).append(finding.get("_source_agent"))
            continue

        # Simple location-based dedup
        location = finding.get("location", {})
        if isinstance(location, str):
            location = {"file": location, "function": None}
        key = (location.get("function"), finding.get("vuln_type"))
        if key in seen and key[0] is not None:
            existing = seen[key]
            existing.setdefault("_also_found_by", []).append(finding.get("_source_agent"))
            continue

        seen[finding["id"]] = finding
        if key[0]:
            seen[key] = finding
        deduplicated.append(finding)

    return deduplicated


def sort_by_severity(findings: list[dict]) -> list[dict]:
    return sorted(findings, key=lambda f: SEVERITY_ORDER.get(f.get("severity", "Informational"), 99))


def check_compound_risks(findings: list[dict]) -> list[str]:
    """
    Identify compound risk combinations and emit escalation notes.
    These are fast static checks — no Claude call needed.
    """
    notes = []
    vuln_types_present = {f.get("vuln_type") for f in findings}
    id_prefixes_present = {f.get("id", "")[:2] for f in findings}

    if "oracle-manipulation" in vuln_types_present and "flash-loan" in vuln_types_present:
        notes.append(
            "COMPOUND RISK (COMP-A): Oracle manipulation + flash loan detected. "
            "An attacker can manipulate the price oracle via flash loan in a single transaction. "
            "Review OR-* and FL-* findings together — combined severity is Critical."
        )

    if "reentrancy" in vuln_types_present and "access-control" in vuln_types_present:
        notes.append(
            "COMPOUND RISK (COMP-G): Reentrancy + missing access control detected. "
            "An attacker may reenter a privileged function mid-flash. Review RE-* and AC-* together."
        )

    if "arithmetic" in vuln_types_present and "logic-error" in vuln_types_present:
        notes.append(
            "COMPOUND RISK (COMP-H): Arithmetic error + logic error detected. "
            "Rounding bugs in collateral calculations can make positions non-liquidatable. "
            "Review AR-* and LG-* together for combined impact."
        )

    # COMP-B: reentrancy + snapshot timing
    if "reentrancy" in vuln_types_present and "SN" in id_prefixes_present:
        notes.append(
            "COMPOUND RISK (COMP-B): Reentrancy + snapshot timing detected. "
            "Reentering during a balance read used for voting power or rewards reads a stale "
            "inflated balance. Review RE-* and SN-* together — combined severity is Critical."
        )

    # COMP-D: fee-on-transfer (TI-*) + economic attack / reward accounting (EA-*)
    if "TI" in id_prefixes_present and "EA" in id_prefixes_present:
        notes.append(
            "COMPOUND RISK (COMP-D): Fee-on-transfer token + reward accounting detected. "
            "Each deposit over-credits reward shares; attacker can drain yield pool incrementally. "
            "Review TI-* and EA-* together."
        )

    # COMP-E: rebasing token (TI-*) + oracle/logic (OR-* or LG-*)
    if "TI" in id_prefixes_present and (
        "oracle-manipulation" in vuln_types_present or "logic-error" in vuln_types_present
    ):
        notes.append(
            "COMPOUND RISK (COMP-E): Rebasing token integration + collateral/oracle issue detected. "
            "Negative rebase can drop all collateral values simultaneously causing mass insolvency. "
            "Review TI-* and OR-*/LG-* findings together."
        )

    # COMP-F: DoS + governance
    if "dos" in vuln_types_present and any(
        "governance" in f.get("title", "").lower() or "quorum" in f.get("description", "").lower()
        for f in findings
    ):
        notes.append(
            "COMPOUND RISK (COMP-F): DoS + governance quorum dependency detected. "
            "Blocking the vote function prevents quorum, freezing protocol upgrades or emergency actions. "
            "Review DS-* alongside any governance findings."
        )

    # COMP-I: missing slippage + oracle manipulation
    if "oracle-manipulation" in vuln_types_present and any(
        "slippage" in f.get("title", "").lower() or "slippage" in f.get("description", "").lower()
        for f in findings
    ):
        notes.append(
            "COMPOUND RISK (COMP-I): Missing slippage check + oracle manipulation detected. "
            "Attacker manipulates price then executes slippage-free swap at manipulated price. "
            "Review OR-* alongside slippage-related findings."
        )

    # COMP-J: snapshot timing + flash loan (governance flash loan)
    if "SN" in id_prefixes_present and "flash-loan" in vuln_types_present:
        notes.append(
            "COMPOUND RISK (COMP-J): Snapshot timing + flash loan detected. "
            "Flash-loan governance attack: borrow tokens → snapshot taken at callback time → "
            "vote passes → repay. Review SN-* and FL-* together — combined severity is Critical."
        )

    return notes


def generate_summary(findings: list[dict]) -> dict:
    severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Informational": 0}
    for f in findings:
        sev = f.get("severity", "Informational")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    return {
        "total": len(findings),
        "by_severity": severity_counts,
        "critical_ids": [f["id"] for f in findings if f.get("severity") == "Critical"],
        "high_ids": [f["id"] for f in findings if f.get("severity") == "High"],
    }


def main():
    print("Loading findings from all agents...")
    all_findings = load_all_findings()

    if not all_findings:
        return

    print(f"\nTotal raw findings: {len(all_findings)}")

    print("Semantic deduplication (embedding-based)...")
    semantically_deduped = semantic_deduplicate(all_findings)

    print("Structural deduplication (location+type)...")
    deduped = deduplicate(semantically_deduped)
    print(f"After deduplication: {len(deduped)} findings")

    sorted_findings = sort_by_severity(deduped)
    compound_notes = check_compound_risks(sorted_findings)
    summary = generate_summary(sorted_findings)

    merged = {
        "generated_at": datetime.now().isoformat(),
        "summary": summary,
        "compound_risk_notes": compound_notes,
        "findings": sorted_findings,
    }

    out_path = OUTPUT_DIR / "merged_findings.json"
    with open(out_path, "w") as f:
        json.dump(merged, f, indent=2)

    print(f"\nMerged findings written to {out_path}")
    print("\nSeverity summary:")
    for sev, count in summary["by_severity"].items():
        if count > 0:
            print(f"  {sev:15s} {count}")

    if compound_notes:
        print("\nCompound risk alerts:")
        for note in compound_notes:
            print(f"  ⚠ {note[:100]}...")

    print("\nReady for report synthesis agent.")
    print("Next step: spawn agents/report_synthesis.md with output/merged_findings.json")


if __name__ == "__main__":
    main()
