#!/usr/bin/env python3
"""P112 — One full assisted dry-run, end-to-end coherence test (research-only, UN-WIRED).

Carries ONE already-safe, confirmed candidate — IQ-AI M-01 (P104) — through every assisted runbook stage
(A intake -> B validate -> C.0 harness-prep -> C PoC handoff -> D submission package -> E human gate -> F outcome)
and proves the path is COHERENT: all artifacts present, NO status leakage, NO auto-submit, ends at
READY_FOR_HUMAN_REVIEW only. This is a WORKFLOW test, not a discovery test — M-01 already has a confirmed runtime
PoC, source trace, defense map, reproduction output, and a mitigation regression (under p104/), all referenced
read-only. The IQ-AI source is NOT mutated and the PoC is NOT re-run (the P104/P109 executed reproduction_output.txt
is the attached runtime evidence).

Reuses the stage components read-only: validate_candidate_invariant, harness_prep (P111), record_assisted_outcome,
funnel. Sets no severity/submission state of its own; `submitted` stays false and `human_final_gate` stays PENDING.

Usage:
    python scripts/assisted/assisted_dry_run.py --self-test
    python scripts/assisted/assisted_dry_run.py --run
"""
from __future__ import annotations

import argparse
import json
import hashlib
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))
sys.path.insert(0, str(ROOT / "scripts" / "investigation"))
import validate_candidate_invariant as V   # noqa: E402  (B validation; read-only)
import harness_prep as HP                   # noqa: E402  (C.0 harness prep, P111; read-only)
import record_assisted_outcome as RO        # noqa: E402  (F outcome recorder; read-only — .validate only)
import funnel as FN                          # noqa: E402  (pipeline status; read-only)

FLAGS = {
    "is_gate": False,
    "research_only": True,
    "review_only": True,
    "routes_in_production": False,
    "routed_manifest_ids": [],
}

ASSISTED = ROOT / "documentation" / "research" / "assisted_mode"
P104 = ASSISTED / "p104"
DEFAULT_OUT = ASSISTED / "p112_dry_run"

# tokens that must NOT appear anywhere in the dry-run artifacts (no auto-submit / no status leakage)
LEAK_TOKENS = ('"submitted": true', "APPROVED_TO_SUBMIT", '"submission_status": "SUBMITTED"', "SUBMITTED_AT")
# internal/tool language forbidden in the PLATFORM-FACING report body (submission_draft + optional_platform_fields)
NON_NEUTRAL = ("audit-watch", "funnel", "detector", "scanner", "eval", "blind", "phase ", "p104", "p109",
               "assisted-mode", "research-only", "self-kill", "harness_prep", "rank_signal")

CANDIDATE = {"subject": "iq-ai-2025-01", "contract": "LiquidityManager", "function": "moveLiquidity",
             "candidate_id": "iq-ai-2025-01__LiquidityManager_moveLiquidity"}


@lru_cache(maxsize=1)
def _cfg() -> Dict[str, Any]:
    return {"candidate": dict(CANDIDATE)}


def _sha12(path: Path) -> Optional[str]:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()[:12]
    except OSError:
        return None


# ---------------------------------------------------------------------------- A. intake + evidence (from P104)

def build_intake() -> Dict[str, Any]:
    return {
        **FLAGS,
        "subject": CANDIDATE["subject"], "repo": "iq-ai", "commit": "db0d369b",
        "contract": CANDIDATE["contract"], "function": CANDIDATE["function"], "entrypoint": "moveLiquidity",
        "candidate_invariant": ("moveLiquidity migrates the bootstrap liquidity into a protocol-created pool at the "
                                "protocol's intended trading fee; it must not adopt an externally pre-created pool "
                                "whose fee/price an attacker chose"),
        "suspected_break": ("addLiquidityToFraxswap uses getPair(currency,agent) and adopts any pre-existing pair, "
                            "setting the intended fee only in the create-branch; createPair is permissionless"),
        "affected_actor": "the agent and its LPs (lost ongoing swap-fee revenue)",
        "attacker_or_trigger_actor": "any EOA that pre-creates the pair before the permissionless migration",
        "source_refs": ["src/LiquidityManager.sol:moveLiquidity", "src/LiquidityManager.sol:addLiquidityToFraxswap"],
        "expected_impact": "migrated pool charges the attacker's fee (1 bps) instead of the intended 100 bps",
        "confidence": "high", "supplied_by": "p112_dry_run (workflow coherence test)",
        # Stage B validates the invariant (POC_HANDOFF). NB: requesting SUBMISSION_PACKAGE here correctly returns
        # BLOCKED_SCOPE_OR_DUPLICATE_PENDING — scope/duplicate are human determinations handled at stages D/E, not B.
        "requested_check": "POC_HANDOFF",
    }


