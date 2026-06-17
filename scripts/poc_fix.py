#!/usr/bin/env python3
"""
poc_fix.py — Turn one fix-list item into the next concrete operator action (deterministic, no LLM).

The dashboard says WHAT is blocked; the fix-list says WHY; `poc-fix <finding_id>` says exactly what to DO next
for one finding. It reads the fix-list, identifies the finding's blocker, stages the right next command/bundle,
and writes a per-finding "fix session". It is a router/stager only — it never decides proof (validate_poc.py
remains the source of truth) and never runs the /poc-validation skill automatically.

Reads:
    output/poc_validation/fix_list.json, engagement_report.json, poc_inventory.json,
    collected_results.json, poc_validation_results.json, output/merged_findings.json

Writes:
    output/poc_validation/fix_sessions/<finding_id>.json
    output/poc_validation/fix_sessions/<finding_id>.md

Usage:
    python scripts/poc_fix.py <finding_id>
      [--mode engagement|submission] [--collect-command "forge test --match-test ... -vvv"]
      [--test-file F] [--test-name N] [--overwrite] [--json]
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import poc_validation_prepare  # noqa: E402
import collect_poc_results  # noqa: E402
import poc_engagement_report  # noqa: E402

SEMANTIC_ACTIONS = {"add_reachability_assertion", "add_impact_assertion", "add_negative_control",
                    "write_missing_poc", "manual_review"}
CHECKLISTS = {
    "add_reachability_assertion": [
        "attacker is an unprivileged external EOA (no owner/admin/governance prank)",
        "the public entrypoint the attacker calls is named",
        "the call chain from entrypoint to the vulnerable sink is shown",
        "the relevant guard/modifier is exercised and shown not to block the path",
        "no privileged setup grants the attacker impossible permissions",
    ],
    "add_impact_assertion": [
        "pre-state is read (named slot/balance) before the action",
        "the attacker action is performed via the real path",
        "post-state is read after the action",
        "observed delta is asserted (assertEq/assertGt/...)",
        "expected delta matches the claimed impact",
        "the violated invariant is named",
    ],
    "add_negative_control": [
        "the unauthorized actor's attempt reverts / is rejected",
        "the correct or patched path behaves differently from the vulnerable path",
        "a duplicate path is not double-counted as a second finding",
    ],
    "add_fork_context": [
        "chain (e.g. mainnet / arbitrum)",
        "fork block number (disclosed, pinned)",
        "deployed contract addresses used",
        "starting balances dealt to the attacker",
        "roles / permissions assumed (must be obtainable on-chain)",
        "any mocks used and why they do not manufacture the bug",
    ],
}


def _load_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return default


def _run(module, argv: list[str]) -> int:
    """Run another script's main() in-process, suppressing its stdout (poc_fix owns the output)."""
    old = sys.argv
    sys.argv = [module.__name__] + argv
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            return module.main()
    finally:
        sys.argv = old


def _collect_template(fid: str, test_file: str | None, test_name: str | None, fork: bool = False) -> str:
    tn = test_name or "<test_name>"
    cmd = (f"forge test --match-test {tn} --fork-url $RPC_URL --fork-block-number <BLOCK> -vvv"
           if fork else f"forge test --match-test {tn} -vvv")
    return (f'./run_pipeline.sh poc-collect --finding-id {fid} '
            f'--test-file {test_file or "<test_file>"} --test-name {tn} --command "{cmd}"')


