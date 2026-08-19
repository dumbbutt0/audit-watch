#!/usr/bin/env python3
"""retag_ton_findings.py — make the TON/FunC corpus reachable to the TON specialist KB queries.

The solodit scraper already ingests FunC/Tact reports (scripts/solodit_scraper.py TARGET_LANGUAGES),
so kb/chroma already holds real TON DEX/jetton findings (STON.fi V2, TONCO CLAMM, Swap Coffee,
PixelSwap, FIVA, ...). But they were all filed under vuln_type="other", and the specialist retriever
applies a hard `vuln_type $eq` filter — so the EVM-category lanes could never reach them.

This one-off, IDEMPOTENT pass re-tags ONLY genuinely-TON documents (two-signal gate: curated TON-protocol
allowlist OR >=2 strong FunC/TON markers in the text) into the TON vuln-type taxonomy
(jetton-theft / sender-spoof / bounce-stranding / message-race / cell-parsing; reuses "arithmetic" for
overflow/precision), stamps chain="ton" + ton_retagged=true, and preserves orig_vuln_type so the change
is reversible. Metadata-only update — embeddings/documents are untouched, and data/evaluation/ is never
read or written (this is reference KB, not ground truth).

Idempotent: re-running recomputes the same deterministic vuln_type and never re-overwrites orig_vuln_type.

Usage:
    python scripts/retag_ton_findings.py --dry-run     # preview; no writes
    python scripts/retag_ton_findings.py               # apply
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import chromadb

ROOT = Path(__file__).resolve().parent.parent
KB_CHROMA = ROOT / "kb" / "chroma"

# Curated allowlist of genuinely-TON protocol names (lowercase substrings). Dotted/spaced forms chosen so
# EVM lookalikes (stakeStone, redStone, mileStone) do NOT match on a bare "ston".
TON_PROTOCOL_MARKERS = (
    "ston.", "stonﬁ", "stonfi", "tonco", "swap coffee", "pixelswap", "fiva", "crouton",
    "torch finance", "bemo", "storm trade", "whales dmcc", "ton studio", "tact compiler",
    "ton amm", "ton dex", "dedust", "megaton",
)
# Strong FunC/TON content markers (>=2 required when the protocol isn't allowlisted).
STRONG_MARKERS = (
    "jetton", "recv_internal", "recv_external", "nanoton", "bounceable", "workchain",
    "begin_cell", "load_msg_addr", "load_coins", ".fc#", ".fc:", "ton amm dex", "toncoin",
    "throw_unless", "op::", "end_parse", "transfer_notification", "func contract",
)
# Title/text -> TON vuln_type. Order = most specific first.
VT_RULES = [
    ("bounce-stranding", ("bounce", "bounced")),
    ("cell-parsing", ("malformed", "multihop cell", "cell can lead", "cell parsing", "slice", "end_parse")),
    ("message-race", ("race condition", "order depend", "order dependence", "overwritten", "concurrent")),
    ("sender-spoof", ("spoof", "owner_address", "arbitrary message", "unauthorized", "initiator",
                      "bypass the pool lock", "bypass", "impersonat")),
    ("jetton-theft", ("steal", "stolen", "theft", "drain", "loss of funds", "jetton loss", "fund loss",
                      "lose funds", "locked fund", "lost deposit", "loss for")),
    ("arithmetic", ("overflow", "underflow", "rounding", "precision", "calculation mismatch", "wrong formula",
                    "incorrect fee", "wrong amount")),
]


def _is_ton(protocol: str, text: str) -> bool:
    p = protocol.lower()
    if any(m in p for m in TON_PROTOCOL_MARKERS):
        return True
    t = text.lower()
    return sum(1 for m in STRONG_MARKERS if m in t) >= 2


def _classify_vt(title: str, text: str) -> str | None:
    # Title is the strongest vuln_type signal — try it alone first so a description keyword can't
    # outrank an explicit title ("...can be stolen" -> jetton-theft, not cell-parsing). Fall back to
    # the full text only when the title names no category.
    for scope in (title.lower(), (title + " " + text).lower()):
        for vt, kws in VT_RULES:
            if any(k in scope for k in kws):
                return vt
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Re-tag the TON/FunC KB corpus into the TON vuln-type taxonomy.")
    ap.add_argument("--dry-run", action="store_true", help="preview classifications; write nothing")
    ap.add_argument("--page", type=int, default=5000)
    args = ap.parse_args()

    if not KB_CHROMA.exists():
        print(f"[retag-ton] no KB at {KB_CHROMA}; run scripts/solodit_scraper.py first", file=sys.stderr)
        return 1
    client = chromadb.PersistentClient(path=str(KB_CHROMA))
    col = client.get_collection("solodit_findings")
    total = col.count()
    print(f"[retag-ton] scanning {total} findings (dry_run={args.dry_run})")

    ton_ids, ton_metas = [], []
    off = 0
    while off < total:
        got = col.get(include=["documents", "metadatas"], limit=args.page, offset=off)
        for _id, doc, meta in zip(got["ids"], got["documents"], got["metadatas"]):
            meta = dict(meta or {})
            protocol = str(meta.get("protocol") or "")
            title = str(meta.get("title") or "")
            text = f"{title} {doc or ''}"
            if not _is_ton(protocol, text):
                continue
            # idempotent metadata edit (preserve original vuln_type once)
            if "orig_vuln_type" not in meta:
                meta["orig_vuln_type"] = str(meta.get("vuln_type") or "other")
            meta["chain"] = "ton"
            meta["ton_retagged"] = True
            new_vt = _classify_vt(title, text)
            if new_vt:
                meta["vuln_type"] = new_vt
            ton_ids.append(_id)
            ton_metas.append(meta)
        off += args.page

    by_proto = Counter(str(m.get("protocol") or "?") for m in ton_metas)
    by_vt = Counter(str(m.get("vuln_type") or "?") for m in ton_metas)
    print(f"[retag-ton] matched {len(ton_ids)} TON findings across {len(by_proto)} protocols")
    print("  by vuln_type:", dict(by_vt.most_common()))
    print("  top protocols:", dict(by_proto.most_common(12)))

    if args.dry_run:
        print("[retag-ton] DRY RUN — no writes. Sample reclassifications:")
        for _id, m in list(zip(ton_ids, ton_metas))[:12]:
            print(f"    {str(m.get('protocol'))[:34]:34} [{m.get('orig_vuln_type'):14}->{m.get('vuln_type'):16}] "
                  f"{str(m.get('title'))[:60]}")
        return 0

    # batch the metadata-only updates
    B = 256
    for i in range(0, len(ton_ids), B):
        col.update(ids=ton_ids[i:i + B], metadatas=ton_metas[i:i + B])
    print(f"[retag-ton] updated {len(ton_ids)} findings (metadata-only; embeddings/documents untouched)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
