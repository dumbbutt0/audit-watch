#!/usr/bin/env python3
"""
run_integrated_poc.py — Runtime PoC Execution Agent.

Upgrades harness-level PoCs to call real protocol code and executes them.
Only processes findings with exploitability_score >= 3.

Usage:
    python scripts/run_integrated_poc.py --all
    python scripts/run_integrated_poc.py --finding-id LG-005
    python scripts/run_integrated_poc.py --all --force
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import anthropic

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path, load_env, load_jsonl, DEFAULT_MODEL
from llm_runtime import require_llm  # no-silent-fail: actionable message instead of credit spend/crash

load_env()

MODEL       = DEFAULT_MODEL
TRIAGE_DIR  = audit_path("data/triage")
EXPLOIT_DIR = audit_path("data/exploitability")
POC_DIR     = audit_path("data/runtime_poc")
POCS_DIR    = audit_path("pocs")
PROMPTS     = Path(__file__).resolve().parent.parent / "prompts"
OUTPUT_DIR  = audit_path("output")

SAFETY_FORBIDDEN = [
    "broadcast", "PRIVATE_KEY", "mainnet", "rm -rf",
    "curl ", "wget ", "eval(", "exec(", "os.system",
]
COMPILE_ERROR_RE = re.compile(r'error\[E\d+\]|^error:', re.MULTILINE)


# ─────────────────────────────────────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_existing(output_path: Path) -> dict[str, dict]:
    return {r["finding_id"]: r for r in load_jsonl(output_path) if "finding_id" in r}


def write_jsonl(records: dict[str, dict], path: Path) -> None:
    with path.open("w") as fh:
        for r in records.values():
            fh.write(json.dumps(r) + "\n")


def strip_fences(raw: str) -> str:
    if raw.startswith("```"):
        raw = re.sub(r'^```[a-z]*\n?', '', raw)
        raw = re.sub(r'\n?```$', '', raw)
    return raw.strip()


def load_merged_findings() -> dict[str, dict]:
    path = OUTPUT_DIR / "merged_findings.json"
    if not path.exists():
        return {}
    return {f["id"]: f for f in json.loads(path.read_text()).get("findings", [])}


def load_exploitability_models() -> dict[str, dict]:
    return {r["finding_id"]: r for r in load_jsonl(EXPLOIT_DIR / "models.jsonl") if "finding_id" in r}


def load_poc_queue_proved() -> set[str]:
    """Return finding IDs that already have a proved result in data/poc_queue/."""
    poc_queue_dir = audit_path("data/poc_queue")
    proved: set[str] = set()
    # Check individual result files (preferred — updated by run_poc_tests.py)
    for result_file in poc_queue_dir.glob("*_result.json"):
        try:
            d = json.loads(result_file.read_text())
            if d.get("status") == "proved" and d.get("finding_id"):
                proved.add(d["finding_id"])
        except (json.JSONDecodeError, OSError):
            pass
    # Also check results.jsonl for any additional entries
    for record in load_jsonl(poc_queue_dir / "results.jsonl"):
        if record.get("status") == "proved" and record.get("finding_id"):
            proved.add(record["finding_id"])
    return proved


def load_all_triage_findings(finding_id: str | None = None) -> list[dict]:
    items = (
        load_jsonl(TRIAGE_DIR / "submit.jsonl") +
        load_jsonl(TRIAGE_DIR / "poc_required.jsonl")
    )
    if finding_id:
        items = [i for i in items if i.get("finding_id") == finding_id]
    return items


def load_existing_poc_code(fid: str) -> str:
    candidates = [
        POCS_DIR / "k2" / fid / "src" / "lib.rs",
        POCS_DIR / fid / "src" / "lib.rs",
    ]
    for c in candidates:
        if c.exists():
            return c.read_text()
    return ""


def safety_check(code: str) -> list[str]:
    violations = []
    for pattern in SAFETY_FORBIDDEN:
        if pattern.lower() in code.lower():
            violations.append(f"forbidden: '{pattern}'")
    return violations


def run_test(run_command: str, cwd: str | None = None,
             timeout: int = 120) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            run_command,
            shell=True,
            capture_output=True, text=True, timeout=timeout, cwd=cwd,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Timeout after {timeout}s"
    except FileNotFoundError as exc:
        return -1, "", f"Command not found: {exc}"


# ─────────────────────────────────────────────────────────────────────────────
# Claude calls
# ─────────────────────────────────────────────────────────────────────────────

def call_poc_generator(original: dict, exploit_model: dict,
                       existing_poc: str, triage: dict,
                       compiler_error: str = "", attempt: int = 0) -> dict:
    system = (PROMPTS / "runtime_poc_executor.md").read_text()

    if attempt > 0 and compiler_error:
        user = json.dumps({
            "repair_attempt": attempt,
            "finding_id": original.get("id", ""),
            "compiler_error": compiler_error[:3000],
            "instruction": "Fix ONLY the compilation error. Do not change test logic.",
        }, indent=2)
    else:
        user = json.dumps({
            "finding":          original,
            "exploitability":   exploit_model,
            "triage":           triage,
            "existing_poc_code": existing_poc[:4000] if existing_poc else None,
            "repo_language":    "rust",
            "repo_framework":   "soroban",
        }, indent=2)

    client = require_llm(skill="poc")
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": user}],
    )

    raw = strip_fences(response.content[0].text)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
    return {}


# ─────────────────────────────────────────────────────────────────────────────
# Per-finding processor
# ─────────────────────────────────────────────────────────────────────────────

def process_finding(triage: dict, original: dict, exploit_model: dict,
                    existing: dict[str, dict], force: bool) -> dict:
    fid = triage.get("finding_id", "")
    ts  = datetime.now(timezone.utc).isoformat()

    if fid in existing and not force:
        print(f"  {fid}: already processed — skip")
        return existing[fid]

    # If a proved fork PoC already exists in poc_queue (e.g., from run_poc_tests.py),
    # record that result directly rather than generating a new one from scratch.
    poc_queue_proved = load_poc_queue_proved()
    if fid in poc_queue_proved and not force:
        poc_queue_dir = audit_path("data/poc_queue")
        queue_result_path = poc_queue_dir / f"{fid}_result.json"
        if queue_result_path.exists():
            try:
                qr = json.loads(queue_result_path.read_text())
                result = {
                    "finding_id":             fid,
                    "runtime_level":          qr.get("poc_level", "L3B"),
                    "status":                 "proved",
                    "real_function_called":   True,
                    "public_entrypoint_called": True,
                    "copied_logic_used":      False,
                    "test_file_path":         qr.get("test_file", ""),
                    "run_command":            qr.get("run_command", ""),
                    "assertion":              "fork PoC — see test_file_path",
                    "stdout_excerpt":         qr.get("stdout_excerpt", "")[:2000],
                    "stderr_excerpt":         "",
                    "limitations":            [],
                    "next_upgrade":           "",
                    "repair_attempts":        0,
                    "analyzed_at":            ts,
                    "_source":                "poc_queue",
                }
                print(f"  {fid}: fork PoC already proved in poc_queue — using existing result")
                return result
            except (json.JSONDecodeError, OSError):
                pass  # fall through to normal generation

    exploit_score = exploit_model.get("exploitability_score", 0)
    if exploit_score < 3:
        print(f"  {fid}: exploitability_score={exploit_score} < 3 — skip (low_exploitability)")
        return {
            "finding_id":    fid,
            "status":        "skipped",
            "reason":        "low_exploitability",
            "runtime_level": 0,
            "exploitability_score": exploit_score,
            "analyzed_at":   ts,
        }

    print(f"  {fid}: generating runtime PoC (exploit_score={exploit_score})...")
    existing_poc = load_existing_poc_code(fid)

    poc_result   = {}
    test_content = ""
    compiler_err = ""
    repair_count = 0
    rc, stdout, stderr = 0, "", ""

    for attempt in range(4):  # initial + 3 repairs
        poc_result = call_poc_generator(
            original, exploit_model, existing_poc, triage,
            compiler_error=compiler_err, attempt=attempt,
        )
        if not poc_result:
            break

        test_content = poc_result.get("test_file_content", "")
        if not test_content:
            break

        # Safety check
        violations = safety_check(test_content)
        if violations:
            print(f"    [SAFETY] Blocked: {violations}")
            return {
                "finding_id":      fid,
                "status":          "blocked",
                "violations":      violations,
                "runtime_level":   0,
                "repair_attempts": 0,
                "analyzed_at":     ts,
            }

        # Write test file
        ext = ".rs"  # Soroban/Rust
        test_path = POC_DIR / f"{fid}_test{ext}"
        test_path.write_text(test_content)

        run_command = poc_result.get("run_command",
                                    f"cargo test --manifest-path {POCS_DIR / 'k2' / fid / 'Cargo.toml'} -- --nocapture")

        rc, stdout, stderr = run_test(run_command)
        repair_count = attempt

        if COMPILE_ERROR_RE.search(stderr) and attempt < 3:
            print(f"    compile error on attempt {attempt + 1} — repairing...")
            compiler_err = stderr
            continue
        break

    # Determine status
    if not test_content:
        status = "inconclusive"
        level  = poc_result.get("runtime_level", 0) if poc_result else 0
    elif violations := safety_check(test_content):
        status, level = "blocked", 0
    elif rc == 0 and ("BUG CONFIRMED" in stdout or "PASS" in stdout or "ok" in stdout.lower()):
        status = "proved"
        level  = poc_result.get("runtime_level", 1)
    elif COMPILE_ERROR_RE.search(stderr):
        status = "failed"
        level  = 0
    else:
        status = "harness_only"
        level  = poc_result.get("runtime_level", 1)

    result = {
        "finding_id":             fid,
        "runtime_level":          poc_result.get("runtime_level", level) if poc_result else level,
        "status":                 status,
        "real_function_called":   poc_result.get("real_function_called", False),
        "public_entrypoint_called": poc_result.get("public_entrypoint_called", False),
        "copied_logic_used":      poc_result.get("copied_logic_used", True),
        "test_file_path":         str(POC_DIR / f"{fid}_test.rs"),
        "test_file_content":      test_content[:3000],
        "run_command":            poc_result.get("run_command", "") if poc_result else "",
        "assertion":              poc_result.get("assertion", "") if poc_result else "",
        "stdout_excerpt":         stdout[:2000],
        "stderr_excerpt":         stderr[:2000],
        "limitations":            poc_result.get("limitations", []) if poc_result else [],
        "next_upgrade":           poc_result.get("next_upgrade", "") if poc_result else "",
        "repair_attempts":        repair_count,
        "analyzed_at":            ts,
    }

    print(f"    → level={result['runtime_level']} status={status} repairs={repair_count}")
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Runtime PoC Execution Agent")
    parser.add_argument("--finding-id", default=None)
    parser.add_argument("--all",   action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if not args.finding_id and not args.all:
        parser.print_help()
        return 1

    POC_DIR.mkdir(parents=True, exist_ok=True)
    output_path = POC_DIR / "results.jsonl"

    merged      = load_merged_findings()
    exploit_map = load_exploitability_models()
    existing    = load_existing(output_path)
    findings    = load_all_triage_findings(args.finding_id)

    if not findings:
        print(f"[error] No findings found{f' for {args.finding_id}' if args.finding_id else ''}")
        return 1

    print(f"Runtime PoC — {len(findings)} finding(s)\n")

    results: dict[str, dict] = {**existing}
    new_results = []

    for triage in findings:
        fid          = triage.get("finding_id", "")
        original     = merged.get(fid, {})
        exploit_model = exploit_map.get(fid, {"exploitability_score": 0})
        result = process_finding(triage, original, exploit_model, existing, args.force)
        results[fid] = result
        new_results.append(result)

    write_jsonl(results, output_path)

    # Summary table
    print(f"\n{'='*65}")
    print(f"  {'Finding':<12} {'Level':<7} {'Status':<14} {'Repairs'}")
    print(f"  {'-'*55}")
    for r in new_results:
        print(f"  {r['finding_id']:<12} {r.get('runtime_level', '-'):<7} "
              f"{r.get('status', '?'):<14} {r.get('repair_attempts', 0)}")
    print(f"\n  Written → {output_path}")

    import subprocess as _sp
    _sp.run([sys.executable, str(Path(__file__).resolve().parent / "generate_status.py")],
            check=False, capture_output=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
