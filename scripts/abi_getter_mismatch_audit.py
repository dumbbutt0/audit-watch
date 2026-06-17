#!/usr/bin/env python3
"""
abi_getter_mismatch_audit.py — cross-file interface / public-getter ABI mismatch detector.

Detects the Hybra M-07 residual class: an interface declares `name(args) returns (R)` but the implementation
exposes `... public name` (a state variable), whose Solidity AUTO-GETTER has a different ABI/selector/return
shape. A call through the interface against the implementation reverts or misdecodes. The body-focused
getter_state lens cannot see this (it is declaration-level + cross-file); this is its narrow sibling.

Reads:  output/coverage_manifest.json (interface DECLARATION items + impl function items),
        the in-scope source files (public state-var declarations are NOT in the manifest), and
        output/coverage_dispositions.json (coverage cross-ref only — never written).
Writes: output/abi_getter_mismatch_audit.{json,md}.  is_gate=False. NEVER writes dispositions/findings.

Routing is done separately by advisory_escalation_gate.py reading `routed_manifest_ids` (high+medium),
strict full-audit only. Low confidence is recorded in `context_only` and never routed.

Usage: python scripts/abi_getter_mismatch_audit.py [--manifest <path>] [--quiet]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import abi_getter_mismatch_taxonomy as agm  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
_FILE_CACHE: dict[str, list[str]] = {}

_CONTRACT_RE = re.compile(r"^\s*(?:abstract\s+)?(contract|library|interface)\s+([A-Za-z_]\w*)")


def _lines(file_rel: str) -> list[str]:
    if file_rel not in _FILE_CACHE:
        try:
            _FILE_CACHE[file_rel] = (ROOT / file_rel).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            _FILE_CACHE[file_rel] = []
    return _FILE_CACHE[file_rel]


def _load(path: Path, key: str):
    if not path.exists():
        return [] if key else {}
    try:
        d = json.loads(path.read_text())
        return d.get(key, []) if key else d
    except (OSError, json.JSONDecodeError):
        return [] if key else {}


def _is_decl(item: dict) -> bool:
    sig = (item.get("signature") or "").strip()
    return sig.endswith(";")  # interface / abstract declaration (no body)


def _scan_public_state_vars(files: list[str]) -> list[dict]:
    """Parse every `public` state-var declaration out of the given source files, tracking the enclosing
    contract/library (NOT interfaces — interfaces have no state)."""
    out = []
    for f in files:
        cur_contract, cur_kind = None, None
        for ln_no, line in enumerate(_lines(f), 1):
            m = _CONTRACT_RE.match(line)
            if m:
                cur_kind, cur_contract = m.group(1), m.group(2)
                continue
            if cur_kind == "interface":
                continue  # interfaces declare functions, not state vars
            parsed = agm.parse_public_state_var(line)
            if parsed:
                parsed = dict(parsed)
                parsed.update({"file": f, "line": ln_no, "contract": cur_contract})
                out.append(parsed)
    return out


def _enclosing_function(file_rel: str, line: int, fn_items: list[dict]) -> dict | None:
    """The in-file function item whose source span contains `line` (greatest start_line <= line)."""
    best = None
    for it in fn_items:
        if it.get("file") != file_rel:
            continue
        sp = it.get("source_span", {})
        st = sp.get("start_line") or 0
        en = sp.get("end_line") or st
        if st <= line and (line <= max(en, st) or line - st <= 120):
            if best is None or st > (best.get("source_span", {}).get("start_line") or 0):
                best = it
    return best


def _find_call_site(iface: str, method: str, fn_items: list[dict]):
    """Find a cast-and-call `IFace(...).method(` across source. Return (file, line, enclosing_fn_item) or None."""
    pat = re.compile(r"\b" + re.escape(iface) + r"\s*\([^;{}]*?\)\s*\.\s*" + re.escape(method) + r"\s*\(")
    files = sorted({it.get("file") for it in fn_items if it.get("file")})
    for f in files:
        for ln_no, line in enumerate(_lines(f), 1):
            if pat.search(line):
                return f, ln_no, _enclosing_function(f, ln_no, fn_items)
    return None


def _name_pairing(iface: str, impl_contract: str | None) -> bool:
    if not impl_contract:
        return False
    base = iface[1:] if (iface.startswith("I") and len(iface) > 1 and iface[1].isupper()) else iface
    return impl_contract == base or impl_contract.startswith(base) or base.startswith(impl_contract)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", help="manifest path (default: live coverage_manifest.json)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    man_path = Path(args.manifest) if args.manifest else audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    if not items:
        raise SystemExit(f"[abi_getter_mismatch_audit] no manifest items at {man_path}")
    fn_items = [it for it in items if it.get("kind") in ("function", "initializer", "constructor")]
    in_scope_ids = {it["id"] for it in items if it.get("in_scope", True)}
    disp = {d["manifest_id"]: d for d in _load(audit_path("output") / "coverage_dispositions.json", "dispositions")}

    # interface/abstract DECLARATIONS grouped by name; explicit impl functions (with bodies) by (contract,name)
    decls_by_name: dict[str, list[dict]] = {}
    impl_fns: dict[tuple, list[dict]] = {}
    for it in fn_items:
        name = it.get("name")
        if not name:
            continue
        if _is_decl(it):
            parsed = agm.parse_decl_signature(it.get("signature", ""))
            if parsed:
                decls_by_name.setdefault(name, []).append({**parsed, "_item": it})
        else:
            parsed = agm.parse_decl_signature(it.get("signature", ""))
            if parsed:
                impl_fns.setdefault((it.get("contract"), name), []).append(parsed)

    files = sorted({it.get("file") for it in items if it.get("file")})
    state_vars = _scan_public_state_vars(files)

    detected, seen = [], set()
    for sv in state_vars:
        decls = decls_by_name.get(sv["name"])
        if not decls:
            continue
        getter = agm.generated_getter_signature(sv)
        for decl in decls:
            res = agm.classify_pair(decl, getter)
            if not res["mismatch"]:
                continue
            # FP control: an explicit impl function (same contract) that matches the decl resolves the call.
            if any(agm.explicit_fn_resolves(decl, fn) for fn in impl_fns.get((sv["contract"], sv["name"]), [])):
                continue
            iface = decl["_item"].get("contract") or ""
            call = _find_call_site(iface, sv["name"], fn_items)
            has_call = call is not None
            pairing = _name_pairing(iface, sv["contract"])
            conf = agm.confidence(has_call, pairing, getter["needs_context"])

            call_file = call_fn_item = call_fn = None
            if call:
                call_file, _ln, call_fn_item = call
                call_fn = call_fn_item.get("name") if call_fn_item else None

            # route the most actionable in-scope item: the call-site function (high) else the interface decl.
            route_item = call_fn_item if (call_fn_item and call_fn_item["id"] in in_scope_ids) else decl["_item"]
            route_id = route_item["id"] if route_item.get("id") in in_scope_ids else None

            key = (decl["_item"]["id"], sv["file"], sv["line"])
            if key in seen:
                continue
            seen.add(key)

            d = disp.get(route_id, {}) if route_id else {}
            detected.append({
                "lens_id": f"AGM-{len(detected) + 1:03d}",
                "mismatch_type": res["mismatch_type"],
                "interface_file": decl["_item"].get("file"),
                "interface_contract": iface,
                "interface_signature": (decl["_item"].get("signature") or "").strip(),
                "interface_decl_id": decl["_item"]["id"],
                "implementation_file": sv["file"],
                "implementation_contract": sv["contract"],
                "state_variable": sv["name"],
                "state_variable_decl": sv["raw"],
                "generated_getter_signature": f"{getter['name']}({','.join(getter['arg_types'])}) returns ("
                                              f"{','.join(getter['return_types'])})",
                "selector_match": res["selector_match"],
                "call_site_file": call_file,
                "call_site_function": call_fn,
                "confidence": conf,
                "route_manifest_id": route_id,
                "route_disposition_status": d.get("status"),
                "reason": (f"interface {iface}.{sv['name']} declares "
                           f"`{decl['_item'].get('signature','').strip()}` but {sv['contract']} exposes "
                           f"`{sv['raw']}` whose auto-getter is "
                           f"{getter['name']}({','.join(getter['arg_types'])})->"
                           f"{','.join(getter['return_types'])} ({res['mismatch_type']})"),
                "missing_context": ("struct/proxy value return shape uninferable — verify in deep pass"
                                    if getter["needs_context"] else None),
            })

    routed = [x for x in detected if x["confidence"] in agm.ROUTED_CONFIDENCE and x["route_manifest_id"]]
    routed_ids = sorted({x["route_manifest_id"] for x in routed})
    context_only = [x for x in detected if x["confidence"] == "low" or not x["route_manifest_id"]]
    n_in_scope = max(1, len(in_scope_ids))
    route_rate = round(len(routed_ids) / n_in_scope, 4)

    ts = datetime.now(timezone.utc).isoformat()
    report = {
        "generated_at": ts, "manifest": str(man_path), "is_gate": False,
        "lens": "abi_getter_mismatch",
        "total_mismatches": len(detected),
        "by_mismatch_type": dict(Counter(x["mismatch_type"] for x in detected)),
        "by_confidence": dict(Counter(x["confidence"] for x in detected)),
        "routed_manifest_ids": routed_ids,
        "route_rate": route_rate,
        "context_only": [x["lens_id"] for x in context_only],
        "detected": detected,
    }
    out = audit_path("output") / "abi_getter_mismatch_audit.json"
    out.write_text(json.dumps(report, indent=2))

    md = [f"# ABI getter/interface mismatch audit\n",
          f"_Generated {ts} · manifest `{man_path}` · NOT a gate_\n",
          f"Mismatches: **{len(detected)}** · routed (high/medium): **{len(routed_ids)}** · "
          f"route_rate **{route_rate}** · context-only **{len(context_only)}**\n",
          "## Detected mismatches\n"]
    if detected:
        for x in detected:
            md.append(f"- **{x['interface_contract']}.{x['state_variable']}** [{x['confidence']}, "
                      f"{x['mismatch_type']}] — iface `{x['interface_signature']}` vs getter "
                      f"`{x['generated_getter_signature']}` — impl `{x['implementation_file']}` — "
                      f"call_site={x['call_site_function']} — route={x['route_manifest_id']}")
    else:
        md.append("- (none)")
    (audit_path("output") / "abi_getter_mismatch_audit.md").write_text("\n".join(md))

    if not args.quiet:
        print(f"[abi_getter_mismatch_audit] {len(detected)} mismatch(es) · routed {len(routed_ids)} "
              f"(rate {route_rate}) · context-only {len(context_only)} · wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
