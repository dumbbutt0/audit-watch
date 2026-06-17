#!/usr/bin/env python3
"""
liquidation_health_accounting_taxonomy.py — pure (no-I/O) classifier for the LIQUIDATION / HEALTH-ACCOUNTING
research prototype. Seeded on Size Credit (P2P fixed-rate credit), Ethos-informed for Liquity-fork CDPs.
Detects liquidation / compensation / replacement / redemption / stability-pool flows where collateral, debt,
credit, CR/health, fees, remainder, redistribution, or liquidator profit may not be conserved or bounded.

Pure classifier (no I/O, no routing): the audit that uses this is ADVISORY and is_gate:false — it routes
high-confidence candidates to a deep pass in strict full-audit only, and NEVER mints / blocks. This taxonomy
is unchanged by the promotion (helper-volume control lives in the audit). NAME-GATE is the primary FP control;
every shape requires the gate AND >=2 term dimensions; broad CDP terms (trove/icr/offset/redeem) are eligible
but inert until a shape's context fires.

Shapes:
  1. collateral_remainder_cap         (Size H-03; Ethos redeemCollateral M-09)
  2. liquidator_profit_bound          (Size H-04)
  3. health_factor_after_action       (Size M-09) — STRONG-PATH gated (no repay-improves-health over-flag)
  4. replacement_swap_fee_accounting  (Size M-11)
  5. credit_sale_bypass               (Size M-05/M-13)
  6. stability_pool_redistribution    (Ethos H-01 StabilityPool offset/reward redistribution)
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "liquidation_health_accounting_patterns.json"

ROUTED_CONFIDENCE = frozenset({"high", "medium"})
_COMMENT_RE = re.compile(r"//[^\n]*|/\*.*?\*/", re.DOTALL)


@lru_cache(maxsize=1)
def _cfg() -> dict:
    try:
        return json.loads(CONFIG.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _terms(key: str, default: list) -> tuple:
    return tuple(_cfg().get(key, default))


# name-gate (Size + Ethos/Liquity CDP vocab) — eligible-but-inert until a shape's context fires
NAME_GATE = lambda: _terms("name_gate", [
    "liquidate", "liquidation", "compensate", "replacement", "repay", "seize", "collateralratio",
    "underwater", "health", "risk", "selfliquidate", "isdebtpositionliquidatable", "validateuserisnotunderwater",
    # CDP / Liquity additions (bare icr/mcr/tcr are intentionally NOT here — too short / substring-collide;
    # the meaningful CR hosts are gated via getcurrenticr/gettcr/recoverymode/collateralratio/trove):
    "redeem", "redeemcollateral", "offset", "stabilitypool", "recoverymode", "checkrecoverymode",
    "getcurrenticr", "gettcr", "trove", "collsurplus", "collateralsurplus", "redistribut",
    "rewardsum", "rewardsperunit", "feeoperation", "lastfeeoperation"])
COLLATERAL = lambda: _terms("collateral_terms", ["collateral", "seize", "collateraltoken", "collsurplus", "coll"])
DEBT = lambda: _terms("debt_terms", ["debt", "borrow", "repay", "futurevalue", "lusd"])
CREDIT = lambda: _terms("credit_terms", ["credit", "creditposition"])
# long, unambiguous health terms (substring match) — bare icr/mcr/tcr are matched word-boundary'd below
HEALTH = lambda: _terms("health_terms", ["collateralratio", "health", "risk", "underwater", "solvency",
                                         "crliquidation", "isuserunderwater", "validateuserisnotunderwater",
                                         "isdebtpositionliquidatable", "recoverymode", "checkrecoverymode",
                                         "getcurrenticr"])
# short CR tokens — substring-collide (e.g. "tcr" ⊂ random ids) so matched as WHOLE WORDS only
HEALTH_WORD = lambda: _terms("health_word_terms", ["icr", "mcr", "tcr"])
PROFIT = lambda: _terms("profit_terms", ["profit", "liquidator", "liquidatorreward", "discount"])
REMAINDER = lambda: _terms("remainder_terms", ["remainder", "leftover", "excess", "cap", "surplus", "redistribut"])
FEE = lambda: _terms("fee_terms", ["swapfee", "fee", "fragmentationfee", "feerecipient", "redemptionfee"])
SALE = lambda: _terms("sale_terms", ["sale", "forsale", "exactamountin", "exactamountout", "tenor", "duedate"])
STATE = lambda: _terms("state_transition_terms", ["reducedebt", "createcreditposition", "createdebt", "mint(",
                                                  "burn(", "transferfrom(", "transfer(", ".borrower =",
                                                  "futurevalue =", "reducedebtandcredit", "redistribut",
                                                  "decreasedebt", "increasedebt", "movependingtroverewards"])
# health_factor_after_action only fires on a STRONG liquidation/redemption/recovery/compensate path —
# NOT on a bare repay-that-improves-health (the documented Size/Ethos over-flag).
STRONG_HEALTH_PATH = lambda: _terms("strong_health_path", ["liquidate", "liquidation", "redeem", "redeemcollateral",
                                                           "recoverymode", "compensate", "seize", "selfliquidate"])
EXCLUDE_NAMES = lambda: _terms("exclude_names",
    ["initialize", "updateconfig", "configparams", "setconfig", "riskconfig", "config", "setter"])


def strip_comments(code: str) -> str:
    return _COMMENT_RE.sub(" ", code or "")


def _has(text: str, terms) -> list:
    t = text.lower()
    return [w for w in terms if w in t]


def _has_accounting(body: str) -> bool:
    """True if the body does real arithmetic / calls a math/compute helper. A name-gated fn WITHOUT this is a
    thin delegate wrapper or a bare getter (e.g. `return state.executeLiquidate(p)`) -> suppressed.
    Recognizes both native operators AND Liquity-style SafeMath (`.add()/.sub()/.mul()/.div()/.divPercent()`)."""
    b = strip_comments(body)
    if re.search(r"[A-Za-z0-9_)\]]\s*[+\-*/%]\s*[A-Za-z0-9_(]", b):
        return True
    if re.search(r"\.\s*(?:add|sub|mul|div|divPercent|mulDiv\w*|decMul|decDiv)\s*\(", b):
        return True
    return bool(re.search(r"\b(?:Math|LiquityMath)\s*\.|_compute\w*\(|compute\w+\(", b))


def classify(name: str, signature: str, file: str, contract: str, snippet: str = "", tags=None) -> list:
    """Return a LIST of shape candidates (possibly empty). Pure; snippet is the (helper-resolved) body."""
    nlow = (name or "").lower()
    clow = (contract or "").lower()
    if any(x in nlow for x in EXCLUDE_NAMES()) and not any(
            a in nlow for a in ("liquidate", "compensate", "repay", "replacement", "seize", "redeem")):
        return []                                          # config/init/admin exclusion
    if not any(g in nlow for g in NAME_GATE()):
        return []                                          # NAME-GATE: primary FP control
    body = strip_comments(snippet or "")
    # thin-wrapper / bare-getter suppression (no accounting logic -> only name/return evidence)
    if not _has_accounting(body):
        return []
    blob = (nlow + " " + body).lower()

    coll = _has(blob, COLLATERAL()); debt = _has(blob, DEBT()); cred = _has(blob, CREDIT())
    health = _has(blob, HEALTH()) + [w for w in HEALTH_WORD() if re.search(r"\b" + re.escape(w) + r"\b", blob)]
    profit = _has(blob, PROFIT()); rem = _has(blob, REMAINDER())
    fee = _has(blob, FEE()); sale = _has(blob, SALE()); state = _has(blob, STATE())
    has_c, has_d = bool(coll), bool(debt or cred)
    on_strong_path = any(p in nlow for p in STRONG_HEALTH_PATH())
    sp_ctx = "stabilitypool" in clow or any(t in nlow for t in ("offset", "rewardsum", "rewardsperunit",
                                                                 "redistribut")) or "redistribut" in blob

    def conf(signal_dim_present: bool) -> str:
        if has_c and has_d and signal_dim_present:
            return "high"
        if (has_c or has_d) and signal_dim_present:
            return "medium"
        return "low"

    out = []

    def add(shape, confidence, reason, missing=""):
        out.append({"finding_shape": shape, "confidence": confidence,
                    "evidence_terms": sorted(set(coll + debt + cred + health + profit + rem + fee + sale))[:12],
                    "collateral_terms": coll, "debt_terms": sorted(set(debt + cred)),
                    "health_terms": health, "fee_terms": sorted(set(fee + sale)),
                    "state_transition_terms": state, "reason": reason, "missing_context": missing})

    # 1. collateral_remainder_cap (Size H-03; Ethos redeemCollateral M-09)
    if (rem or "redeem" in nlow) and has_c and (has_d or profit or fee or "borrower" in blob or "liquidator" in blob):
        add("collateral_remainder_cap", conf(True),
            f"{name} computes/transfers a collateral remainder/surplus/redemption amount but its bound vs "
            f"debt-repaid / collateral-seized / fee / entitlement is unclear — verify it is bounded correctly")

    # 4. replacement_swap_fee_accounting (Size M-11) — before generic profit
    if "replacement" in nlow and (fee or sale) and (has_d or "borrower" in blob or "lender" in blob):
        add("replacement_swap_fee_accounting", conf(bool(fee)),
            f"{name} is a replacement flow using {sorted(set(fee+sale))[:3]} — verify the swap/issuance fee is "
            f"charged to the correct side and not omitted")

    # 2. liquidator_profit_bound (Size H-04)
    if profit and (has_c or has_d or cred) and (fee or has_c or "reward" in blob or has_d):
        add("liquidator_profit_bound", conf(True),
            f"{name} derives liquidator {profit} from collateral/debt/credit — verify the reward is computed on "
            f"the CONVERTED collateral-token amount (not the debt-token amount) and is bounded")

    # 6. stability_pool_redistribution (Ethos H-01) — SP offset/reward/redistribution accounting
    if any(t in nlow for t in ("offset", "rewardsum", "rewardsperunit", "redistribut")) and sp_ctx and (has_c or has_d):
        add("stability_pool_redistribution", conf(True) if (has_c and has_d) else "medium",
            f"{name} performs stability-pool offset / reward-per-unit / redistribution accounting on "
            f"collateral/debt — verify per-unit reward/loss math conserves value (no floor-division underflow / "
            f"sign error) across the offset")

    # 5. credit_sale_bypass (Size M-05/M-13)
    if ("compensate" in nlow or sale) and cred and (sale or fee) and (has_d or "borrower" in blob):
        add("credit_sale_bypass", conf(bool(sale or fee)),
            f"{name} runs credit/sale logic ({sorted(set(sale+fee))[:3]}) touching debt/credit — verify forSale / "
            f"fragmentation-fee / tenor constraints cannot be bypassed")

    # 3. health_factor_after_action (Size M-09) — STRONG-PATH gated; delegation inherits CR enforcement.
    delegates_to_liquidation = "executeliquidate" in blob or bool(re.search(r"\.\s*liquidate\s*\(", body))
    if state and (has_c or has_d or cred) and not health and on_strong_path and not delegates_to_liquidation:
        unresolved = bool(re.search(r"\.\s*validate\w*\(|validate\w*\(", body))
        add("health_factor_after_action", "needs_context" if unresolved else conf(True),
            f"{name} (on a liquidation/redemption/recovery/compensate path) mutates debt/collateral/credit "
            f"({state}) with no CR/health check visible — verify solvency is enforced before/after the action",
            missing="CR/health check may be in a separate validate* function" if unresolved else "")

    return out
