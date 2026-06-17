#!/usr/bin/env python3
"""
static_analysis.py

Pre-analysis tool. Runs slither and solc on a contract and produces
output/static.json consumed by all specialist agents.

Usage:
    python tools/static_analysis.py contracts/Vault.sol
    python tools/static_analysis.py contracts/  # analyses all .sol files

Dependencies:
    slither-analyzer (pip install slither-analyzer)
    solc (install via solc-select: pip install solc-select && solc-select install auto)
"""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from audit_context import audit_path

OUTPUT_DIR = audit_path("output")


TAINT_DETECTORS = [
    "reentrancy-eth",
    "reentrancy-no-eth",
    "controlled-delegatecall",
    "msg-value-loop",
    "arbitrary-send-eth",
    "arbitrary-send-erc20",
    "unchecked-lowlevel",
    "suicidal",
]

# ERC-4626 function signatures that trigger the erc4626.md specialist agent
ERC4626_SIGNATURES = {
    "deposit(uint256,address)",
    "withdraw(uint256,address,address)",
    "mint(uint256,address)",
    "redeem(uint256,address,address)",
    "convertToShares(uint256)",
    "convertToAssets(uint256)",
    "totalAssets()",
    "previewDeposit(uint256)",
    "previewWithdraw(uint256)",
    "previewMint(uint256)",
    "previewRedeem(uint256)",
    "maxDeposit(address)",
    "maxWithdraw(address)",
}

# EIP-1153 transient storage opcodes (hex)
TSTORE_OPCODE = "5d"
TLOAD_OPCODE  = "5c"


def _find_slither() -> str:
    """Return the slither binary path, checking venv and user local installs."""
    for candidate in [
        shutil.which("slither"),
        str(Path(sys.executable).parent / "slither"),
        str(Path.home() / ".local" / "bin" / "slither"),
    ]:
        if candidate and Path(candidate).exists():
            return candidate
    return "slither"


def _slither_extra_args(contract_path: Path) -> list[str]:
    """Return extra slither args if a slither.config.json or node_modules exists nearby."""
    extra = []
    # Walk up to find slither.config.json
    check = contract_path if contract_path.is_dir() else contract_path.parent
    for directory in [check, *check.parents]:
        cfg = directory / "slither.config.json"
        if cfg.exists():
            try:
                cfg_data = json.loads(cfg.read_text())
                if "solc_remaps" in cfg_data:
                    # Resolve relative remap roots to absolute paths so slither
                    # finds node_modules regardless of CWD.
                    remap = cfg_data["solc_remaps"]
                    if "=" in remap:
                        prefix, target = remap.split("=", 1)
                        abs_target = str((directory / target).resolve()) + "/"
                        remap = f"{prefix}={abs_target}"
                    extra += ["--solc-remaps", remap]
                if "filter_paths" in cfg_data:
                    extra += ["--filter-paths", cfg_data["filter_paths"]]
            except (json.JSONDecodeError, KeyError):
                pass
            break
        nm = directory / "node_modules" / "@openzeppelin"
        if nm.exists():
            extra += ["--solc-remaps", f"@openzeppelin/={directory.resolve()}/node_modules/@openzeppelin/"]
            extra += ["--filter-paths", "node_modules"]
            break
    return extra


def run_slither(contract_path: Path) -> dict:
    """Run slither with JSON output and return parsed results."""
    slither_bin = _find_slither()
    extra = _slither_extra_args(contract_path)
    cmd = [
        slither_bin, str(contract_path),
        "--json", "-",
        "--disable-color",
        "--detect", ",".join(TAINT_DETECTORS),
    ] + extra
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if result.stdout:
            return json.loads(result.stdout)
        if result.returncode not in (0, 1):
            print(f"Warning: slither exited {result.returncode}: {result.stderr[:200]}")
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Warning: slither failed — {e}")
        print("Install slither: pip install slither-analyzer")
    return {}


