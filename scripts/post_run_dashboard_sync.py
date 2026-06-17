#!/usr/bin/env python3
"""post_run_dashboard_sync.py — safe post-run dashboard sync hook (research-only, read-only on submissions).

After a completed audit/hunt phase, route that run's candidates into the shared dashboard mirror
(documentation/research/funnel/synced_findings.generated.json) via the multi-source adapter layer in
scripts/sync_hunt_findings.py, then emit a sync-status payload the dashboard reads
(output_research/funnel/sync_status.json).

Guarantees:
  * NEVER submits / routes / promotes / changes severity verdicts (delegates writing to sync_hunt_findings,
    whose records all carry research_only=true / routing_allowed=false / submission_ready=false).
  * Existing records are PRESERVED; the underlying write hard-fails if any record would be deleted
    (unless --allow-delete is threaded through), and uses atomic temp->backup->replace.
  * --dry-run shows the exact planned changes and writes nothing to the mirror.

Usage:
  python scripts/post_run_dashboard_sync.py --audit-id size-credit-2024-06-blind --phase-id P223 \
      --source-adapter size_credit --workspace documentation/research/assisted_mode/p223_size_credit_hunt \
      [--set-active|--no-set-active] [--dry-run] [--allow-delete]
"""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import sync_hunt_findings as shf            # noqa: E402  (multi-source sync + atomic write + adapters)
import audit_context                        # noqa: E402  (active-audit switch)

DEFAULT_MIRROR = ROOT / "documentation/research/funnel/synced_findings.generated.json"
SYNC_STATUS = ROOT / "output_research/funnel/sync_status.json"

# default workspace per adapter (deliverables dir holding CANDIDATE_REGISTER.json + the scorecard)
_DEFAULT_WS = {
    "zeta": "documentation/research/assisted_mode/p215_full_funnel_rehearsal",
    "size_credit": "documentation/research/assisted_mode/p223_size_credit_hunt",
}


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _read_json(p):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None


