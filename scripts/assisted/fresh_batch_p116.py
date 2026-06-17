#!/usr/bin/env python3
"""P116 — Fresh discovery batch on the CORRECTED (permissionless-first) ranking (research-only, UN-WIRED).

After P115 fixed actor_clarity to read signature modifiers (and the discovery selectors apply the permissionless soft
gate), privileged functions are demoted. P116 runs the assisted discovery process again on this corrected ranking — a
fresh batch of 3, excluding the confirmed controls and everything run in P113+P114 — to exercise the corrected
ranking and extend the truthful terminal-state distribution. Goal is NOT to force findings; ranking selects order,
never validates. Reuses the P114 batch driver (terminal_distribution) read-only via its additive params.

Honest, source-read result: the corrected ranking surfaces a HIGHER-QUALITY candidate than P114's privileged
dead-ends — CuratorRewardsDistributor.distribute, a genuinely permissionless reward distributor adjacent to phi's
awarded H-03 — but per discipline it stays NEEDS_CONTEXT (the hypotheses need cross-contract + runtime evidence, not
source alone). Nothing is promoted.

Usage:
    python scripts/assisted/fresh_batch_p116.py --self-test
    python scripts/assisted/fresh_batch_p116.py --run
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))
sys.path.insert(0, str(ROOT / "scripts" / "investigation"))
import terminal_distribution as TD   # noqa: E402  (P114 batch driver; reused read-only via additive params)
import assisted_fresh_run as AFR     # noqa: E402

FLAGS = {
    "is_gate": False,
    "research_only": True,
    "review_only": True,
    "routes_in_production": False,
    "routed_manifest_ids": [],
}

DEFAULT_CORPUS = ROOT / "documentation" / "research" / "assisted_mode" / "p105" / "benchmark_corpus.json"
DEFAULT_OUT = ROOT / "documentation" / "research" / "assisted_mode" / "p116_fresh_batch"

# everything already run in P113 + P114 (excluded so P116 is a genuinely fresh batch)
ALREADY_RUN_P116 = set(TD.ALREADY_RUN) | {
    ("wildcat-2024-08", "WildcatMarket", "closeMarket"),                                  # P114 (now privileged)
    ("wildcat-2024-08", "WildcatMarketWithdrawals", "repayAndProcessUnpaidWithdrawalBatches"),  # P114
    ("phi-2024-08", "PhiNFT1155", "claimFromFactory"),                                    # P114 (now privileged)
}

# honest source-read rationales (analyst_evidence stays None -> truthful, unforced terminals)
P116_RATIONALES = {
    ("munchables-2024-07", "MigrationManager", "burnRemainingPurchasedNFTs"): (
        "Read MigrationManager.burnRemainingPurchasedNFTs. `external override`, gated by a `seal` flag and a caller "
        "guard (`_user == msg.sender` OR the target user has already chosen a migration action). It sets "
        "`_userPurchasedAction[_user]=LOCKED_BURN` then burns the user's UNLOCKED, unclaimed purchased NFTs in a "
        "bounded paginated loop (_skip..SKIP_AMOUNT). A possible griefing path — calling for another `_user` who has "
        "set an action, forcing a burn/choice — depends on the full migration state machine (`_userPurchasedAction` "
        "semantics) and would need runtime to confirm or refute. No source-provable exploit; not provably safe. "
        "Truthful terminal: NEEDS_CONTEXT."),
    ("phi-2024-08", "CuratorRewardsDistributor", "distribute"): (
        "Read CuratorRewardsDistributor.distribute — a genuinely PERMISSIONLESS reward distributor (the corrected "
        "ranking surfaced this instead of P114's privileged dead-ends). Two source-visible, nameable hypotheses: "
        "(1) UNBOUNDED-LOOP DoS — it loops twice over `credContract.getCuratorAddresses(credId,0,0)` (all curators) "
        "and `phiRewardsContract.depositBatch(...)` over the whole array; if an attacker can cheaply add many sybil "
        "curators (Cred.buyShareCred), the loops/batch exceed gas and rewards become undistributable — matching phi's "
        "awarded H-03 reward-distribution DoS. (2) ROYALTY-TO-CALLER — `_msgSender().safeTransferETH(royaltyfee + "
        "dust)` sends the withdrawRoyalty to whoever calls distribute (the authors even slither-disable "
        "`arbitrary-send-eth`); if the royalty is meant for the protocol, a permissionless keeper harvests it. "
        "NEITHER is closable from source alone: the DoS needs the cross-contract curator-growth cost + a runtime gas "
        "measurement; the royalty needs intent/spec (keeper-fee vs protocol-leak). I did not fabricate a trace. "
        "Truthful terminal: NEEDS_CONTEXT with a strong, specific hypothesis (next step: confirm curator-array growth "
        "cost in Cred + measure depositBatch gas; confirm intended royalty recipient)."),
    ("munchables-2024-07", "MigrationManager", "burnNFTs"): (
        "Read MigrationManager.burnNFTs. `external override`, `seal`-gated, caller guard (`_user == msg.sender` OR "
        "target user chose an action); bounded paginated loop burning the user's LOCKED, unclaimed NFTs and awarding "
        "points. Same class as burnRemainingPurchasedNFTs — a force-burn/wrong-choice griefing path is conceivable "
        "but needs the full migration lifecycle + runtime to confirm/refute. No source-provable exploit; not provably "
        "safe. Truthful terminal: NEEDS_CONTEXT."),
}


def run(corpus: Dict[str, Any]) -> Dict[str, Any]:
    return TD.run_batch(corpus, n=3, already_run=ALREADY_RUN_P116, rationales=P116_RATIONALES)


def _self_test() -> int:
    ok = True

    def chk(cond, m):
        nonlocal ok
        ok &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {m}")

    chk(FLAGS["is_gate"] is False and FLAGS["routes_in_production"] is False, "FLAGS un-wired")
    if not DEFAULT_CORPUS.is_file():
        print("  [SKIP] corpus absent")
        print("SELF-TEST:", "OK" if ok else "FAILED")
        return 0 if ok else 1
    corpus = json.loads(DEFAULT_CORPUS.read_text(encoding="utf-8"))

    sel = TD.select_next_n(corpus, n=3, already_run=ALREADY_RUN_P116)
    keys = {(c["subject"], c["contract"], c["function"]) for c in sel["selected"]}
    chk(len(sel["selected"]) == 3, "exactly 3 fresh candidates")
    chk(("phi-2024-08", "CuratorRewardsDistributor", "distribute") in keys, "corrected ranking surfaces distribute")
    chk(("ramses-2024-10", "RamsesV3Pool", "swap") not in keys, "P113 swap excluded")
    chk(not (keys & {("wildcat-2024-08", "WildcatMarket", "closeMarket"),
                     ("phi-2024-08", "PhiNFT1155", "claimFromFactory")}), "P114 privileged fns excluded/demoted")
    chk(all(c["permissionless"] for c in sel["selected"]), "all selected are permissionless")
    chk(any(s["reason"].startswith("excluded: already-run") for s in sel["skipped"]), "skip log records already-run")

    b = run(corpus)
    chk(len(b["per_candidate"]) == 3, "3 candidates run")
    chk(all(m["terminal_state"] in AFR.TERMINALS for m in b["metrics"]), "all terminals in allowed set")
    chk(all(m["terminal_state"] == "NEEDS_CONTEXT" for m in b["metrics"]), "honest run -> NEEDS_CONTEXT x3")
    chk(b["safety_all_pass"] and b["no_unsafe_package"], "safety holds; no unsafe package")
    chk(all(not m["package_allowed"] for m in b["metrics"]), "no package without runtime confirmation")
    chk(b["overall_pass"], "overall pass")
    # the distribute candidate carries the strong hypothesis
    dist = next(pc for pc in b["per_candidate"] if pc["candidate"]["function"] == "distribute")
    rat = dist["result"]["analyst_rationale"].lower()
    chk("unbounded" in rat and "royalty" in rat and "h-03" in rat, "distribute records the DoS + royalty hypotheses")
    chk(json.dumps(b["terminal_distribution"]) == json.dumps(run(corpus)["terminal_distribution"]), "deterministic")

    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--corpus")
    ap.add_argument("--out-dir")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    if args.run:
        corpus = json.loads(Path(args.corpus or DEFAULT_CORPUS).read_text(encoding="utf-8"))
        b = run(corpus)
        out = TD.write_bundle(b, Path(args.out_dir) if args.out_dir else DEFAULT_OUT)
        print(f"P116 fresh batch (corrected ranking) — OVERALL PASS={b['overall_pass']}")
        print(f"  distribution: {b['terminal_distribution']}")
        for m in b["metrics"]:
            print(f"  {m['candidate']:<58} {m['terminal_state']:<14} harness={m['harness_class']} "
                  f"pkg_allowed={m['package_allowed']}")
        print(f"  safety_all_pass={b['safety_all_pass']} no_unsafe_package={b['no_unsafe_package']}")
        print(f"  -> {out['dir']}")
        return 0 if b["overall_pass"] else 1
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
