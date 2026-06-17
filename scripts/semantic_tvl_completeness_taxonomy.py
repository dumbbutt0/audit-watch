#!/usr/bin/env python3
"""
semantic_tvl_completeness_taxonomy.py — pure (no-I/O) classifier for the SEMANTIC TVL-COMPLETENESS research
prototype. Models, per connector, two sets:

  D = external value DESTINATIONS its entrypoints write (gauge.deposit / positionManager.mint / market.deposit
      / borrow / ...), and
  R = the SOURCES its TVL reader(s) read (token/gauge/staking balanceOf, positionManager.positions(tokenId)
      vs pool.positions(tickKey), getReserves, oracle.getValue, ...).

A candidate is `D minus R`: value written to an external destination that the TVL reader does not read (or read
via an equivalent source). This is a RESEARCH heuristic — "absence" cannot be proven by reading one function,
so confidence is conservatively demoted (needs_context) under indirection. NOT a production lens; the audit
that uses this is read-only, is_gate:false, never routes.

Seed cases (NOYA): H-06 Aerodrome (stake→IGauge.deposit; TVL reads only IERC20(pool).balanceOf →
omitted_external_stake_balance); H-20 UNIv3 (mint via positionManager tokenId; TVL reads pool.positions(tick
key) not positionManager.positions(tokenId) → position_manager_ownership_assumption).
"""
from __future__ import annotations

import re

ROUTED_CONFIDENCE = frozenset({"high", "medium"})   # research-only; not consumed by any gate

# --- TVL reader function names (position-VALUE readers only; NOT getUnderlyingTokens token-list getters,
# NOT the generic getValue oracle helper — both caused base-class / duplicate noise) ---
TVL_FN_NAMES = ("_getpositiontvl", "getpositiontvl", "gettvl", "_gettvl", "totalassets", "positiontvl",
                "calculatetvl")

# --- value-moving destination verbs (principal), and the verbs/terms we must NOT treat as destinations ---
DEST_VERBS = ("deposit", "stake", "mint", "increaseliquidity", "addliquidity", "supply", "borrow",
              "repay", "lend", "redeem", "openborrowposition", "depositintomarket", "transfertomarket",
              "depositweiintodefaultaccount", "increasePosition".lower())
CLAIM_VERBS = ("getreward", "claimreward", "claimrewards", "collect", "harvest", "claim")
APPROVE_VERBS = ("approve", "forceapprove", "safeapprove", "increaseallowance")
ROUTER_HINTS = ("swap", "router", "lifi", "bridge")
RECIPIENT_TOKENS = ("msg.sender", "recipient", "to,", "to )", "_to", "user", "owner")

_COMMENT_RE = re.compile(r"//[^\n]*|/\*.*?\*/", re.DOTALL)
# <receiver>.<verb>(  — receiver is an identifier or a cast like IGauge(gauge) / positionManager
_CALL_RE = re.compile(r"([A-Za-z_]\w*(?:\s*\([^;{}]*\))?)\s*\.\s*([A-Za-z_]\w*)\s*\(")


def strip_comments(code: str) -> str:
    return _COMMENT_RE.sub(" ", code or "")


def _base(receiver: str) -> str:
    """Innermost receiver identifier: strip an interface cast `IGauge(gauge)`->`gauge`, take the last dotted
    segment (`poolInfo.gauge`->`gauge`), lowercased. Used to check whether the TVL reads the SAME external
    contract the entrypoint wrote to (receiver-base equivalence — the key precision control)."""
    r = (receiver or "").strip()
    m = re.match(r"^I?[A-Za-z]\w*\(\s*(.*?)\s*\)$", r)
    if m:
        r = m.group(1)
    r = r.split(",")[0].strip().split(".")[-1].strip()
    return r.lower()


def is_tvl_fn(name: str) -> bool:
    return any(t in (name or "").lower() for t in TVL_FN_NAMES)


