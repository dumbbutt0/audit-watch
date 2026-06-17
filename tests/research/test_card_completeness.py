"""P225 — card-completeness contract: a designated answer in every field, on every bug.

Covers: no blank field on any committed bug (all tracks) · seal fills a sparse card to 100% designated ·
seal never overwrites real values (no invention) · the three axes are DECOUPLED (completeness != sufficiency
!= submission-readiness) · distinct tokens are preserved (not collapsed) · WARNING_LOW_EVIDENCE_DEPTH is a
non-blocking flag · the gate hard-fails on a blank but PASSES honest placeholders.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import finding_detail as fd                 # noqa: E402
import validate_hunt_sync_completion as vc  # noqa: E402

MIRROR = ROOT / "documentation/research/funnel/synced_findings.generated.json"


def _mirror_cids():
    if not MIRROR.exists():
        return []
    return [r.get("candidate_id") for r in json.loads(MIRROR.read_text()).get("findings", []) if r.get("candidate_id")]


def _all_contract_fields(ve):
    """Yield every contracted leaf field value for assertion."""
    for section, spec in fd.CARD_CONTRACT.items():
        node = ve.get(section)
        if spec["kind"] in ("flat_list", "row_list"):
            yield section, node
        elif spec["kind"] == "dict_of_lists":
            for lname in spec["lists"]:
                yield f"{section}.{lname}", (node or {}).get(lname)
        else:
            sec = node if isinstance(node, dict) else {}
            for cat in ("scalar", "proof", "human", "severity", "reach", "proof_list", "na_list"):
                for f in spec.get(cat, []):
                    yield f"{section}.{f}", sec.get(f)
            for f in spec.get("row_list_fields", {}):
                yield f"{section}.{f}", sec.get(f)


# ---------------- 1. no blank field on any committed bug, across tracks ----------------
@pytest.mark.parametrize("key", [f"funnel:{c}" for c in _mirror_cids()]
                         + ["runtime:H5-abracadabra-lockingrewards-boost"])
def test_no_blank_field_any_bug(key):
    d = fd.load_unified_detail(key)
    ve = d.get("verifier_evidence") or {}
    if not ve:
        pytest.skip(f"{key}: no verifier card (track without card)")
    blanks = [name for name, val in _all_contract_fields(ve) if fd._is_blank(val)]
    assert blanks == [], f"{key} blank fields: {blanks}"
    assert ve["evidence_completeness"]["card_completeness"]["status"] == "COMPLETE"
    assert ve["evidence_completeness"]["disclaimer"] == fd.COMPLETENESS_DISCLAIMER


# ---------------- 2. seal fills a sparse card to 100% designated ----------------
def test_seal_fills_sparse_card():
    sparse = {"report_summary": {}, "mechanism": {}, "function_map": [], "attacker_model": {},
              "exploit_steps": [], "defense_map": [], "poc_verification": {}, "impact_severity": {},
              "intent_scope_operator": {}, "novelty_duplicate": {}, "conversion": {}, "main_blocker": {},
              "final_triage": {}, "red_flags": [], "evidence_backup": {}, "top_line_status": {}}
    sealed = fd._seal_and_score(dict(sparse))
    blanks = [name for name, val in _all_contract_fields(sealed) if fd._is_blank(val)]
    assert blanks == [], f"seal left blanks: {blanks}"
    # an all-blank card is 0% artifact-backed -> low-evidence WARNING (non-blocking), still COMPLETE
    ec = sealed["evidence_completeness"]
    assert ec["card_completeness"]["status"] == "COMPLETE"
    assert ec["evidence_sufficiency"]["status"] == "WARNING_LOW_EVIDENCE_DEPTH"
    assert ec["submission_readiness"]["submission_ready"] is False


# ---------------- 3. seal never overwrites real values (no invention) ----------------
def test_seal_preserves_real_values():
    ev = {"mechanism": {"one_sentence": "real mechanism text", "root_cause": "rc",
                        "refutation_condition": "x", "why_not_refuted": "y"},
          "exploit_steps": ["step A", "step B"]}
    sealed = fd._seal_and_score(dict(ev))
    assert sealed["mechanism"]["one_sentence"] == "real mechanism text"
    assert sealed["exploit_steps"] == ["step A", "step B"]


# ---------------- 4. distinct tokens preserved (not collapsed) ----------------
def test_distinct_tokens_preserved():
    sealed = fd._seal_and_score({})
    # proof->MISSING_EVIDENCE, scalar->unknown, human->HUMAN_PENDING, reach->REACHABILITY_UNKNOWN, na->NOT_APPLICABLE
    assert sealed["mechanism"]["one_sentence"] == fd.MISSING_EVIDENCE
    assert sealed["mechanism"]["refutation_condition"] == fd.UNK
    assert sealed["novelty_duplicate"]["novelty_status"] == fd.HUMAN_PENDING
    assert sealed["attacker_model"]["reachability_class"] == fd.REACHABILITY_UNKNOWN
    assert sealed["impact_severity"]["downgrade_arguments"] == [fd.NOT_APPLICABLE]
    # all five tokens are distinct
    assert len({fd.MISSING_EVIDENCE, fd.UNK, fd.HUMAN_PENDING, fd.REACHABILITY_UNKNOWN, fd.NOT_APPLICABLE}) == 5


# ---------------- 5. three axes are decoupled ----------------
def test_axes_decoupled_on_h5():
    d = fd.load_unified_detail("runtime:H5-abracadabra-lockingrewards-boost")
    ec = (d.get("verifier_evidence") or {}).get("evidence_completeness") or {}
    if not ec:
        pytest.skip("H5 card unavailable")
    # H5 is fully designated AND high artifact depth, yet still NOT submission-ready (independent human gate)
    assert ec["card_completeness"]["status"] == "COMPLETE"
    assert ec["evidence_sufficiency"]["pct_artifact_backed"] >= 50
    assert ec["submission_readiness"]["submission_ready"] is False


# ---------------- 6. gate hard-fails a blank, passes honest placeholders ----------------
def test_gate_blocks_blank_passes_placeholder():
    # honest placeholder card (fully sealed) -> NOT a failure
    good = fd._seal_and_score({})
    fails_good = vc._blank_contract_fields(good)
    assert fails_good == [], f"sealed placeholders wrongly flagged: {fails_good}"
    # blank a contracted field -> the gate detects it
    good["mechanism"]["one_sentence"] = ""        # re-introduce a blank
    fails_bad = vc._blank_contract_fields(good)
    assert any("mechanism.one_sentence" in f for f in fails_bad)


def test_check_cards_passes_real_cards():
    # the real-world hunt log's PoC-proven candidates must each render a complete, safe verifier card.
    import funnel
    cids = [(r.get("finding_id") or r.get("record_id")) for r in funnel.load_records().get("records", [])
            if r.get("poc_status") == "REPRODUCED"]
    if not cids:
        pytest.skip("no real-world candidate findings")
    fails = vc.check_cards(cids)
    assert fails == [], fails
