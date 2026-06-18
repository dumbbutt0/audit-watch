"""compute_metrics surfaces a read-only detection-lens (mechanism-class) inventory so the system can
MEASURE its recall capability — not just FP/recall on ground truth. The recall-loop lenses authored
2026-06 (incl. the three Move lenses) must show up as reincorporated + eval-anchored."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import compute_metrics as cm  # noqa: E402


def test_lens_inventory_present_and_shaped():
    m = cm.compute()
    li = m["lens_inventory"]
    assert li["total_classes"] > 0
    assert li["reincorporated_total"] > 0
    assert set(("move", "rust", "solidity")).issubset(li["by_language"].keys())
    for b in li["by_language"].values():
        assert b["total"] >= b["reincorporated"] >= 0
        assert b["total"] >= b["seeded"] >= 0


def test_new_recall_loop_lenses_are_eval_anchored():
    li = cm.compute()["lens_inventory"]
    slugs = {r["slug"]: r for r in li["reincorporated_classes"]}
    # the three Move lenses authored this loop, with their awarded eval anchors
    for slug, anchor in (
        ("move-address-param-not-signer-auth", "secret-vault-aptos-2025-07-blind:H-02"),
        ("move-onchain-data-not-private", "secret-vault-aptos-2025-07-blind:H-01"),
        ("move-insecure-onchain-randomness", "pizza-drop-aptos-2025-08-blind:M-01"),
    ):
        assert slug in slugs, f"{slug} missing from reincorporated lens inventory"
        assert slugs[slug]["language"] == "move"
        assert anchor in slugs[slug]["awarded_examples"]