def _dest_kind(receiver: str, verb: str) -> str:
    r = receiver.lower()
    if "gauge" in r:
        return "gauge"
    if "stak" in r:
        return "staking"
    if "positionmanager" in r or "nonfungible" in r or "nfpm" in r:
        return "position_manager"
    if "borrow" in r or "borrow" in verb or verb in ("borrow", "openborrowposition", "repay"):
        return "lending"
    if "market" in r or "morpho" in r or "silo" in r or "depositwithdrawal" in r or "comet" in r:
        return "market"
    if verb in ("mint", "increaseliquidity", "addliquidity") and ("pool" in r or "pair" in r):
        return "pool_lp"
    if verb in ("stake", "deposit") :
        return "staking"
    return "external"


def parse_destinations(body: str) -> list[dict]:
    """External value-moving calls in an entrypoint body. Skips approve-only, claim/reward, router, and
    recipient-controlled transfers."""
    b = strip_comments(body)
    out = []
    for m in _CALL_RE.finditer(b):
        receiver, verb = m.group(1).strip(), m.group(2).lower()
        if verb in APPROVE_VERBS or verb in CLAIM_VERBS:
            continue
        if verb not in DEST_VERBS:
            continue
        rl = receiver.lower()
        if any(h in rl for h in ROUTER_HINTS):
            continue                                  # transient router, not a persistent value holder
        if "iconnector(" in rl or rl == "connector":
            continue                                  # connector-to-connector transfer, not an external protocol
        # recipient-controlled transfer (value to a user/recipient, not a connector-owned external position)
        call_args = b[m.end(): m.end() + 120].lower()
        recipient_controlled = (verb in ("transfer", "safetransfer") and
                                any(tok in call_args for tok in RECIPIENT_TOKENS))
        out.append({"verb": verb, "receiver": receiver, "base": _base(receiver),
                    "kind": _dest_kind(receiver, verb),
                    "recipient_controlled": recipient_controlled, "call": f"{receiver}.{m.group(2)}(...)"})
    return [d for d in out if not d["recipient_controlled"]]


def parse_tvl_reads(body: str) -> list[dict]:
    """Sources read inside a TVL function (+ resolved helpers). Records the receiver kind."""
    b = strip_comments(body)
    out = []
    for m in _CALL_RE.finditer(b):
        receiver, fn = m.group(1).strip(), m.group(2).lower()
        rl = receiver.lower()
        if fn == "balanceof":
            if "gauge" in rl:
                kind = "gauge"
            elif "stak" in rl:
                kind = "staking"
            elif "market" in rl or "morpho" in rl or "silo" in rl:
                kind = "market"
            else:
                kind = "local_token"
            out.append({"read": "balanceOf", "receiver": receiver, "base": _base(receiver), "kind": kind})
        elif fn == "positions":
            kind = "position_manager_tokenId" if ("positionmanager" in rl or "nonfungible" in rl) else "pool_tick"
            out.append({"read": "positions", "receiver": receiver, "base": _base(receiver), "kind": kind})
        elif fn in ("getreserves", "slot0"):
            out.append({"read": fn, "receiver": receiver, "base": _base(receiver), "kind": "pool_reserves"})
        elif fn in ("getaccountwei", "getaccountcollateral", "getaccountpar", "getaccount", "borrowbalance",
                    "debtbalance", "balanceofunderlying", "getuserposition"):
            out.append({"read": fn, "receiver": receiver, "base": _base(receiver), "kind": "market"})
    return out


def is_claim_only(body: str) -> bool:
    b = strip_comments(body)
    has_claim = any(re.search(r"\.\s*" + v + r"\s*\(", b, re.I) for v in CLAIM_VERBS)
    has_dest = bool(parse_destinations(b))
    return has_claim and not has_dest


