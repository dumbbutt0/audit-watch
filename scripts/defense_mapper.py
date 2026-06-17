#!/usr/bin/env python3
"""
defense_mapper.py — Maps existing contract defenses onto findings.

Run after static_analysis.py (Step 1.5), before specialist agents.
Resolves inherited modifiers from parent contracts, classifies defense
coverage per finding, and writes output/defense_map.json.

Usage:
    python scripts/defense_mapper.py [--contract <path>] [--function-only]
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path

OUTPUT_DIR = audit_path("output")

DEFENSE_MODIFIERS: dict[str, dict] = {
    "nonReentrant":         {"class": "reentrancy",      "strength": "strong"},
    "ReentrancyGuard":      {"class": "reentrancy",      "strength": "strong"},
    "onlyOwner":            {"class": "access_control",  "strength": "strong"},
    "onlyRole":             {"class": "access_control",  "strength": "strong"},
    "onlyAdmin":            {"class": "access_control",  "strength": "strong"},
    "onlyOperator":         {"class": "access_control",  "strength": "strong"},
    "onlyStrategist":       {"class": "access_control",  "strength": "strong"},
    "onlyGovernor":         {"class": "access_control",  "strength": "strong"},
    "onlyGuardian":         {"class": "access_control",  "strength": "strong"},
    "onlyEmergencyAdmin":   {"class": "access_control",  "strength": "strong"},
    "whenNotPaused":        {"class": "pausable",        "strength": "strong"},
    "whenPaused":           {"class": "pausable",        "strength": "strong"},
    "validAddress":         {"class": "input_validation","strength": "weak"},
    "nonZeroAmount":        {"class": "input_validation","strength": "weak"},
    "checkSlippage":        {"class": "slippage",        "strength": "strong"},
    "timelockGuard":        {"class": "timelock",        "strength": "strong"},
}

# Map vuln_type → defense class for coverage assessment
VULN_TO_DEFENSE_CLASS: dict[str, str] = {
    "reentrancy":          "reentrancy",
    "access-control":      "access_control",
    "flash-loan":          "reentrancy",
    "oracle-manipulation": "slippage",
    "price-manipulation":  "slippage",
    "front-running":       "slippage",
}


def load_static_data() -> dict:
    path = OUTPUT_DIR / "static.json"
    if not path.exists():
        print("  [defense_mapper] static.json not found — skipping defense resolution")
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as e:
        print(f"  [defense_mapper] static.json parse error: {e}")
        return {}


def load_all_findings() -> list[dict]:
    findings = []
    for path in sorted(OUTPUT_DIR.glob("findings_*.json")):
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        agent = data.get("agent", "")
        if agent == "protocol_context":
            continue
        for f in data.get("findings", []):
            findings.append(f)
    return findings


def build_modifier_index(static: dict) -> dict[str, list[str]]:
    """Build {function_name: [modifier_names]} from static.json functions list."""
    index: dict[str, list[str]] = {}
    for fn in static.get("functions", []):
        name = fn.get("name", "")
        mods = fn.get("modifiers", [])
        if name:
            index[name] = mods
    return index


def build_contract_modifier_index(static: dict) -> dict[str, dict[str, list[str]]]:
    """Build {contract_name: {function_name: [modifier_names]}} for inheritance resolution."""
    index: dict[str, dict[str, list[str]]] = {}
    for fn in static.get("functions", []):
        contract = fn.get("contract", "")
        name = fn.get("name", "")
        mods = fn.get("modifiers", [])
        if contract and name:
            index.setdefault(contract, {})[name] = mods
    return index


def extract_inheritance_chain(source_text: str) -> dict[str, list[str]]:
    """Parse contract inheritance from Solidity source."""
    chain: dict[str, list[str]] = {}
    pattern = re.compile(
        r'\bcontract\s+(\w+)\s+is\s+([\w\s,]+?)\s*\{',
        re.MULTILINE,
    )
    for match in pattern.finditer(source_text):
        contract_name = match.group(1)
        parents_raw = match.group(2)
        parents = [p.strip() for p in parents_raw.split(",") if p.strip()]
        chain[contract_name] = parents
    return chain


def resolve_inherited_modifiers(
    fn_name: str,
    contract_name: str,
    contract_modifier_index: dict[str, dict[str, list[str]]],
    inheritance: dict[str, list[str]],
    _visited: set[str] | None = None,
) -> list[dict]:
    """Walk the inheritance chain to find all modifiers applied to fn_name."""
    if _visited is None:
        _visited = set()
    if contract_name in _visited:
        return []
    _visited.add(contract_name)

    results: list[dict] = []

    # Check direct modifiers on this contract
    direct_mods = contract_modifier_index.get(contract_name, {}).get(fn_name, [])
    for mod in direct_mods:
        results.append({
            "modifier": mod,
            "defined_in": contract_name,
            "inherited": contract_name not in contract_modifier_index,  # simplified flag
        })

    # Recurse into parents
    for parent in inheritance.get(contract_name, []):
        results.extend(
            resolve_inherited_modifiers(fn_name, parent, contract_modifier_index, inheritance, _visited)
        )

    return results


def assess_coverage(
    applicable_defenses: list[dict],
    vuln_type: str,
) -> str:
    """Determine defense coverage for a given vuln_type."""
    expected_class = VULN_TO_DEFENSE_CLASS.get(vuln_type)
    if not applicable_defenses:
        return "none"
    if not expected_class:
        return "partial" if applicable_defenses else "none"

    for defense in applicable_defenses:
        mod_name = defense.get("modifier", "")
        meta = DEFENSE_MODIFIERS.get(mod_name, {})
        if meta.get("class") == expected_class and meta.get("strength") == "strong":
            return "full"

    # Has some defenses but not the right class
    return "partial"


def identify_evasion_paths(
    fn_name: str,
    static: dict,
    applicable_defenses: list[dict],
) -> str:
    """Check CFG edges for paths that might skip a modifier."""
    if not applicable_defenses:
        return ""

    cfg_edges = static.get("cfg_edges", [])
    if not cfg_edges:
        return ""

    # Look for internal calls from guarded function to unguarded callee
    # that could constitute a re-entry path
    guarded_fn_names = {
        defense.get("defined_in", fn_name) for defense in applicable_defenses
    }

    reentry_paths = []
    for edge in cfg_edges:
        caller = edge.get("from", "")
        callee = edge.get("to", "")
        call_type = edge.get("type", "")

        if caller == fn_name and call_type in ("external", "low_level"):
            reentry_paths.append(f"external call to {callee!r} from within {fn_name!r}")

    if reentry_paths:
        return "Potential re-entry: " + "; ".join(reentry_paths[:3])
    return ""


def map_finding_to_defenses(
    finding: dict,
    modifier_index: dict[str, list[str]],
    contract_modifier_index: dict[str, dict[str, list[str]]],
    inheritance: dict[str, list[str]],
    static: dict,
) -> dict:
    """Produce one defense mapping record for a finding."""
    fid = finding.get("id", "?")
    location = finding.get("location", {})
    fn_name = location.get("function", "")
    contract_name = ""

    # Try to infer contract from static functions list
    for fn in static.get("functions", []):
        if fn.get("name") == fn_name:
            contract_name = fn.get("contract", "")
            break

    vuln_type = finding.get("vuln_type", "")
    applicable_defenses: list[dict] = []
    inherited_from = ""

    if fn_name:
        # Direct modifiers first
        direct_mods = modifier_index.get(fn_name, [])
        for mod in direct_mods:
            meta = DEFENSE_MODIFIERS.get(mod, {})
            if meta:
                applicable_defenses.append({
                    "modifier": mod,
                    "class": meta["class"],
                    "strength": meta["strength"],
                    "defined_in": contract_name or "unknown",
                    "inherited": False,
                })

        # Resolve via inheritance chain
        if contract_name and inheritance:
            inherited = resolve_inherited_modifiers(
                fn_name, contract_name, contract_modifier_index, inheritance
            )
            for item in inherited:
                mod = item["modifier"]
                meta = DEFENSE_MODIFIERS.get(mod, {})
                if meta and not any(d["modifier"] == mod for d in applicable_defenses):
                    applicable_defenses.append({
                        "modifier": mod,
                        "class": meta["class"],
                        "strength": meta["strength"],
                        "defined_in": item["defined_in"],
                        "inherited": True,
                    })
                    if meta.get("strength") == "strong" and not inherited_from:
                        inherited_from = item["defined_in"]

    coverage = assess_coverage(applicable_defenses, vuln_type)
    evasion = ""
    if coverage == "full":
        evasion = identify_evasion_paths(fn_name, static, applicable_defenses)

    return {
        "finding_id": fid,
        "vulnerable_function": fn_name,
        "vulnerable_contract": contract_name,
        "applicable_defenses": applicable_defenses,
        "coverage": coverage,
        "evasion_path": evasion,
        "inherited_from": inherited_from,
        "coverage_note": _build_coverage_note(applicable_defenses, coverage, inherited_from),
    }


def _build_coverage_note(
    defenses: list[dict],
    coverage: str,
    inherited_from: str,
) -> str:
    if not defenses:
        return "No applicable defenses found"
    names = [d["modifier"] for d in defenses]
    base = f"{coverage.capitalize()} coverage via {names}"
    if inherited_from:
        base += f" (inherited from {inherited_from})"
    return base


def build_function_map(static: dict) -> dict[str, dict]:
    """Build a per-function defense map (no finding required)."""
    modifier_index = build_modifier_index(static)
    result = {}
    for fn in static.get("functions", []):
        fn_name = fn.get("name", "")
        if not fn_name:
            continue
        mods = modifier_index.get(fn_name, [])
        defenses = []
        for mod in mods:
            meta = DEFENSE_MODIFIERS.get(mod, {})
            if meta:
                defenses.append({
                    "modifier": mod,
                    "class": meta["class"],
                    "strength": meta["strength"],
                    "defined_in": fn.get("contract", "unknown"),
                    "inherited": False,
                })
        result[fn_name] = {
            "function": fn_name,
            "contract": fn.get("contract", ""),
            "defenses": defenses,
            "has_strong_defense": any(d["strength"] == "strong" for d in defenses),
        }
    return result


def load_contract_source(contract_path: str | None) -> str:
    """Load contract source for inheritance chain extraction."""
    if not contract_path:
        # Try to find from static.json contract field
        static_path = OUTPUT_DIR / "static.json"
        if static_path.exists():
            try:
                data = json.loads(static_path.read_text())
                contract_path = data.get("contract")
            except json.JSONDecodeError:
                pass

    if not contract_path:
        return ""

    p = Path(contract_path)
    if not p.exists():
        # Try relative to project root
        root = Path(__file__).resolve().parent.parent
        p = root / contract_path
    if not p.is_file():
        return ""

    if p.is_dir():
        # Read all .sol files
        source = ""
        for sol in p.rglob("*.sol"):
            try:
                source += sol.read_text()
            except OSError:
                pass
        return source

    try:
        return p.read_text()
    except OSError:
        return ""


def main():
    parser = argparse.ArgumentParser(description="Map defenses onto findings")
    parser.add_argument("--contract", help="Path to contract file or directory")
    parser.add_argument("--function-only", action="store_true",
                        help="Map defenses per function (no findings required)")
    args = parser.parse_args()

    print("Defense Mapper — Step 1.5\n")

    static = load_static_data()
    if not static:
        result = {"generated_at": _now(), "defense_mappings": {}, "error": "static.json not found or empty"}
        _write_output(result)
        print("  Wrote empty defense_map.json (static.json absent)")
        return

    modifier_index = build_modifier_index(static)
    contract_modifier_index = build_contract_modifier_index(static)
    print(f"  Indexed {len(modifier_index)} functions from static.json")

    # Load contract source for inheritance resolution
    source = load_contract_source(args.contract)
    inheritance = extract_inheritance_chain(source) if source else {}
    if inheritance:
        print(f"  Resolved inheritance chain: {list(inheritance.keys())}")
    else:
        print("  No contract source — skipping inheritance resolution")

    if args.function_only:
        fn_map = build_function_map(static)
        out_path = OUTPUT_DIR / "defense_map_functions.json"
        out_path.write_text(json.dumps({"generated_at": _now(), "functions": fn_map}, indent=2))
        print(f"  Wrote {out_path}")
        return

    findings = load_all_findings()
    print(f"  Processing {len(findings)} findings")

    mappings: dict[str, dict] = {}
    full_coverage_count = 0
    none_coverage_count = 0

    for finding in findings:
        fid = finding.get("id", "?")
        mapping = map_finding_to_defenses(
            finding, modifier_index, contract_modifier_index, inheritance, static
        )
        mappings[fid] = mapping

        if mapping["coverage"] == "full":
            full_coverage_count += 1
            evasion = mapping["evasion_path"]
            if not evasion:
                print(f"  [!] {fid}: FULL coverage, no evasion path → will be tagged 'already_guarded'")
            else:
                print(f"  [~] {fid}: FULL coverage but evasion path found: {evasion[:60]}")
        elif mapping["coverage"] == "none":
            none_coverage_count += 1

    result = {
        "generated_at": _now(),
        "summary": {
            "total_findings": len(findings),
            "full_coverage": full_coverage_count,
            "none_coverage": none_coverage_count,
            "partial_coverage": len(findings) - full_coverage_count - none_coverage_count,
        },
        "defense_mappings": mappings,
    }

    _write_output(result)

    # Hard-tag findings with full coverage + no evasion path at Step 1.5.
    # This makes the defense mapper authoritative: triage_findings.py reads this
    # file and hard-rejects listed findings immediately — Gate 4 still validates
    # but is no longer the first place already_guarded is enforced.
    already_guarded = []
    for finding in findings:
        fid = finding.get("id", "?")
        m = mappings.get(fid, {})
        if m.get("coverage") == "full" and not m.get("evasion_path", ""):
            names = [d.get("modifier") for d in m.get("applicable_defenses", [])]
            already_guarded.append({
                "finding_id": fid,
                "invalidation_tag": "already_guarded",
                "reason": f"full defense coverage via {names} — no evasion path",
                "tagged_at_step": "1.5",
                "tagged_at": _now(),
            })

    defense_rejected_path = OUTPUT_DIR / "defense_rejected.jsonl"
    if already_guarded:
        with open(defense_rejected_path, "w") as f:
            for entry in already_guarded:
                f.write(json.dumps(entry) + "\n")
        print(f"\n  Hard-tagged {len(already_guarded)} finding(s) as 'already_guarded' → output/defense_rejected.jsonl")
    elif defense_rejected_path.exists():
        defense_rejected_path.unlink()

    print(f"\n  Summary: {full_coverage_count} full-coverage, {none_coverage_count} no-coverage, "
          f"{len(findings) - full_coverage_count - none_coverage_count} partial")
    print(f"  Wrote output/defense_map.json")


def _write_output(data: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "defense_map.json").write_text(json.dumps(data, indent=2))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    main()
