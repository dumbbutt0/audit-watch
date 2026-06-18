#!/usr/bin/env python3
"""
live_reachability_check.py — on-chain evidence for the deployment-reachability axis (deterministic, no LLM).

Turns reachability from a human guess into EVIDENCE when on-chain coordinates exist. Reads the optional
`onchain` block of audits/<id>/deployment_manifest.json and, using the existing QuickNode backends
(tools/quicknode_mcp.py), checks for each target finding:
  - is the vulnerable function's 4-byte selector present in the deployed (proxy-resolved) bytecode? absent
    => not_wired (strong live evidence the function isn't deployed);
  - (optional) is the gating storage slot active (nonzero / equals expected)? inactive => not_wired.

BEST-EFFORT and FAIL-OPEN: no QUICKNODE_ENDPOINT_<CHAIN> env, no address, or a non-contract address ->
every target is `checklist_required` (a human must verify), NEVER a fabricated verdict. The substring
selector search over-reports PRESENCE rather than absence, so a `not_wired` verdict is conservative
(it will not falsely block a deployed function).

Writes output/live_reachability.json. submission_risk_audit.py folds this into the reachability axis;
precision_gate.py then blocks on `not_wired` in submission mode.

  manifest onchain block (all optional):
    {"onchain": {"address": "0x..", "chain": "ethereum",
                 "targets": [{"finding_id": "F-1", "signature": "withdraw(uint256)"}],
                 "storage_assertions": [{"finding_id": "F-1", "slot": 3, "expect_nonzero": true}]}}

Usage: python scripts/live_reachability_check.py [--quiet]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tools"))
from audit_context import audit_path  # noqa: E402


def _keccak256(data: bytes) -> bytes:
    try:
        from Crypto.Hash import keccak  # pycryptodome
        h = keccak.new(digest_bits=256)
        h.update(data)
        return h.digest()
    except Exception:
        from eth_hash.auto import keccak as _k  # eth-hash fallback
        return _k(data)


def _selector(signature: str) -> str:
    """4-byte selector hex (no 0x) for a canonical function signature like 'withdraw(uint256)'."""
    return _keccak256(signature.encode())[:4].hex().lower()


def _load(p: Path, default):
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return default


def _onchain_cfg() -> dict | None:
    m = _load(audit_path("deployment_manifest.json"), None)
    if isinstance(m, dict) and isinstance(m.get("onchain"), dict):
        return m["onchain"]
    return None


def _checklist(reason: str) -> dict:
    return {"level": "checklist_required", "rationale": reason}


def build() -> dict:
    ts = datetime.now(timezone.utc).isoformat()
    cfg = _onchain_cfg()
    out = {"schema": "live_reachability/v1", "generated_at": ts, "checked": False,
           "address": None, "chain": None, "findings": {}}

    if not cfg or not cfg.get("address"):
        out["note"] = "no on-chain coordinates (deployment_manifest.json onchain.address) — reachability stays a checklist"
        return out

    address = cfg["address"]
    chain = (cfg.get("chain") or "ethereum").lower()
    out["address"], out["chain"] = address, chain

    try:
        import quicknode_mcp as qn  # tools/quicknode_mcp.py
    except Exception as e:  # pragma: no cover - import guard
        out["note"] = f"quicknode backend unavailable ({type(e).__name__}) — reachability stays a checklist"
        return out

    bc = qn.get_bytecode(address, chain)
    if not bc or not bc.get("is_contract"):
        out["note"] = "no deployed bytecode (missing QUICKNODE_ENDPOINT or non-contract address) — reachability stays a checklist"
        # still emit per-finding checklist so the manifest's intent is visible
        for t in cfg.get("targets", []) or []:
            if t.get("finding_id"):
                out["findings"][t["finding_id"]] = _checklist("on-chain query unavailable — verify manually")
        return out

    out["checked"] = True
    # resolve proxy implementation if present — the logic (and selectors) live in the impl
    code_hex = (bc.get("bytecode_hex") or "").lower()
    impl = bc.get("implementation_address")
    if impl:
        impl_bc = qn.get_bytecode(impl, chain)
        if impl_bc and impl_bc.get("bytecode_hex"):
            code_hex = impl_bc["bytecode_hex"].lower()
            out["implementation_address"] = impl

    # 1) selector-in-bytecode
    for t in cfg.get("targets", []) or []:
        fid, sig = t.get("finding_id"), t.get("signature")
        if not fid or not sig:
            continue
        sel = _selector(sig)
        present = sel in code_hex
        if present:
            out["findings"][fid] = {"level": "wired", "selector": sel,
                                    "rationale": f"on-chain: selector 0x{sel} ({sig}) present in deployed bytecode @ {address}"}
        else:
            out["findings"][fid] = {"level": "not_wired", "selector": sel,
                                    "rationale": f"on-chain: selector 0x{sel} ({sig}) ABSENT from deployed bytecode @ {address} "
                                                 f"— vulnerable function likely not deployed (probable OUT OF SCOPE)"}

    # 2) storage assertions (gating config active?) — a failed assertion downgrades to not_wired
    for a in cfg.get("storage_assertions", []) or []:
        fid, slot = a.get("finding_id"), a.get("slot")
        if not fid or slot is None:
            continue
        sv = qn.get_storage_slots(address, chain, [int(slot)])
        raw = (sv.get("slots", {}) or {}).get(str(int(slot)))
        if raw is None:
            # couldn't read — don't override a wired/selector result with a fabricated negative
            out["findings"].setdefault(fid, _checklist(f"storage slot {slot} unreadable — verify manually"))
            continue
        val = int(raw, 16) if isinstance(raw, str) else 0
        ok = (val != 0) if a.get("expect_nonzero") else True
        if "expect_eq" in a:
            ok = ok and (val == int(str(a["expect_eq"]), 16))
        if not ok:
            out["findings"][fid] = {"level": "not_wired", "slot": int(slot), "value": raw,
                                    "rationale": f"on-chain: gating storage slot {slot} inactive (value {raw}) @ {address} "
                                                 f"— vulnerable config not active (probable OUT OF SCOPE)"}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    doc = build()
    (audit_path("output") / "live_reachability.json").write_text(json.dumps(doc, indent=2) + "\n")
    if not args.quiet:
        if not doc.get("checked"):
            print(f"Live reachability: skipped — {doc.get('note', 'no on-chain coordinates')}")
        else:
            nw = [f for f, v in doc["findings"].items() if v.get("level") == "not_wired"]
            print(f"Live reachability @ {doc['address']} ({doc['chain']}): {len(doc['findings'])} target(s) — "
                  f"not_wired {len(nw)}")
            for f in nw:
                print(f"   {f}: {doc['findings'][f]['rationale']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