def classify_group(contract: str, dest_list: list[dict], read_list: list[dict],
                   tvl_fn: str, indirection: bool = False) -> list[dict]:
    """Given a connector's destinations (from entrypoints) and TVL reads, emit D\\R candidates.
    `indirection` (registry/proxy/base-helper destination) demotes confidence to needs_context."""
    read_kinds = {r["kind"] for r in read_list}
    read_bases = {r["base"] for r in read_list}
    # RECEIVER-BASE EQUIVALENCE: a destination whose external receiver the TVL also reads is COVERED
    # (e.g. SNXCoreProxy.deposit covered by SNXCoreProxy.getAccountCollateral; gauge.deposit by gauge.balanceOf).
    uncovered = [d for d in dest_list if d["base"] not in read_bases]
    dest_kinds = {d["kind"] for d in uncovered}
    cands = []

    def _mk(shape, dest, missing, conf, reason):
        return {"connector_contract": contract, "finding_shape": shape,
                "value_destination": dest["kind"], "destination_call": dest["call"],
                "tvl_function": tvl_fn, "tvl_sources_seen": sorted(read_kinds),
                "missing_tvl_source": missing, "confidence": ("needs_context" if indirection else conf),
                "reason": reason}

    # 1. gauge / staking destination whose receiver the TVL never reads
    for d in uncovered:
        if d["kind"] in ("gauge", "staking"):
            cands.append(_mk("omitted_external_stake_balance", d, f"{d['base']}.balanceOf(this)", "high",
                             f"{contract}.{tvl_fn} reads {sorted(read_kinds)} but {d['call']} stakes value into "
                             f"a {d['kind']} (`{d['base']}`) the TVL never reads"))
            break

    # 2. positionManager mint but TVL reads pool/tick liquidity, not positionManager.positions(tokenId)
    if "position_manager" in dest_kinds and "position_manager_tokenId" not in read_kinds \
            and read_kinds & {"pool_tick", "pool_reserves"}:
        d = next(x for x in uncovered if x["kind"] == "position_manager")
        cands.append(_mk("position_manager_ownership_assumption", d, "positionManager.positions(tokenId)",
                         "medium",
                         f"{contract}.{tvl_fn} reads pool/tick liquidity, not positionManager.positions(tokenId) — "
                         f"assumes the connector owns all liquidity in the tick range ({d['call']})"))

    # 4. borrow/lend destination unread on the market side
    if "lending" in dest_kinds and not (read_kinds & {"market"}):
        d = next(x for x in uncovered if x["kind"] == "lending")
        cands.append(_mk("collateral_debt_side_omission", d, "debt/collateral account reader", "medium",
                         f"{contract}.{tvl_fn} reads {sorted(read_kinds)} but {d['call']} opens a borrow/lend "
                         f"position; verify both collateral and debt sides are valued"))

    # 5. only local token balance read, but an external market/pool destination exists (catch-all, lower prio)
    if not cands and (dest_kinds & {"market", "external", "pool_lp"}) and read_kinds <= {"local_token", "pool_reserves"}:
        d = next(x for x in uncovered if x["kind"] in ("market", "external", "pool_lp"))
        cands.append(_mk("local_balance_only_tvl", d, f"{d['kind']} position reader", "medium",
                         f"{contract}.{tvl_fn} reads only local balances {sorted(read_kinds)} but {d['call']} "
                         f"moves value into an external {d['kind']}"))
    return cands


def classify_left_behind(contract: str, has_decrease_remove: bool, dest_list: list[dict],
                         read_list: list[dict], tvl_fn: str) -> list[dict]:
    """external_position_left_behind: a decrease/remove entrypoint exists while a stake destination is neither
    unwound nor read by TVL."""
    read_bases = {r["base"] for r in read_list}
    read_kinds = {r["kind"] for r in read_list}
    if not has_decrease_remove:
        return []
    for d in dest_list:
        if d["kind"] in ("gauge", "staking") and d["base"] not in read_bases:
            return [{"connector_contract": contract, "finding_shape": "external_position_left_behind",
                     "value_destination": d["kind"], "destination_call": d["call"], "tvl_function": tvl_fn,
                     "tvl_sources_seen": sorted(read_kinds), "missing_tvl_source": f"{d['kind']} unwind/read",
                     "confidence": "needs_context",
                     "reason": (f"{contract} has a decrease/remove entrypoint and a {d['kind']} stake "
                                f"destination the TVL never reads — external position may remain after local "
                                f"state is removed")}]
    return []
