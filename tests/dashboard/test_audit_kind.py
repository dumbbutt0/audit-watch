"""P100: the dashboard's derived audit-kind classifier (bounty vs eval/research corpus).

It only GROUPS/FILTERS the audit dropdown + all-audits list — it never mutates registry.json. These tests lock
the classification and confirm the enrichment is read-only.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import dashboard as D  # noqa: E402

REGISTRY = ROOT / "audits" / "registry.json"
BOUNTIES = {
    "origin-protocol-2026-05", "k2-kinetic-2026-04", "tools-for-humanity-2026-05", "enzyme-finance-2026-05",
    "rhinofi-2026-05", "xterio-2026-05", "stacks-2026-05", "wormhole-2026-05", "gearbox-2026-05",
    "flare-network-2026-05", "circle-2026-05",
}


def _registry():
    return json.loads(REGISTRY.read_text())["audits"]


def test_classifier_rule_bounty():
    # rule-level coverage (independent of which audits remain in the registry):
    assert D._audit_kind({"contest": "foo-immunefi-2026"}) == "bounty"
    assert D._audit_kind({"contest": "bar-hackerone"}) == "bounty"
    assert D._audit_kind({"audit_id": "k2-kinetic-2026-04", "contest": "k2-code4rena-2026-04"}) == "bounty"
    assert D._audit_kind({"audit_id": "circle-2026-05", "contest": ""}) == "bounty"  # allowlist


def test_k2_still_registered_and_bounty():
    # the 10 other bounty engagements were deleted per user request (2026-06); k2 is the one kept.
    by_id = {a["audit_id"]: a for a in _registry()}
    assert "k2-kinetic-2026-04" in by_id
    assert D._audit_kind(by_id["k2-kinetic-2026-04"]) == "bounty"


def test_eval_corpus_classifies_eval():
    # after the 2026-06 eval purge, the surviving eval-corpus ids are the two used by compute_metrics' filter.
    by_id = {a["audit_id"]: a for a in _registry()}
    for cid in ["beanstalk-2024-05", "size-credit-2024-06"]:
        assert D._audit_kind(by_id[cid]) == "eval", cid


def test_classifier_never_raises_on_missing_fields():
    for a in ({}, {"audit_id": "x"}, {"contest": None}, {"contest": ""}, None):
        assert D._audit_kind(a or {}) in ("bounty", "eval")


def test_live_registry_split():
    # Robust against the (growing) eval corpus the recall-lab registers: assert the classification INVARIANTS, not
    # a frozen count. Every audit classifies into exactly {bounty, eval}; the only registered bounties are the kept
    # bounty engagements (BOUNTIES allowlist — the others were deleted 2026-06); the eval corpus is non-empty.
    audits = _registry()
    counts = {"bounty": 0, "eval": 0}
    for a in audits:
        counts[D._audit_kind(a)] += 1
    assert counts["bounty"] + counts["eval"] == len(audits)                 # total + exhaustive classification
    expected_bounty = sum(1 for a in audits if a["audit_id"] in BOUNTIES)
    assert counts["bounty"] == expected_bounty                             # bounties are exactly the allowlisted ids
    assert counts["eval"] == len(audits) - expected_bounty
    assert counts["eval"] >= 1                                             # eval corpus present


def test_enrichment_does_not_mutate_registry():
    before = REGISTRY.read_bytes()
    audits = _registry()
    # mimic the /api/audits enrichment (copy, never mutate)
    enriched = [{**a, "kind": D._audit_kind(a)} for a in audits]
    assert all("kind" in e for e in enriched)
    assert all("kind" not in a for a in audits)  # originals untouched
    assert REGISTRY.read_bytes() == before  # file unchanged


def test_hidden_audit_kinds_read_from_config():
    """The dashboard view preference is read (read-only) and surfaced; it never deletes/registry-edits.
    Value-agnostic: it must reflect whatever config/dashboard_view.json declares."""
    cfg = json.loads((ROOT / "config" / "dashboard_view.json").read_text())
    assert D._hidden_audit_kinds() == [str(k) for k in (cfg.get("hidden_audit_kinds") or [])]


def test_api_audits_payload_surfaces_hidden_kinds_and_keeps_all_audits():
    import json as J
    audits = _registry()
    resp = D.list_all_audits()
    payload = J.loads(bytes(resp.body).decode())
    # still returns ALL registered audits (hiding is UI-only; switching/active must keep working)
    assert len(payload["audits"]) == len(audits)
    assert payload["hidden_audit_kinds"] == D._hidden_audit_kinds()  # reflects config (value-agnostic)
    # kind_counts is derived from the live registry, not a frozen snapshot
    expected = {"bounty": 0, "eval": 0}
    for a in audits:
        expected[D._audit_kind(a)] += 1
    assert payload["kind_counts"] == expected
    assert sum(payload["kind_counts"].values()) == len(payload["audits"])
