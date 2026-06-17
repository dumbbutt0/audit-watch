#!/usr/bin/env python3
"""
generate_poc_test.py — Generate and run a PoC test, with a repair loop.

Reads the PoC plan, generates test code via Claude, writes the test file,
runs it, and repairs compile errors up to --max-repair-attempts times.

Usage:
    python scripts/generate_poc_test.py --finding-id AR-001 --repo contracts/2026-04-k2
    python scripts/generate_poc_test.py --finding-id AR-001 --repo contracts/2026-04-k2 --max-repair-attempts 3

Safety limits:
    - Never touches mainnet/testnet
    - Never uses private keys
    - Never broadcasts transactions
    - Only runs local cargo/forge tests
    - Only modifies files under pocs/ or test directories
    - Never deletes repo files
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
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
POC_DIR    = audit_path("data/poc_queue")
POCS_DIR   = audit_path("pocs")
TRIAGE_DIR = audit_path("data/triage")
PROMPTS    = Path(__file__).resolve().parent.parent / "prompts"

COMPILE_ERROR_PATTERN = re.compile(r'error\[E\d+\]|^error:', re.MULTILINE)

# Safety guard: forbidden patterns in generated test code
SAFETY_FORBIDDEN = [
    "broadcast", "sendTransaction", "PRIVATE_KEY", "mainnet",
    "fs::remove", "std::fs::remove", "rm -rf",
]


# ─────────────────────────────────────────────────────────────────────────────
# Loaders
# ─────────────────────────────────────────────────────────────────────────────

def load_plan(finding_id: str) -> dict:
    path = POC_DIR / f"{finding_id}_plan.json"
    if not path.exists():
        raise SystemExit(
            f"[error] Plan not found: {path}\n"
            f"Run: python scripts/generate_poc_plan.py --finding-id {finding_id}"
        )
    return json.loads(path.read_text())


def load_original_finding(finding_id: str) -> dict:
    merged = audit_path("output/merged_findings.json")
    if merged.exists():
        data = json.loads(merged.read_text())
        for f in data.get("findings", []):
            if f["id"] == finding_id:
                return f
    return {}


def load_repo_profile() -> dict:
    path = POC_DIR / "repo_profile.json"
    if path.exists():
        return json.loads(path.read_text())
    # Fall back to the audit's declared language so Move/Sui audits get the Sui-Move PoC template
    # (templates/move_poc/, `sui move test`) instead of the Soroban default.
    try:
        import sys as _sys
        _sys.path.insert(0, str(Path(__file__).resolve().parent))
        from audit_context import audit_language as _al
        lang = _al()
        if lang == "move":
            return {"language": "move", "framework": "sui"}
    except Exception:
        pass
    return {"language": "rust", "framework": "soroban"}


def load_nearby_test_content(plan: dict, repo: Path) -> list[dict]:
    """Read the actual content of nearby test files for the writer's context."""
    tests = []
    unit_test_dir = repo / "tests" / "unit-tests" / "src"
    if unit_test_dir.exists():
        # Audit finding tests are most relevant
        for name in ["audit_finding_03_silent_overflow.rs", "audit_finding_03_fix_verification.rs"]:
            p = unit_test_dir / name
            if p.exists():
                tests.append({"file": str(p.relative_to(repo)), "content": p.read_text()[:4000]})
    return tests


def load_triage(finding_id: str) -> dict:
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
    return {}


# ─────────────────────────────────────────────────────────────────────────────
# Safety check
# ─────────────────────────────────────────────────────────────────────────────

def safety_check(code: str) -> list[str]:
    violations = []
    for pattern in SAFETY_FORBIDDEN:
        if pattern.lower() in code.lower():
            violations.append(f"Forbidden pattern in generated code: '{pattern}'")
    return violations


# ─────────────────────────────────────────────────────────────────────────────
# Cargo.toml generation for pocs/k2/{FINDING_ID}/
# ─────────────────────────────────────────────────────────────────────────────