def _active_id():
    try:
        return audit_context.get_active_audit().get("audit_id")
    except Exception:
        return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Safe post-run dashboard sync hook")
    ap.add_argument("--audit-id", required=True)
    ap.add_argument("--phase-id", required=True)
    ap.add_argument("--source-adapter", default=None, help="zeta|size_credit (auto-detected from --audit-id if omitted)")
    ap.add_argument("--workspace", default=None, help="deliverables dir with CANDIDATE_REGISTER.json (adapter default if omitted)")
    ap.add_argument("--out", default=str(DEFAULT_MIRROR))
    ap.add_argument("--status-out", default=str(SYNC_STATUS))
    grp = ap.add_mutually_exclusive_group()
    grp.add_argument("--set-active", dest="set_active", action="store_true")
    grp.add_argument("--no-set-active", dest="set_active", action="store_false")
    ap.set_defaults(set_active=False)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--allow-delete", action="store_true")
    args = ap.parse_args(argv)

    adapter_name, _ = shf.resolve_adapter(args.source_adapter, args.audit_id)
    ws = args.workspace or _DEFAULT_WS.get(adapter_name)
    if not ws:
        print(f"[abort] no --workspace and no default for adapter '{adapter_name}'"); return 2
    ws_path = ROOT / ws

    # ---- 1. validate run artifacts exist ----
    missing = []
    reg = ws_path / "CANDIDATE_REGISTER.json"
    if not reg.exists():
        missing.append(str(reg.relative_to(ROOT)))
    if not (ROOT / "audits" / args.audit_id / "output" / "merged_findings.json").exists():
        missing.append(f"audits/{args.audit_id}/output/merged_findings.json")
    if missing:
        print(f"[abort] required run artifacts missing: {missing}"); return 2

    active_before = _active_id()

    # ---- 2. optionally switch active audit ----
    if args.set_active and not args.dry_run:
        try:
            audit_context.switch_audit(args.audit_id)
        except Exception as exc:
            print(f"[abort] could not switch active audit: {exc}"); return 2
    active_after = _active_id()

    # ---- 3. run the multi-source sync (delegates the atomic write + deletion guard + validation) ----
    summary_path = ROOT / "output_research/funnel/.last_sync_summary.json"
    sync_argv = [
        "--phase", args.phase_id, "--audit", args.audit_id, "--workspace", ws,
        "--source-adapter", adapter_name, "--out", args.out,
        "--summary-out", str(summary_path), "--strict",
    ]
    sync_argv += ["--dry-run"] if args.dry_run else ["--write"]
    if args.allow_delete:
        sync_argv += ["--allow-delete"]
    rc = shf.main(sync_argv)
    summ = _read_json(summary_path) or {}

    # ---- 4. compute global + unsynced counts from the resulting mirror ----
    mirror = _read_json(args.out) or {}
    findings = mirror.get("findings", []) if isinstance(mirror, dict) else []
    global_count = len(findings)
    synced_cids = {r.get("candidate_id") for r in findings if isinstance(r, dict)}
    reg_doc = _read_json(reg) or {}
    reg_cids = [c.get("id") for c in reg_doc.get("candidates", []) if isinstance(c, dict)]
    unsynced = [c for c in reg_cids if c not in synced_cids]  # for dry-run these are the would-be-added

    # ---- 5. best-effort completion guard (reader/card visibility); downgrades status to PARTIAL on issues ----
    guard_fails: list = []
    if not args.dry_run:
        try:
            import validate_hunt_sync_completion as vc
            prefix = f"{shf.ADAPTERS[adapter_name]['rid_prefix']}:{args.phase_id}:"
            cands = [{"id": c.get("id"), "claimed_severity": c.get("claimed_severity") or c.get("severity_ceiling")}
                     for c in reg_doc.get("candidates", []) if isinstance(c, dict)]
            drq_dir = ROOT / "output_research/dry_run_submission_queue"
            drq_ids = {p.stem for p in drq_dir.glob(f"{args.audit_id.split('-')[0].upper()}*.json")} if drq_dir.exists() else set()
            gf, _gw, _rep = vc.run_checks(cands, findings, drq_ids, {"phase": args.phase_id, "prefix": prefix})
            guard_fails = list(gf)
        except Exception as exc:
            guard_fails = [f"completion guard error: {exc}"]

    # ---- 6. derive status ----
    if rc not in (0,):
        status = "FAILED"
    elif args.dry_run:
        status = "DRY_RUN"
    elif guard_fails or unsynced or summ.get("validation_errors"):
        status = "PARTIAL"
    else:
        status = "OK"

    payload = {
        "timestamp": _now(),
        "phase_id": args.phase_id,
        "audit_id": args.audit_id,
        "adapter": adapter_name,
        "status": status,
        "active_audit_before": active_before,
        "active_audit_after": active_after,
        "records_added": summ.get("added_count"),
        "records_updated": summ.get("updated_count"),
        "records_preserved": summ.get("preserved_count"),
        "records_deleted": summ.get("deleted_count"),
        "total_records": summ.get("total_records", global_count),
        "global_candidate_count": global_count,
        "unsynced_count": len(unsynced),
        "unsynced": unsynced,
        "mirror_hash_before": summ.get("hash_before"),
        "mirror_hash_after": summ.get("hash_after"),
        "backup_path": summ.get("backup_path"),
        "unresolved_artifacts": summ.get("unresolved_artifacts", []),
        "validation_errors": summ.get("validation_errors", []),
        "completion_guard_failures": guard_fails,
        "mirror_path": shf._rel(args.out),
        "sync_report": shf._rel(summary_path),
        "dry_run": bool(args.dry_run),
        "research_only": True, "review_only": True,
        "routes_in_production": False, "routing_allowed": False,
    }

    # ---- 7. write sync_status.json (atomic) + print concise summary ----
    shf.atomic_write_with_backup(Path(args.status_out), json.dumps(payload, indent=2) + "\n")

    print("=" * 60)
    print(f"POST-RUN DASHBOARD SYNC — {status}")
    print(f"  phase={args.phase_id} audit={args.audit_id} adapter={adapter_name}")
    print(f"  active audit: {active_before} -> {active_after}")
    print(f"  records: +{payload['records_added']} added / ~{payload['records_updated']} updated / "
          f"={payload['records_preserved']} preserved / -{payload['records_deleted']} deleted")
    print(f"  global candidates visible: {global_count}  ·  unsynced: {len(unsynced)}{(' '+str(unsynced)) if unsynced else ''}")
    print(f"  mirror hash: {payload['mirror_hash_before']} -> {payload['mirror_hash_after']}")
    print(f"  backup: {payload['backup_path']}")
    if guard_fails:
        print(f"  completion-guard failures ({len(guard_fails)}): {guard_fails[:6]}")
    if summ.get("validation_errors"):
        print(f"  validation errors ({len(summ['validation_errors'])}): {summ['validation_errors'][:6]}")
    print(f"  status report: {shf._rel(args.status_out)}")
    print("=" * 60)
    return 0 if status in ("OK", "DRY_RUN") else (0 if status == "PARTIAL" else rc or 1)


if __name__ == "__main__":
    raise SystemExit(main())
