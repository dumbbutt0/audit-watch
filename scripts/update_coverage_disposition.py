#!/usr/bin/env python3
"""
update_coverage_disposition.py — Set/append a coverage disposition (deterministic, no LLM).

Used by link_findings_to_manifest.py, coverage_sweep_write.py, and humans. Enforces the disposition
contract at write time: cleared⇒evidence+clear_reason, finding⇒>=1 finding_ref, deferred⇒scope reason.

Usage:
    python scripts/update_coverage_disposition.py --id <manifest_id> --status cleared \
        --evidence "LibFoo.sol:42 guard require(msg.sender==owner)" --clear-reason "owner-gated, no attacker path"
    python scripts/update_coverage_disposition.py --id <manifest_id> --status finding --finding-ref CC-001
    python scripts/update_coverage_disposition.py --id <manifest_id> --status assigned --pass deep --agent oracle
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import read_completeness_utils as rcu  # noqa: E402

ALLOWED = {"unassigned", "assigned", "examined", "cleared", "finding", "deferred_out_of_scope"}


def _load() -> tuple[Path, dict, dict]:
    p = audit_path("output") / "coverage_dispositions.json"
    if not p.exists():
        raise SystemExit("[update_coverage_disposition] dispositions missing — run init_coverage_dispositions.py first.")
    data = json.loads(p.read_text())
    idx = {d["manifest_id"]: d for d in data.get("dispositions", [])}
    return p, data, idx


def apply_update(d: dict, status: str, evidence=None, finding_ref=None, clear_reason=None,
                 scope_reason=None, assigned_pass=None, assigned_agent=None,
                 attacker_reachability=None, guard_or_invariant=None, no_impact_reason=None,
                 clear_depends_on=None, dependency_clearance_status=None, dependency_reason=None,
                 dependency_evidence=None, downstream_guard_claim=None, downstream_guard_type=None,
                 dependency_review_required=None, routed_reason=None,
                 guard_locality=None, path_dominance_evidence=None, alternative_paths_considered=None,
                 cross_artifact_lifecycle=None,
                 math_estimator_proof=None,
                 dynamic_weight_lifecycle_proof=None,
                 dependency_name=None, dependency_scope=None,
                 dependency_status=None, proof_status=None,
                 read_state=None, read_block_reason=None, read_block_ack=None,
                 duplicate_of=None, generated_interface_reason=None) -> list[str]:
    """Mutate disposition d in place; return list of validation errors (empty = ok).

    The dependency_* / downstream_* fields are OPTIONAL metadata describing a clear that relies on
    another in-scope dependency (guard/estimator/oracle/math-rule/invariant/lifecycle check). They are
    stored when provided and consumed by validate_dependency_clears.py + the writer enforcement; they do
    not change the status enum or the gate contract. See documentation/dependency_clear_policy.md.
    """
    errors: list[str] = []
    if status not in ALLOWED:
        return [f"invalid status '{status}' (allowed: {sorted(ALLOWED)})"]
    if read_state is not None and read_state not in rcu.ALLOWED_READ_STATES:
        return [f"invalid read_state '{read_state}' (allowed: {sorted(rcu.ALLOWED_READ_STATES)})"]
    if evidence:
        d["evidence"] = sorted(set(d.get("evidence", []) + list(evidence)))
    if finding_ref:
        d["finding_refs"] = sorted(set(d.get("finding_refs", []) + list(finding_ref)))
    if clear_reason is not None:
        d["clear_reason"] = clear_reason
    if scope_reason is not None:
        d["scope_reason"] = scope_reason
    # strong-clear fields (required for high-attack-surface clears; enforced by sweep_write + gate)
    if attacker_reachability is not None:
        d["attacker_reachability"] = attacker_reachability
    if guard_or_invariant is not None:
        d["guard_or_invariant"] = guard_or_invariant
    if no_impact_reason is not None:
        d["no_impact_reason"] = no_impact_reason
    if assigned_pass is not None:
        d["assigned_pass"] = assigned_pass
    if assigned_agent is not None:
        d["assigned_agent"] = assigned_agent
    # dependency-clear metadata (optional; backward-compatible — stored only when provided)
    if clear_depends_on is not None:
        d["clear_depends_on"] = list(clear_depends_on)
    if dependency_clearance_status is not None:
        d["dependency_clearance_status"] = dependency_clearance_status
    if dependency_reason is not None:
        d["dependency_reason"] = dependency_reason
    if dependency_evidence is not None:
        d["dependency_evidence"] = list(dependency_evidence)
    if downstream_guard_claim is not None:
        d["downstream_guard_claim"] = bool(downstream_guard_claim)
    if downstream_guard_type is not None:
        d["downstream_guard_type"] = downstream_guard_type
    if dependency_review_required is not None:
        d["dependency_review_required"] = bool(dependency_review_required)
    if routed_reason is not None:
        d["routed_reason"] = routed_reason
    # locality / path-dominance metadata (optional; required to clear with a NON-LOCAL guard — the guard
    # must dominate every attacker-reachable path. See documentation/dependency_clear_policy.md).
    if guard_locality is not None:
        d["guard_locality"] = guard_locality
    if path_dominance_evidence is not None:
        d["path_dominance_evidence"] = path_dominance_evidence
    if alternative_paths_considered is not None:
        d["alternative_paths_considered"] = alternative_paths_considered
    # cross-artifact lifecycle metadata (optional; records that an in-scope controller's grip on an
    # artifact's lifecycle was reviewed — status ∈ cross_artifact_lifecycle_risk / cross_artifact_scope_linked
    # / lifecycle_under_escalated / lifecycle_cleared_with_local_proof. See documentation/bridge_lifecycle_escalation_policy.md).
    if cross_artifact_lifecycle is not None:
        d["cross_artifact_lifecycle"] = cross_artifact_lifecycle
    # math-estimator proof (optional; required to strong-clear math-estimator-sensitive items — see
    # documentation/math_estimator_proof_policy.md). Stored when provided; consumed by
    # validate_math_estimator_clears.py + the writer enforcement. Backward-compatible.
    if math_estimator_proof is not None:
        d["math_estimator_proof"] = math_estimator_proof
    # dynamic-weight lifecycle proof (P174 F1; optional; required to strong-clear a lifecycle-sensitive
    # weight-set/update surface — see config/dynamic_weight_lifecycle_patterns.json). Stored when provided;
    # consumed by validate_dynamic_weight_lifecycle_clears.py + the writer enforcement. Backward-compatible.
    if dynamic_weight_lifecycle_proof is not None:
        d["dynamic_weight_lifecycle_proof"] = dynamic_weight_lifecycle_proof
    # P177 clear-time evidence-capture fields (optional; let a clear carry COMPLETE structured dependency
    # metadata + proof status so guarded-downstream can adjudicate precisely instead of blunt-routing. Stored
    # when provided; consumed by dependency_clear_utils.classify_clear + dependency_route_decision. Additive.).
    if dependency_name is not None:
        d["dependency_name"] = dependency_name
    if dependency_scope is not None:
        d["dependency_scope"] = dependency_scope
    if dependency_status is not None:
        d["dependency_status"] = dependency_status
    if proof_status is not None:
        d["proof_status"] = proof_status
    # P245 #3 read-completeness fields (optional, additive; orthogonal to the status enum). Consumed
    # only by the read-completeness gate when explicitly enforced (default-off). See
    # scripts/read_completeness_utils.py.
    if read_state is not None:
        d["read_state"] = read_state
    if read_block_reason is not None:
        d["read_block_reason"] = read_block_reason
    if read_block_ack is not None:
        d["read_block_ack"] = bool(read_block_ack)
    if duplicate_of is not None:
        d["duplicate_of"] = duplicate_of
    if generated_interface_reason is not None:
        d["generated_interface_reason"] = generated_interface_reason
    d["status"] = status
    d["updated_at"] = datetime.now(timezone.utc).isoformat()
    # contract enforcement
    if status == "cleared":
        if not d.get("evidence"):
            errors.append("cleared requires >=1 evidence reference")
        if not d.get("clear_reason"):
            errors.append("cleared requires a clear_reason")
    if status == "finding" and not d.get("finding_refs"):
        errors.append("finding requires >=1 finding_ref")
    if status == "deferred_out_of_scope" and not (d.get("scope_reason") or d.get("clear_reason")):
        errors.append("deferred_out_of_scope requires a scope reason")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True, dest="mid")
    ap.add_argument("--status", required=True)
    ap.add_argument("--evidence", action="append", default=[])
    ap.add_argument("--finding-ref", action="append", default=[])
    ap.add_argument("--clear-reason")
    ap.add_argument("--scope-reason")
    ap.add_argument("--pass", dest="assigned_pass")
    ap.add_argument("--agent", dest="assigned_agent")
    ap.add_argument("--attacker-reachability")
    ap.add_argument("--guard-or-invariant")
    ap.add_argument("--no-impact-reason")
    # P245 #3 read-completeness fields
    ap.add_argument("--read-state", choices=sorted(rcu.ALLOWED_READ_STATES))
    ap.add_argument("--read-block-reason")
    ap.add_argument("--read-block-ack", action="store_true",
                    help="human acknowledgment that a BLOCKED_BY_* item was deliberately left unread")
    ap.add_argument("--duplicate-of", help="canonical manifest id this DUPLICATE_WRAPPER mirrors")
    ap.add_argument("--generated-interface-reason")
    args = ap.parse_args()

    p, data, idx = _load()
    if args.mid not in idx:
        raise SystemExit(f"[update_coverage_disposition] unknown manifest id: {args.mid}")
    errors = apply_update(idx[args.mid], args.status, args.evidence or None,
                          args.finding_ref or None, args.clear_reason, args.scope_reason,
                          args.assigned_pass, args.assigned_agent,
                          args.attacker_reachability, args.guard_or_invariant, args.no_impact_reason,
                          read_state=args.read_state, read_block_reason=args.read_block_reason,
                          read_block_ack=(True if args.read_block_ack else None),
                          duplicate_of=args.duplicate_of,
                          generated_interface_reason=args.generated_interface_reason)
    if errors:
        print(f"[error] {args.mid}: " + "; ".join(errors), file=sys.stderr)
        return 1
    p.write_text(json.dumps(data, indent=2))
    print(f"[ok] {args.mid} → {args.status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