PURE_ARITHMETIC_CARGO = """\
[package]
name = "poc-{pkg_name}"
version = "0.1.0"
edition = "2021"

[[test]]
name = "poc"
path = "src/lib.rs"
"""

POC_WORKSPACE_CARGO = """\
[workspace]
members = [{members}]
resolver = "2"
"""


def ensure_poc_cargo(finding_id: str) -> Path:
    """Create Cargo.toml for the PoC crate if it doesn't exist."""
    poc_crate_dir = POCS_DIR / "k2" / finding_id
    poc_crate_dir.mkdir(parents=True, exist_ok=True)
    (poc_crate_dir / "src").mkdir(exist_ok=True)

    cargo_path = poc_crate_dir / "Cargo.toml"
    if not cargo_path.exists():
        pkg_name = finding_id.lower().replace("-", "_")
        cargo_path.write_text(PURE_ARITHMETIC_CARGO.format(pkg_name=pkg_name))

    # Ensure workspace Cargo.toml at pocs/k2/
    ws_path = POCS_DIR / "k2" / "Cargo.toml"
    if not ws_path.exists():
        # Discover existing members
        members = [
            f'"{d.name}"'
            for d in (POCS_DIR / "k2").iterdir()
            if d.is_dir() and (d / "Cargo.toml").exists()
        ]
        ws_path.write_text(POC_WORKSPACE_CARGO.format(members=", ".join(members)))
    else:
        # Add this finding to existing workspace if not already there
        content = ws_path.read_text()
        if f'"{finding_id}"' not in content:
            content = content.replace('members = [', f'members = [\n    "{finding_id}",', 1)
            ws_path.write_text(content)

    return poc_crate_dir


# ─────────────────────────────────────────────────────────────────────────────
# Claude: generate test code
# ─────────────────────────────────────────────────────────────────────────────

def call_writer(
    plan: dict,
    original: dict,
    triage: dict,
    profile: dict,
    nearby_tests: list[dict],
    previous_code: str = "",
    compiler_error: str = "",
    attempt: int = 0,
) -> dict:
    system = (PROMPTS / "poc_writer.md").read_text()

    user_parts = []

    if attempt > 0 and compiler_error:
        user_parts.append(
            f"## REPAIR ATTEMPT {attempt}\n\n"
            f"The previous test had a compiler error. Fix ONLY the compilation issue. "
            f"Do not change the test logic.\n\n"
            f"### Compiler Error\n```\n{compiler_error[:3000]}\n```\n\n"
            f"### Current Test Code\n```rust\n{previous_code}\n```\n\n"
        )
    else:
        user_parts.append(f"## Finding: {plan.get('finding_id', '?')}\n")
        user_parts.append("## PoC Plan\n```json\n" + json.dumps(plan, indent=2) + "\n```\n")
        user_parts.append("## Original Finding\n```json\n" + json.dumps(original, indent=2) + "\n```\n")
        user_parts.append("## Triage Record\n```json\n" + json.dumps(triage, indent=2) + "\n```\n")
        user_parts.append("## Repository Profile\n```json\n" + json.dumps(profile, indent=2) + "\n```\n")
        if nearby_tests:
            user_parts.append("## Reference Test Files\n")
            for t in nearby_tests:
                user_parts.append(f"### {t['file']}\n```rust\n{t['content']}\n```\n")

    user_parts.append(
        "\nGenerate the test code. Return JSON with fields: "
        "file_path, run_command, cargo_toml (if needed), test_code, "
        "expected_output_contains, explanation."
    )

    client = require_llm(skill="poc")
    response = client.messages.create(
        model=MODEL,
        max_tokens=6144,
        system=system,
        messages=[{"role": "user", "content": "\n".join(user_parts)}],
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = re.sub(r'^```[a-z]*\n?', '', raw)
        raw = re.sub(r'\n?```$', '', raw)
        raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Try to extract JSON from mixed output
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if m:
            try:
                result = json.loads(m.group(0))
            except json.JSONDecodeError:
                result = {}
        else:
            result = {}

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Claude: review result
# ─────────────────────────────────────────────────────────────────────────────

def call_reviewer(plan: dict, original: dict, test_code: str,
                  stdout: str, stderr: str, returncode: int) -> dict:
    system = (PROMPTS / "poc_reviewer.md").read_text()
    user = json.dumps({
        "finding": original,
        "plan": plan,
        "test_code_excerpt": test_code[:2000],
        "stdout": stdout[:2000],
        "stderr": stderr[:2000],
        "exit_code": returncode,
    }, indent=2)

    client = require_llm(skill="poc")
    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = re.sub(r'^```[a-z]*\n?', '', raw)
        raw = re.sub(r'\n?```$', '', raw)
        raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "status":           "inconclusive",
            "assertion_hit":    False,
            "evidence_summary": stdout[:500] or "(no output)",
            "verdict":          "Reviewer returned malformed JSON",
            "next_steps":       ["Manual review required"],
        }


