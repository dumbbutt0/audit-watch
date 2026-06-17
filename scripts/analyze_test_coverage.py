#!/usr/bin/env python3
"""
analyze_test_coverage.py — Test coverage gap analysis.

Scans the project's test suite and identifies public/external contract functions
that have no corresponding test. Ranks untested functions by a risk score and
writes the top candidates to output/coverage_gaps.json for downstream agents.

Usage:
    python scripts/analyze_test_coverage.py --contract contracts/ --tests test/
    python scripts/analyze_test_coverage.py --contract contracts/ --tests test/ --top 20
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path

ROOT = Path(__file__).resolve().parent.parent

# Test file patterns for Foundry, Hardhat, Pytest, Rust
TEST_FILE_PATTERNS = [
    "**/*.t.sol",
    "**/*.test.ts",
    "**/*.test.js",
    "**/*.spec.ts",
    "**/*.spec.js",
    "**/test_*.py",
    "**/*_test.py",
    "**/*_test.rs",
    "**/test_*.rs",
]

# Keywords in function bodies that raise the risk score
HIGH_RISK_KEYWORDS = {
    "transfer": 3,
    "mint": 3,
    "burn": 3,
    "withdraw": 3,
    "deposit": 3,
    "borrow": 3,
    "repay": 3,
    "liquidate": 3,
    "swap": 2,
    "execute": 2,
    "upgrade": 2,
    "initialize": 2,
    "selfdestruct": 3,
    "delegatecall": 3,
    "call": 2,
}

# Visibility tokens that make a function externally accessible
EXTERNAL_VISIBILITY = {"public", "external"}


def _find_test_dirs(project_root: Path, explicit: list[Path]) -> list[Path]:
    candidates = list(explicit)
    for name in ("test", "tests", "test_suite"):
        p = project_root / name
        if p.is_dir():
            candidates.append(p)
    return [p for p in candidates if p.is_dir()]


def _collect_test_files(dirs: list[Path]) -> list[Path]:
    files = []
    for d in dirs:
        for pattern in TEST_FILE_PATTERNS:
            files.extend(d.rglob(pattern.lstrip("**/")))
    # Deduplicate
    return list({p.resolve(): p for p in files}.values())


def _extract_tested_names(test_files: list[Path]) -> set[str]:
    """Return all identifiers that appear as function calls in test files."""
    tested = set()
    call_re = re.compile(r'\b([a-zA-Z_]\w*)\s*\(')
    for path in test_files:
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in call_re.finditer(source):
            tested.add(m.group(1))
    return tested


def _extract_sol_functions(sol_files: list[Path]) -> list[dict]:
    """Parse Solidity source files to find public/external functions."""
    fn_re = re.compile(
        r'function\s+(\w+)\s*\(([^)]*)\)\s*(public|external|internal|private)?'
        r'([^{]*?)\{',
        re.MULTILINE | re.DOTALL,
    )
    modifier_re = re.compile(r'\b(onlyOwner|onlyRole|nonReentrant|whenNotPaused|initializer|\w+Only)\b')

    functions = []
    for path in sol_files:
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        # Extract contract names so we can attribute functions
        contract_re = re.compile(r'\bcontract\s+(\w+)\b')
        contracts = contract_re.findall(source)
        contract_name = contracts[-1] if contracts else path.stem

        for m in fn_re.finditer(source):
            fn_name, params_raw, visibility, rest = m.groups()
            visibility = (visibility or "internal").strip()
            if visibility not in EXTERNAL_VISIBILITY:
                continue

            rest = rest or ""
            modifiers = modifier_re.findall(rest)
            is_permissionless = not modifiers

            # Check function body for high-risk operations (next 300 chars after opening brace)
            body_start = m.end()
            body_snippet = source[body_start: body_start + 300]
            risk_score = 0
            matched_keywords = []
            for kw, score in HIGH_RISK_KEYWORDS.items():
                if kw in body_snippet:
                    risk_score += score
                    matched_keywords.append(kw)

            if is_permissionless:
                risk_score += 2

            # Complex params = struct / array args
            if "[" in params_raw or "struct" in params_raw or "calldata" in params_raw:
                risk_score += 1

            line_num = source[: m.start()].count("\n") + 1

            functions.append({
                "name": fn_name,
                "contract": contract_name,
                "file": str(path),
                "line": line_num,
                "visibility": visibility,
                "modifiers": modifiers,
                "is_permissionless": is_permissionless,
                "risk_keywords": matched_keywords,
                "risk_score": risk_score,
            })

    return functions


def analyse(contract_paths: list[Path], test_dirs: list[Path], top_n: int) -> dict:
    sol_files = []
    for cp in contract_paths:
        if cp.is_dir():
            sol_files.extend(cp.rglob("*.sol"))
        elif cp.suffix == ".sol":
            sol_files.append(cp)

    # Exclude test files from the contract list
    sol_files = [p for p in sol_files if not any(
        part in str(p) for part in ("test", "mock", "Mock", "Test", "fixture")
    )]

    test_files = _collect_test_files(test_dirs)
    tested_names = _extract_tested_names(test_files)
    all_functions = _extract_sol_functions(sol_files)

    untested = [f for f in all_functions if f["name"] not in tested_names]
    tested = [f for f in all_functions if f["name"] in tested_names]

    # Sort untested by risk score desc, then name asc
    untested.sort(key=lambda f: (-f["risk_score"], f["name"]))
    top = untested[:top_n]

    result = {
        "summary": {
            "total_public_functions": len(all_functions),
            "tested_functions": len(tested),
            "untested_functions": len(untested),
            "coverage_pct": round(100 * len(tested) / max(len(all_functions), 1), 1),
            "test_files_scanned": len(test_files),
            "contract_files_scanned": len(sol_files),
        },
        "top_untested_high_risk": top,
        "all_untested": untested,
    }

    out_path = audit_path("output") / "coverage_gaps.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))

    print(f"Coverage analysis complete:")
    print(f"  Contract files scanned : {result['summary']['contract_files_scanned']}")
    print(f"  Test files scanned     : {result['summary']['test_files_scanned']}")
    print(f"  Public/external fns    : {result['summary']['total_public_functions']}")
    print(f"  Tested                 : {result['summary']['tested_functions']} "
          f"({result['summary']['coverage_pct']}%)")
    print(f"  Untested               : {result['summary']['untested_functions']}")
    print(f"  Top {top_n} high-risk untested functions:")
    for f in top:
        perm = " [permissionless]" if f["is_permissionless"] else ""
        kws = ",".join(f["risk_keywords"][:3])
        print(f"    score={f['risk_score']:2d}  {f['contract']}.{f['name']}{perm}  [{kws}]")
    print(f"\n  Output written to: {out_path}")

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Test coverage gap analysis for Solidity projects")
    parser.add_argument("--contract", required=True, nargs="+",
                        help="Path(s) to contract file(s) or directory")
    parser.add_argument("--tests", nargs="*", default=[],
                        help="Path(s) to test directory/directories (auto-detected if omitted)")
    parser.add_argument("--top", type=int, default=15,
                        help="Number of top high-risk untested functions to report (default 15)")
    args = parser.parse_args()

    contract_paths = [Path(p) for p in args.contract]
    explicit_test_dirs = [Path(p) for p in args.tests]
    test_dirs = _find_test_dirs(ROOT, explicit_test_dirs)

    if not test_dirs:
        print("Warning: no test directories found. "
              "Specify with --tests test/ or create a test/ directory.")

    analyse(contract_paths, test_dirs, args.top)
    return 0


if __name__ == "__main__":
    sys.exit(main())