def handle(action: str, fid: str, item: dict, inv: dict, vr: dict, mf: dict, args) -> dict:
    """Return {generated_commands, prepared_bundle_path, checklist, next_operator_step, details}."""
    out = {"generated_commands": [], "prepared_bundle_path": None, "checklist": [],
           "next_operator_step": "", "details": []}
    bundle_rel = f"output/poc_validation/bundles/{fid}.json"

    def stage_bundle():
        _run(poc_validation_prepare, ["--finding-id", fid, "--overwrite"])
        out["prepared_bundle_path"] = bundle_rel
        out["generated_commands"].append(f"python scripts/poc_validation_prepare.py --finding-id {fid} --overwrite")

    if action == "write_missing_poc":
        out["details"] = [
            f"affected functions: {', '.join(inv.get('affected_functions') or []) or '—'}",
            f"affected files: {', '.join(inv.get('affected_files') or []) or '—'}",
            f"manifest refs: {', '.join(item.get('manifest_refs') or inv.get('manifest_refs') or []) or '—'}",
            f"minimum proof goal: {inv.get('minimum_proof_goal') or '—'}",
            f"suggested strategy: {inv.get('suggested_test_strategy') or '—'}",
            f"attacker entrypoint: {inv.get('required_attacker_entrypoint') or '—'}",
            f"impact to assert: {inv.get('required_impact_assertion') or mf.get('impact') or '—'}",
        ]
        suggested = "pocs/foundry/test/" + fid.replace("-", "_") + ".t.sol"
        out["details"].append(f"suggested test path: {suggested}")
        stage_bundle()
        out["generated_commands"].append(_collect_template(fid, args.test_file, args.test_name))
        out["next_operator_step"] = (f"Write the PoC at {suggested} (call the real entrypoint as an unprivileged "
                                     f"EOA, assert the impact), then run poc-collect, then poc-validate.")

    elif action == "add_collected_log":
        tf = args.test_file or item.get("test_file")
        tn = args.test_name or item.get("test_name")
        if args.collect_command:
            cargs = ["--finding-id", fid, "--command", args.collect_command, "--quiet"]
            if tf:
                cargs += ["--test-file", tf]
            if tn:
                cargs += ["--test-name", tn]
            _run(collect_poc_results, cargs)
            out["generated_commands"].append(
                f'python scripts/collect_poc_results.py --finding-id {fid} '
                f'{("--test-file " + tf + " ") if tf else ""}{("--test-name " + tn + " ") if tn else ""}'
                f'--command "{args.collect_command}"  [executed]')
            out["next_operator_step"] = "Collected. Now run: python scripts/validate_poc.py"
        else:
            out["generated_commands"].append(_collect_template(fid, tf, tn))
            out["next_operator_step"] = ("Run the collect command above (fill in <…>), then "
                                         "python scripts/validate_poc.py.")

    elif action in ("add_reachability_assertion", "add_impact_assertion", "add_negative_control", "manual_review"):
        stage_bundle()
        out["checklist"] = (CHECKLISTS.get(action) or [])
        if action == "manual_review":
            out["checklist"] = [f"unresolved: {r}" for r in (item.get("exact_missing_requirements") or [])] \
                or ["no usable proof yet — inspect the finding, source, test, and raw log manually"]
        out["next_operator_step"] = f"Run /poc-validation on {bundle_rel} (apply the checklist), then validate_poc.py."

    elif action == "add_fork_context":
        out["checklist"] = CHECKLISTS["add_fork_context"]
        tf = args.test_file or item.get("test_file")
        tn = args.test_name or item.get("test_name")
        out["generated_commands"].append(_collect_template(fid, tf, tn, fork=True))
        out["next_operator_step"] = ("Convert the test to a fork test with the disclosed assumptions above, "
                                     "then run the collect command and validate_poc.py.")

    elif action == "downgrade_severity":
        supported = vr.get("severity_supported")
        out["details"] = [f"claimed severity: {item.get('severity')}",
                          f"severity supported by the PoC: {supported or 'unproven'}",
                          f"why: {item.get('why_blocked')}"]
        out["next_operator_step"] = (f"Lower the finding's severity to {supported or 'the demonstrated impact'}, "
                                     "OR strengthen the PoC to demonstrate the higher impact, then re-validate.")

    elif action == "remove_invalid_setup":
        warns = vr.get("warnings") or []
        flagged = [w for w in warns if any(k in w for k in
                   ("storage_mutation", "prank_as_privileged", "mock", "fork_without_disclosed"))]
        out["details"] = [f"invalid-setup signals: {', '.join(flagged) or 'see why_blocked'}",
                          f"why: {item.get('why_blocked')}"]
        out["next_operator_step"] = ("Remove the setup that manufactures the bug (vm.store / admin prank / "
                                     "result-hardcoding mock); reproduce via the real path, then re-validate.")

    elif action == "resolve_duplicate":
        dup = mf.get("duplicate_of")
        out["details"] = [f"duplicate_of: {dup or '(relationship recorded in triage)'}",
                          f"why: {item.get('why_blocked')}"]
        out["next_operator_step"] = ("Confirm the duplicate relationship; merge into the primary finding or mark "
                                     "duplicate_proof — do not submit twice.")

    elif action == "reject_poc":
        out["details"] = [f"why invalid: {item.get('why_blocked')}",
                          f"failed: {', '.join(item.get('exact_missing_requirements') or []) or '—'}"]
        out["next_operator_step"] = ("Rewrite the PoC to drive the claim on the real path, or close the finding "
                                     "if the claim cannot be substantiated.")

    else:
        out["next_operator_step"] = "Inspect the finding manually — no recognized fix action."
    return out


def load_context(pv: Path, mode: str | None = None, regen: bool = True):
    """Load fix-list + finding artifacts. Returns (er, inv_by, vr_by, mf_by, fix_by, fl, mode).
    If `regen`, (re)generates the fix-list when it's missing or its mode mismatches `mode`."""
    fl = _load_json(pv / "fix_list.json")
    file_mode = (fl or {}).get("mode")
    want_mode = mode or file_mode or "engagement"
    if regen and (fl is None or (mode and mode != file_mode)):
        _run(poc_engagement_report, ["--mode", want_mode, "--quiet"])
        fl = _load_json(pv / "fix_list.json", {"ordered_items": [], "mode": want_mode})
    resolved_mode = (fl or {}).get("mode", want_mode)
    er = _load_json(pv / "engagement_report.json", {"findings": []}) or {"findings": []}
    inv_by = {c["finding_id"]: c for c in (_load_json(pv / "poc_inventory.json", {"candidates": []}) or {}).get("candidates", [])}
    vr_by = {r["finding_id"]: r for r in (_load_json(pv / "poc_validation_results.json", {"results": []}) or {}).get("results", [])}
    mf_by = {f.get("id") or f.get("finding_id"): f
             for f in (_load_json(audit_path("output") / "merged_findings.json", {}) or {}).get("findings", [])}
    fix_by = {it["finding_id"]: it for it in (fl or {}).get("ordered_items", [])}
    return er, inv_by, vr_by, mf_by, fix_by, fl, resolved_mode


