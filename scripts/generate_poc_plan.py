#!/usr/bin/env python3
"""
generate_poc_plan.py — Generate a PoC test plan for a specific finding.

Reads the finding from triage data + queue, loads relevant source code,
calls Claude with the poc_planner prompt, and saves the plan JSON.

Usage:
    python scripts/generate_poc_plan.py --finding-id AR-001
    python scripts/generate_poc_plan.py --finding-id AR-001 --repo contracts/2026-04-k2
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

if Path(".env").exists():
    for _line in Path(".env").read_text().splitlines():
        if "=" in _line and not _line.startswith("#"):
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip("\"'"))

import anthropic

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path
from llm_runtime import require_llm  # no-silent-fail: actionable message instead of credit spend/crash

MODEL      = "claude-sonnet-4-6"
TRIAGE_DIR = audit_path("data/triage")
POC_DIR    = audit_path("data/poc_queue")
PROMPTS    = Path(__file__).resolve().parent.parent / "prompts"


# ─────────────────────────────────────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────────────────────────────────────

def load_finding(finding_id: str) -> dict:
    """Load triage record + original finding for a given ID."""
    for bucket in ["poc_required", "submit", "downgraded"]:
        path = TRIAGE_DIR / f"{bucket}.jsonl"
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            t = json.loads(line)
            if t.get("finding_id") == finding_id:
                return t
    raise SystemExit(f"[error] {finding_id} not found in any triage bucket")


def load_original_finding(finding_id: str) -> dict:
    merged = audit_path("output") / "merged_findings.json"
    if merged.exists():
        data = json.loads(merged.read_text())
        for f in data.get("findings", []):
            if f["id"] == finding_id:
                return f
    # Fallback: scan individual findings files
    for path in audit_path("output").glob("findings_*.json"):
        data = json.loads(path.read_text())
        for f in data.get("findings", []):
            if f["id"] == finding_id:
                return f
    return {}


def load_queue_entry(finding_id: str) -> dict:
    for p in ["p0", "p1", "p2", "p3"]:
        path = POC_DIR / f"{p}.jsonl"
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            e = json.loads(line)
            if e.get("finding_id") == finding_id:
                return e
    return {}


def load_source_code(location, repo_root: Path) -> str:
    """Load the source file at the finding's location."""
    if isinstance(location, str):
        location = {"file": location}
    file_path = location.get("file", "")
    if not file_path:
        return ""
    # Try repo-relative path
    candidates = [
        repo_root / file_path,
        Path(file_path),
        repo_root / Path(*Path(file_path).parts[-4:]),
    ]
    for candidate in candidates:
        if candidate.exists():
            try:
                lines = candidate.read_text().splitlines()
                ls = location.get("line_start", 1)
                le = location.get("line_end", len(lines))
                # Include context: 30 lines before and after
                start = max(0, ls - 30)
                end   = min(len(lines), le + 30)
                excerpt = "\n".join(lines[start:end])
                return f"// {candidate}\n// Lines {start+1}-{end}\n\n{excerpt}"
            except Exception:
                pass
    return location.get("code_snippet", "")


def load_nearby_tests(location, repo_root: Path) -> list[dict]:
    """Find test files in the same contract directory."""
    if isinstance(location, str):
        location = {"file": location}
    file_path = location.get("file", "")
    if not file_path:
        return []
    # Find the contract name from the path
    parts = Path(file_path).parts
    contract_dir = None
    for i, part in enumerate(parts):
        if part == "contracts" and i + 1 < len(parts):
            contract_dir = parts[i + 1]
            break
    if not contract_dir:
        return []

    # Look for test files in unit-tests directory
    unit_test_dir = repo_root / "tests" / "unit-tests" / "src"
    tests = []
    if unit_test_dir.exists():
        for test_file in sorted(unit_test_dir.glob("*.rs")):
            content = test_file.read_text(errors="ignore")
            # Prioritize files related to this contract
            if contract_dir.replace("-", "_") in test_file.name or "audit" in test_file.name:
                tests.insert(0, {"file": str(test_file.relative_to(repo_root)), "content": content[:3000]})
            elif len(tests) < 3:
                tests.append({"file": str(test_file.relative_to(repo_root)), "content": content[:1500]})
    return tests[:4]


def load_repo_profile() -> dict:
    path = POC_DIR / "repo_profile.json"
    if path.exists():
        return json.loads(path.read_text())
    return {"language": "rust", "framework": "soroban", "test_command": "cargo test"}


