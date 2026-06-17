#!/usr/bin/env python3
"""
liquidation_health_accounting_audit.py — LIQUIDATION / HEALTH-ACCOUNTING advisory detector
(is_gate:false). Seeded by the Size Credit eval (H-03/H-04/M-09/M-11), Ethos-informed for Liquity CDPs.

Function-scoped: for each manifest function whose NAME is name-gated (liquidate/compensate/replacement/
repay/CR-health/redeem/offset), it brace-matches the body (+ one level of same-contract helper resolution so
a CR check in a called helper is credited), runs liquidation_health_accounting_taxonomy.classify(), and emits
candidates. Writes output/liquidation_health_accounting_audit.json.

Routing is ADVISORY and HIGH-ONLY: `routed_manifest_ids` carries high-confidence, in-scope candidates only;
internal helpers that a high entrypoint calls are attached as `context_helpers` rather than routed separately
(volume control). The advisory_escalation_gate consumes routed_manifest_ids ONLY in strict full-audit mode and
routes them to a deep pass (`liquidation_health_accounting_review`). This detector NEVER mints findings and
NEVER blocks a gate.

Usage: python scripts/liquidation_health_accounting_audit.py [--manifest <path>] [--no-source] [--quiet]
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
import liquidation_health_accounting_taxonomy as lha  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
_FILE_CACHE: dict[str, list[str]] = {}
_BODY_MAX_LINES = 400
_LOCAL_CALL_RE = re.compile(r"(?<![.\w])([A-Za-z_]\w*)\s*\(")


def _load(path: Path, key: str) -> list:
    try:
        d = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return []
    return d.get(key, []) if isinstance(d, dict) else d


def _function_body(file_rel, start, use_source) -> str:
    if not use_source or not file_rel or not start:
        return ""
    if file_rel not in _FILE_CACHE:
        try:
            _FILE_CACHE[file_rel] = (ROOT / file_rel).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            _FILE_CACHE[file_rel] = []
    lines = _FILE_CACHE[file_rel]
    if not lines:
        return ""
    i = max(0, (start or 1) - 1)
    n = len(lines)
    j = i
    # scan up to 25 lines for the opening brace — Liquity fns have long multi-line signatures (many params +
    # modifiers) before `{`; an 8-line window missed e.g. RedemptionHelper.redeemCollateral.
    while j < min(n, i + 25) and "{" not in lines[j]:
        j += 1
    if j >= min(n, i + 25) or "{" not in lines[j]:
        return ""
    depth, out, started = 0, [], False
    for k in range(j, min(n, j + _BODY_MAX_LINES)):
        line = lines[k]
        out.append(line)
        depth += line.count("{") - line.count("}")
        if "{" in line:
            started = True
        if started and depth <= 0:
            break
    return "\n".join(out)[:8000]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest")
    ap.add_argument("--no-source", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    man_path = Path(args.manifest) if args.manifest else audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    if not items:
        raise SystemExit(f"[liquidation_health_accounting_audit] no manifest items at {man_path}")
    use_source = not args.no_source

    fn_items = [it for it in items if it.get("kind") in ("function", "initializer", "constructor")]
    in_scope_ids = {it["id"] for it in items if it.get("in_scope", True)}
    # same-contract name->body for one-level helper resolution
    bodies_by_contract: dict[str, dict[str, str]] = defaultdict(dict)
    for it in fn_items:
        span = it.get("source_span", {})
        bodies_by_contract[it.get("contract", "")][it.get("name", "")] = \
            _function_body(it.get("file", ""), span.get("start_line"), use_source)

    candidates = []
    for it in fn_items:
        name, contract, mid = it.get("name", ""), it.get("contract", ""), it.get("id")
        body = bodies_by_contract[contract].get(name, "")
        # +1-level same-contract helper resolution (credit a CR check in a called helper)
        resolved = body
        for called in set(_LOCAL_CALL_RE.findall(body)):
            if called != name and called in bodies_by_contract[contract]:
                resolved += "\n" + bodies_by_contract[contract][called]
        for c in lha.classify(name, it.get("signature", ""), it.get("file", ""), contract, snippet=resolved,
                              tags=it.get("tags")):
            c.update({"contract": contract, "function": name, "file": it.get("file"),
                      "lens_id": f"{contract}:{name}:{c['finding_shape']}",
                      "in_scope": mid in in_scope_ids, "manifest_id": mid,
                      "visibility": it.get("visibility", ""),
                      "false_positive_controls": "name-gated to liquidation/compensate/CR fns; two term-dimensions; "
                                                 "transfers/deposit/reward/oracle/admin/generic suppressed"})
            candidates.append(c)

    # de-dup identical lens_ids
    seen, uniq = set(), []
    for c in candidates:
        if c["lens_id"] in seen:
            continue
        seen.add(c["lens_id"]); uniq.append(c)
    candidates = uniq

    by_conf = Counter(c["confidence"] for c in candidates)

    # ----- routing (advisory, HIGH-ONLY) + internal-helper volume control -----
    # Only HIGH, in-scope candidates can route. Partition into top-level entrypoints (public/external, not
    # `_`-prefixed) vs internal helpers (internal/private visibility or `_`-prefixed). Attach a helper to a
    # same-contract high ENTRYPOINT whose body calls it (context, not an independent route); a helper with no
    # candidate-entrypoint caller routes standalone. Routes only to deep pass — never mints.
    def _is_helper(c: dict) -> bool:
        return c["visibility"] in ("internal", "private") or c["function"].startswith("_")

    high = [c for c in candidates if c["confidence"] == "high" and c["in_scope"]]
    entrypoints = [c for c in high if not _is_helper(c)]
    helpers = [c for c in high if _is_helper(c)]
    # context_helpers[entrypoint manifest_id] = [helper records attached]
    context_helpers: dict[str, list] = defaultdict(list)
    attached_ids = set()
    attached_pairs = set()  # (entrypoint_mid, helper_mid) — one record per helper per entrypoint
    for h in helpers:
        caller = next((e for e in entrypoints if e["contract"] == h["contract"]
                       and re.search(r"(?<![.\w])" + re.escape(h["function"]) + r"\s*\(",
                                     bodies_by_contract[e["contract"]].get(e["function"], ""))), None)
        if caller is not None:
            attached_ids.add(h["manifest_id"])
            if (caller["manifest_id"], h["manifest_id"]) not in attached_pairs:
                attached_pairs.add((caller["manifest_id"], h["manifest_id"]))
                context_helpers[caller["manifest_id"]].append(
                    {"manifest_id": h["manifest_id"], "function": h["function"], "finding_shape": h["finding_shape"]})
    # routed = high entrypoints + orphan helpers (no candidate-entrypoint caller)
    routed_ids = sorted({c["manifest_id"] for c in entrypoints}
                        | {h["manifest_id"] for h in helpers if h["manifest_id"] not in attached_ids})
    for c in candidates:
        if c["manifest_id"] in context_helpers:
            c["context_helpers"] = context_helpers[c["manifest_id"]]

    report = {
        "lens": "liquidation_health_accounting", "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest": str(man_path), "is_gate": False, "research_only": False, "routes_in_production": True,
        "routing": "advisory_high_only_strict_full_audit",
        "raw_candidates": len(candidates),
        "by_shape": dict(Counter(c["finding_shape"] for c in candidates)),
        "by_confidence": dict(by_conf),
        "high": by_conf.get("high", 0), "medium": by_conf.get("medium", 0),
        "low": by_conf.get("low", 0), "needs_context": by_conf.get("needs_context", 0),
        "routed_manifest_ids": routed_ids,
        "helper_attachments": {k: v for k, v in context_helpers.items()},
        "candidates": candidates,
    }
    out = audit_path("output") / "liquidation_health_accounting_audit.json"
    out.write_text(json.dumps(report, indent=2))

    if not args.quiet:
        print(f"[liquidation_health_accounting_audit] advisory HIGH-ONLY (routes via advisory_escalation_gate "
              f"in strict full-audit; never mints) · candidates {len(candidates)} · high {report['high']} "
              f"· routed {len(routed_ids)} · helpers-attached {len(attached_ids)} · wrote {out}")
        for mid in routed_ids:
            c = next(x for x in candidates if x["manifest_id"] == mid)
            ctx = f" +{len(context_helpers[mid])} helper-ctx" if mid in context_helpers else ""
            print(f"   → {c['contract']}.{c['function']} [{c['finding_shape']}]{ctx}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