def process_finding(fid: str, item: dict, inv_entry: dict, vr: dict, mf: dict, args, mode: str) -> dict:
    """Run the fix handler, write fix_sessions/<fid>.{json,md}, and return the session dict."""
    pv = audit_path("output", "poc_validation")
    action = item.get("recommended_next_action", "manual_review")
    res = handle(action, fid, item, inv_entry or {}, vr or {}, mf or {}, args)
    session = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "finding_id": fid,
        "title": item.get("title", ""),
        "mode": mode,
        "current_bucket": item.get("current_bucket"),
        "recommended_next_action": action,
        "why_blocked": item.get("why_blocked"),
        "exact_missing_requirements": item.get("exact_missing_requirements", []),
        "generated_commands": res["generated_commands"],
        "prepared_bundle_path": res["prepared_bundle_path"],
        "checklist": res["checklist"],
        "next_operator_step": res["next_operator_step"],
        "details": res["details"],
    }
    sess_dir = pv / "fix_sessions"
    sess_dir.mkdir(parents=True, exist_ok=True)
    (sess_dir / f"{fid}.json").write_text(json.dumps(session, indent=2))

    md = [f"# Fix session — {fid} ({mode} mode)", "", f"_generated {session['generated_at']}_", "",
          f"**{item.get('title','')}** · severity {item.get('severity')} · bucket `{session['current_bucket']}`", "",
          f"**Next action:** `{action}`", "", f"**Why blocked:** {session['why_blocked']}", ""]
    if session["exact_missing_requirements"]:
        md += ["**Missing requirements:** " + ", ".join(session["exact_missing_requirements"]), ""]
    if res["details"]:
        md += ["## Details", ""] + [f"- {d}" for d in res["details"]] + [""]
    if res["checklist"]:
        md += ["## Checklist", ""] + [f"- [ ] {c}" for c in res["checklist"]] + [""]
    if res["generated_commands"]:
        md += ["## Commands", "", "```"] + res["generated_commands"] + ["```", ""]
    if res["prepared_bundle_path"]:
        md += [f"**Bundle staged:** `{res['prepared_bundle_path']}` — "
               f"run `/poc-validation` on it (the skill writes reviewer notes; the validator decides proof).", ""]
    md += ["## Next operator step", "", res["next_operator_step"], ""]
    (sess_dir / f"{fid}.md").write_text("\n".join(md) + "\n")
    return session


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("finding_id", nargs="?", help="finding to stage the next fix action for")
    ap.add_argument("--mode", choices=["engagement", "submission"], default=None)
    ap.add_argument("--collect-command", default=None)
    ap.add_argument("--test-file", default=None)
    ap.add_argument("--test-name", default=None)
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--json", action="store_true", dest="as_json")
    args = ap.parse_args()

    if not args.finding_id:
        print("usage: poc_fix.py <finding_id> [--mode …] [--collect-command …] [--json]", file=sys.stderr)
        return 2
    fid = args.finding_id
    pv = audit_path("output", "poc_validation")
    er, inv_by, vr_by, mf_by, fix_by, fl, mode = load_context(pv, args.mode)

    item = fix_by.get(fid)
    if item is None:
        # not on the fix-list: either already ready, eval-only, or unknown
        rec = next((f for f in er.get("findings", []) if f["finding_id"] == fid), None)
        if rec is None:
            print(f"[poc_fix] unknown finding '{fid}' — not in this audit's PoC inventory.", file=sys.stderr)
            return 2
        bucket = rec.get("bucket")
        msg = ("already submission-ready — nothing to fix." if bucket == "submission_ready"
               else "eval-only — no PoC required." if bucket == "eval_only_not_required"
               else f"in bucket '{bucket}' — no fix action staged.")
        print(f"[poc_fix] {fid}: {msg}")
        return 0

    session = process_finding(fid, item, inv_by.get(fid, {}), vr_by.get(fid, {}), mf_by.get(fid, {}), args, mode)
    res = session  # session carries the same fields used below

    if args.as_json:
        print(json.dumps(session, indent=2))
    else:
        print(f"[poc_fix] {fid} ({mode}): {session['recommended_next_action']}")
        print(f"  why: {session['why_blocked']}")
        for c in res["generated_commands"]:
            print(f"  $ {c}")
        if res["prepared_bundle_path"]:
            print(f"  → Run /poc-validation on {res['prepared_bundle_path']}")
        print(f"  next: {res['next_operator_step']}")
        print(f"  session: {pv / 'fix_sessions' / (fid + '.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