# ─────────────────────────────────────────────────────────────────────────────
# Test runner
# ─────────────────────────────────────────────────────────────────────────────

def run_test(run_command: str, cwd: Path | None = None) -> tuple[int, str, str]:
    """Run the test command and return (returncode, stdout, stderr)."""
    print(f"  Running: {run_command}")
    try:
        proc = subprocess.run(
            run_command.split(),
            capture_output=True,
            text=True,
            timeout=120,
            cwd=cwd,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Test timed out after 120 seconds"
    except FileNotFoundError as e:
        return -1, "", f"Command not found: {e}"


def is_compile_error(stderr: str) -> bool:
    return bool(COMPILE_ERROR_PATTERN.search(stderr))


# ─────────────────────────────────────────────────────────────────────────────
# Result persistence
# ─────────────────────────────────────────────────────────────────────────────

def save_result(finding_id: str, status: str, test_file: str, run_command: str,
                stdout: str, stderr: str, assertion_hit: bool,
                evidence_summary: str, next_steps: list[str], repair_attempts: int) -> dict:
    result = {
        "finding_id":       finding_id,
        "status":           status,
        "test_file":        test_file,
        "run_command":      run_command,
        "stdout_excerpt":   stdout[:2000],
        "stderr_excerpt":   stderr[:2000],
        "assertion_hit":    assertion_hit,
        "repair_attempts":  repair_attempts,
        "evidence_summary": evidence_summary,
        "next_steps":       next_steps,
        "generated_at":     datetime.now(timezone.utc).isoformat(),
    }

    # Save individual result
    POC_DIR.mkdir(parents=True, exist_ok=True)
    result_path = POC_DIR / f"{finding_id}_result.json"
    result_path.write_text(json.dumps(result, indent=2))

    # Append to bucket JSONL
    bucket_file = POC_DIR / ("generated.jsonl" if status == "proved" else "failed.jsonl")
    with bucket_file.open("a") as fh:
        fh.write(json.dumps(result) + "\n")

    # Always append to results.jsonl
    with (POC_DIR / "results.jsonl").open("a") as fh:
        fh.write(json.dumps(result) + "\n")

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate and run a PoC test for a finding",
        epilog="Safety: only runs local tests, never touches mainnet or private keys.",
    )
    parser.add_argument("--finding-id",         required=True)
    parser.add_argument("--repo",               default="contracts/2026-04-k2")
    parser.add_argument("--max-repair-attempts", type=int, default=3)
    parser.add_argument("--plan-only",          action="store_true",
                        help="Generate test code but do not run it")
    args = parser.parse_args()

    fid  = args.finding_id
    repo = Path(args.repo)

    print(f"PoC Generator — {fid}\n")

    plan     = load_plan(fid)
    original = load_original_finding(fid)
    triage   = load_triage(fid)
    profile  = load_repo_profile()
    nearby   = load_nearby_test_content(plan, repo)

    poc_crate_dir = ensure_poc_cargo(fid)
    test_file_path = poc_crate_dir / "src" / "lib.rs"
    # Always use the canonical manifest path; ignore whatever path the planner invented
    run_command = f"cargo test --manifest-path {POCS_DIR / 'k2' / fid / 'Cargo.toml'} -- --nocapture"

    test_code     = ""
    repair_attempts = 0
    compiler_error  = ""

    for attempt in range(args.max_repair_attempts + 1):
        print(f"\n  {'Generating' if attempt == 0 else 'Repairing'} test code "
              f"(attempt {attempt + 1}/{args.max_repair_attempts + 1})...")

        writer_output = call_writer(
            plan, original, triage, profile, nearby,
            previous_code=test_code,
            compiler_error=compiler_error,
            attempt=attempt,
        )

        test_code = writer_output.get("test_code", "")
        if not test_code:
            print("  [warn] Writer returned no test_code")
            continue

        # Safety check
        violations = safety_check(test_code)
        if violations:
            print(f"  [SAFETY] Blocked: {violations}")
            save_result(fid, "failed", str(test_file_path), run_command,
                        "", str(violations), False,
                        "Safety check blocked generated code", violations, repair_attempts)
            return 1

        # Write Cargo.toml if provided
        if writer_output.get("cargo_toml"):
            (poc_crate_dir / "Cargo.toml").write_text(writer_output["cargo_toml"])

        # Write test file
        test_file_path.write_text(test_code)
        print(f"  Written: {test_file_path}")

        if args.plan_only:
            print(f"  --plan-only: skipping test run")
            print(f"  Run command: {run_command}")
            return 0

        # Run the test
        rc, stdout, stderr = run_test(run_command)
        repair_attempts = attempt

        print(f"  Exit code: {rc}")
        if stdout:
            print(f"  Stdout: {stdout[:300]}")
        if stderr:
            print(f"  Stderr: {stderr[:300]}")

        if is_compile_error(stderr) and attempt < args.max_repair_attempts:
            print(f"  Compile error — will repair (attempt {attempt + 1}/{args.max_repair_attempts})")
            compiler_error = stderr
            continue

        # Ask reviewer to interpret result
        print(f"\n  Calling reviewer...")
        review = call_reviewer(plan, original, test_code, stdout, stderr, rc)
        status          = review.get("status", "inconclusive")
        assertion_hit   = review.get("assertion_hit", rc == 0)
        evidence        = review.get("evidence_summary", stdout[:500])
        next_steps      = review.get("next_steps", [])
        repair_hint     = review.get("repair_hint")

        if status == "compile_error" and repair_hint and attempt < args.max_repair_attempts:
            compiler_error = repair_hint
            continue

        result = save_result(
            fid, status, str(test_file_path), run_command,
            stdout, stderr, assertion_hit, evidence, next_steps, repair_attempts,
        )

        print(f"\n  ┌─ Result ─────────────────────────────────────────────")
        print(f"  │ Status:         {status}")
        print(f"  │ Assertion hit:  {assertion_hit}")
        print(f"  │ Repair cycles:  {repair_attempts}")
        print(f"  │ Evidence:       {evidence[:120]}")
        print(f"  └──────────────────────────────────────────────────────")
        print(f"\n  Result saved → {POC_DIR / f'{fid}_result.json'}")
        return 0

    # Max repairs exhausted
    save_result(
        fid, "compile_error", str(test_file_path), run_command,
        "", compiler_error, False,
        f"Could not fix compile errors after {args.max_repair_attempts} attempts",
        [f"Manual repair required. Last error: {compiler_error[:200]}"],
        repair_attempts,
    )
    print(f"\n  [fail] Max repair attempts ({args.max_repair_attempts}) exhausted")
    return 1


if __name__ == "__main__":
    sys.exit(main())
