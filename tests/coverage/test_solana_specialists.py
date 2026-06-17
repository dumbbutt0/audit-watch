"""P3 — Solana specialist bundle + seeded mechanism classes. Locks: the Solana-native classes are registered
with language:rust + status:seeded (so they NEVER count toward Solidity recall), the specialist agent files exist
with their core anchors, and ite-audit routes by language.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_solana_classes_language_tagged_and_status_valid():
    c = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    sol = [k for k in c if k.startswith("solana-")]
    assert len(sol) >= 8
    for k in sol:
        assert c[k].get("language") == "rust", k
        assert c[k].get("status") in ("seeded", "reincorporated"), k
        # honesty: a class only carries awarded_examples once it's eval-EARNED (reincorporated); seeded = none yet
        if c[k]["status"] == "seeded":
            assert c[k].get("awarded_examples") == [], k
        else:
            assert c[k].get("awarded_examples"), k
    # the critical Solana classes are present
    for k in ("solana-missing-signer-check", "solana-missing-owner-check", "solana-cpi-arbitrary-program",
              "solana-pda-seed-collision", "solana-reinit-missing-init-guard"):
        assert k in c, k


def test_solana_agent_files_exist_with_anchors():
    am = (ROOT / "agents" / "solana_account_model.md").read_text()
    assert "Signer" in am and "owner" in am.lower() and "discriminator" in am and "checked_add" in am
    cpi = (ROOT / "agents" / "solana_cpi.md").read_text()
    assert "invoke_signed" in cpi and "find_program_address" in cpi.lower() and "remaining_accounts" in cpi


def test_ite_audit_routes_by_language():
    s = (ROOT / ".claude" / "skills" / "ite-audit" / "SKILL.md").read_text()
    assert "audit_language()" in s and "solana_account_model.md" in s and "rust" in s


def test_solidity_classes_have_no_language_or_solidity():
    # Solidity classes must NOT be accidentally tagged rust/move (would drop them from the Solidity scoreboard).
    # Non-Solidity classes are not always prefixed (e.g. cross-chain LayerZero rust classes), so the invariant
    # is keyed on the explicit language tag: every class language must be one of the known languages, and any
    # non-solidity class must declare its language explicitly (so the scoreboard separation is intentional).
    c = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    for k, v in c.items():
        lang = v.get("language", "solidity")
        assert lang in ("solidity", "rust", "move"), k
        if k.startswith("solana-"):
            assert lang == "rust", k
        if k.startswith("move-"):
            assert lang == "move", k


def test_move_classes_language_tagged_and_status_valid():
    # Move/Sui classes are language:move + status:seeded (NEVER count toward Solidity or Rust recall) until the
    # recall lab earns them on scored Sui/Move contests.
    c = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    mv = [k for k in c if k.startswith("move-")]
    assert len(mv) >= 7
    for k in mv:
        assert c[k].get("language") == "move", k
        assert c[k].get("status") in ("seeded", "reincorporated"), k
        if c[k]["status"] == "seeded":
            assert c[k].get("awarded_examples") == [], k
    for k in ("move-clmm-liquidity-overflow", "move-capability-safety", "move-hot-potato-bypass",
              "move-object-ownership", "move-coin-balance-conservation"):
        assert k in c, k


def test_move_agent_files_exist_with_anchors():
    cm = (ROOT / "agents" / "move_clmm_math.md").read_text()
    assert "checked_shlw" in cm and "get_liquidity_from_amount" in cm and "rounding" in cm.lower()
    oc = (ROOT / "agents" / "move_object_capability.md").read_text()
    assert "hot potato" in oc.lower() or "hot-potato" in oc.lower()
    assert "capability" in oc.lower() and "Balance" in oc


def test_ite_audit_routes_move():
    s = (ROOT / ".claude" / "skills" / "ite-audit" / "SKILL.md").read_text()
    assert "move_clmm_math.md" in s and "move_object_capability.md" in s and "**move**" in s
