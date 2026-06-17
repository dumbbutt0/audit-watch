#!/usr/bin/env python3
"""Phase 2 corpus miner (research-only, throwaway). Discovers candidate sibling-function pairs across
the swept manifests so we build the rule set from a real corpus. NOT a detector, NOT wired.

For each contract: pair functions that are siblings (name-stem kinship OR shared-call overlap), record
their shared internal calls / state-write targets / events and a coarse asymmetry flag. Emits a markdown
table to stdout (captured into sibling_function_candidates.md)."""
import json, re, os, sys
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher

ROOT = Path(__file__).resolve().parent.parent.parent
SUBJECTS = [
    "panoptic-2025-12-strict-eval", "revert-lend-2024-03-strict-eval", "silo-finance-2025-03-strict-eval",
    "hybra-finance-2025-10-strict-eval", "swan-dria-2024-10-strict-eval", "ark-project-2024-07-strict-eval",
    "recall-2025-02-strict-eval", "zaros-2025-01-part-2-eval", "quantamm-2024-12-strict-eval",
    "beanstalk-2024-05-eval2", "size-credit-2024-06", "noya-2024-04-eval", "blackhole-2025-05-eval",
    "ethos-reserve-2023-02-liquidation-health", "maia-talos-2023-05-semantic-tvl", "tokemak-2023-06-semantic-tvl",
]
VARIANT_AFFIX = ["_many", "many", "batch", "_batch", "for", "to", "all", "multiple", "internal", "single", "s"]
_FC = {}
_COMMENT = re.compile(r"//[^\n]*|/\*.*?\*/", re.DOTALL)
_CALL = re.compile(r"(?<![.\w])([A-Za-z_]\w*)\s*\(")
_DOTCALL = re.compile(r"\.([A-Za-z_]\w*)\s*\(")
_REQUIRE = re.compile(r"\brequire\s*\(|\brevert\b|\bif\s*\([^)]*\)\s*(revert|return|break)")
_WRITE = re.compile(r"([A-Za-z_]\w*(?:\[[^\]]*\])?(?:\.[A-Za-z_]\w*)?)\s*(?:\+=|-=|=)(?![=])")
_EMIT = re.compile(r"\bemit\s+([A-Za-z_]\w*)")
KEYWORDS = {"if", "for", "while", "return", "require", "revert", "assert", "emit", "memory", "storage",
            "uint", "uint256", "address", "bool", "new", "else", "break", "continue", "function"}


def body(file_rel, start, end):
    if not file_rel or not start:
        return ""
    if file_rel not in _FC:
        try:
            _FC[file_rel] = (ROOT / file_rel).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            _FC[file_rel] = []
    lines = _FC[file_rel]
    if not lines:
        return ""
    i = max(0, start - 1)
    e = min(len(lines), (end or start) + 1)
    return _COMMENT.sub(" ", "\n".join(lines[i:e]))[:8000]


def feats(b):
    calls = {c for c in _CALL.findall(b) if c not in KEYWORDS}
    calls |= set(_DOTCALL.findall(b))
    writes = {w for w in _WRITE.findall(b) if w not in KEYWORDS and not w.isdigit()}
    return {"calls": calls, "writes": writes, "emits": set(_EMIT.findall(b)),
            "requires": len(_REQUIRE.findall(b))}


def stem(n):
    s = n.lower().lstrip("_")
    for a in sorted(VARIANT_AFFIX, key=len, reverse=True):
        if s.endswith(a) and len(s) > len(a) + 2:
            return s[: -len(a)]
    return s


def main():
    rows, total_pairs = [], 0
    for subj in SUBJECTS:
        mp = ROOT / "audits" / subj / "output" / "coverage_manifest.json"
        if not mp.exists():
            continue
        items = json.loads(mp.read_text()).get("items", [])
        by_c = defaultdict(list)
        for it in items:
            if it.get("kind") != "function" or it.get("mutability") in ("view", "pure"):
                continue
            if not it.get("in_scope", True):
                continue
            by_c[it.get("contract", "")].append(it)
        for c, fns in by_c.items():
            for it in fns:
                sp = it.get("source_span", {})
                it["_f"] = feats(body(it.get("file", ""), sp.get("start_line"), sp.get("end_line")))
            for i in range(len(fns)):
                for j in range(i + 1, len(fns)):
                    a, b = fns[i], fns[j]
                    na, nb = a.get("name", ""), b.get("name", "")
                    fa, fb = a["_f"], b["_f"]
                    shared = fa["calls"] & fb["calls"]
                    if not shared and not (fa["writes"] & fb["writes"]):
                        continue
                    name_kin = stem(na) == stem(nb) and na != nb
                    jacc = len(shared) / max(1, len(fa["calls"] | fb["calls"]))
                    if not name_kin and (len(shared) < 2 or jacc < 0.3):
                        continue
                    only_a = (fa["calls"] - fb["calls"]) - {na, nb}
                    only_b = (fb["calls"] - fa["calls"]) - {na, nb}
                    asym = bool(only_a ^ only_b) or fa["requires"] != fb["requires"] \
                        or a.get("modifiers") != b.get("modifiers")
                    total_pairs += 1
                    rows.append({
                        "subject": subj, "contract": c, "A": na, "B": nb,
                        "name_kin": name_kin, "shared": len(shared), "jaccard": round(jacc, 2),
                        "only_A": sorted(only_a)[:6], "only_B": sorted(only_b)[:6],
                        "req_diff": fa["requires"] - fb["requires"],
                        "mod_diff": a.get("modifiers") != b.get("modifiers"), "asym": asym,
                    })
    # rank: asymmetric, name-kin, more shared
    rows.sort(key=lambda r: (r["asym"], r["name_kin"], r["shared"]), reverse=True)
    print(f"# Sibling-Function Candidates — Phase 2 corpus mining\n")
    print(f"Discovered **{total_pairs}** sibling candidate pairs across 16 subjects "
          f"(in-scope, non-view, name-stem OR shared-call kinship). Top asymmetric candidates below; "
          f"full machine list in `sibling_candidates.json`.\n")
    print("| Subject | Contract | A | B | kin | shared | jacc | only in A | only in B | req∆ | mod∆ |")
    print("|---|---|---|---|:--:|:--:|:--:|---|---|:--:|:--:|")
    for r in [r for r in rows if r["asym"]][:60]:
        print(f"| {r['subject'].split('-202')[0]} | {r['contract']} | {r['A']} | {r['B']} | "
              f"{'Y' if r['name_kin'] else '-'} | {r['shared']} | {r['jaccard']} | "
              f"{','.join(r['only_A']) or '—'} | {','.join(r['only_B']) or '—'} | {r['req_diff']} | "
              f"{'Y' if r['mod_diff'] else '-'} |")
    json.dump(rows, open(Path(__file__).parent / "sibling_candidates.json", "w"), indent=1)
    # summary
    asym = [r for r in rows if r["asym"]]
    kin = [r for r in asym if r["name_kin"]]
    print(f"\n## Summary\n- total candidate pairs: **{total_pairs}**")
    print(f"- asymmetric (a parity gap signal present): **{len(asym)}**")
    print(f"- name-stem siblings among asymmetric: **{len(kin)}** (the high-confidence tier)")
    bys = defaultdict(int)
    for r in kin:
        bys[r["subject"].split("-202")[0]] += 1
    print(f"- name-stem asymmetric by subject: " + ", ".join(f"{k}={v}" for k, v in sorted(bys.items(), key=lambda x: -x[1])))


if __name__ == "__main__":
    main()
