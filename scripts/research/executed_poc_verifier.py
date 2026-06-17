#!/usr/bin/env python3
"""P294 — executed-PoC verification hook (the FP oracle). RESEARCH-ONLY, ADVISORY, UN-WIRED.

Inverts the FP economics: instead of a fail-closed pattern gate, precision comes from PROOF. A candidate is
"confirmed" ONLY when a declared EXPLOIT test in its pocs/<id>/ dir actually runs under `forge` and PASSes AND
satisfies L1+L2+L3. `attacker_verified` is derived from the real run + a deterministic structural parse of the test
source — never from a self-asserted "proved" field and never from an assertion-string scan of intent.

Exploit/refutation polarity is AUTHOR-DECLARED in pocs/<id>/poc_manifest.json (exploit_tests/refutation_tests/
control_tests), so a refutation PoC that forge-PASSes (it proves the bug is ABSENT, e.g. salty Pools.deposit) is
correctly NOT confirmed. The execution itself reuses the deterministic collect_poc_results.py runner.

Authority: never submits, never sets severity/reportable/submission_ready, un-wired from confirm_gate/min_confirm_gate.
Safety: local forge only; no mainnet/keys/broadcast; writes only under pocs/ + output/poc_validation/.

Importable: verify_poc(poc_dir, audit_id=None, finding_id=None) -> verification_record (advisory-stamped).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "config/research_executed_poc_verifier.json").read_text())
FORGE_TIMEOUT = int(CFG["forge_timeout_seconds"])
L1_ATTACKER = [m.lower() for m in CFG["l1_attacker_markers"]]
L2_FLIP = [m.lower() for m in CFG["l2_state_flip_markers"]]
L3_ASSERT = [m.lower() for m in CFG["l3_outcome_assert_markers"]]
COPIED = [m.lower() for m in CFG["copied_logic_markers"]]
FORBIDDEN_FLAGS = CFG["safety"]["forbidden_forge_flags"]
_FORGE_PASS = re.compile(r"\[PASS\]\s+([A-Za-z_]\w*)")
_FORGE_FAIL = re.compile(r"\[FAIL[^]]*\]\s+([A-Za-z_]\w*)")

# advisory contract — hard-stamped on every record (mirrors the research-platform invariants)
_STAMP = {"is_gate": False, "research_only": True, "emits_findings": False, "routes_in_production": False,
          "routed_manifest_ids": [], "severity": None, "reportable": False, "submission_ready": False,
          "concluded": False, "production_routing": False, "auto_submitted": False}


def _now():
    return datetime.now(timezone.utc).isoformat()


def _test_file(poc_dir: Path) -> Path | None:
    cands = sorted((poc_dir / "test").glob("*.t.sol")) if (poc_dir / "test").is_dir() else []
    if not cands:
        cands = sorted(poc_dir.rglob("test/*.t.sol"))
    # ignore the forge-std library's own tests
    cands = [c for c in cands if "lib/forge-std" not in str(c)]
    return cands[0] if cands else None


def _fn_body(src: str, fn: str) -> str:
    """Extract a test function body by brace-matching (deterministic; tolerant of formatting)."""
    m = re.search(r"function\s+" + re.escape(fn) + r"\s*\([^)]*\)[^{]*\{", src)
    if not m:
        return ""
    i = m.end() - 1
    depth = 0
    for j in range(i, len(src)):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                return src[i:j + 1]
    return src[i:]


def _l_levels(body: str) -> dict:
    """Deterministic L1/L2/L3 structural parse of one test-function body (lowercased)."""
    b = body.lower()
    l1 = any(m in b for m in L1_ATTACKER) and ("(" in b)            # attacker entry + a call
    # L2: a before/after state flip — either vm.load, or two reads of state asserted to differ (before/after vars),
    # or a balance read compared. Require at least one flip marker AND at least one assertion present.
    flip = any(m in b for m in L2_FLIP)
    has_assert = any(m in b for m in L3_ASSERT)
    l2 = flip and has_assert
    l3 = has_assert                                                 # an outcome assertion is present
    copied = any(m in b for m in COPIED)
    return {"l1": bool(l1 and not copied), "l2": bool(l2), "l3": bool(l3), "copied_logic": copied}


def _safe_command(cmd: str) -> bool:
    c = cmd.lower()
    return not any(f.lower() in c for f in FORBIDDEN_FLAGS)


def _run_forge(poc_dir: Path, test_fn: str) -> dict:
    """Execute one test via forge (local only). Returns {passed, raw_log, run_command, exit_code}."""
    # forge --match-test is a regex over the test name; a trailing `$` excludes the implicit `()` and makes forge
    # report "no tests match", so anchor the START with a word boundary — exact and collision-free.
    cmd = ["forge", "test", "--match-test", rf"^{test_fn}\b", "-vv"]
    run_command = " ".join(cmd)
    if not _safe_command(run_command):
        return {"passed": False, "raw_log": "REFUSED: unsafe forge flags", "run_command": run_command, "exit_code": -2}
    try:
        p = subprocess.run(cmd, cwd=str(poc_dir), capture_output=True, text=True, timeout=FORGE_TIMEOUT)
        blob = (p.stdout or "") + "\n" + (p.stderr or "")
        passed = (f"[PASS] {test_fn}" in blob) or bool(re.search(r"\[PASS\]\s+" + re.escape(test_fn) + r"\b", blob))
        failed = bool(re.search(r"\[FAIL[^]]*\]\s+" + re.escape(test_fn) + r"\b", blob))
        return {"passed": bool(passed and not failed and p.returncode == 0), "raw_log": blob,
                "run_command": run_command, "exit_code": p.returncode}
    except subprocess.TimeoutExpired:
        return {"passed": False, "raw_log": "TIMEOUT", "run_command": run_command, "exit_code": -1}
    except FileNotFoundError:
        return {"passed": False, "raw_log": "forge not found", "run_command": run_command, "exit_code": -3}


def _write_log(finding_id: str, test_fn: str, blob: str) -> str:
    out = ROOT / "output/poc_validation/raw"
    out.mkdir(parents=True, exist_ok=True)
    p = out / f"p294_{finding_id}_{test_fn}.log"
    p.write_text(blob)
    return str(p.relative_to(ROOT))


def verify_poc(poc_dir, audit_id=None, finding_id=None) -> dict:
    """Verify one candidate's PoC by ACTUAL execution. attacker_verified is set ONLY by a real exploit-test PASS
    that also satisfies L1+L2+L3. Returns an advisory verification_record."""
    poc_dir = Path(poc_dir)
    finding_id = finding_id or poc_dir.name
    rec = dict(_STAMP, finding_id=finding_id, poc_dir=str(poc_dir), audit_id=audit_id, verified_at=_now(),
               attacker_verified=False, validity_confirmed=False, logic_verified=False, validity_mode=None,
               status="inconclusive", l1=False, l2=False, l3=False,
               exploit_tests=[], refutation_tests=[], control_tests=[], runs=[], evidence_snapshot={},
               source_basis=None)

    man_path = poc_dir / "poc_manifest.json"
    if not man_path.exists():
        rec["status"] = "inconclusive"
        rec["source_basis"] = "no poc_manifest.json (author-declared exploit/refutation intent required)"
        return rec
    man = json.loads(man_path.read_text())
    exploit = man.get("exploit_tests", []) or []
    refute = man.get("refutation_tests", []) or []
    control = man.get("control_tests", []) or []
    validity_mode = man.get("validity_mode", "exploit")
    rec["validity_mode"] = validity_mode
    rec.update(exploit_tests=exploit, refutation_tests=refute, control_tests=control,
               evidence_snapshot={k: man.get(k) for k in ("locus", "attacker_entry", "l2_claim", "claimed_outcome")})

    tf = _test_file(poc_dir)
    if not tf:
        rec["status"] = "inconclusive"
        rec["source_basis"] = "no .t.sol test file found in poc dir"
        return rec
    src = tf.read_text()

    # ---- no declared exploit test -> cannot be confirmed (e.g. a refutation-only PoC like salty Pools.deposit) ----
    if not exploit:
        ran = []
        for fn in refute:
            r = _run_forge(poc_dir, fn)
            r["log_ref"] = _write_log(finding_id, fn, r["raw_log"])
            r.pop("raw_log")
            ran.append({"test": fn, "kind": "refutation", **r})
        rec["runs"] = ran
        all_ref_pass = bool(refute) and all(x["passed"] for x in ran)
        rec["status"] = "refuted_by_execution" if all_ref_pass else "no_exploit_test"
        rec["attacker_verified"] = False
        rec["source_basis"] = ("declared refutation test(s) PASS -> the exploit hypothesis is refuted by execution"
                               if all_ref_pass else "no declared exploit test; refutation not cleanly proven")
        return rec

    # ---- run every declared exploit test; structural L1/L2/L3 from its source; confirm only on REAL pass + levels ----
    runs = []
    levels_all = {"l1": True, "l2": True, "l3": True}
    all_pass = True
    for fn in exploit:
        body = _fn_body(src, fn)
        lv = _l_levels(body) if body else {"l1": False, "l2": False, "l3": False, "copied_logic": False}
        r = _run_forge(poc_dir, fn)
        r["log_ref"] = _write_log(finding_id, fn, r["raw_log"])
        r.pop("raw_log")
        runs.append({"test": fn, "kind": "exploit", "levels": lv, **r})
        all_pass = all_pass and r["passed"]
        for k in ("l1", "l2", "l3"):
            levels_all[k] = levels_all[k] and lv.get(k, False)
    rec["runs"] = runs
    rec.update(l1=levels_all["l1"], l2=levels_all["l2"], l3=levels_all["l3"])

    if not all_pass:
        rec["status"] = "refuted_by_execution"
        rec["source_basis"] = "a declared exploit/bug test did NOT pass under forge -> not demonstrated"
        return rec

    # ---- P299 logic-bug validity mode: a logic/correctness bug has no attacker entry; it is confirmed by a passing
    #      DIFFERENTIAL (the bug test PASSES + a declared corrected-CONTROL PASSES that diverges) + L2(named value/
    #      state) + L3(outcome) + an assertion_map tying the divergence to the awarded bug. L1 is NOT required. The
    #      failing-bug-test case already returned `refuted` above, so logic mode can never rescue a failing bug test. ----
    if validity_mode == "logic_differential":
        ctrl_runs = []
        for fn in control:
            r = _run_forge(poc_dir, fn)
            r["log_ref"] = _write_log(finding_id, fn, r["raw_log"])
            r.pop("raw_log")
            ctrl_runs.append({"test": fn, "kind": "control", **r})
        rec["runs"] = runs + ctrl_runs
        control_pass = bool(control) and all(x["passed"] for x in ctrl_runs)
        has_map = bool(man.get("assertion_map"))
        # The DIFFERENTIAL is the named-value evidence: for a value-correctness bug there is no before/after state
        # flip (L2 is exploit-shaped) — the divergence is the bug test's asserted value vs the corrected control's.
        # So the logic gate = a passing corrected-control + L3(outcome assert in the bug test) + assertion_map.
        if control_pass and levels_all["l3"] and has_map:
            rec["status"] = "confirmed_by_logic_differential"
            rec["validity_confirmed"] = True
            rec["logic_verified"] = True
            rec["source_basis"] = ("logic_differential: bug test + corrected-control both PASS under forge with an "
                                   "L3 outcome assertion and an assertion_map divergence -> the correctness bug is "
                                   "proven by the bug-vs-corrected-reference differential (no attacker entry; the "
                                   "divergence is the named-value evidence)")
            return rec
        rec["status"] = "setup_only"
        miss = []
        if not control_pass:
            miss.append("a passing corrected-control test (the differential)")
        if not has_map:
            miss.append("assertion_map")
        if not levels_all["l3"]:
            miss.append("L3 outcome assertion")
        rec["source_basis"] = ("logic_differential bug test PASSes but missing " + ", ".join(miss)
                               + " -> not a clean differential confirmation")
        return rec

    if not (levels_all["l1"] and levels_all["l2"] and levels_all["l3"]):
        rec["status"] = "setup_only"
        missing = [k.upper() for k in ("l1", "l2", "l3") if not levels_all[k]]
        rec["source_basis"] = f"exploit test PASSes but missing {','.join(missing)} (structural L-levels not all met)"
        return rec
    # all declared exploit tests PASS under forge AND L1+L2+L3 satisfied -> confirmed by proof
    rec["status"] = "confirmed_by_execution"
    rec["attacker_verified"] = True
    rec["validity_confirmed"] = True
    rec["source_basis"] = ("declared exploit test(s) PASS under forge with L1(attacker entry)+L2(named state flip)"
                           "+L3(outcome assert) -> impact proven by execution")
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--poc-dir", required=True)
    ap.add_argument("--audit-id")
    ap.add_argument("--finding-id")
    a = ap.parse_args()
    rec = verify_poc(a.poc_dir, a.audit_id, a.finding_id)
    print(json.dumps(rec, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