def build_evidence() -> Dict[str, Any]:
    """The P104-derived evidence blocks that the validator requires to reach VALIDATED_FOR_POC_HANDOFF."""
    return {
        "depth_trace": {
            "localized_mechanism": "LiquidityManager.addLiquidityToFraxswap getPair(currency,agent) adopt-vs-create",
            "controlled_inputs": "attacker pre-creates the (currency,agent) Fraxswap pair at 1 bps before migration",
            "pre_state": "no protocol pair yet; attacker createPair sets a low fee + skewed reserves",
            "operation_trace": ("moveLiquidity -> addLiquidityToFraxswap; getPair returns the attacker pair -> the "
                                "else-branch adopts it; the intended fee is applied only in the create-branch"),
            "boundary_cases": "migrated pool fee = attacker 1 bps vs intended 100 bps; permissionless trigger",
            "post_state": "the live trading pool charges the attacker's fee for the life of the pool",
            "concrete_outcome": "PASS",
        },
        "adversarial_ordering": {
            "relied_upon_invariant": "migration uses a protocol-created pair at the intended fee",
            "mechanism_class": "ordering_race",
            "counterexample_found": True,
            "counterexample_trace": ("attacker createPair(currency,agent,1bps) BEFORE anyone calls the permissionless "
                                     "moveLiquidity -> migration adopts the attacker pair (reproduced on a Fraxtal fork)"),
        },
        "impact_assessment": {
            "impact_class": "medium", "proven_magnitude": "significant",
            "source_true": True, "source_backed": True,
            "material_consequence": ["reward_loss_not_recoverable", "protocol_loss"],
        },
    }


# ---------------------------------------------------------------------------- D. submission package (runbook D)

