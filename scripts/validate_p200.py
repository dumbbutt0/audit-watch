#!/usr/bin/env python3
"""
P200 — Blind fresh-corpus validation of the P199 severity-gate discriminator (predy-2024-05-holdout).

READ-ONLY / OFFLINE eval harness. EVAL_HARNESS_ONLY. Does NOT route, submit, promote, demote, or set production
severity. Applies the P199 SEVERITY_GATE_PROPOSAL discriminator offline to FROZEN blind outputs.

Subcommands:
  build-prompts   freeze blind prompts (deep_trace.md + verbatim source) per surface; token-scan
  gate            apply P199 discriminator offline to frozen raw_outputs -> OFFLINE_SEVERITY_CALIBRATION.json
  score           post-freeze: read predy report.md, score original-vs-calibrated -> metrics.json
"""
import json, os, re, sys, argparse, hashlib

ROOT = "/home/dummy/clones/audit-watch/smart-contract-auditor"
SRC = os.path.join(ROOT, "audits/predy-2024-05-holdout/contracts/src")
DEEP_TRACE = os.path.join(ROOT, "prompts/deep_trace.md")
OUT = os.path.join(ROOT, "documentation/research/assisted_mode/p200_severity_gate_validation")
PROMPTS = os.path.join(OUT, "blind_prompts")
RAW = os.path.join(OUT, "raw_outputs")
REPORT = os.path.join(ROOT, "audits/predy-2024-05-holdout/_sealed_answer_key/report.md")

EVAL_HARNESS_ONLY = True
ROUTES_IN_PRODUCTION = False

# Pre-registered blind sample (frozen in COVERAGE_MANIFEST.md). (id, file, focus, area, line_span_or_None)
SURFACES = [
    ("predy-01", "PredyPool.sol", "trade", "trade entry / value-flow / reentrancy", None),
    ("predy-02", "PredyPool.sol", "reallocate", "reallocation accounting", None),
    ("predy-03", "PredyPool.sol", "execLiquidationCall", "liquidation entry", None),
    ("predy-04", "PredyPool.sol", "supply / withdraw", "supply accounting", None),
    ("predy-05", "PredyPool.sol", "take (onlyByLocker)", "locker auth / value-flow", None),
    ("predy-06", "libraries/logic/LiquidationLogic.sol", "liquidate / checkVaultIsDanger", "liquidation / solvency", None),
    ("predy-07", "libraries/PositionCalculator.sol", "isLiquidatable / calculateMinMargin", "solvency math", None),
    ("predy-08", "libraries/logic/TradeLogic.sol", "trade / callTradeAfterCallback", "settlement callback / reentrancy", None),
    ("predy-09", "PriceFeed.sol", "getSqrtPrice", "Pyth oracle", None),
    ("predy-10", "libraries/UniHelper.sol", "getSqrtTWAP / callUniswapObserve", "Uniswap TWAP oracle", None),
    ("predy-11", "libraries/SlippageLib.sol", "checkPrice", "slippage / MEV", None),
    ("predy-12", "base/SettlementCallbackLib.sol", "execSettlement / sell / buy", "settlement value flow", None),
    ("predy-13", "markets/gamma/GammaTradeMarket.sol", "_executeTrade / _verifyOrder", "order auth / signature", None),
    ("predy-14", "markets/perp/PerpMarketV1.sol", "executeOrderV3 / _verifyOrderV3", "perp order auth", None),
    ("predy-15", "libraries/orders/DecayLib.sol", "decay / decay2", "dutch-auction pricing", None),
    ("predy-16", "libraries/Perp.sol", "reallocate / settleUserBalance", "share/interest accounting", (1, 380)),
]

# answer-key leakage tokens that must NOT appear in any blind prompt
LEAK_TOKENS = ["[H-0", "[M-0", "[C-0", "[L-0", "github.com/code-423n4", "Risk Findings", "Severity Criteria"]


