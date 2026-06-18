"""Recall-lab: Secret Vault (CodeHawks 2025-07) FRESH BLIND move/APTOS audit. NOTE: Aptos-flavor Move (not Sui,
the specialists' usual target) — labeled as such; the system had ZERO Aptos coverage so its misses are genuine
new Move lenses that also apply to Sui. Blind recall 1.00 (caught both Highs + the Medium). Reasoning-gap
classes reincorporated into the Move specialist: H-02 (authorization via a caller-supplied address arg instead
of a verified signer) -> move_object_capability #8; H-01 (plaintext secret in world-readable on-chain storage)
-> move_object_capability #9."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_secret_vault_miss_classes():
    c = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    for slug, fid in (("move-address-param-not-signer-auth", "secret-vault-aptos-2025-07-blind:H-02"),
                      ("move-onchain-data-not-private", "secret-vault-aptos-2025-07-blind:H-01")):
        assert slug in c and c[slug]["status"] == "reincorporated"
        assert fid in c[slug]["awarded_examples"]
        assert c[slug]["language"] == "move"
        assert "description" in c[slug] and c[slug]["agent"] == "move_object_capability"


def test_secret_vault_sections():
    mc = (ROOT / "agents" / "move_object_capability.md").read_text()
    # H-02: address-param-not-signer auth
    assert "move-address-param-not-signer-auth" in mc
    assert "signer::address_of" in mc and "tx_context::sender" in mc
    # H-01: on-chain storage is public
    assert "move-onchain-data-not-private" in mc
    assert "world-readable" in mc and "plaintext" in mc
