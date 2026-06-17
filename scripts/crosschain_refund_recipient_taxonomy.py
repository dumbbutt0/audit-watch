#!/usr/bin/env python3
"""
crosschain_refund_recipient_taxonomy.py — pure (no-I/O) classifier for the CROSS-CHAIN REFUND-RECIPIENT lens.

Generalized CLASS of the P306 decent M-05 + H-03 misses: cross-chain value flows refund to the WRONG recipient.
  (i)  a cross-chain send in an INTERMEDIARY (router/adapter/executor) sets the LZ refundAddress = msg.sender, but
       msg.sender is the intermediary -> refund stranded (decent M-05).
  (ii) an executor-style fn takes a source-chain `from`/`sender` param, makes an external target.call, and on
       FAILURE refunds to that `from` -> a foreign-chain address that may be unusable on this chain (decent H-03).

RESEARCH-ONLY: read-only, is_gate:false, routes_in_production:false — never mints or routes. High precision over
recall. +1-level helper resolution is done by the runner; this module is pure. Anchored on decent
DecentEthRouter._bridgeWithPayload (i) and DecentBridgeExecutor._executeWeth/_executeEth (ii).
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "crosschain_refund_recipient_patterns.json"
_COMMENT_RE = re.compile(r"//[^\n]*|/\*.*?\*/", re.DOTALL)
_REFUND_TO_SENDER_RE = re.compile(r"refund\w*\s*[:=]\s*(payable\s*\(\s*)?msg\.sender")


@lru_cache(maxsize=1)
def _cfg() -> dict:
    try:
        return json.loads(CONFIG.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _t(key: str, default):
    return _cfg().get(key, default)


def strip_comments(code: str) -> str:
    return _COMMENT_RE.sub(" ", code or "")


def _any(text: str, terms) -> list:
    return [w for w in terms if w in text]


def has_send(text: str) -> bool:
    return bool(_any(strip_comments(text or "").lower(), _t("send_primitives", [])))


def _is_intermediary(contract: str, sig: str, body: str) -> bool:
    clow = (contract or "").lower()
    if any(t in clow for t in _t("intermediary_name_terms", [])):
        return True
    s = strip_comments(sig or "").lower()
    return "only" in s          # an onlyX modifier in the declaration -> called by another contract


def _source_role_in_sig(sig: str):
    s = strip_comments(sig or "").lower()
    for role in _t("source_param_roles", []):
        if re.search(r"address\s+(_)?" + re.escape(role) + r"\b", s):
            return role
    return None


def is_view(signature: str) -> bool:
    s = strip_comments(signature or "").lower()
    return " view " in s or " pure " in s or "view returns" in s or "pure returns" in s


def classify(name: str, signature: str, file: str, contract: str, snippet: str = "",
             kind: str = "function", tags=None) -> list:
    body = strip_comments(snippet or "").lower()
    sig = strip_comments(signature or "").lower()
    if is_view(signature):
        return []
    out = []

    # ---- sub-shape (i): cross-chain send + refundAddress=msg.sender in an intermediary ----
    if has_send(body) and _REFUND_TO_SENDER_RE.search(body) and _is_intermediary(contract, sig, body):
        out.append({
            "finding_shape": "crosschain_refund_to_msg_sender",
            "sub_shape": "i_refund_to_intermediary", "confidence": "high",
            "explanation": (f"{name} performs a cross-chain send with the refund address set to msg.sender, but "
                            f"{contract} is an intermediary (router/adapter/executor) — refunded gas/native is "
                            f"stranded at the intermediary instead of reaching the end user (decent M-05 class)."),
            "signals": {"refund_to_msg_sender": True, "intermediary": True},
            "suppression_status": "none",
        })

    # ---- sub-shape (ii): executor failure-refund to a source-chain `from` param ----
    role = _source_role_in_sig(sig)
    has_call = bool(_any(body, _t("external_call_markers", [])))
    has_failure = bool(_any(body, _t("failure_markers", [])))
    if role and has_call and has_failure:
        # a transfer/send back to the source param (payable(from).transfer / weth.transfer(from / transfer(from,)
        refund_to_src = bool(re.search(r"payable\s*\(\s*" + re.escape(role) + r"\s*\)", body) or
                             re.search(r"transfer\s*\(\s*" + re.escape(role) + r"\b", body) or
                             re.search(r"\.\s*transfer\s*\([^;]*\b" + re.escape(role) + r"\b", body) or
                             re.search(re.escape(role) + r"\s*\.\s*(transfer|call|send)\s*\(", body))
        if refund_to_src and "address(this)" not in re.findall(r".{0,40}" + re.escape(role) + r".{0,40}", body).__str__():
            out.append({
                "finding_shape": "crosschain_refund_to_source_param",
                "sub_shape": "ii_failure_refund_to_source", "confidence": "high",
                "explanation": (f"{name} takes a source-chain `{role}` param, makes an external target.call, and on "
                                f"failure refunds to `{role}` — a foreign-chain/source address that may be unusable "
                                f"or attacker-influenced on this chain (decent H-03 class)."),
                "signals": {"source_param": role, "external_call": True, "failure_refund_to_source": True},
                "suppression_status": "none",
            })
    return out