def _submission_package(poc: Dict[str, Any]) -> Dict[str, str]:
    draft = (
        "# Permissionless liquidity migration adopts an attacker-pre-created pool, bypassing the intended fee\n\n"
        "**Severity: Medium.** Subject: IQ-AI @ `db0d369b`.\n\n"
        "## Summary\n"
        "`LiquidityManager.moveLiquidity` is permissionless and migrates the bootstrap liquidity to Fraxswap via "
        "`addLiquidityToFraxswap`, which calls `getPair(currency, agent)` and **adopts any pre-existing pair**, "
        "applying the protocol's intended fee only when it has to create the pair. Because `createPair` is "
        "permissionless, an attacker can pre-create the `(currency, agent)` pair with an attacker-chosen fee and "
        "skewed reserves before migration; the protocol then migrates into the attacker's pool at the attacker's fee.\n\n"
        "## Root cause\n"
        "- `moveLiquidity()` — external, no access control.\n"
        "- `addLiquidityToFraxswap()` — the pair-exists branch never checks the existing pair's fee equals the "
        "intended `fee`, nor that the pair was protocol-created; the intended fee is set only in the create branch.\n"
        "- `createPair` is permissionless on the external Fraxswap factory.\n\n"
        "## Attack scenario\n"
        "1. An agent's bootstrap pool reaches its end-criterion.\n"
        "2. An attacker (no protocol role) calls `fraxswapFactory.createPair(currency, agent, lowFee)`.\n"
        "3. Anyone calls `moveLiquidity()`; the migration adopts the attacker's pair.\n"
        "4. The live trading pool charges the attacker's fee and started at the attacker's price.\n\n"
        "## Impact\n"
        "The migrated pool charges the attacker's swap fee (**1 bps** in the proof) instead of the intended "
        "**100 bps** — roughly 99% of ongoing swap-fee revenue to the agent/LPs is lost for the life of the pool, "
        "and the attacker controls the pool's initial price/reserves. Bounded to fee revenue + migration mispricing "
        "→ **Medium**.\n\n"
        "## Recommended mitigation\n"
        "In the pair-exists branch, reject a pre-existing pair whose fee differs from intent:\n"
        "```solidity\nrequire((10_000 - fraxswapPair.fee()) == fee, \"unexpected pre-existing pair fee\");\n```\n"
        "(or restrict pair creation / require the pair be protocol-created, and add slippage/min-out guards to the "
        "alignment swaps).\n"
    )
    evidence = (
        "# Evidence bundle\n\n"
        "- Subject/commit: IQ-AI @ `db0d369b`; in-scope `src/LiquidityManager.sol` sha256(first14) `9a68efe4b6664f`.\n"
        f"- PoC: `{poc['test_file']}` — `{poc['test_command']}`.\n"
        f"- Vulnerable-source result: {poc['vulnerable_result']}.\n"
        f"- Mitigation regression: {poc['patched_result']} (source restored to `9a68efe4b6664f` afterward).\n"
        f"- Unrelated tests: {poc['unrelated_tests_result']}.\n"
        f"- Runtime evidence file: `{poc['runtime_evidence_path']}` (sha256:12 `{poc['runtime_evidence_sha']}`), "
        "executed on a Fraxtal mainnet fork @ block 12,918,968.\n"
        "- No external/answer-key dependence; derived and reproduced from source.\n"
    )
    gate = (
        "# Pre-submission gate (reject-first)\n\n"
        "- [x] Executable PoC reproduces on vulnerable source; minimal patch validated; source restored.\n"
        "- [x] Impact bounded and source-backed (Medium); no overclaim.\n"
        "- [x] Report body is platform-neutral.\n"
        "- [ ] **Scope** — PENDING human determination.\n"
        "- [ ] **Duplicate / publicly-known** — PENDING human determination.\n"
        "- [ ] **Program severity tier** — PENDING human determination.\n\n"
        "**Verdict: READY_FOR_HUMAN_REVIEW** — the only open items are human scope/duplicate/program-rule checks. "
        "Not submitted.\n"
    )
    reviewer = (
        "# Reviewer notes (INTERNAL)\n\n"
        "_Assisted-mode caveat: this candidate was prepared by an assisted research workflow; a human must own "
        "scope, duplicate, program severity tier, and the submit decision. Nothing here is submitted._\n\n"
        "- Why real: the exploit reproduces on a Fraxtal fork (intended feeBps 100 → adopted 1); the minimal guard "
        "makes the migration revert on the attacker pair while a clean migration still succeeds.\n"
        "- Why Medium: bounded to lost swap-fee revenue + attacker-controlled migration price; no direct theft of "
        "user principal.\n"
        "- What to run: the documented `forge test` command on the pinned commit; then the patch regression; restore "
        "source and verify the hash.\n"
    )
    fields = (
        "# Optional platform fields (DRAFT — NOT FINAL)\n\n"
        "- Title: Permissionless liquidity migration adopts an attacker-pre-created pool, bypassing the intended fee\n"
        "- Severity (proposed, conservative): Medium\n"
        "- Affected contract: LiquidityManager (`moveLiquidity` / `addLiquidityToFraxswap`)\n"
        "- Impact class: lost protocol/LP swap-fee revenue + attacker-controlled migration price\n"
    )
    return {"submission_draft.md": draft, "evidence_bundle.md": evidence, "pre_submission_gate.md": gate,
            "reviewer_notes.md": reviewer, "optional_platform_fields.md": fields}


# ---------------------------------------------------------------------------- the dry-run

