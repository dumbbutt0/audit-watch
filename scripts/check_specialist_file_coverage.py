#!/usr/bin/env python3
"""check_specialist_file_coverage.py  (p322)

Enforcement layer for "the cold /ite-audit opens ALL in-scope files in each specialist's remit".

P315 made the coverage GATE fail-closed (every in-scope manifest item must be dispositioned).
But the hybra-finance M-02 autopsy showed a specialty-relevant file (GaugeV2.emergencyWithdraw, a
reward bug) can still slip through with a LIGHT sweep-clear instead of being OPENED by the reward
specialist — so the banked specialist classes never fire on it. This check surfaces exactly that gap:
any in-scope file whose name/path matches a specialist trigger but which has NO specialist-grade
disposition (finding / needs_deep_pass) — i.e. it is only `cleared` (light sweep) or still unassigned.

Read-only / advisory by default; --strict exits non-zero if any specialty-trigger file lacks a
specialist-grade pass, so it can be wired before the review gate.
"""
import json, sys, re, argparse
from audit_context import audit_path  # noqa

# specialty trigger keywords -> the specialist that must OPEN files matching them
SPECIALTY_TRIGGERS = {
    "reward|gauge|bribe|stake|staking|incentive|emission|distributor": "reward/economic_attack/behavioral_state",
    "oracle|price|twap|ema|feed|chainlink": "oracle",
    "vault|erc4626|escrow|collateral|deposit|withdraw|redeem": "erc4626/token_integration",
    "vote|voting|governor|governance|checkpoint|veNFT|delegate": "logic/access_control",
    "swap|pool|tick|liquidity|amm|sqrt": "oracle/arithmetic/logic",
    "fee|commission|royalty|penalty": "economic_attack",
    "auth|admin|owner|role|access|guardian|factory": "access_control",
}
SPECIALIST_GRADE = {"finding", "needs_deep_pass"}  # a real specialist pass, not a light sweep-clear


def load(path):
    try:
        return json.load(open(path))
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="exit 1 if any specialty file lacks a specialist-grade pass")
    args = ap.parse_args()

    out = audit_path("output")
    manifest = load(out / "coverage_manifest.json")
    disp = load(out / "coverage_dispositions.json")
    if not manifest or not disp:
        print("[check] manifest/dispositions not found — run build_coverage_manifest + init first")
        return 0

    items = manifest.get("items", manifest) if isinstance(manifest, dict) else manifest
    dlist = disp.get("dispositions", disp.get("items", disp)) if isinstance(disp, dict) else disp
    # map manifest_id/file -> disposition status
    status_by_file = {}
    for d in (dlist if isinstance(dlist, list) else []):
        f = d.get("file") or d.get("path")
        st = d.get("status") or d.get("disposition")
        if f:
            status_by_file.setdefault(f, set()).add(st)

    in_scope_files = sorted({(i.get("file") or i.get("path")) for i in items
                             if (i.get("in_scope", True) and (i.get("status") != "deferred_out_of_scope"))})
    in_scope_files = [f for f in in_scope_files if f]

    gaps = []
    for f in in_scope_files:
        low = f.lower()
        for pat, owner in SPECIALTY_TRIGGERS.items():
            if re.search(pat, low):
                sts = status_by_file.get(f, set())
                if not (sts & SPECIALIST_GRADE):
                    gaps.append((f, owner, sorted(s for s in sts if s) or ["unassigned"]))
                break

    print(f"[check] in-scope files: {len(in_scope_files)} | specialist-coverage gaps: {len(gaps)}")
    for f, owner, sts in gaps[:60]:
        print(f"  GAP  {f.split('/')[-1]:42} specialist={owner:34} status={sts}")
    if gaps:
        print("[check] ^ specialty-relevant files NOT opened at specialist grade (only sweep-cleared/unassigned).")
        print("        The cold /ite-audit must OPEN these with the owning specialist's class checklist (hybra M-02 lesson).")
        if args.strict:
            return 1
    else:
        print("[check] OK — every specialty-relevant in-scope file has a specialist-grade pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
