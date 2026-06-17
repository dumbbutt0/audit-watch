#!/usr/bin/env python3
"""
specialist_coverage_gate.py — fail loudly when a target's PROFILE requires specialists that never ran.

The Panoptic eval missed both Highs (H-01 access-control re-init, H-02 cross-contract reentrancy) because
Step-2 ran math-focused in-session reasoning instead of the full specialist swarm. There was no record of
which specialists were *required* for the target, so the gap was silent. This gate fixes that: it detects
the target profile from static.json flags + manifest function-name signatures, computes the mandatory
specialists, and checks which `output/findings_<name>.json` exist (existence = the specialist ran).

In strict full-audit it EXITS 1 when a required specialist is missing, unless an explicit budget waiver is
recorded in `output/specialist_waiver.json`. In advisory mode it warns and exits 0. Writes
`output/specialist_coverage.json`.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# Profile → trigger signatures over manifest function names (lower-cased), plus static.json flags.
PROFILE_SIGNATURES = {
    "erc4626_shares": [r"converttoshares", r"converttoassets", r"totalassets", r"previewredeem",
                       r"previewdeposit", r"\bredeem\b", r"maxwithdraw"],
    "lending_liquidation_solvency": [r"liquidat", r"solven", r"\bmargin\b", r"collateral", r"baddebt",
                                     r"\bseize\b", r"\bborrow", r"\bdebt\b"],
    "oracle_twap": [r"oracle", r"\btwap\b", r"\bema\b", r"getprice", r"observe", r"slot0", r"mediantick"],
    "cross_contract_settlement": [r"settle", r"\bdelegate\b", r"\brevoke\b", r"\brefund\b"],
    "nft_collateral": [r"onerc721received", r"erc721", r"\bnft\b", r"position", r"collateraltoken",
                       r"tokenid"],
}

# When ANY DeFi-core profile matches, these specialists are mandatory (the user's required set:
# reentrancy · access-control/init · oracle/TWAP · liquidation/solvency · ERC4626/shares · math/precision).
DEFI_CORE_REQUIRED = ["reentrancy", "access_control", "oracle", "logic", "economic_attack",
                      "erc4626", "arithmetic"]

# Profiles dense enough to demand the full ADVERSARIAL swarm — named specialist outputs, not single-summary
# DEFI-core (Revert Lend ran DEFI-core but still missed callback/permit/4626 issues in examined code).
HIGH_DENSITY_PROFILES = {"lending_liquidation_solvency", "erc4626_shares", "oracle_twap", "nft_collateral"}
HIGH_DENSITY_REQUIRED = ["access_control_init", "reentrancy_callback", "permit_signature",
                         "erc4626_vault_accounting", "oracle_liquidation", "transformer_external_call",
                         "math_precision"]


def _policy() -> dict:
    try:
        return json.loads((ROOT / "config" / "agent_policy.json").read_text()).get("coverage_policy", {})
    except Exception:
        return {}


def _load(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def detect_profiles(static: dict, manifest: dict) -> list[str]:
    names = " ".join((i.get("name") or "").lower() for i in manifest.get("items", [])
                     if i.get("kind") in ("function", "constructor", "initializer"))
    profiles = []
    for prof, sigs in PROFILE_SIGNATURES.items():
        hits = sum(1 for s in sigs if re.search(s, names))
        if prof == "erc4626_shares" and (static.get("is_erc4626") or hits >= 4):
            profiles.append(prof)
        elif prof != "erc4626_shares" and hits >= 2:
            profiles.append(prof)
    return profiles


def risk_density(manifest: dict) -> float:
    items = [i for i in manifest.get("items", []) if i.get("in_scope", True)]
    if not items:
        return 0.0
    risky = sum(1 for i in items if (i.get("attack_surface_score", 0) >= 3) or i.get("external_calls"))
    return round(risky / len(items), 3)


def required_specialists(profiles: list[str], manifest: dict | None = None,
                         density_threshold: float = 0.15) -> tuple[list[str], bool]:
    """Return (required, high_density). DEFI-core when any profile matches; plus the named adversarial swarm
    when a high-density profile is present and risk density exceeds the threshold."""
    if not profiles:
        return [], False
    required = list(DEFI_CORE_REQUIRED)
    density = risk_density(manifest or {})
    high_density = bool(HIGH_DENSITY_PROFILES & set(profiles)) and density > density_threshold
    if high_density:
        required += [s for s in HIGH_DENSITY_REQUIRED if s not in required]
    return required, high_density


def present_specialists() -> set[str]:
    out = audit_path("output")
    found = set()
    for p in out.glob("findings_*.json"):
        found.add(p.stem[len("findings_"):])
    return found


def _waived() -> dict[str, str]:
    w = _load(audit_path("output") / "specialist_waiver.json")
    waivers = {}
    for item in (w.get("waivers") or w.get("specialists") or []):
        if isinstance(item, dict) and item.get("specialist") and item.get("reason"):
            waivers[item["specialist"]] = item["reason"]
    return waivers


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    pol = _policy()
    full_audit = os.environ.get("AUDITWATCH_FULL_AUDIT") == "1"
    enabled = pol.get("mandatory_specialist_profiles_enabled", True)
    strict = enabled and (pol.get("mandatory_specialist_strict", False)
                          or (pol.get("mandatory_specialist_strict_full_audit", True) and full_audit))

    density_threshold = pol.get("specialist_density_threshold", 0.15)
    static = _load(audit_path("output") / "static.json")
    manifest = _load(audit_path("output") / "coverage_manifest.json")
    profiles = detect_profiles(static, manifest) if enabled else []
    required, high_density = required_specialists(profiles, manifest, density_threshold)
    density = risk_density(manifest)
    present = present_specialists()
    waivers = _waived()

    missing = [s for s in required if s not in present and s not in waivers]
    waived_missing = [s for s in required if s not in present and s in waivers]

    report = {
        "gate": "specialist_coverage", "strict": strict, "full_audit": full_audit,
        "profiles": profiles, "risk_density": density, "high_density": high_density,
        "required": required, "present": sorted(present),
        "missing": missing,
        "waived_recall_risk": {s: waivers[s] for s in waived_missing},
    }
    (audit_path("output") / "specialist_coverage.json").write_text(json.dumps(report, indent=2))

    blocked = bool(missing) and strict
    if not args.quiet:
        tag = "STRICT" if strict else "advisory"
        print(f"Specialist coverage gate: {tag}  ·  profiles={profiles or '[]'}")
        print(f"  required {len(required)} · present-of-required "
              f"{len([s for s in required if s in present])} · missing {len(missing)}"
              + (f" · waived {len(waived_missing)}" if waived_missing else ""))
        for s in missing:
            print(f"   ✗ MISSING required specialist: {s} (no output/findings_{s}.json)")
        if blocked:
            print("  → BLOCK: run the missing specialists (/ite-audit) or record a waiver in "
                  "output/specialist_waiver.json")
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
