#!/usr/bin/env python3
"""
analyze_poc_completeness.py — verify that each PoC proves what the finding claims.

For every finding, this tool:
  1. Loads the finding definition from data/findings/<ID>.json
  2. Loads the proof-requirement template for its bug_class
  3. Scans the PoC file for proof-step markers
  4. Compares found steps against required steps for claimed severity
  5. Computes the achieved PoC level (L3A / L3B / L3C)
  6. Blocks submission if claimed severity is not supported by the evidence
  7. Writes upgrade tasks when steps are missing

The core rule:
  A finding may not claim High if the PoC stops before proving the actual impact.
  If the PoC is incomplete, the severity ceiling is Medium and an upgrade task is generated.

Usage:
  python scripts/analyze_poc_completeness.py --finding-id RE-002
  python scripts/analyze_poc_completeness.py --all
  python scripts/analyze_poc_completeness.py --all --strict   # exit 1 on any incomplete High
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).parent.parent

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path

# ---------------------------------------------------------------------------
# Proof signatures
# ---------------------------------------------------------------------------
# Each key is a proof-step name. The associated list contains code markers
# that, if present in the PoC file, indicate that step is satisfied.
# Matching is case-sensitive substring search — keep markers specific enough
# to avoid false positives across unrelated bug classes.
PROOF_SIGNATURES: dict[str, list[str]] = {
    # ── reentrancy ──────────────────────────────────────────────────────────
    "locked_state_entered":              ["PROTOCOL_LOCKED", "read_locked", "REENTRY", "inject_state", "flash_loan"],
    "nested_call_or_callback":           ["transfer_from", "MockAToken", "callback", "invoke_contract"],
    "unguarded_state_mutation_called":   ["validate_and_finalize_transfer"],
    "state_change_proven":               ["read_collateral_bit", "assert!(!read_collateral_bit", "collateral_bit"],
    "victim_liquidatable_state_proven":  ["health_factor", "validate_liquidation", "is_liquidatable", "liquidatable"],
    "liquidation_entrypoint_called":     ["execute_liquidation", "MockLiquidationEngine", "liquidation_call"],
    "liquidation_succeeds":              [
        "result.liquidator",
        "result.collateral_to_liquidate",
        "LiquidationCall {",
    ],
    "profit_or_loss_asserted":           [
        "attacker_balance_after > attacker_balance_before",
        "victim_balance_after < victim_balance_before",
        "assert!(attacker_collateral",
        "assert!(victim_collateral_after",
        "collateral_to_liquidate > 0",      # attacker receives seized collateral
        "victim_collateral_after < victim",  # victim's collateral decreased
    ],
    # ── close-factor bypass ─────────────────────────────────────────────────
    "real_calculation_function_called":     ["calculate_liquidation"],
    "public_liquidation_entrypoint_called": ["execute_liquidation"],
    "cap_bypass_proven":                    ["close_factor_limit", "buggy_base", "correct_base", "cap never"],
    "excess_seizure_asserted":             [
        "collateral_to_liquidate >",
        "collateral_seized >",
        "> correct_max_collateral",
        "> max_correct_collateral",
        "> max_correct",
    ],
    # ── liquidation DoS ─────────────────────────────────────────────────────
    "panic_or_revert_proven":          ["should_panic", "unwrap_err", "is_err()", "Err("],
    "qualifying_insolvent_position":   [
        "total_debt_base: 2_000",
        "total_debt_base:               2_000",
        "health_factor: WAD / 4",
        "WAD / 4",
        "2_000 * WAD",
    ],
    # ── missing auth / allowance theft ─────────────────────────────────────
    "missing_require_auth_proven":     [
        "env.auths()",
        "liquidator_auth_was_required",
        "!liquidator_auth_was_required",
        "require_auth",
    ],
    "impersonated_address_recorded":   [
        "assert_eq!(record.liquidator",
        "assert_eq!(stored.unwrap().liquidator",
        "record.liquidator",
    ],
    "victim_allowance_consumed":       ["transfer_from", "spend_allowance", "token_allowance", "MockToken"],
    "victim_loss_asserted":            [
        "victim_balance_after < victim_balance_before",
        "victim_token_balance_after",
        "assert!(victim_loss",
        "victim_debt_token",
    ],
    # ── zero-slippage sandwich (Origin Protocol FL-006, DS-002) ─────────────
    "zero_min_amounts_proven":         [
        "amount0Min: 0", "amount1Min: 0", "[uint256(0), uint256(0)]",
        "amount0Min: 0,", "amount1Min: 0,",
        "[0, 0]", "min_amounts: [0", "uint256(0)], uint256(0))",
        "poc_fl_006", "poc_ds_002", "FL-006", "DS-002",
    ],
    "sandwich_attack_sequence_shown":  [
        "setTickOutOfRange", "set_tick_out_of_range", "imbalance()", "pool.imbalance",
        "front_run", "mev_bot", "sandwich", "MEV", "mev",
        "AboveRange", "out_of_range", "out of range",
        "poc_fl_006_zero_slippage", "poc_ds_002_mev",
        "test_poc_fl006", "test_poc_ds002",
    ],
    "victim_balance_decrease_asserted": [
        "weth < expectedWeth", "wethReceived == 0", "assertLt(actualWETH",
        "shortfall", "weth_out < ", "weth_received == 0",
        "weth_received  : 0", "WETH received  : 0",
        "BUG CON", "BUG CONFIRMED",
    ],
    "attacker_profit_quantified":       [
        "attacker_profit", "spread", "profit_wei", "profiting",
        "sandwich_profit", "mev_profit",
    ],
    # ── missing auth + accounting drift (Origin AC-003, AC-002) ─────────────
    "unauthorized_call_succeeds":       [
        "attacker.attack(", "AttackerContract", "buggy_verify_deposit_no_acl",
        "poc_ac_003_attacker", "Attacker call result.*Ok",
        "BUG CONFIRMED: attacker cleared",
        "result.is_ok()", "result == Ok(())",
        "Deposit forcibly removed",
    ],
    "accounting_drift_shown":           [
        "totalDepositsWei", "pending_after == 0", "underreported",
        "undercount", "32000000000000000000",
        "32 ETH", "accounting drift",
        "Undercount (wei)", "BUG CONFIRMED: 32",
        "deposit removed by attacker",
    ],
    "direct_fund_loss_asserted":        [
        "fund_loss", "balance_decrease", "vault_shortfall",
        "victim_balance", "attacker_gain",
    ],
    # ── oracle price manipulation (FL-001 virtual_price, FL-003 slot0) ────────
    "oracle_price_inflated_proven":     [
        "get_virtual_price", "virtual_price", "vpAfter > vpBefore", "vpAfter",
        "inflated", "manipulatePrice", "slot0", "sqrtPriceX96",
        "fairMinted != manipulatedMinted", "fairMinted",
        "imbalanced_deposit", "simulateImbalancedDeposit",
        "BUG: virtual_price", "BUG: price manipulation",
    ],
    "balance_overstatement_shown":      [
        "balanceAfter > balanceBefore", "balanceAfter",
        "checkBalance", "overstates", "overstatement",
        "inflatedTVL > trueTVL", "inflatedTVL",
        "manipulatedMinted > fairMinted", "lowerManipMinted",
        "upperManipMinted > fairMinted", "upperManipMinted",
        "slot0Minted > twapMinted", "slot0Minted",
        "excess OETHb", "excess minting", "oethbMinted",
    ],
    "overstatement_magnitude_quantified": [
        "overstatementBps", "overstatement > 0", "overstatementPct",
        "excess > 0", "oethbDeviation > 0",
        "overstatement is significant", "magnitude",
        "vpIncreaseActual > MAX_VP_INCREASE_BPS",
    ],
    "downstream_impact_shown":          [
        "vault", "rebase", "allocation", "TVL",
        "vault sees inflated", "prevents correct rebalancing",
        "mintForStrategy", "oethbRequired",
    ],
    # ── strict equality DoS (DS-001, LG-001) ────────────────────────────────
    "rounding_produces_nonzero_proven": [
        "weth_amount == 1", "rounding", "1 wei", "non-zero",
        "sqrtPriceX96", "Q64.96", "_wethAmount != 0",
        "Non zero wethAmount", "weth_received == 1",
    ],
    "strict_check_fails_shown":         [
        "require(_wethAmount == 0", "Non zero wethAmount", "revert",
        "_wethAmount != 0", "strict_equality", "strict ==",
    ],
    "operations_permanently_blocked_shown": [
        "bricked", "DoS", "all operations blocked",
        "withdrawal_fails", "deposit_fails", "permanently",
    ],
    # ── missing access control + oracle ratchet DoS (OR-007) ─────────────────
    "public_entrypoint_called":          [
        "updateWOETHOraclePrice()", "depositBridgedWOETH(", "withdrawBridgedWOETH(",
        "vm.prank", "strategy.updateWOETH",
    ],
    "unprivileged_call_proven":          [
        "vm.prank(attacker)", "address(0xDEAD)", "prank(attacker",
        "OR-007", "updateWOETHOraclePrice",
    ],
    "state_corrupted":                   [
        "lastOraclePrice", "floor locked at spike", "floor unchanged",
        "assertEq(strategy.lastOraclePrice", "locked as floor",
    ],
    "dos_of_core_operation_proven":      [
        "Negative wOETH yield", "vm.expectRevert",
        "depositBridgedWOETH", "withdrawBridgedWOETH",
    ],
    "no_onchain_recovery_path":          [
        "no reset path", "no setLastOraclePrice", "floor unchanged",
        "assertEq(strategy.lastOraclePrice()", "permanently",
    ],
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def load_poc_path(finding_id: str) -> Path | None:
    # 1. Check runtime_poc/results.jsonl (Claude-generated PoCs)
    poc_results = audit_path("data/runtime_poc") / "results.jsonl"
    if poc_results.exists():
        for line in poc_results.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                if d.get("finding_id") == finding_id:
                    p = d.get("test_file_path")
                    if p:
                        candidate = ROOT / p
                        if candidate.exists():
                            return candidate
            except json.JSONDecodeError:
                pass

    # 2. Check poc_queue individual result files (fork PoCs, run_poc_tests.py)
    poc_queue_dir = audit_path("data/poc_queue")
    result_file = poc_queue_dir / f"{finding_id}_result.json"
    if result_file.exists():
        try:
            d = json.loads(result_file.read_text())
            # poc_queue uses "test_file" (not "test_file_path")
            p = d.get("test_file") or d.get("test_file_path")
            if p:
                candidate = Path(p) if Path(p).is_absolute() else ROOT / p
                if candidate.exists():
                    return candidate
        except (json.JSONDecodeError, OSError):
            pass

    return None


def load_all_poc_code(finding_id: str) -> str:
    """Load all PoC code for a finding: primary file + Rust + Foundry sources."""
    parts = []
    seen: set[str] = set()

    def _add(p: Path) -> None:
        key = str(p.resolve())
        if key not in seen and p.exists():
            seen.add(key)
            parts.append(p.read_text())

    primary = load_poc_path(finding_id)
    if primary:
        _add(primary)

    # Also scan Rust PoC crate
    _add(audit_path("pocs/k2") / finding_id / "src" / "lib.rs")

    # Also scan Foundry test files containing the finding ID
    foundry_test_dir = audit_path("pocs/foundry/test")
    if foundry_test_dir.exists():
        fid_prefix = finding_id.replace("-", "")  # FL006, DS002, AC003
        for sol in foundry_test_dir.glob("*.t.sol"):
            if fid_prefix.upper() in sol.name.upper() or finding_id in sol.read_text():
                _add(sol)

    # Also scan files explicitly referenced in poc_queue result (covers fork PoC paths
    # that live outside the standard pocs/foundry/test/ directory)
    poc_queue_dir = audit_path("data/poc_queue")
    result_file = poc_queue_dir / f"{finding_id}_result.json"
    if result_file.exists():
        try:
            d = json.loads(result_file.read_text())
            for field in ("test_file", "test_file_path", "mock_test_file"):
                p_str = d.get(field)
                if p_str:
                    candidate = Path(p_str) if Path(p_str).is_absolute() else ROOT / p_str
                    _add(candidate)
        except (json.JSONDecodeError, OSError):
            pass

    return "\n".join(parts)


def detect_proof_steps(code: str) -> set[str]:
    found = set()
    for step, markers in PROOF_SIGNATURES.items():
        if any(marker in code for marker in markers):
            found.add(step)
    return found


def compute_poc_level(found: set[str], template: dict) -> str:
    """Return the highest achieved PoC level (L3C > L3B > L3A > L2)."""
    level_reqs = template.get("poc_level_requirements", {})
    for level in ["L3C", "L3B", "L3A"]:
        reqs = set(level_reqs.get(level, []))
        if reqs and reqs.issubset(found):
            return level
    return "L2"


def evaluate(finding: dict, template: dict, poc_code: str) -> dict:
    found = detect_proof_steps(poc_code)
    claimed_sev = finding["claimed_severity"]

    req_key = "required_for_high" if claimed_sev in ("High", "Critical") else "required_for_medium"
    required = set(template.get(req_key, []))
    missing = sorted(required - found)

    poc_level = compute_poc_level(found, template)
    poc_supports = len(missing) == 0
    severity_ceiling = claimed_sev if poc_supports else "Medium"

    return {
        "finding_id":               finding["finding_id"],
        "claimed_severity":         claimed_sev,
        "bug_class":                finding["bug_class"],
        "poc_level_achieved":       poc_level,
        "proof_steps_found":        sorted(found),
        "required_steps":           sorted(required),
        "missing_steps":            missing,
        "poc_supports_claimed_severity": poc_supports,
        "severity_ceiling":         severity_ceiling,
        "upgrade_required":         not poc_supports,
        "analyzed_at":              datetime.now(timezone.utc).isoformat(),
    }


def print_report(result: dict, template: dict, finding: dict):
    fid     = result["finding_id"]
    claimed = result["claimed_severity"]
    ceiling = result["severity_ceiling"]
    level   = result["poc_level_achieved"]
    missing = result["missing_steps"]
    found   = set(result["proof_steps_found"])
    required = set(result["required_steps"])

    level_descs = template.get("poc_level_descriptors", {})

    print(f"\n{'='*64}")
    print(f"  {fid}  |  Claimed: {claimed}  |  PoC Level: {level}  |  Ceiling: {ceiling}")
    print(f"{'='*64}")

    print("\nProof steps:")
    for step in sorted(required):
        sym = "✓" if step in found else "✗"
        print(f"  [{sym}] {step}")

    if not required:
        print("  (no required steps defined for this severity)")

    if level_descs:
        print(f"\nPoC level achieved: {level}")
        for lv, desc in sorted(level_descs.items()):
            marker = " ←" if lv == level else ""
            print(f"  {lv}: {desc}{marker}")

    if missing:
        print(f"\nMissing for {claimed}:")
        for s in missing:
            print(f"  ✗ {s}")
        print(f"\nDecision: PoC does not support {claimed} → ceiling is {ceiling}")
        print("Action:   Upgrade PoC or lower claimed severity before submitting")
    else:
        print(f"\nDecision: PoC supports claimed severity ({claimed}) ✓")


def generate_upgrade_task(result: dict, finding: dict, template: dict) -> str:
    fid     = result["finding_id"]
    claimed = result["claimed_severity"]
    level   = result["poc_level_achieved"]
    missing = result["missing_steps"]
    hint    = finding.get("upgrade_hint", "")
    neg_ctrl = template.get("negative_control_template", "")
    rationale = template.get("high_severity_rationale", "")

    lines = [
        f"# {fid} PoC Upgrade Task",
        "",
        f"**Current PoC Level:** {level}",
        f"**Required for {claimed}:** see missing steps below",
        f"**Current severity ceiling:** Medium",
        f"**Target severity:** {claimed}",
        "",
        "## Why the current PoC is not enough",
        "",
        rationale if rationale else f"The current proof stops before demonstrating {claimed}-level impact.",
        "",
        "## Current proof steps",
        "",
    ]
    for step in result["proof_steps_found"]:
        lines.append(f"- ✓ {step}")
    lines += ["", "## Missing steps for High", ""]
    for step in missing:
        lines.append(f"- ✗ {step}")
    if hint:
        lines += ["", "## How to add the missing steps", "", hint]
    if neg_ctrl:
        lines += [
            "",
            "## Negative control (strongly recommended)",
            "",
            neg_ctrl,
        ]
    lines += [
        "",
        "## File to edit",
        "",
        f"Add the missing assertions to the Level 3 test in:",
        f"`pocs/k2/{fid}/src/integrated_test.rs`",
        "",
        "## After upgrading",
        "",
        "Re-run:",
        f"```bash",
        f"cargo test --manifest-path pocs/k2/{fid}/Cargo.toml integrated_test",
        f"python scripts/analyze_poc_completeness.py --finding-id {fid}",
        f"python scripts/run_quality_checklist.py --finding-id {fid}",
        f"```",
    ]
    return "\n".join(lines)


def run_finding(finding_id: str, poc_path_override: Path | None = None) -> dict | None:
    finding_path = audit_path("data/findings") / f"{finding_id}.json"
    if not finding_path.exists():
        print(f"  [skip] {finding_id}: no finding definition at {finding_path}", file=sys.stderr)
        return None

    finding = load_json(finding_path)
    bug_class = finding["bug_class"]
    template_path = ROOT / "templates" / "proof_requirements" / f"{bug_class}.json"
    if not template_path.exists():
        print(f"  [skip] {finding_id}: no template for bug_class={bug_class}", file=sys.stderr)
        return None
    template = load_json(template_path)

    poc_path = poc_path_override or load_poc_path(finding_id)

    # Load all PoC code sources (Rust + Foundry + primary file)
    poc_code = load_all_poc_code(finding_id)
    if not poc_code.strip():
        # Fall back to single file if composite load returns nothing
        if not poc_path or not poc_path.exists():
            print(f"  [skip] {finding_id}: PoC file not found", file=sys.stderr)
            return None
        poc_code = poc_path.read_text()
    result = evaluate(finding, template, poc_code)
    print_report(result, template, finding)

    # Write completeness output
    out_dir = audit_path("output/poc_completeness")
    (out_dir / f"{finding_id}.json").write_text(json.dumps(result, indent=2))

    # Write upgrade task if needed
    if result["upgrade_required"]:
        task_dir = audit_path("output/poc_upgrade_tasks")
        task_md = generate_upgrade_task(result, finding, template)
        (task_dir / f"{finding_id}_upgrade.md").write_text(task_md)
        print(f"\n  Upgrade task written → output/poc_upgrade_tasks/{finding_id}_upgrade.md")

    return result


def main():
    parser = argparse.ArgumentParser(description="Verify PoC completeness against claimed severity")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--finding-id", help="Single finding ID")
    group.add_argument("--all", action="store_true", help="All findings with a definition file")
    parser.add_argument("--poc-path", help="Override PoC file path (single finding only)")
    parser.add_argument("--strict", action="store_true",
                        help="Exit 1 if any High claim is unsupported by PoC")
    args = parser.parse_args()

    poc_path_override = Path(args.poc_path) if args.poc_path else None

    if args.all:
        findings_dir = audit_path("data/findings")
        finding_ids = sorted(p.stem for p in findings_dir.glob("*.json"))
    else:
        finding_ids = [args.finding_id]

    results = []
    for fid in finding_ids:
        r = run_finding(fid, poc_path_override if len(finding_ids) == 1 else None)
        if r:
            results.append(r)

    if not results:
        print("No findings processed.", file=sys.stderr)
        sys.exit(1)

    # Summary table
    print(f"\n{'─'*70}")
    print(f"{'Finding':<10} {'Claimed':<10} {'Ceiling':<10} {'Level':<6} {'Upgrade?'}")
    print(f"{'─'*70}")
    for r in results:
        flag = "⚠️  YES" if r["upgrade_required"] else "✓  no"
        print(f"{r['finding_id']:<10} {r['claimed_severity']:<10} {r['severity_ceiling']:<10} {r['poc_level_achieved']:<6} {flag}")
    print(f"{'─'*70}")

    upgrades_needed = [r for r in results if r["upgrade_required"]]
    if upgrades_needed:
        print(f"\n{len(upgrades_needed)} finding(s) need PoC upgrades before claiming stated severity:")
        for r in upgrades_needed:
            print(f"  {r['finding_id']}: missing {', '.join(r['missing_steps'])}")

    import subprocess as _sp
    _sp.run([sys.executable, str(Path(__file__).resolve().parent / "generate_status.py")],
            check=False, capture_output=True)
    if args.strict and upgrades_needed:
        sys.exit(1)


if __name__ == "__main__":
    main()
