#!/usr/bin/env python3
"""P296 — verification-agent loop (RESEARCH-ONLY, ADVISORY, UN-WIRED).

Drives the P295 PoC backlog: emit a per-locus build-spec -> a PoC is produced (by ANY means: subagent / in-session /
manual /poc writer) under pocs/p296/<audit>__<id>/ -> the P294 executed-PoC verifier JUDGES it. The verifier is the
SOLE confirmer; any builder self-report (agent_report.json) is recorded as `agent_claimed` but never trusted.
A verifier-PASS whose manifest lacks an `assertion_map` (tying the assertion back to the candidate) is flagged
`confirmed_but_unmapped` and is NOT a clean confirmation. confirmed-FP = 0 is tied to verifier-confirmed only.

  emit   -> writes build_specs.json + pocs/p296/<id>/SPEC.md
  judge  -> runs the verifier over pocs/p296/* + updates loop_results / funnel / backlog
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/research"))
import executed_poc_verifier as epv  # noqa: E402

CFG = json.loads((ROOT / "config/research_verification_agent_loop.json").read_text())
PHASE = ROOT / "documentation/research/assisted_mode/p296_verification_agent_loop"
OUT = PHASE / "outputs"
TARGET_ROOT = ROOT / CFG["target_root"]
REFUTATION_CONTROL = ("salty-Pools-deposit-callback", "pocs/p290/salty-2024-01-holdout/Pools_deposit")
_STAMP = {"research_only": True, "is_gate": False, "emits_findings": False, "severity": None, "reportable": False,
          "submission_ready": False, "concluded": False, "production_routing": False, "auto_submitted": False}


def _slug(audit, awarded_id):
    return f"{audit}__{awarded_id}"


def emit_specs():
    OUT.mkdir(parents=True, exist_ok=True)
    specs = []
    for loc in CFG["tractable_allowlist"]:
        slug = _slug(loc["audit"], loc["awarded_id"])
        target = f"{CFG['target_root']}/{slug}"
        spec = {**_STAMP, "audit": loc["audit"], "awarded_id": loc["awarded_id"], "locus": loc["locus"],
                "mechanism_hint": loc["mechanism_hint"],
                "source_paths": [f"audits/{loc['audit']}/{p}" for p in loc["source_paths"]],
                "target_dir": target, "forge_std_lib": CFG["forge_std_lib"],
                "l_levels_contract": CFG["l_levels_contract"], "manifest_schema": CFG["manifest_schema"],
                "tier_c_rules": CFG["safety"]}
        specs.append(spec)
        d = ROOT / target
        d.mkdir(parents=True, exist_ok=True)
        (d / "SPEC.md").write_text(_spec_md(spec))
    (OUT / "build_specs.json").write_text(json.dumps({**_STAMP, "specs": specs}, indent=2))
    print(f"[emit] {len(specs)} build-specs -> {CFG['target_root']}/<audit>__<id>/SPEC.md")
    return specs


def _spec_md(s) -> str:
    return (f"# P296 PoC build-spec — {s['audit']} {s['awarded_id']}\n\n"
            f"**Locus:** `{s['locus']}`\n\n**Mechanism hint (from the recorded reveal/lens notes):**\n"
            f"{s['mechanism_hint']}\n\n**Source to read (read-only):**\n"
            + "".join(f"- `{p}`\n" for p in s["source_paths"])
            + f"\n**Write ONLY under:** `{s['target_dir']}/` (foundry.toml + lib symlink to `{s['forge_std_lib']}` + "
            "test/ + poc_manifest.json). Do NOT edit existing modules, contest source, or answer keys.\n\n"
            "**Tier-C faithfulness:** copy the bug-locus control-flow VERBATIM; mock only what's necessary; forge-std "
            "only; no fork/keys/broadcast.\n\n**L1/L2/L3 contract (required for a confirmation):**\n"
            f"- L1: {s['l_levels_contract']['L1']}\n- L2: {s['l_levels_contract']['L2']}\n"
            f"- L3: {s['l_levels_contract']['L3']}\n\n"
            "**poc_manifest.json (required, incl. `assertion_map` mapping each exploit test's assertion back to THIS "
            "candidate's bug):**\n```json\n" + json.dumps(s["manifest_schema"], indent=2) + "\n```\n\n"
            "Name the exploit test `test_..._PASS_SUPPORTED`. If the mechanism does not reproduce, write a refutation "
            "test and set `exploit_tests: []` — an honest refute is correct, not a failure.\n")


def _agent_claim(poc_dir: Path):
    f = poc_dir / "agent_report.json"
    if f.exists():
        try:
            return json.loads(f.read_text()).get("agent_claimed")
        except Exception:
            return None
    return None


def judge(out: Path = OUT, specs_path: Path | None = None):
    out.mkdir(parents=True, exist_ok=True)
    specs = json.loads((specs_path or (OUT / "build_specs.json")).read_text())["specs"]
    results = []
    for s in specs:
        slug = _slug(s["audit"], s["awarded_id"])
        d = ROOT / CFG["target_root"] / slug
        man = d / "poc_manifest.json"
        row = {"audit": s["audit"], "awarded_id": s["awarded_id"], "locus": s["locus"], "poc_dir": str(d.relative_to(ROOT)),
               "poc_present": man.exists(), "agent_claimed": _agent_claim(d)}
        if not man.exists():
            row.update(verifier_verdict="not_built", attacker_verified=False, clean_confirmation=False)
            results.append(row)
            continue
        rec = epv.verify_poc(d, audit_id=s["audit"], finding_id=f"{s['audit']}-{s['awarded_id']}")
        manifest = json.loads(man.read_text())
        has_map = bool(manifest.get("assertion_map"))
        verified = bool(rec.get("attacker_verified"))
        clean = verified and has_map
        row.update(verifier_verdict=rec.get("status"), attacker_verified=verified,
                   l1=rec.get("l1"), l2=rec.get("l2"), l3=rec.get("l3"), has_assertion_map=has_map,
                   clean_confirmation=clean,
                   confirmed_but_unmapped=(verified and not has_map),
                   runs=[{k: r.get(k) for k in ("test", "passed", "log_ref")} for r in rec.get("runs", [])])
        results.append(row)

    # refutation control (negative check): must NOT confirm
    fid, pd = REFUTATION_CONTROL
    cr = epv.verify_poc(ROOT / pd, finding_id=fid)
    refutation = {"finding_id": fid, "verifier_verdict": cr.get("status"), "attacker_verified": cr.get("attacker_verified")}

    new_confirmed = [r for r in results if r.get("clean_confirmation")]
    attempted = [r for r in results if r["poc_present"]]
    # confirmed-FP (tied to verifier): a clean confirmation that isn't a real awarded locus (all here are awarded) OR
    # the refutation control confirming, OR a verifier-PASS with no assertion map counted as confirmed.
    confirmed_fp = (1 if refutation["attacker_verified"] else 0) + sum(1 for r in results if r.get("confirmed_but_unmapped"))

    pc = CFG["pass_condition"]
    summary = {**_STAMP, "label": "P296_VERIFICATION_AGENT_LOOP",
               "attempted": len(attempted), "new_confirmations": len(new_confirmed),
               "new_confirmed_loci": [f"{r['audit']}:{r['awarded_id']}" for r in new_confirmed],
               "confirmed_but_unmapped": [f"{r['audit']}:{r['awarded_id']}" for r in results if r.get("confirmed_but_unmapped")],
               "refuted_or_setup": [f"{r['audit']}:{r['awarded_id']}" for r in results
                                    if r["poc_present"] and not r.get("clean_confirmation")],
               "not_built": [f"{r['audit']}:{r['awarded_id']}" for r in results if not r["poc_present"]],
               "confirmed_false_positive_count": confirmed_fp,
               "refutation_control": refutation,
               "pass_condition": pc,
               "pass": (len(attempted) >= pc["min_attempted"] and len(new_confirmed) >= pc["min_new_confirmations"]
                        and confirmed_fp == pc["confirmed_fp_must_be"]),
               "results": results}
    (out / "loop_results.json").write_text(json.dumps(summary, indent=2))

    # cumulative recall-of-confirmed: P295 baseline 6 loci + the new clean confirmations
    p295 = json.loads((ROOT / "documentation/research/assisted_mode/p295_recall_of_confirmed_corpus/outputs/recall_funnel.json").read_text())
    base = p295["total_loci_confirmed_by_execution"]
    (out / "recall_funnel.json").write_text(json.dumps({**_STAMP,
        "p295_baseline_confirmed_loci": base, "p296_new_confirmations": len(new_confirmed),
        "new_confirmations_this_run": len(new_confirmed),
        "total_loci_confirmed_by_execution": base + len(new_confirmed),
        "confirmed_false_positive_count": confirmed_fp}, indent=2))
    (out / "guard_report.json").write_text(json.dumps({**_STAMP, "module": "verification_agent_loop",
        "verifier_is_sole_confirmer": True, "confirmed_false_positive_count": confirmed_fp,
        "every_clean_confirmation_has_log_and_map": all(
            r.get("has_assertion_map") and any(x.get("passed") and x.get("log_ref") for x in r.get("runs", []))
            for r in new_confirmed)}, indent=2))
    print(json.dumps({k: summary[k] for k in ("attempted", "new_confirmations", "new_confirmed_loci",
                      "confirmed_but_unmapped", "refuted_or_setup", "not_built",
                      "confirmed_false_positive_count", "pass")}, indent=2))
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["emit", "judge"])
    ap.add_argument("--out-dir", default=None, help="phase outputs dir (default P296); judge writes the cumulative "
                    "result here. Specs are always read from the P296 emit location.")
    a = ap.parse_args()
    if a.cmd == "emit":
        emit_specs()
    else:
        out = (ROOT / a.out_dir) if a.out_dir else OUT
        judge(out=out, specs_path=OUT / "build_specs.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