def md5_8(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()[:8]


def read_span(path, span):
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    if span:
        a, b = span
        return "".join(lines[a - 1:b])
    return "".join(lines)


def cmd_build_prompts(_):
    os.makedirs(PROMPTS, exist_ok=True)
    deep = open(DEEP_TRACE, encoding="utf-8").read()
    leaks = []
    for sid, rel, focus, area, span in SURFACES:
        src = read_span(os.path.join(SRC, rel), span)
        prompt = (
            deep
            + "\n\n=== INPUT: ONE FUNCTION UNDER TRACE ===\n"
            + f"high_suspicion_invariant: solvency / accounting / authorization correctness of `{focus}`\n"
            + f"dangerous_interaction: external/permissionless entry into `{focus}` in `{rel}` ({area})\n\n"
            + f"Trace the function(s) `{focus}` in the verbatim source below. Run STEP 0 mechanism inventory,\n"
            + "carry forward every supported mechanism, then return ONLY the JSON verdict per the schema above.\n\n"
            + f"=== VERBATIM SOURCE: {rel} ===\n```solidity\n" + src + "\n```\n"
        )
        for tok in LEAK_TOKENS:
            if tok in prompt:
                leaks.append((sid, tok))
        with open(os.path.join(PROMPTS, f"{sid}.txt"), "w", encoding="utf-8") as f:
            f.write(prompt)
    print(f"wrote {len(SURFACES)} prompts to {PROMPTS}")
    print("LEAK SCAN:", "CLEAN" if not leaks else f"LEAKS {leaks}")
    print("deep_trace.md md5_8:", md5_8(DEEP_TRACE))


# ---------------------------------------------------------------------------
# OFFLINE P199 SEVERITY GATE (deterministic, answer-key-blind, frozen pre-scoring)
# Implements the P199 SEVERITY_GATE_PROPOSAL discriminator as a fixed, auditable
# classifier over each frozen blind output's OWN evidence. No per-case tuning,
# no answer-key input -> genuine out-of-sample application.
# ---------------------------------------------------------------------------

# Keyword signal sets (lowercased substring match).
VALUE_EXTRACTION = [
    "drain", "steal", "stolen", "theft", "extract value", "extracts the difference",
    "takeover", "take over", "insolvency", "insolvent", "bad debt", "fund loss", "loses funds",
    "lose funds", "permanent fund loss", "phantom margin", "inflated margin", "pool is short",
    "pool loss", "net short", "shortchanged", "drained", "more shares than", "excess tokens",
    "over-credited", "more than their pro-rata", "absorbs", "absorb", "unauthorized privileged",
    "unauthorized vault", "without committing", "zero token commitment", "surplus quote",
]
DOS_GRIEFING = [
    "dos", "denial of service", "griefing", "grief", "brick", "bricked", "stuck",
    "permanently unfillable", "lockout", "oracle lockout", "unavailable", "liveness",
    "cannot be liquidated", "permanently stuck", "permanent griefing", "unserviced",
    "block legitimate", "blocks legitimate", "blocking legitimate",
]
PRECISION = [
    "truncation", "truncate", "truncates", "rounding", "precision", "dust", "off by one",
    "off-by-one", "1 wei", "systematic rounding", "systematic bias",
]
COMPLIANCE_LOCAL = ["compliance", "restriction gap", "bounded local", "bounded mispricing", "single user", "local loss", "local under-credit"]
PERMISSIONLESS_POS = [
    "permissionless", "any eoa", "unprivileged", "any caller", "no role", "no privileged",
    "any user", "any market participant", "any address", "any contract that", "no special role",
    "no admin", "not admin-only", "not admin-gated",
]
ADMIN_TRUSTED = ["onlyoperator", "only operator", "admin key", "trusted prerequisite", "governance role", "owner-only", "requires admin", "privileged keys needed"]
# the High value-claim is conditioned on code the agent could NOT see / a runtime dispute
HARNESS_CONDITIONAL = [
    "not provided", "not shown", "not visible", "cannot be ruled out", "burden of proof",
    "cannot be determined", "cannot determine", "internals, which are not", "without seeing",
    "source of that library", "source not provided", "depends entirely on", "is unknown from this source",
    "not resolvable", "cannot confirm", "cannot be confirmed", "belongs to harness",
]


def _hits(text, terms):
    t = text.lower()
    return [w for w in terms if w in t]


def classify(candidate):
    sel = candidate.get("selected_mechanisms") or candidate.get("chosen_mechanism") or []
    if isinstance(sel, dict):
        sel = [sel]
    sel0 = sel[0] if sel else {}
    sel0_text = json.dumps(sel0).lower()
    imp = candidate.get("impact_direction", {})
    imp_text = (json.dumps(imp) if isinstance(imp, (dict, list)) else str(imp)).lower()
    full = sel0_text + " " + imp_text

    ve = _hits(full, VALUE_EXTRACTION)
    dos = _hits(full, DOS_GRIEFING)
    prec = _hits(full, PRECISION)
    comp = _hits(full, COMPLIANCE_LOCAL)
    perm_pos = _hits(full, PERMISSIONLESS_POS)
    admin = _hits(full, ADMIN_TRUSTED)
    # harness-conditional keyed on the PRIMARY selected mechanism only (its own value-claim)
    harness = _hits(sel0_text, HARNESS_CONDITIONAL)

    # primary impact category from the PRIMARY selected mechanism
    sel0_ve = _hits(sel0_text, VALUE_EXTRACTION)
    sel0_dos = _hits(sel0_text, DOS_GRIEFING)
    sel0_prec = _hits(sel0_text, PRECISION)
    sel0_comp = _hits(sel0_text, COMPLIANCE_LOCAL)
    if sel0_prec and not sel0_ve:
        category = "precision"
    elif sel0_comp and not sel0_ve:
        category = "compliance_local"
    elif sel0_dos and not sel0_ve:
        category = "dos_griefing"
    elif sel0_ve:
        category = "value_extraction"
    elif sel0_dos:
        category = "dos_griefing"
    else:
        category = "indeterminate"

    permissionless = bool(perm_pos) and not admin
    harness_conditional = bool(harness)

    # P199 reject-first decision tree
    if category == "value_extraction":
        if permissionless and not harness_conditional:
            label = "HIGH_CONFIRMED"
        elif harness_conditional:
            label = "NEEDS_HARNESS_FOR_SEVERITY"
        else:  # admin/trusted prerequisite -> cap Medium
            label = "MEDIUM_OR_LOWER_CALIBRATED"
    elif category in ("dos_griefing", "precision", "compliance_local"):
        label = "MEDIUM_OR_LOWER_CALIBRATED"
    else:
        label = "NEEDS_HARNESS_FOR_SEVERITY"

    return {
        "category": category,
        "calibrated_label": label,
        "permissionless": permissionless,
        "harness_conditional": harness_conditional,
        "signals": {
            "value_extraction": ve, "dos_griefing": dos, "precision": prec,
            "compliance_local": comp, "permissionless_pos": perm_pos, "admin_trusted": admin,
            "harness_conditional_primary": harness,
        },
    }


# ---------------------------------------------------------------------------
# FROZEN RUBRIC GRADES (authoritative). The keyword classify() above proved too
# noisy to faithfully apply the P199 8-dimension discriminator (it false-promoted
# predy-11 MEDIUM->HIGH, mis-categorised predy-02 as 'precision', mis-set predy-06
# permissionless). So the authoritative calibration is the P199 rubric applied by
# the orchestrator to each frozen output's OWN evidence, ANSWER-KEY-BLIND, and
# frozen here as constants before any answer-key read. classify() output is kept
# as supplementary audit signal only. Reject-first: HIGH only on a source-PROVEN
# permissionless theft/insolvency/permanent-loss/priv-transition of material
# magnitude; unproven reachability/magnitude -> NEEDS_HARNESS; DoS/griefing/
# precision/bounded-local -> Medium.
RUBRIC_GRADES = {
    "predy-01": {"label": "NEEDS_HARNESS_FOR_SEVERITY", "value_path": "vault-takeover/theft",
                 "permissionless": True, "magnitude": "unproven", "reachability": "conditional_on_unseen",
                 "permanence": "n/a",
                 "rationale": "Theft claim rests on createOrGetVault having no owner check — that function is NOT in the shown file; reachability conditional on unseen GlobalData code. Reject-first: unproven reachability -> harness."},
    "predy-02": {"label": "MEDIUM_OR_LOWER_CALIBRATED", "value_path": "griefing/adversarial-timing",
                 "permissionless": True, "magnitude": "bounded", "reachability": "executable",
                 "permanence": "recoverable",
                 "rationale": "Primary impact = permissionless reallocate causing LP fee-loss via adversarial timing + settlement DoS ('may simply grief'). Griefing/MEV-timing, not proven theft -> Medium."},
    "predy-03": {"label": "NEEDS_HARNESS_FOR_SEVERITY", "value_path": "over-liquidation/theft",
                 "permissionless": True, "magnitude": "unproven", "reachability": "conditional_on_unseen",
                 "permanence": "n/a",
                 "rationale": "Agent itself: 'burden of proof ... belongs to harness review — source of that library not provided'. closeRatio bound unproven from shown source -> harness."},
    "predy-04": {"label": "NEEDS_HARNESS_FOR_SEVERITY", "value_path": "share-inflation/stale-rate theft",
                 "permissionless": True, "magnitude": "unproven", "reachability": "conditional_on_unseen",
                 "permanence": "n/a",
                 "rationale": "Stale-rate and first-depositor inflation both conditioned on unseen SupplyLogic ('accrual ordering cannot be confirmed'); generic pattern asserted without mint math -> harness."},
    "predy-05": {"label": "NEEDS_HARNESS_FOR_SEVERITY", "value_path": "pool-drain/theft",
                 "permissionless": True, "magnitude": "unproven", "reachability": "conditional_on_unseen",
                 "permanence": "n/a",
                 "rationale": "Agent: entitlement cap 'depends entirely on globalData.take() internals, which are not visible'. Drain conditional on unseen code -> harness."},
    "predy-06": {"label": "MEDIUM_OR_LOWER_CALIBRATED", "value_path": "DoS/griefing (recipient revert)",
                 "permissionless": True, "magnitude": "bounded", "reachability": "executable",
                 "permanence": "recoverable",
                 "rationale": "Primary selected = vault.recipient revert bricks liquidation (DoS/griefing); secondary partial-close bad-debt is bounded/conditional. DoS-dominant -> Medium."},
    "predy-07": {"label": "HIGH_CONFIRMED", "value_path": "oracle-no-staleness -> insolvency/wrongful-liq",
                 "permissionless": True, "magnitude": "material", "reachability": "executable",
                 "permanence": "permanent",
                 "rationale": "Missing staleness/deviation guard on getSqrtIndexPrice/external price IS visible in shown source; insolvency or wrongful-liquidation, permissionless. Matches P199 genuine-High oracle class."},
    "predy-08": {"label": "HIGH_CONFIRMED", "value_path": "unchecked hook + checkSafe-after-callback -> theft",
                 "permissionless": True, "magnitude": "material", "reachability": "executable",
                 "permanence": "permanent",
                 "rationale": "IHooks(msg.sender) cast with no whitelist and checkSafe AFTER external callback both visible in shown source -> reentrancy/phantom-margin. (Caveat: callback-to-caller may be by design — flagged.)"},
    "predy-09": {"label": "HIGH_CONFIRMED", "value_path": "Chainlink-no-staleness -> mispricing/insolvency",
                 "permissionless": True, "magnitude": "material", "reachability": "executable",
                 "permanence": "permanent",
                 "rationale": "latestRoundData destructured to quoteAnswer only, single require(>0), no updatedAt/answeredInRound — visible in shown source. Classic High oracle staleness."},
    "predy-10": {"label": "HIGH_CONFIRMED", "value_path": "TWAP->spot manipulation -> insolvency",
                 "permissionless": True, "magnitude": "material", "reachability": "executable",
                 "permanence": "permanent",
                 "rationale": "Fallback to oldest observation with no minimum window IS visible; TWAP degrades to manipulable spot, flash-swap permissionless -> under-collateralized borrow."},
    "predy-11": {"label": "MEDIUM_OR_LOWER_CALIBRATED", "value_path": "bounded MEV / sandwich",
                 "permissionless": True, "magnitude": "bounded", "reachability": "speculative",
                 "permanence": "per-trade",
                 "rationale": "Agent verdict MEDIUM; short/long bound-label inversion is speculative ('if convention is opposite'); impact bounded per-trade MEV. Reject-first keeps Medium (must NOT promote)."},
    "predy-12": {"label": "HIGH_CONFIRMED", "value_path": "settlement accounting shortfall -> direct pool loss",
                 "permissionless": True, "magnitude": "material", "reachability": "executable",
                 "permanence": "permanent",
                 "rationale": "buy() returns maxQuoteAmount-quoteAmount (not -quoteAmountToUni) — arithmetic VISIBLE and traced concretely in shown source; pool short by quoteAmount-quoteAmountToUni, filler permissionless."},
    "predy-13": {"label": "NEEDS_HARNESS_FOR_SEVERITY", "value_path": "filler-whitelist bypass (auth)",
                 "permissionless": True, "magnitude": "unproven", "reachability": "executable",
                 "permanence": "n/a",
                 "rationale": "minMargin==0 filler-check-after-trade ordering IS visible, but the fund-loss magnitude of executing a validly-signed order as non-filler is unproven (front-run/forced-liq speculative) -> harness, not auto-High."},
    "predy-14": {"label": "NEEDS_HARNESS_FOR_SEVERITY", "value_path": "filler bypass + verify-after-execute",
                 "permissionless": True, "magnitude": "unproven", "reachability": "executable",
                 "permanence": "n/a",
                 "rationale": "Same filler-ordering as predy-13 plus verify-after-execute; cost-pulled-post-trade fund-loss conditioned on price manipulation (unproven). Auth bug visible, magnitude unproven -> harness."},
    "predy-15": {"label": "MEDIUM_OR_LOWER_CALIBRATED", "value_path": "precision truncation + overflow DoS",
                 "permissionless": True, "magnitude": "dust/bounded", "reachability": "executable",
                 "permanence": "per-trade",
                 "rationale": "Agent verdict MEDIUM; division-truncation bias (dust) + overflow DoS. Precision/DoS -> Medium."},
    "predy-16": {"label": "HIGH_CONFIRMED", "value_path": "rebalance pool-can-go-negative -> insolvency",
                 "permissionless": True, "magnitude": "material", "reachability": "executable",
                 "permanence": "permanent",
                 "rationale": "settleUserBalance debits shared rebalance pool with no balance check (pool can go negative) + stale-index settle — both visible in the shown span; solvency break / fund mis-allocation, permissionless."},
}


def cmd_gate(_):
    rows = []
    for sid, rel, focus, area, span in SURFACES:
        cand = json.load(open(os.path.join(RAW, f"{sid}.json")))
        c = classify(cand)
        rg = RUBRIC_GRADES[sid]
        rows.append({
            "id": sid, "surface": f"{focus} ({rel})", "area": area,
            "blind_verdict": cand.get("verdict"),
            "calibrated_label": rg["label"],   # authoritative
            "rubric": rg,
            "keyword_signal_supplementary": {"category": c["category"], "label": c["calibrated_label"],
                                             "permissionless": c["permissionless"],
                                             "harness_conditional": c["harness_conditional"],
                                             "signals": c["signals"]},
        })
    out = {
        "_meta": {"phase": "P200", "eval_harness_only": EVAL_HARNESS_ONLY,
                  "routes_in_production": ROUTES_IN_PRODUCTION,
                  "note": "Offline P199 discriminator applied to FROZEN blind outputs, answer-key-blind. FREEZE 2."},
        "calibration": rows,
    }
    with open(os.path.join(OUT, "OFFLINE_SEVERITY_CALIBRATION.json"), "w") as f:
        json.dump(out, f, indent=2)
    from collections import Counter
    bc = Counter(r["blind_verdict"] for r in rows)
    cc = Counter(r["calibrated_label"] for r in rows)
    print("blind verdicts :", dict(bc))
    print("calibrated     :", dict(cc))
    for r in rows:
        print(f"  {r['id']}: {r['blind_verdict']:>14} -> {r['calibrated_label']:<28} [{r['rubric']['value_path']}]")


# ---------------------------------------------------------------------------
# POST-FREEZE SCORING (answer key opened only here, after FREEZE 1 + FREEZE 2)
# ---------------------------------------------------------------------------
AWARDED = {  # predy-2024-05 report.md
    "H-01": ("High", "Reallocation depends on slot0 price, manipulable"),
    "H-02": ("High", "Liquidators bypass remaining negative-margin check, loss to protocol"),
    "H-03": ("High", "One pair steals another pair's Uniswap liquidity during reallocate (same pool/ticks)"),
    "H-04": ("High", "Liquidation transfers token from Market instead of liquidator when remainingMargin<0"),
    "M-01": ("Medium", "Liquidity manipulation possible when trading"),
    "M-02": ("Medium", "updateIRMParams does not applyInterestForToken before updating irmParams"),
    "M-03": ("Medium", "Incorrect price for negative ticks due to lack of rounding down"),
    "M-04": ("Medium", "Chainlink latestRoundData might return stale/incorrect results"),
    "M-05": ("Medium", "DoS in GammaTradeMarket._removePosition prevents liquidation"),
    "M-06": ("Medium", "Vaults immune from liquidation by setting vault.recipient to blacklisted token"),
    "M-07": ("Medium", "Reallocation sends exceed quoteTokens to Market instead of reallocator"),
    "M-08": ("Medium", "PriceFeed does not return correct price for quote pairs"),
}

# Post-freeze surface -> awarded mapping. match_quality:
#   exact          = blind PRIMARY mechanism IS the awarded finding
#   secondary      = blind found it as a NON-primary carried mechanism
#   surface_diff   = same surface/area as an awarded finding but DIFFERENT mechanism (recall miss)
#   none           = blind mechanism not awarded
SURFACE_MAP = {
    "predy-01": {"matches": [], "note": "vault-takeover mechanism not awarded"},
    "predy-02": {"matches": [("H-01", "surface_diff"), ("H-03", "surface_diff"), ("M-07", "surface_diff")],
                 "note": "reallocate surface has awarded H-01/H-03/M-07 but blind found griefing/timing, NOT slot0/shared-tick/excess-quote -> recall miss"},
    "predy-03": {"matches": [], "note": "closeRatio-bound mechanism not awarded"},
    "predy-04": {"matches": [], "note": "supply share-inflation not awarded"},
    "predy-05": {"matches": [], "note": "take() drain not awarded"},
    "predy-06": {"matches": [("M-06", "exact"), ("H-02", "secondary"), ("H-04", "surface_diff")],
                 "note": "selected[0]=M-06 (recipient bricks liq) exact; selected[1]=H-02 (negative-margin bypass) exact; H-04 same branch diff framing"},
    "predy-07": {"matches": [("M-04", "secondary"), ("M-08", "secondary")],
                 "note": "isLiquidatable oracle-no-staleness overlaps M-04/M-08 (Medium); feeAmount mechanism not awarded"},
    "predy-08": {"matches": [], "note": "hook/checkSafe mechanism not awarded (likely recall FP)"},
    "predy-09": {"matches": [("M-04", "exact"), ("M-08", "secondary")],
                 "note": "selected[0]=Chainlink no-staleness = M-04 exact; decimalsDiff = M-08 partial"},
    "predy-10": {"matches": [("M-03", "secondary")],
                 "note": "selected[1]=negative-tick truncation = M-03 exact; PRIMARY TWAP->spot not separately awarded"},
    "predy-11": {"matches": [("M-01", "exact")], "note": "liquidity manipulation when trading = M-01"},
    "predy-12": {"matches": [], "note": "settlement buy() accounting shortfall not in awarded H/M"},
    "predy-13": {"matches": [], "note": "filler-whitelist bypass not awarded"},
    "predy-14": {"matches": [], "note": "filler/verify-after-execute not awarded"},
    "predy-15": {"matches": [], "note": "decay truncation/overflow not awarded"},
    "predy-16": {"matches": [("H-01", "surface_diff"), ("H-03", "surface_diff")],
                 "note": "Perp.reallocate surface; blind found stale-index/pool-negative, not the awarded slot0/shared-tick -> recall miss"},
}

CEIL = {"CRITICAL_THREAD": "High+", "HIGH_THREAD": "High", "MEDIUM_THREAD": "Medium",
        "DEAD_END": "None", "NEEDS_MORE_CONTEXT": "None"}
CAL_TIER = {"HIGH_CONFIRMED": "High", "MEDIUM_OR_LOWER_CALIBRATED": "Medium",
            "NEEDS_HARNESS_FOR_SEVERITY": "Harness", "SOURCE_REFUTED": "None", "INSUFFICIENT_EVIDENCE": "None"}


def cmd_score(_):
    cal = {r["id"]: r for r in json.load(open(os.path.join(OUT, "OFFLINE_SEVERITY_CALIBRATION.json")))["calibration"]}
    per = []
    for sid, rel, focus, area, span in SURFACES:
        r = cal[sid]; mp = SURFACE_MAP[sid]
        ceil = CEIL[r["blind_verdict"]]
        catier = CAL_TIER[r["calibrated_label"]]
        # best mechanism-matched awarded finding (exact preferred over secondary)
        exact = [m for m in mp["matches"] if m[1] == "exact"]
        secondary = [m for m in mp["matches"] if m[1] == "secondary"]
        matched = (exact or secondary)
        awarded_sev = None; matched_id = None; mq = None
        if matched:
            matched_id, mq = matched[0]
            awarded_sev = AWARDED[matched_id][0]
        per.append({"id": sid, "surface": f"{focus}", "blind_verdict": r["blind_verdict"],
                    "ceiling_tier": ceil, "calibrated_label": r["calibrated_label"], "calibrated_tier": catier,
                    "matched_awarded": matched_id, "match_quality": mq, "awarded_severity": awarded_sev,
                    "all_matches": mp["matches"], "note": mp["note"]})

    # severity-scoring subset = surfaces with an exact/secondary mechanism match to an awarded finding
    matched_rows = [p for p in per if p["matched_awarded"]]
    awarded_medium = [p for p in matched_rows if p["awarded_severity"] == "Medium"]
    awarded_high = [p for p in matched_rows if p["awarded_severity"] == "High"]

    # over-HIGH on matched awarded-Medium: ceiling High vs calibrated High
    ceil_overhigh = [p for p in awarded_medium if p["ceiling_tier"].startswith("High")]
    cal_overhigh = [p for p in awarded_medium if p["calibrated_tier"] == "High"]
    # genuine-High preservation (matched awarded-High): did calibration keep it >= High (or Harness, not Medium/None)?
    high_kept_high = [p for p in awarded_high if p["calibrated_tier"] == "High"]
    high_to_harness = [p for p in awarded_high if p["calibrated_tier"] == "Harness"]
    high_to_medium = [p for p in awarded_high if p["calibrated_tier"] == "Medium"]
    high_to_none = [p for p in awarded_high if p["calibrated_tier"] == "None"]

    # High mechanisms the blind run actually found (exact OR secondary), anywhere across surfaces,
    # with how the calibration graded that surface (captures multi-mechanism folding e.g. predy-06 H-02).
    high_found_anywhere = []
    for p in per:
        for fid, q in p["all_matches"]:
            if AWARDED[fid][0] == "High" and q in ("exact", "secondary"):
                high_found_anywhere.append({"id": p["id"], "awarded": fid, "match_quality": q,
                                            "surface_calibrated_tier": p["calibrated_tier"],
                                            "surface_calibrated_label": p["calibrated_label"]})

    from collections import Counter
    metrics = {
        "_meta": {"phase": "P200", "corpus": "predy-2024-05-holdout", "eval_harness_only": EVAL_HARNESS_ONLY,
                  "routes_in_production": ROUTES_IN_PRODUCTION,
                  "blind_model": "sonnet", "freeze1_raw_outputs": "4aede343", "freeze2_calibration": "1e158f1e"},
        "n_surfaces": len(per),
        "awarded_counts": {"High": 4, "Medium": 8},
        "blind_ceiling_distribution": dict(Counter(p["ceiling_tier"] for p in per)),
        "calibrated_distribution": dict(Counter(p["calibrated_label"] for p in per)),
        "ceiling_ge_high": sum(1 for p in per if p["ceiling_tier"].startswith("High")),
        "calibrated_high_confirmed": sum(1 for p in per if p["calibrated_tier"] == "High"),
        "mechanism_matched_surfaces": len(matched_rows),
        "matched_awarded_medium": [p["id"] + "->" + p["matched_awarded"] for p in awarded_medium],
        "matched_awarded_high": [p["id"] + "->" + p["matched_awarded"] for p in awarded_high],
        "over_high_on_matched_medium": {
            "ceiling": [p["id"] for p in ceil_overhigh],
            "calibrated": [p["id"] for p in cal_overhigh],
            "ceiling_rate": f"{len(ceil_overhigh)}/{len(awarded_medium)}",
            "calibrated_rate": f"{len(cal_overhigh)}/{len(awarded_medium)}",
            "fixed_by_gate": [p["id"] for p in ceil_overhigh if p not in cal_overhigh],
            "still_over_high": [p["id"] for p in cal_overhigh],
        },
        "genuine_high_preservation": {
            "matched_high_found": [p["id"] + "->" + p["matched_awarded"] for p in awarded_high],
            "kept_high": [p["id"] for p in high_kept_high],
            "routed_harness": [p["id"] for p in high_to_harness],
            "demoted_to_medium": [p["id"] for p in high_to_medium],
            "demoted_to_none": [p["id"] for p in high_to_none],
        },
        "high_mechanisms_found_anywhere": high_found_anywhere,
        "recall_miss_high_surfaces": [p["id"] + " " + p["note"] for p in per
                                      if any(q[1] == "surface_diff" and AWARDED[q[0]][0] == "High" for q in p["all_matches"])
                                      and not p["matched_awarded"]],
        "unawarded_high_confirmed": [p["id"] for p in per if p["calibrated_tier"] == "High" and not p["matched_awarded"]],
        "per_surface": per,
    }
    with open(os.path.join(OUT, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)
    print(json.dumps({k: v for k, v in metrics.items() if k not in ("per_surface",)}, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build-prompts").set_defaults(fn=cmd_build_prompts)
    sub.add_parser("gate").set_defaults(fn=cmd_gate)
    sub.add_parser("score").set_defaults(fn=cmd_score)
    args = ap.parse_args()
    args.fn(args)
