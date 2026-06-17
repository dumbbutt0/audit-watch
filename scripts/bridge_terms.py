#!/usr/bin/env python3
"""
bridge_terms.py — shared bridge-vocabulary + helpers for the bridge thread-escalation guard.

A deep-analysis thread whose text mentions any of these terms is BRIDGE-RELEVANT and may not be silently
dropped at synthesis: it must be escalated to a finding OR carry a concrete invalidation (exact sink +
attacker entrypoint + one resolution). See documentation/bridge_lifecycle_escalation_policy.md.
"""
from __future__ import annotations

import re

# PRIMARY = genuine bridge / cross-chain coordination + bridge-structural vocabulary. A thread is
# bridge-relevant if it matches any primary term. Round 2 (Silo): the generic vault verbs deposit/withdraw/
# mint/burn/lock/recipient were DEMOTED out of this set — on a non-bridge vault target they tripped the gate
# on every share-mutation thread. They now only escalate when paired with a cross-chain context term (below).
PRIMARY_BRIDGE_TERMS = frozenset({
    "bridge", "crosschain", "cross_chain", "message", "endpoint", "relayer", "domain", "chainid",
    "escrow", "remote", "sourcechain", "destinationchain", "release", "collection", "handler",
    "retry", "replay", "onerc721received", "ownership", "initializer", "proxy", "upgrade",
    "whitelist", "mapping", "custody",
})
# GENERIC vault verbs: present on MANY non-bridge vault/lending targets. Bridge-relevant ONLY when a
# cross-chain context term is also present (see CROSS_CHAIN_CONTEXT) — "deposit on L2 bridge" is bridge,
# a bare "deposit/withdraw" share-mutation thread is not.
GENERIC_VAULT_VERBS = frozenset({"deposit", "withdraw", "mint", "burn", "lock", "recipient", "transfer"})
# SECONDARY = L2 / oracle / sequencer terms that appear on MANY non-bridge targets (Revert Lend T-004 was
# blocked on a pure 'l2' match). These count as bridge-relevant ONLY when a primary term is also present;
# pure L2/oracle/sequencer risk is left to the oracle specialist / checkpoint_liveness lens (untouched here).
SECONDARY_L2_ORACLE_TERMS = frozenset({"l1", "l2", "oracle", "sequencer", "twap"})

# The pairing context for a generic vault verb: any primary coordination term, or an L1/L2 bridge-context
# token. (oracle/sequencer/twap are NOT bridge context — they're left to the oracle specialist.)
CROSS_CHAIN_CONTEXT = PRIMARY_BRIDGE_TERMS | {"l1", "l2"}

# Back-compat alias.
BRIDGE_TERMS = PRIMARY_BRIDGE_TERMS | GENERIC_VAULT_VERBS | SECONDARY_L2_ORACLE_TERMS

# Word-boundary regex so "l1"/"l2" don't match inside unrelated identifiers, but multi-word/snake terms
# still match. (We intentionally keep these as whole-word matches to avoid noise.)
_WORD_RE = re.compile(r"[a-z0-9]+")

# Vague labels that are NOT a concrete invalidation on their own.
_VAGUE = re.compile(
    r"\b(low\s*confidence|already\s*covered|needs?\s*more\s*evidence|"
    r"minor|low\s*sev|low\s*severity|n/?a|not\s*applicable|none|unclear|"
    r"maybe|might|could|possibly|speculative|tbd|todo|review\s*later)\b",
    re.IGNORECASE,
)


def thread_text(thread: dict) -> str:
    parts = [thread.get("title", ""), thread.get("entry_conditions", ""),
             thread.get("attacker_class", ""), thread.get("impact_estimate", ""),
             thread.get("evidence", "")]
    vp = thread.get("violation_path") or []
    if isinstance(vp, list):
        parts += [str(x) for x in vp]
    else:
        parts.append(str(vp))
    return " ".join(parts)


def matched_bridge_terms(text: str) -> list[str]:
    """Primary bridge/coordination terms in the text (used for the gate message)."""
    toks = set(_WORD_RE.findall((text or "").lower()))
    return sorted(t for t in PRIMARY_BRIDGE_TERMS if t in toks)


def matched_secondary_terms(text: str) -> list[str]:
    toks = set(_WORD_RE.findall((text or "").lower()))
    return sorted(t for t in SECONDARY_L2_ORACLE_TERMS if t in toks)


def matched_generic_vault_verbs(text: str) -> list[str]:
    toks = set(_WORD_RE.findall((text or "").lower()))
    return sorted(t for t in GENERIC_VAULT_VERBS if t in toks)


def is_bridge_thread(thread: dict) -> bool:
    """Bridge-relevant iff a PRIMARY coordination/structural term is present, OR a generic vault verb
    (deposit/withdraw/mint/burn/lock/recipient/transfer) is paired with a cross-chain context term
    (any primary term, or L1/L2). A secondary L2/oracle/sequencer term alone — and now a bare generic
    vault verb alone — is NOT bridge-relevant: that suppresses the Revert Lend pure-'l2' false block and
    the Silo non-bridge vault-verb false trigger, leaving oracle/sequencer + share-accounting risk to the
    oracle specialist / vault lenses."""
    text = thread_text(thread)
    if matched_bridge_terms(text):
        return True
    toks = set(_WORD_RE.findall((text or "").lower()))
    if (GENERIC_VAULT_VERBS & toks) and (CROSS_CHAIN_CONTEXT & toks):
        return True
    return False


def is_vague(text: str) -> bool:
    t = (text or "").strip()
    return (not t) or bool(_VAGUE.search(t))
