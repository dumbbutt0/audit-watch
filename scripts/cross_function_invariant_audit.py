#!/usr/bin/env python3
"""
cross_function_invariant_audit.py — recall lens for CROSS-FUNCTION / BOUNDARY invariant mismatches.
Unlike per-item lenses, it PAIRS functions within a contract (and, for batch counters, across the manifest)
to flag candidate writer/reader invariant gaps that a local clear cannot rule out, and routes them to
needs_deep_pass. NOT a gate; never mutates dispositions; never finding-mints. Two-signal, FP-tight.

Recovers the Recall miss classes: H-03 (toHash store-key vs toTracingId read-key), H-04 (batch count
exceeds the limit checked elsewhere), H-06 (cross-function reentrancy: a nonReentrant external-call fn whose
post-call state a sibling non-guarded fn consumes), H-07 (queue compaction skips entries).

Writes output/cross_function_invariant_audit.{json,md}.
Usage: python scripts/cross_function_invariant_audit.py [--manifest <path>] [--no-source]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import cross_function_invariant_taxonomy as cfi  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
_FILE_CACHE: dict[str, list[str]] = {}

_WRITER_RE = re.compile(r"(store|commit|add|push|set|record|deposit|register|create|enqueue|append|put|save)", re.I)
_READER_RE = re.compile(r"(get|read|lookup|exec|process|verify|apply|claim|consume|propagate|find|resolve)", re.I)
_COMPACT_RE = re.compile(r"(compact|prune|clean|gc|sweep|drop|remove)", re.I)
_BATCH_RE = re.compile(r"(batch|msg|message|nonce|checkpoint|count)", re.I)


def _snippet(file_rel, start, end, use_source):
    if not use_source or not file_rel or not start:
        return ""
    if file_rel not in _FILE_CACHE:
        try:
            _FILE_CACHE[file_rel] = (ROOT / file_rel).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            _FILE_CACHE[file_rel] = []
    lines = _FILE_CACHE[file_rel]
    return "\n".join(lines[max(0, (start or 1) - 1):min(len(lines), end or start or 1)])[:4000] if lines else ""


def _load(path: Path, key: str):
    if not path.exists():
        return [] if key else {}
    try:
        d = json.loads(path.read_text())
        return d.get(key, []) if key else d
    except (OSError, json.JSONDecodeError):
        return [] if key else {}


def _cov(disp, mid):
    st = disp.get(mid, {}).get("status")
    return ("covered_by_finding" if st == "finding" else "examined_but_cleared" if st == "cleared"
            else "deferred" if st == "deferred_out_of_scope" else "uncovered")


def _hit(family, writer, reader, written, consumed, invariant, mismatch, entry, sink, why, primary_id,
         secondary_id=None, severity="High"):
    return {
        "family": family, "writer_function": writer, "reader_function": reader,
        "written_state": written, "consumed_state": consumed,
        "expected_invariant": invariant, "observed_mismatch": mismatch,
        "attacker_entrypoint": entry, "downstream_sink": sink,
        "why_local_clear_is_insufficient": why,
        "required_deep_pass": True, "severity_ceiling_hint": severity,
        "manifest_id": primary_id, "secondary_manifest_id": secondary_id, "high_risk": True,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest")
    ap.add_argument("--no-source", action="store_true")
    args = ap.parse_args()

    man_path = Path(args.manifest) if args.manifest else audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    if not items:
        raise SystemExit(f"[cross_function_invariant_audit] no manifest items at {man_path}")
    tax = cfi.load_taxonomy()
    disp = {d["manifest_id"]: d for d in _load(audit_path("output") / "coverage_dispositions.json", "dispositions")}
    use_source = not args.no_source

    by_contract: dict[str, list[dict]] = defaultdict(list)
    for it in items:
        if it.get("kind") not in ("function", "constructor", "initializer"):
            continue
        if not it.get("in_scope", True):
            continue
        span = it.get("source_span", {})
        snip = _snippet(it.get("file", ""), span.get("start_line"), span.get("end_line"), use_source)
        cls = cfi.classify(it.get("name", ""), it.get("signature", ""), it.get("file", ""),
                           it.get("contract", ""), snippet=snip, tags=it.get("tags"))
        cls["id"] = it["id"]
        cls["line"] = span.get("start_line")
        by_contract[it.get("contract") or "?"].append(cls)

    hits: list[dict] = []

    # ---- Family 1: store-key vs read-key divergence (H-03) ----
    # Two distinct key-deriving calls used by different functions in the same contract that share state.
    for contract, fns in by_contract.items():
        keyed = [f for f in fns if f["key_calls"] and f["has_shared_state"]]
        union = set().union(*[set(f["key_calls"]) for f in keyed]) if keyed else set()
        if len(union) >= 2:
            # find a pair using *different* key derivations
            for i, a in enumerate(keyed):
                for b in keyed[i + 1:]:
                    if set(a["key_calls"]) != set(b["key_calls"]) and (set(a["key_calls"]) - set(b["key_calls"])):
                        writer, reader = (a, b) if _WRITER_RE.search(a["name"] or "") else (b, a)
                        hits.append(_hit(
                            "store_key_vs_read_key_divergence", f"{contract}.{writer['name']}",
                            f"{contract}.{reader['name']}",
                            f"key via {','.join(writer['key_calls'])}", f"key via {','.join(reader['key_calls'])}",
                            "the key used to STORE an entry must equal the key used to READ/verify it",
                            f"writer derives a key with {writer['key_calls']} but reader uses {reader['key_calls']} — a stored entry may never be found",
                            f"{contract}.{writer['name']} (whoever can trigger a store)",
                            f"{contract}.{reader['name']} lookup/verify",
                            "a per-function clear of either side looks correct in isolation; the bug only exists in the DISAGREEMENT between the two key derivations",
                            writer["id"], reader["id"]))
                        break

    # ---- Family 2: counter / limit divergence (H-04) ----
    # A function increments a batch/msg counter with NO local limit check, while a limit check exists
    # somewhere in the manifest.
    limit_fns = [(c, f) for c, fns in by_contract.items() for f in fns if f["has_limit_check"] and _BATCH_RE.search(f["name"] or "")]
    limit_fns += [(c, f) for c, fns in by_contract.items() for f in fns if f["has_limit_check"]]
    for contract, fns in by_contract.items():
        for f in fns:
            if f["has_counter_increment"] and not f["has_limit_check"] and _BATCH_RE.search((f["name"] or "") + (f["contract"] or "")):
                # only flag if a limit check for batches exists elsewhere (the bound is enforced in a different fn)
                reader = next((rf for rc, rf in limit_fns if rf["id"] != f["id"]), None)
                if reader:
                    hits.append(_hit(
                        "counter_limit_divergence", f"{contract}.{f['name']}",
                        f"{reader['contract']}.{reader['name']}",
                        "batch/message counter incremented", "limit checked separately",
                        "the counter incremented by the writer must be bounded by the same limit the reader enforces",
                        f"{contract}.{f['name']} appends/increments without a local limit check; the limit is enforced only in {reader['contract']}.{reader['name']} — the writer can drive the count past the limit or out of sync",
                        f"{contract}.{f['name']}", f"{reader['contract']}.{reader['name']} (limit enforcement)",
                        "clearing the writer locally ('it just increments a counter') misses that the increment is unbounded relative to the limit enforced in another function",
                        f["id"], reader["id"]))

    # ---- Family 3: cross-function reentrancy (H-06) ----
    # A nonReentrant fn that makes an external/native call, with a sibling state-mutating fn that is NOT
    # guarded — the per-function guard does not cover re-entry through the sibling.
    for contract, fns in by_contract.items():
        guarded_ext = [f for f in fns if f["has_reentrancy_guard"] and f["has_external_call"]]
        unguarded_mut = [f for f in fns if not f["has_reentrancy_guard"] and (f["has_counter_increment"] or f["has_queue_op"] or f["has_shared_state"])]
        for g in guarded_ext:
            sibling = next((u for u in unguarded_mut if u["id"] != g["id"]), None)
            if sibling:
                hits.append(_hit(
                    "cross_function_reentrancy", f"{contract}.{g['name']}",
                    f"{contract}.{sibling['name']}",
                    "shared state touched around an external/native call", "same shared state mutated by an unguarded sibling",
                    "if an external call can re-enter, every function that mutates the shared state must be covered by the SAME guard",
                    f"{contract}.{g['name']} is nonReentrant and makes an external call, but {contract}.{sibling['name']} mutates shared state WITHOUT the guard — re-entry through the sibling is not prevented",
                    f"{contract}.{g['name']} (native/external transfer recipient)",
                    f"{contract}.{sibling['name']} (unguarded state mutation)",
                    "a clear citing 'nonReentrant' is insufficient: nonReentrant only locks re-entry into the SAME function, not cross-function re-entry through {0}".format(sibling['name']),
                    g["id"], sibling["id"]))

    # ---- Family 4: queue compaction / drop skip (H-07) ----
    for contract, fns in by_contract.items():
        for f in fns:
            if f["has_queue_op"] and _COMPACT_RE.search(f["name"] or ""):
                hits.append(_hit(
                    "queue_key_length_bound_divergence", f"{contract}.{f['name']}",
                    f"{contract}.{f['name']} (loop index vs pending count)",
                    "queue entries appended", "compaction/drop iterates entries",
                    "compaction must iterate exactly the live entries; loop index must be relative to the pending range, not an absolute index",
                    f"{contract}.{f['name']} compacts/prunes a queue — an index-vs-count mismatch can skip pending entries (matured releases never paid / never dropped)",
                    f"{contract}.{f['name']}", "pending release / queue consumers",
                    "a local clear of a compaction loop is insufficient without proving the index base matches the pending-count base; off-by-one skips are invisible without that cross-check",
                    f["id"], None, severity="High"))

    # dedup by (family, manifest_id, secondary)
    seen = set(); deduped = []
    for h in hits:
        k = (h["family"], h["manifest_id"], h["secondary_manifest_id"])
        if k in seen:
            continue
        seen.add(k); deduped.append(h)
    hits = deduped

    for h in hits:
        h["coverage"] = _cov(disp, h["manifest_id"])

    high_risk_ids = sorted({h["manifest_id"] for h in hits if h["high_risk"]}
                           | {h["secondary_manifest_id"] for h in hits if h["high_risk"] and h["secondary_manifest_id"]})
    by_fam = Counter(h["family"] for h in hits)
    ts = datetime.now(timezone.utc).isoformat()
    report = {
        "lens": "cross_function_invariant", "generated_at": ts, "manifest": str(man_path), "is_gate": False,
        "source_snippets": use_source, "total_candidate_pairs": len(hits),
        "by_family": dict(by_fam.most_common()),
        "high_risk_manifest_ids": high_risk_ids, "detected": hits,
    }
    out = audit_path("output") / "cross_function_invariant_audit.json"
    out.write_text(json.dumps(report, indent=2))

    md = [f"# Cross-function / boundary invariant audit\n",
          f"_Generated {ts} · manifest `{man_path}` · NOT a gate · candidate writer/reader pairs → needs_deep_pass_\n",
          f"**{len(hits)}** candidate cross-function invariant pairs · **{len(high_risk_ids)}** high-risk manifest items\n",
          "## By family", "| family | n |", "|---|---|"] + [f"| {c} | {n} |" for c, n in by_fam.most_common()]
    md += ["\n## Candidate pairs\n", "| family | writer → reader | observed mismatch | coverage |", "|---|---|---|---|"]
    for h in hits:
        md.append(f"| {h['family']} | {h['writer_function']} → {h['reader_function']} | {h['observed_mismatch'][:90]} | {h['coverage']} |")
    (audit_path("output") / "cross_function_invariant_audit.md").write_text("\n".join(md) + "\n")

    print(f"[ok] cross_function_invariant_audit → {out}")
    print(f"     candidate pairs {len(hits)} · high-risk items {len(high_risk_ids)} · by_family {dict(by_fam.most_common())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