def run_dry_run(out_dir: Path, write: bool = True) -> Dict[str, Any]:
    out_dir = Path(out_dir)
    checks: Dict[str, Any] = {}
    artifacts: Dict[str, str] = {}

    # --- A. intake
    intake = build_intake()
    checks["1_intake_present"] = bool(intake.get("candidate_invariant"))

    # --- B. validation (reuse validate_candidate_invariant read-only)
    vres = V.validate({**intake, **build_evidence()})
    validation = {"decision": vres.decision, "reason": vres.reason}
    checks["2_validation_present_and_validated"] = (vres.decision == V.VALIDATED)

    # --- C.0 harness prep (reuse P111 read-only)
    prep = HP.prepare(CANDIDATE["subject"], CANDIDATE["contract"], CANDIDATE["function"])
    checks["3_harness_prep_present"] = bool(
        prep["harness_classification"] == "HARNESS_COMPLEX" and prep["scaffold_inert"])

    # --- C. PoC handoff (reference existing P104 evidence, read-only; no re-run)
    repro = P104 / "reproduction_output.txt"
    poc = {
        "poc_status": "REPRODUCED",
        "test_file": "p104/M01PreCreatePairPoC.t.sol",
        "test_command": "forge test --match-test test_M01_attacker_precreate_low_fee_is_adopted --evm-version cancun",
        "vulnerable_result": "exploit reproduced (intended feeBps 100, attacker-adopted feeBps 1)",
        "patched_result": "PASS (guard reverts on the attacker pair; clean migration still succeeds)",
        "unrelated_tests_result": "PASS",
        "minimal_patch_validated": True,
        "source_chain_complete": True,
        "unsupported_claims_present": False,
        "runtime_evidence_path": "documentation/research/assisted_mode/p104/reproduction_output.txt",
        "runtime_evidence_sha": _sha12(repro),
        "runtime_evidence_provenance": "executed P104; re-executed live in P109",
    }
    checks["4_poc_handoff_present_runtime_attached"] = bool(
        poc["poc_status"] == "REPRODUCED" and repro.is_file() and poc["runtime_evidence_sha"])

    # --- D. submission package (runbook D)
    pkg = _submission_package(poc)
    body = (pkg["submission_draft.md"] + "\n" + pkg["optional_platform_fields.md"]).lower()
    platform_neutral = not any(tok in body for tok in NON_NEUTRAL)
    checks["5_submission_package_generated"] = (len(pkg) == 5 and platform_neutral)

    # --- E. human gate (reached, NOT completed)
    final_human_gate = "PENDING"
    checks["6_human_gate_reached_not_completed"] = (final_human_gate == "PENDING")

    # --- F. outcome — funnel pipeline status + recorder behaviour (no write, submitted false)
    record = {
        "record_id": CANDIDATE["candidate_id"], "subject": CANDIDATE["subject"],
        "contract": CANDIDATE["contract"], "function": CANDIDATE["function"],
        "conversion": "CLEAN_HIT", "severity_gate": "passed", "adversarial_result": "PASS", "severity_fp": False,
        "poc": {k: poc[k] for k in ("poc_status", "test_file", "test_command", "vulnerable_result",
                                    "patched_result", "minimal_patch_validated", "unrelated_tests_result",
                                    "source_chain_complete", "unsupported_claims_present")},
        "submission": {"submission_status": "READY_FOR_HUMAN_REVIEW",
                       "evidence_bundle_path": str(out_dir / "submission_package" / "evidence_bundle.md"),
                       "pre_submission_gate_path": str(out_dir / "submission_package" / "pre_submission_gate.md"),
                       "duplicate_check_status": "PENDING", "scope_check_status": "PENDING",
                       "severity_check_status": "SUPPORTED", "final_human_gate": final_human_gate},
    }
    pipeline_status = FN.compute_pipeline_status(record)
    checks["8_outcome_ready_for_human_review_only"] = (pipeline_status == "SUBMISSION_READY_HUMAN_REVIEW")

    # recorder: a NON-submitted ready record is RECORD_OK; an attempt to submit without APPROVED is BLOCKED.
    ready_outcome = {**FLAGS, "candidate_id": CANDIDATE["candidate_id"], "subject": CANDIDATE["subject"],
                     "source_mode": "assisted", "human_final_gate": "PENDING", "submitted": False,
                     "outcome": "pending", "submission_status": "READY_FOR_HUMAN_REVIEW",
                     "poc_status": "REPRODUCED", "claimed_severity": "medium"}
    ro_ready = RO.validate(ready_outcome)
    ro_probe = RO.validate({**ready_outcome, "submitted": True})  # must be blocked (no APPROVED_TO_SUBMIT)
    checks["7_no_auto_submit"] = bool(
        ro_ready[0] == RO.RECORD_OK and ready_outcome["submitted"] is False
        and ro_probe[0] == RO.BLOCKED_INVALID_GATE)

    # --- safety assertions
    all_blob = json.dumps({"intake": intake, "validation": validation, "harness": {k: v for k, v in prep.items()
                          if k != "scaffold"}, "poc": poc, "record": record,
                          "ready_outcome": ready_outcome}) + "\n".join(pkg.values()) + prep["scaffold"]
    no_leak = not any(tok in all_blob for tok in LEAK_TOKENS)
    no_auto_submit = (record["submission"]["final_human_gate"] == "PENDING"
                      and ready_outcome["submitted"] is False and pipeline_status != "SUBMITTED")
    checks_all = all(checks.values())

    result = {
        **FLAGS,
        "schema": "p112_assisted_dry_run_v1",
        "candidate": dict(CANDIDATE),
        "stages": {
            "A_intake": intake, "B_validation": validation,
            "C0_harness_prep": {"classification": prep["harness_classification"],
                                "scaffold_inert": prep["scaffold_inert"],
                                "required_components": prep["required_components"]},
            "C_poc_handoff": poc,
            "D_submission_package": sorted(pkg.keys()),
            "E_human_gate": {"final_human_gate": final_human_gate, "completed": False},
            "F_outcome": {"pipeline_status": pipeline_status, "recorder_ready": ro_ready[0],
                          "recorder_submit_probe": ro_probe[0], "submitted": False},
        },
        "criteria": checks,
        "safety": {"no_status_leakage": no_leak, "no_auto_submit": no_auto_submit,
                   "platform_neutral_report": platform_neutral},
        "overall_pass": bool(checks_all and no_leak and no_auto_submit),
        "_pkg": pkg, "_prep": prep,
    }
    if write:
        artifacts = _write_bundle(result, out_dir)
        result["artifacts"] = artifacts
    result.pop("_pkg", None)
    result.pop("_prep", None)
    return result