# ─────────────────────────────────────────────────────────────────────────────
# Claude call
# ─────────────────────────────────────────────────────────────────────────────

def call_planner(
    finding_id: str,
    triage: dict,
    original: dict,
    queue_entry: dict,
    source_code: str,
    nearby_tests: list[dict],
    repo_profile: dict,
) -> dict:
    system = (PROMPTS / "poc_planner.md").read_text()

    user_parts = [
        f"## Finding ID: {finding_id}\n",
        "## Triage Record\n```json\n" + json.dumps(triage, indent=2) + "\n```\n",
        "## Original Finding\n```json\n" + json.dumps(original, indent=2) + "\n```\n",
        "## Queue Entry\n```json\n" + json.dumps(queue_entry, indent=2) + "\n```\n",
        "## Repository Profile\n```json\n" + json.dumps(repo_profile, indent=2) + "\n```\n",
    ]

    if source_code:
        user_parts.append(f"## Source Code (bug location)\n```rust\n{source_code}\n```\n")

    if nearby_tests:
        user_parts.append("## Nearby Test Files (for pattern reference)\n")
        for t in nearby_tests:
            user_parts.append(f"### {t['file']}\n```rust\n{t['content']}\n```\n")

    user_parts.append(
        "\nGenerate a PoC plan for this finding. "
        "Return ONLY valid JSON matching the poc_plan schema. No commentary."
    )

    client = require_llm(skill="poc")
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": "\n".join(user_parts)}],
    )

    raw = response.content[0].text.strip()
    # Strip code fences
    if raw.startswith("```"):
        raw = re.sub(r'^```[a-z]*\n?', '', raw)
        raw = re.sub(r'\n?```$', '', raw)
        raw = raw.strip()

    try:
        plan = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[warn] Planner returned malformed JSON: {e}")
        print(f"Raw (first 500): {raw[:500]}")
        # Build minimal fallback plan
        plan = {
            "finding_id":   finding_id,
            "test_name":    f"poc_{finding_id.lower().replace('-', '_')}",
            "goal":         original.get("impact", ""),
            "poc_approach": queue_entry.get("poc_approach", "pure_arithmetic"),
            "minimal_setup": [],
            "attack_steps":  [],
            "assertions":    [],
            "files_to_create": [f"pocs/k2/{finding_id}/src/lib.rs"],
            "files_to_modify": [],
            "run_command":   f"cargo test --manifest-path pocs/k2/{finding_id}/Cargo.toml -- --nocapture",
            "expected_output": "BUG CONFIRMED",
            "failure_modes": ["Parse error in planner — manual review required"],
            "notes":         f"Plan generation parse error: {e}",
        }

    plan["finding_id"] = finding_id  # ensure correct
    # Normalize run_command to canonical manifest path (planner sometimes invents wrong paths)
    plan["run_command"] = f"cargo test --manifest-path pocs/k2/{finding_id}/Cargo.toml -- --nocapture"
    return plan


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate a PoC plan for a triaged finding")
    parser.add_argument("--finding-id", required=True)
    parser.add_argument("--repo",       default="contracts/2026-04-k2",
                        help="Path to the target repository")
    args = parser.parse_args()

    fid      = args.finding_id
    repo     = Path(args.repo)

    print(f"Generating PoC plan for {fid}...\n")

    triage      = load_finding(fid)
    original    = load_original_finding(fid)
    queue_entry = load_queue_entry(fid)
    profile     = load_repo_profile()
    source_code = load_source_code(original.get("location", {}), repo)
    nearby      = load_nearby_tests(original.get("location", {}), repo)

    print(f"  Source code loaded: {bool(source_code)}")
    print(f"  Nearby tests found: {len(nearby)}")
    print(f"  Calling Claude ({MODEL})...")

    plan = call_planner(fid, triage, original, queue_entry, source_code, nearby, profile)

    # Save plan
    POC_DIR.mkdir(parents=True, exist_ok=True)
    plan_path = POC_DIR / f"{fid}_plan.json"
    plan_path.write_text(json.dumps(plan, indent=2))
    print(f"\n  Plan saved → {plan_path}")
    print(f"  Test name:    {plan.get('test_name', '?')}")
    print(f"  Approach:     {plan.get('poc_approach', '?')}")
    print(f"  Run command:  {plan.get('run_command', '?')}")
    print(f"  Files:        {plan.get('files_to_create', [])}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