def run_solc_ast(contract_path: Path) -> dict:
    """Run solc --ast-compact-json and return the AST."""
    cmd = [
        "solc", "--ast-compact-json", "--allow-paths", ".",
        str(contract_path)
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0 and result.stdout:
            # solc outputs text before the JSON; find the JSON object
            lines = result.stdout.split("\n")
            json_lines = []
            in_json = False
            for line in lines:
                if line.strip().startswith("{"):
                    in_json = True
                if in_json:
                    json_lines.append(line)
            if json_lines:
                return json.loads("\n".join(json_lines))
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Warning: solc AST failed — {e}")
        print("Install solc: pip install solc-select && solc-select install auto")
    return {}


def extract_functions(slither_data: dict) -> list[dict]:
    """Extract function signatures from slither output."""
    functions = []
    for contract in slither_data.get("contracts", []):
        for fn in contract.get("functions", []):
            functions.append({
                "name": fn.get("name"),
                "contract": contract.get("name"),
                "visibility": fn.get("visibility"),
                "modifiers": fn.get("modifiers", []),
                "is_payable": fn.get("payable", False),
                "parameters": fn.get("parameters", []),
                "returns": fn.get("returns", []),
            })
    return functions


def extract_state_variables(slither_data: dict) -> list[dict]:
    """Extract state variables from slither output."""
    variables = []
    for contract in slither_data.get("contracts", []):
        for var in contract.get("state_variables", []):
            variables.append({
                "name": var.get("name"),
                "type": var.get("type"),
                "contract": contract.get("name"),
                "visibility": var.get("visibility"),
            })
    return variables


def extract_external_calls(slither_data: dict) -> list[dict]:
    """Extract external call sites — highest priority for reentrancy/flash loan agents."""
    calls = []
    for detector_result in slither_data.get("results", {}).get("detectors", []):
        if "call" in detector_result.get("check", "").lower():
            for element in detector_result.get("elements", []):
                calls.append({
                    "function": element.get("name"),
                    "source_file": element.get("source_mapping", {}).get("filename_short"),
                    "line": element.get("source_mapping", {}).get("lines", [None])[0],
                    "type": detector_result.get("check"),
                })
    return calls


def extract_compiler_version(contract_path: Path) -> str:
    """Read pragma statement from source."""
    try:
        source = contract_path.read_text()
        for line in source.split("\n"):
            if line.strip().startswith("pragma solidity"):
                return line.strip()
    except Exception:
        pass
    return "unknown"


def _finding_file(det: dict) -> str:
    """Best-effort source file for a detector hit: element source_mapping, else description regex."""
    for element in det.get("elements", []):
        sm = element.get("source_mapping", {})
        f = sm.get("filename_short") or sm.get("filename_relative")
        if f:
            return f
    m = re.search(r'(contracts/[^\s#)]+\.sol)', det.get("description", ""))
    return m.group(1) if m else ""


def extract_slither_detectors(slither_data: dict) -> list[dict]:
    """Extract raw slither detector hits for reference."""
    hits = []
    for det in slither_data.get("results", {}).get("detectors", []):
        hits.append({
            "check": det.get("check"),
            "impact": det.get("impact"),
            "severity": det.get("impact"),  # alias: downstream consumers key on `severity`
            "confidence": det.get("confidence"),
            "file": _finding_file(det),
            "description": det.get("description", "")[:400],
        })
    return hits


def extract_tainted_sinks(slither_data: dict) -> list[dict]:
    """Extract taint analysis results: tainted-calls, arbitrary-send-*, controlled-delegatecall."""
    sinks = []
    for det in slither_data.get("results", {}).get("detectors", []):
        check = det.get("check", "")
        if check not in TAINT_DETECTORS:
            continue
        for element in det.get("elements", []):
            sinks.append({
                "function": element.get("name", "unknown"),
                "tainted_parameter": element.get("type", "unknown"),
                "sink_type": check,
                "confidence": det.get("confidence", "Medium"),
                "impact": det.get("impact", "Medium"),
                "description": det.get("description", "")[:300],
                "source_file": element.get("source_mapping", {}).get("filename_short"),
                "line": (element.get("source_mapping", {}).get("lines") or [None])[0],
            })
    return sinks


def extract_delegatecall_risks(slither_data: dict) -> list[dict]:
    """Extract controlled-delegatecall findings specifically."""
    risks = []
    for det in slither_data.get("results", {}).get("detectors", []):
        if det.get("check") != "controlled-delegatecall":
            continue
        for element in det.get("elements", []):
            risks.append({
                "function": element.get("name", "unknown"),
                "confidence": det.get("confidence", "High"),
                "description": det.get("description", "")[:300],
                "source_file": element.get("source_mapping", {}).get("filename_short"),
                "line": (element.get("source_mapping", {}).get("lines") or [None])[0],
            })
    return risks


def run_mythril(contract_path: Path, timeout_seconds: int = 300) -> list[dict]:
    """Run Mythril symbolic execution and return parsed issues. Non-fatal."""
    try:
        result = subprocess.run(
            ["myth", "analyze", str(contract_path), "--execution-timeout", str(timeout_seconds), "-o", "json"],
            capture_output=True, text=True, timeout=timeout_seconds + 30,
        )
        if result.stdout:
            data = json.loads(result.stdout)
            return [
                {
                    "swc_id": issue.get("swc-id"),
                    "title": issue.get("title"),
                    "severity": issue.get("severity"),
                    "description": issue.get("description", {}).get("head", "")[:300],
                    "function": issue.get("extra", {}).get("discoveryTime"),
                    "line": issue.get("sourceMap", "").split(":")[0] if issue.get("sourceMap") else None,
                }
                for issue in data.get("issues", [])
            ]
    except FileNotFoundError:
        pass  # Mythril not installed — silent skip
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
        print(f"Warning: Mythril analysis failed — {e}", file=sys.stderr)
    return []


def detect_erc4626(source: str) -> bool:
    """Return True if the contract source implements ERC-4626 interface."""
    match_count = sum(1 for sig in ERC4626_SIGNATURES if sig.split("(")[0] in source)
    return match_count >= 4  # require at least 4 signature matches


def detect_transient_storage(bytecode_hex: str, source: str) -> bool:
    """Return True if TSTORE/TLOAD opcodes or ReentrancyGuardTransient appear."""
    if "ReentrancyGuardTransient" in source or "tstore" in source.lower() or "tload" in source.lower():
        return True
    if not bytecode_hex:
        return False
    code_body = bytecode_hex.replace("0x", "")
    opcodes = [code_body[i:i+2] for i in range(0, len(code_body), 2)]
    return TSTORE_OPCODE in opcodes or TLOAD_OPCODE in opcodes


def get_compiled_bytecode(contract_path: Path) -> str:
    """Get compiled bytecode hex for opcode scanning."""
    try:
        result = subprocess.run(
            ["solc", "--bin", str(contract_path)],
            capture_output=True, text=True, timeout=60,
        )
        for line in result.stdout.split("\n"):
            line = line.strip()
            if len(line) > 10 and all(c in "0123456789abcdefABCDEF" for c in line):
                return line
    except Exception:
        pass
    return ""


def analyse(contract_path: Path) -> dict:
    print(f"Analysing {contract_path}...")

    slither_data = run_slither(contract_path)
    ast_data = run_solc_ast(contract_path)
    compiler_version = extract_compiler_version(contract_path)

    tainted_sinks = extract_tainted_sinks(slither_data)
    delegatecall_risks = extract_delegatecall_risks(slither_data)

    # Layer 3: Mythril symbolic execution
    mythril_issues = run_mythril(contract_path)

    # Conditional agent triggers: read source for signature + opcode detection
    try:
        source = contract_path.read_text(errors="replace")
    except Exception:
        source = ""
    bytecode_hex = get_compiled_bytecode(contract_path)

    is_erc4626 = detect_erc4626(source)
    has_transient_storage = detect_transient_storage(bytecode_hex, source)

    # Proxy detection (extend existing delegatecall_risks)
    is_proxy = bool(delegatecall_risks) or any(
        kw in source for kw in ("ERC1967", "_IMPLEMENTATION_SLOT", "TransparentUpgradeableProxy",
                                "UUPSUpgradeable", "BeaconProxy", "0x363d3d373d")
    )

    static = {
        "contract_path": str(contract_path),
        "compiler_version": compiler_version,
        "functions": extract_functions(slither_data),
        "state_variables": extract_state_variables(slither_data),
        "external_calls": extract_external_calls(slither_data),
        "slither_findings": extract_slither_detectors(slither_data),
        "tainted_sinks": tainted_sinks,
        "delegatecall_risks": delegatecall_risks,
        "mythril_issues": mythril_issues,
        "is_erc4626": is_erc4626,
        "has_transient_storage": has_transient_storage,
        "is_proxy": is_proxy,
        "ast_available": bool(ast_data),
        "slither_available": bool(slither_data),
        "mythril_available": len(mythril_issues) >= 0,
    }

    # Fallback: if slither not installed, do basic regex parsing
    if not slither_data:
        print("Slither not available — falling back to regex parsing.")
        static.update(parse_source_fallback(contract_path))

    out_path = OUTPUT_DIR / "static.json"
    with open(out_path, "w") as f:
        json.dump(static, f, indent=2)

    # ── viz: emit HYPOTHESIS_BORN for each slither detector hit ─────────────
    try:
        from viz.event_emitter import emit as _viz_emit
        _contracts = [str(contract_path)] if isinstance(contract_path, Path) else [str(p) for p in contract_path] if hasattr(contract_path, '__iter__') else []
        for _hit in static.get("slither_findings", []):
            _conf_map = {"High": 0.75, "Medium": 0.55, "Low": 0.3}
            _viz_emit("HYPOTHESIS_BORN", source_agent="static_analysis", payload={
                "hypothesis_text": _hit.get("description", ""),
                "label": _hit.get("check", "") + ": " + _hit.get("description", "")[:50],
                "exploit_class": _hit.get("check", "unknown"),
                "severity_ceiling": _hit.get("impact", "UNKNOWN").upper(),
                "confidence": _conf_map.get(_hit.get("confidence", "Low"), 0.3),
                "linked_contracts": _contracts,
            })
    except Exception:
        pass

    print(f"Static analysis written to {out_path}")
    print(f"  Functions found: {len(static['functions'])}")
    print(f"  State variables: {len(static['state_variables'])}")
    print(f"  External call sites: {len(static['external_calls'])}")
    print(f"  Slither detector hits: {len(static['slither_findings'])}")
    print(f"  Tainted sinks: {len(static['tainted_sinks'])}")
    print(f"  Delegatecall risks: {len(static['delegatecall_risks'])}")
    print(f"  Mythril issues: {len(static['mythril_issues'])}")
    print(f"  ERC-4626 detected: {static['is_erc4626']}")
    print(f"  Transient storage (EIP-1153): {static['has_transient_storage']}")
    print(f"  Proxy pattern detected: {static['is_proxy']}")

    return static


EXCLUDED_SCAN_DIRS = ("/mocks/", "/test/", "/node_modules/", "/lib/", "/script/")


def _find_project_root(target: Path) -> Path | None:
    """Walk up from target to find a foundry.toml or hardhat config (project root)."""
    start = target if target.is_dir() else target.parent
    for d in [start, *start.parents]:
        if (d / "foundry.toml").exists() or (d / "hardhat.config.js").exists() \
           or (d / "hardhat.config.ts").exists():
            return d
    return None


def _in_scope_sources(contracts_dir: Path) -> list[Path]:
    """All .sol files under contracts_dir excluding mocks/test/vendored code."""
    out = []
    for f in contracts_dir.rglob("*.sol"):
        posix = f.as_posix()
        if any(x in posix for x in EXCLUDED_SCAN_DIRS):
            continue
        if f.name == "AuditAggregator.sol":
            continue
        out.append(f)
    return out


def _aggregate_source_inventory(sources: list[Path]) -> tuple[list[dict], list[dict]]:
    """Best-effort function + external-call inventory via regex across all in-scope files.

    Slither's `--json` detector output does not include a contract/function list, so this
    source scan supplies the navigation inventory while slither supplies the real findings.
    """
    functions: list[dict] = []
    external_calls: list[dict] = []
    fn_pattern = re.compile(
        r'function\s+(\w+)\s*\(([^)]*)\)\s*(public|external|internal|private)?\s*([^{]*){',
        re.MULTILINE,
    )
    call_patterns = [r'\.call\s*\{', r'\.transfer\s*\(', r'\.send\s*\(',
                     r'IERC20\(', r'IUniswap', r'IChainlink']
    for f in sources:
        try:
            source = f.read_text(errors="replace")
        except OSError:
            continue
        rel = f.name
        for m in fn_pattern.finditer(source):
            fn_name, _params, visibility, rest = m.groups()
            modifiers = re.findall(r'\b(onlyOwner|nonReentrant|onlyRole|whenNotPaused|\w+Modifier)\b', rest or "")
            functions.append({
                "name": fn_name,
                "contract": f.stem,
                "visibility": visibility or "unknown",
                "modifiers": modifiers,
                "is_payable": "payable" in (rest or ""),
                "source_file": rel,
            })
        for pattern in call_patterns:
            for m in re.finditer(pattern, source):
                external_calls.append({
                    "type": pattern,
                    "line": source[:m.start()].count('\n') + 1,
                    "function": "unknown",
                    "source_file": rel,
                })
    return functions, external_calls


def analyse_project(target: Path) -> dict:
    """Whole-project static analysis: one slither run via compile_for_analysis.sh.

    Replaces the broken per-file loop that ran slither without remappings and silently
    fell back to regex on every file. Compilation (incl. stack-too-deep fallbacks) is
    owned by scripts/compile_for_analysis.sh.
    """
    project_root = _find_project_root(target)
    if project_root is None:
        print("[static] No foundry.toml/hardhat config found — falling back to per-file scan.")
        return {}

    print(f"[static] Project root: {project_root}")
    compile_script = Path(__file__).resolve().parent.parent / "scripts" / "compile_for_analysis.sh"
    slither_json = f"/tmp/slither_{project_root.parent.name}_{project_root.name}.json"

    layer = "?"
    slither_data: dict = {}
    try:
        proc = subprocess.run(
            ["bash", str(compile_script), str(project_root), slither_json],
            capture_output=True, text=True, timeout=2400,
        )
        for line in proc.stdout.splitlines():
            if line.startswith("LAYER="):
                layer = line.split("=", 1)[1].strip()
            elif line.startswith("SLITHER_JSON="):
                slither_json = line.split("=", 1)[1].strip()
        if Path(slither_json).exists():
            slither_data = json.loads(Path(slither_json).read_text())
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as e:
        print(f"[static] compile_for_analysis.sh failed: {e}")

    detectors = slither_data.get("results", {}).get("detectors", [])
    slither_ok = bool(slither_data.get("success") or detectors)

    contracts_dir = project_root / "contracts"
    if not contracts_dir.is_dir():
        contracts_dir = target if target.is_dir() else project_root
    sources = _in_scope_sources(contracts_dir)
    functions, source_calls = _aggregate_source_inventory(sources)

    # Detector-based extraction (the high-value, previously-broken part).
    tainted_sinks = extract_tainted_sinks(slither_data)
    delegatecall_risks = extract_delegatecall_risks(slither_data)
    slither_calls = extract_external_calls(slither_data)
    external_calls = slither_calls + source_calls

    # Flag detection scans the whole in-scope tree, not a single file.
    joined = ""
    for f in sources[:400]:
        try:
            joined += f.read_text(errors="replace")
        except OSError:
            pass
    is_erc4626 = detect_erc4626(joined)
    has_transient_storage = detect_transient_storage("", joined)
    is_proxy = bool(delegatecall_risks) or any(
        kw in joined for kw in ("ERC1967", "_IMPLEMENTATION_SLOT", "TransparentUpgradeableProxy",
                                "UUPSUpgradeable", "BeaconProxy", "delegatecall", "LibDiamond",
                                "DiamondCut")
    )

    static = {
        "contract_path": str(target),
        "project_root": str(project_root),
        "compile_layer": layer,
        "compiler_version": (sources and extract_compiler_version(sources[0])) or "unknown",
        "functions": functions,
        "state_variables": [],
        "external_calls": external_calls,
        "slither_findings": extract_slither_detectors(slither_data),
        "tainted_sinks": tainted_sinks,
        "delegatecall_risks": delegatecall_risks,
        "mythril_issues": [],
        "is_erc4626": is_erc4626,
        "has_transient_storage": has_transient_storage,
        "is_proxy": is_proxy,
        "ast_available": slither_ok,
        "slither_available": slither_ok,
        "mythril_available": False,
    }

    if not slither_ok:
        print("[static] WARNING: slither produced no results — static.json has only the "
              "regex source inventory. Detector fields are EMPTY. Do not trust an empty "
              "findings set as 'clean'. Check /tmp/compile_slither*.log.", file=sys.stderr)

    out_path = OUTPUT_DIR / "static.json"
    out_path.write_text(json.dumps(static, indent=2))

    print(f"Static analysis written to {out_path}")
    print(f"  Compile layer:        {layer}")
    print(f"  Slither available:    {slither_ok}")
    print(f"  Functions (source):   {len(functions)}")
    print(f"  External call sites:  {len(external_calls)}")
    print(f"  Slither detector hits:{len(static['slither_findings'])}")
    print(f"  Tainted sinks:        {len(tainted_sinks)}")
    print(f"  Delegatecall risks:   {len(delegatecall_risks)}")
    print(f"  ERC-4626 detected:    {is_erc4626}")
    print(f"  Transient storage:    {has_transient_storage}")
    print(f"  Proxy/Diamond:        {is_proxy}")
    return static


def parse_source_fallback(contract_path: Path) -> dict:
    """
    Minimal regex-based parsing when slither is unavailable.
    Less accurate but gives agents something to work with.
    """
    source = contract_path.read_text()

    functions = []
    fn_pattern = re.compile(
        r'function\s+(\w+)\s*\(([^)]*)\)\s*(public|external|internal|private)?\s*([^{]*){',
        re.MULTILINE
    )
    for m in fn_pattern.finditer(source):
        fn_name, params, visibility, rest = m.groups()
        modifiers = re.findall(r'\b(onlyOwner|nonReentrant|onlyRole|whenNotPaused|\w+Modifier)\b', rest or "")
        functions.append({
            "name": fn_name,
            "contract": "unknown",
            "visibility": visibility or "unknown",
            "modifiers": modifiers,
            "is_payable": "payable" in (rest or ""),
        })

    external_calls = []
    call_patterns = [
        r'\.call\s*\{',
        r'\.transfer\s*\(',
        r'\.send\s*\(',
        r'IERC20\(',
        r'IUniswap',
        r'IChainlink',
    ]
    for pattern in call_patterns:
        for m in re.finditer(pattern, source):
            line_num = source[:m.start()].count('\n') + 1
            external_calls.append({
                "type": pattern,
                "line": line_num,
                "function": "unknown",
            })

    return {
        "functions": functions,
        "state_variables": [],
        "external_calls": external_calls,
        "slither_findings": [],
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/static_analysis.py <contract.sol|contracts/>")
        sys.exit(1)

    # Language dispatch: rust audits use the Rust/Solana adapter, which writes the SAME
    # static.json schema. The Solidity path below is byte-unchanged for language=solidity.
    try:
        from audit_context import audit_language as _audit_language
        if _audit_language() == "rust":
            import static_analysis_rust  # noqa: WPS433  (tools/ on sys.path via the file's own dir)
            sys.exit(static_analysis_rust.main())
    except SystemExit:
        raise
    except Exception as _e:  # noqa: BLE001  — never break the Solidity path on a dispatch hiccup
        print(f"[static] language dispatch check skipped ({_e}); proceeding with Solidity path")

    target = Path(sys.argv[1])

    if target.is_dir():
        # Whole-project run: one slither pass with correct remappings + compile fallback.
        result = analyse_project(target)
        if not result:
            # No foundry/hardhat project detected — last-resort per-file regex scan.
            sol_files = [f for f in target.rglob("*.sol")
                         if not any(x in f.as_posix() for x in EXCLUDED_SCAN_DIRS)]
            print(f"[static] No build framework detected; per-file regex scan of "
                  f"{len(sol_files)} files (degraded — no slither detectors).")
            for sol_file in sol_files:
                analyse(sol_file)
    elif target.is_file():
        analyse(target)
    else:
        print(f"Error: {target} does not exist.")
        sys.exit(1)