def _write_bundle(result: Dict[str, Any], out_dir: Path) -> Dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "intake.json").write_text(json.dumps(result["stages"]["A_intake"], indent=2) + "\n", encoding="utf-8")
    (out_dir / "validation.json").write_text(json.dumps(result["stages"]["B_validation"], indent=2) + "\n",
                                             encoding="utf-8")
    HP.write_bundle(result["_prep"], out_dir=out_dir / "harness_prep")
    (out_dir / "poc_handoff.json").write_text(json.dumps(result["stages"]["C_poc_handoff"], indent=2) + "\n",
                                              encoding="utf-8")
    pkg_dir = out_dir / "submission_package"
    pkg_dir.mkdir(exist_ok=True)
    for name, body in result["_pkg"].items():
        (pkg_dir / name).write_text(body, encoding="utf-8")
    rep = {k: v for k, v in result.items() if not k.startswith("_")}
    (out_dir / "dry_run_report.json").write_text(json.dumps(rep, indent=2) + "\n", encoding="utf-8")
    (out_dir / "dry_run_report.md").write_text(_render_md(result), encoding="utf-8")
    return {"dir": str(out_dir)}


def _render_md(r: Dict[str, Any]) -> str:
    s = r["stages"]
    L = ["# P112 — Assisted dry-run (IQ-AI M-01): coherence report", "",
         f"**OVERALL PASS: {r['overall_pass']}**  ·  research-only, un-wired. One confirmed candidate carried "
         "intake → human-review, no auto-submit.", "",
         "## Stage path",
         f"- A intake — invariant supplied ✓",
         f"- B validation — `{s['B_validation']['decision']}`",
         f"- C.0 harness prep — `{s['C0_harness_prep']['classification']}` (scaffold inert: "
         f"{s['C0_harness_prep']['scaffold_inert']})",
         f"- C PoC handoff — `{s['C_poc_handoff']['poc_status']}`; runtime evidence "
         f"`{s['C_poc_handoff']['runtime_evidence_path']}` (sha {s['C_poc_handoff']['runtime_evidence_sha']})",
         f"- D submission package — {', '.join(s['D_submission_package'])}",
         f"- E human gate — final_human_gate=`{s['E_human_gate']['final_human_gate']}` (completed: "
         f"{s['E_human_gate']['completed']})",
         f"- F outcome — pipeline status `{s['F_outcome']['pipeline_status']}`; recorder ready "
         f"`{s['F_outcome']['recorder_ready']}`; submit-probe `{s['F_outcome']['recorder_submit_probe']}`; "
         f"submitted={s['F_outcome']['submitted']}",
         "", "## Pass criteria"]
    for k in sorted(r["criteria"]):
        L.append(f"- [{'x' if r['criteria'][k] else ' '}] {k}")
    L += ["", "## Safety",
          f"- no_status_leakage: {r['safety']['no_status_leakage']}",
          f"- no_auto_submit: {r['safety']['no_auto_submit']}",
          f"- platform_neutral_report: {r['safety']['platform_neutral_report']}", "",
          "_The workflow stops at READY_FOR_HUMAN_REVIEW. A human owns scope, duplicate, program severity, and the "
          "submit decision; nothing here is submitted._", ""]
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------- self-test

