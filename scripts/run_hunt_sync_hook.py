#!/usr/bin/env python3
"""run_hunt_sync_hook.py — P218 mandatory post-stage dashboard-sync hook (research-only, read-only on inputs).

The required end-of-hunt completion step. Runs, in order:
  1. scripts/sync_hunt_findings.py --write --strict   (regenerate the synced mirror from real artifacts)
  2. scripts/validate_hunt_sync_completion.py --strict (fail unless every candidate is current/safe/visible)
Then writes sync metrics. Exits non-zero if either step fails — so a hunt cannot be "complete" with a stale or
incomplete dashboard.

WRITES ONLY:
  * documentation/research/funnel/synced_findings.generated.json  (the generated mirror; backed up first by the wrapper)
  * output_research/funnel/sync_hook_metrics.json                 (sync metrics)
NEVER touches route/submit/promote code, runtime_policy.json, the curated funnel_records.json, or any audit source.
"""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import sync_hunt_findings as shf            # noqa: E402
import validate_hunt_sync_completion as vc  # noqa: E402

DEFAULT_METRICS = ROOT / "output_research/funnel/sync_hook_metrics.json"
DEFAULT_MIRROR = ROOT / "documentation/research/funnel/synced_findings.generated.json"


def main(argv=None):
    ap = argparse.ArgumentParser(description="P218 mandatory hunt dashboard-sync hook")
    ap.add_argument("--phase", required=True)
    ap.add_argument("--audit", required=True)
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--candidate-register", default=None)
    ap.add_argument("--l3-dir", default="output_research/l3_readiness")
    ap.add_argument("--dry-run-queue", default="output_research/dry_run_submission_queue")
    ap.add_argument("--scorecard", default=None)
    ap.add_argument("--out", default=str(DEFAULT_MIRROR))
    ap.add_argument("--metrics", default=str(DEFAULT_METRICS))
    ap.add_argument("--skip-live", action="store_true", help="completion guard data-only (no reader/card checks)")
    args = ap.parse_args(argv)

    common = ["--phase", args.phase, "--audit", args.audit, "--workspace", args.workspace,
              "--l3-dir", args.l3_dir, "--dry-run-queue", args.dry_run_queue]
    if args.candidate_register:
        common += ["--candidate-register", args.candidate_register]
    if args.scorecard:
        common += ["--scorecard", args.scorecard]

    print("[hook] step 1/2: sync_hunt_findings --write --strict")
    rc1 = shf.main(common + ["--out", args.out, "--write", "--strict"])
    if rc1 != 0:
        print("[hook] ABORT — sync wrapper failed; dashboard NOT marked current", file=sys.stderr)
        return rc1

    # write sync metrics BEFORE the guard (so the guard sees them present), then update with the guard result.
    mirror = json.loads(Path(args.out).read_text()) if Path(args.out).exists() else {"findings": []}
    recs = mirror.get("findings", [])
    pop = sum(shf.score_record(r)["populated"] for r in recs)
    tot = sum(shf.score_record(r)["total"] for r in recs)
    metrics = {
        "phase": args.phase, "audit": args.audit, "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "synced_records": len(recs),
        "completeness_pct": (round(100 * pop / tot) if tot else 0),
        "completeness_populated": pop, "completeness_total": tot,
        "all_safety_ok": all(vc._safety_ok(r) for r in recs),
        "wrapper_rc": rc1, "completion_guard_rc": None, "completion_ok": None,
        "mirror": str(Path(args.out).relative_to(ROOT)) if str(args.out).startswith(str(ROOT)) else str(args.out),
        "research_only": True, "review_only": True, "routes_in_production": False, "routing_allowed": False,
    }
    Path(args.metrics).parent.mkdir(parents=True, exist_ok=True)
    Path(args.metrics).write_text(json.dumps(metrics, indent=2) + "\n")

    print("[hook] step 2/2: validate_hunt_sync_completion --strict")
    guard_argv = common + ["--synced-mirror", args.out, "--metrics", args.metrics, "--strict"]
    if args.skip_live:
        guard_argv.append("--skip-live")
    rc2 = vc.main(guard_argv)

    metrics["completion_guard_rc"] = rc2
    metrics["completion_ok"] = rc2 == 0
    Path(args.metrics).write_text(json.dumps(metrics, indent=2) + "\n")
    print(f"[hook] wrote sync metrics → {args.metrics} (records={len(recs)} completeness={metrics['completeness_pct']}% "
          f"safety_ok={metrics['all_safety_ok']} completion_ok={metrics['completion_ok']})")

    if rc2 != 0:
        print("[hook] ABORT — completion guard failed; hunt NOT complete", file=sys.stderr)
        return rc2
    print("[hook] OK — dashboard mirror current and complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
