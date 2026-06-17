#!/usr/bin/env python3
"""P205 — vultisig L3 second-corpus validation harness helper (READ-ONLY/offline, EVAL_HARNESS_ONLY).
build-prompts: freeze blind threat-ceiling prompts (deep_trace.md + verbatim vultisig source) per surface; token-scan.
(Scoring is done separately after harness runs.)"""
import os, argparse, hashlib

ROOT = "/home/dummy/clones/audit-watch/smart-contract-auditor"
SRC = os.path.join(ROOT, "audits/vultisig-2024-06-holdout/contracts/src")
DEEP_TRACE = os.path.join(ROOT, "prompts/deep_trace.md")
OUT = os.path.join(ROOT, "documentation/research/assisted_mode/p205_l3_vultisig_validation")
PROMPTS = os.path.join(OUT, "blind_prompts")
LEAK = ["[H-0", "[M-0", "[C-0", "[L-0", "code-423n4", "Risk Findings", "Severity Criteria"]

SURFACES = [
    ("v-01", "ILOPool.sol", "buy (raise/deposit)", "fund-custody / accounting"),
    ("v-02", "ILOPool.sol", "claim (vested claim + fees)", "fee/vesting accounting"),
    ("v-03", "ILOPool.sol", "launch (V3 liquidity)", "launch / liquidity / DoS"),
    ("v-04", "ILOPool.sol", "claimRefund / claimProjectRefund", "refund custody / permanent-lock"),
    ("v-05", "ILOManager.sol", "initialize / initILOPool", "init / access-control"),
    ("v-06", "ILOManager.sol", "launch / claimRefund / setPlatformFee / setFeeTaker", "manager control / fees"),
    ("v-07", "base/ILOWhitelist.sol", "whitelist set/remove/isWhitelisted/setOpenToAll", "access-control / whitelist"),
    ("v-08", "base/LiquidityManagement.sol", "addLiquidity / uniswapV3MintCallback", "V3 mint callback / payment"),
]


def md5_8(p): return hashlib.md5(open(p, "rb").read()).hexdigest()[:8]


def cmd_build_prompts(_):
    os.makedirs(PROMPTS, exist_ok=True)
    deep = open(DEEP_TRACE, encoding="utf-8").read()
    leaks = []
    for sid, rel, focus, cat in SURFACES:
        src = open(os.path.join(SRC, rel), encoding="utf-8").read()
        prompt = (deep + "\n\n=== INPUT: ONE FUNCTION UNDER TRACE ===\n"
                  + f"high_suspicion_invariant: ILO fund-custody / vesting / authorization correctness of `{focus}`\n"
                  + f"dangerous_interaction: external/permissionless entry into `{focus}` in `{rel}` ({cat})\n\n"
                  + f"Trace `{focus}` in the verbatim source below. Run STEP 0 mechanism inventory, carry forward every\n"
                  + "supported mechanism, then return ONLY the JSON verdict per the schema above.\n\n"
                  + f"=== VERBATIM SOURCE: {rel} ===\n```solidity\n" + src + "\n```\n")
        for t in LEAK:
            if t in prompt: leaks.append((sid, t))
        open(os.path.join(PROMPTS, f"{sid}.txt"), "w", encoding="utf-8").write(prompt)
    print(f"wrote {len(SURFACES)} prompts; LEAK:", "CLEAN" if not leaks else leaks, "| deep_trace", md5_8(DEEP_TRACE))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build-prompts").set_defaults(fn=cmd_build_prompts)
    a = ap.parse_args(); a.fn(a)