def _self_test() -> int:
    ok = True

    def chk(cond, m):
        nonlocal ok
        ok &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {m}")

    chk(FLAGS["is_gate"] is False and FLAGS["routes_in_production"] is False, "FLAGS un-wired")

    if not (P104 / "reproduction_output.txt").is_file():
        print("  [SKIP] P104 artifacts absent — cannot run the live M-01 dry-run")
        print("SELF-TEST:", "OK" if ok else "FAILED")
        return 0 if ok else 1

    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="p112_"))
    r = run_dry_run(tmp / "bundle", write=True)
    r2 = run_dry_run(tmp / "bundle2", write=False)

    chk(r["stages"]["B_validation"]["decision"] == "VALIDATED_FOR_POC_HANDOFF", "B -> VALIDATED_FOR_POC_HANDOFF")
    chk(r["stages"]["C0_harness_prep"]["classification"] == "HARNESS_COMPLEX", "C.0 -> HARNESS_COMPLEX")
    chk(r["stages"]["C_poc_handoff"]["poc_status"] == "REPRODUCED", "C -> REPRODUCED with runtime evidence")
    chk(len(r["stages"]["D_submission_package"]) == 5, "D -> 5-file submission package")
    chk(r["stages"]["E_human_gate"]["final_human_gate"] == "PENDING", "E -> human gate PENDING (reached, not done)")
    chk(r["stages"]["F_outcome"]["pipeline_status"] == "SUBMISSION_READY_HUMAN_REVIEW", "F -> READY_FOR_HUMAN_REVIEW")
    chk(r["stages"]["F_outcome"]["recorder_submit_probe"] == "BLOCKED_INVALID_GATE", "submit w/o APPROVED -> BLOCKED")
    chk(all(r["criteria"].values()), "all 8 pass-criteria True")
    chk(r["safety"]["no_status_leakage"] and r["safety"]["no_auto_submit"], "no status leakage / no auto-submit")
    chk(r["safety"]["platform_neutral_report"], "submission report body is platform-neutral")
    chk(r["overall_pass"] is True, "overall_pass")
    # determinism (ignore the write-only artifacts key)
    a = {k: v for k, v in r.items() if k != "artifacts"}
    chk(json.dumps(a, sort_keys=True) == json.dumps(r2, sort_keys=True), "deterministic")
    # bundle files exist
    d = tmp / "bundle"
    for f in ("intake.json", "validation.json", "poc_handoff.json", "dry_run_report.json", "dry_run_report.md"):
        chk((d / f).is_file(), f"bundle file {f} written")
    chk((d / "submission_package" / "submission_draft.md").is_file(), "submission package written")
    chk((d / "harness_prep" / "harness_prep.md").is_file(), "harness_prep bundle written")

    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--out-dir")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    if args.run:
        r = run_dry_run(Path(args.out_dir) if args.out_dir else DEFAULT_OUT)
        print(f"P112 assisted dry-run (IQ-AI M-01) — OVERALL PASS={r['overall_pass']}")
        for k in sorted(r["criteria"]):
            print(f"  [{'x' if r['criteria'][k] else ' '}] {k}")
        print(f"  safety: {r['safety']}")
        print(f"  final pipeline status: {r['stages']['F_outcome']['pipeline_status']} "
              f"(submitted={r['stages']['F_outcome']['submitted']})")
        print(f"  -> {r['artifacts']['dir']}")
        return 0 if r["overall_pass"] else 1
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
