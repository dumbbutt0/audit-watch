/* Mock dashboard state — mirrors /api/state response shape.
   Used when the static HTML is opened without a backend (file://) or when
   /api/state is unreachable. The four K2 findings match the verification
   checklist exactly. */

window.MOCK_STATE = {
  timestamp: new Date().toISOString(),
  pipeline: {
    stage_1_static: {
      done: true,
      contract_path: "src/K2Lending.sol",
      compiler: "0.8.23",
      function_count: 47,
      detail: "src/K2Lending.sol · solc 0.8.23 · 47 fns"
    },
    stage_2_agents: {
      done: true,
      agents_run: ["reentrancy", "arithmetic", "logic", "access_control", "oracle"],
      findings_per_agent: { reentrancy: 1, arithmetic: 1, logic: 2 },
      finding_count: 4,
      total_raw: 4
    },
    stage_3_report: {
      done: true,
      compound_risk_count: 1,
      detail: "4 findings · 1 compound"
    },
    stage_4_triage: {
      done: true,
      submit: 3,
      poc_required: 1,
      downgraded: 0,
      rejected: 0
    },
    stage_5_specialist: {
      done: true,
      exploitability_done: 4,
      judge_done: 4,
      severity_done: 4,
      total_findings: 4
    },
    stage_6_poc: {
      done: true,
      proved: 4,
      failed: 0,
      pending: 0,
      level_dist: { L3C: 3, L3B: 1, L3A: 0, L2: 0 }
    },
    stage_7_checklist: {
      done: true,
      passed: 0,
      ready: 0,
      conditional: 4,
      failed: 0,
      blocked: 0
    },
    stage_8_gate: {
      done: true,
      high_supported: 3,
      ceiling_downgraded: 1,
      downgraded_to_medium: 1,
      upgrade_required: 0
    }
  },
  kb: {
    total_findings: 4827,
    last_run: new Date(Date.now() - 4 * 60 * 1000).toISOString(),
    cycles: 142,
    continuous_running: true,
    scraper_log_tail: [
      "2026-05-12 14:23:01 [INFO] cycle 142 complete — 12 new findings indexed",
      "2026-05-12 14:23:01 [INFO] embedding batch size=12 · 1.42s",
      "2026-05-12 14:22:58 [INFO] fetched 3 reports from code4rena · 9 from sherlock",
      "2026-05-12 14:22:55 [INFO] starting cycle 142 (continuous mode)",
      "2026-05-12 14:18:33 [INFO] cycle 141 complete — 0 new findings"
    ]
  },
  severity_distribution: { Critical: 0, High: 3, Medium: 1, Low: 0, Informational: 0 },
  triage_funnel: { total_raw: 4, submit: 3, poc_required: 1, downgraded: 0, rejected: 0 },
  findings: [
    {
      id: "LG-005",
      title: "Liquidation bonus drained via flash-loan triggered partial-liquidation loop",
      agent: "logic",
      raw_severity: "High",
      triage_status: "submit",
      triage_score: 31,
      recommended_severity: "High",
      calibrated_severity: "High",
      severity_ceiling: "High",
      exploitability_score: 5,
      duplicate_risk: "low",
      duplicate_probability: 0.08,
      poc_status: "proved",
      poc_level: "L3C",
      poc_runtime_level: 3,
      upgrade_required: false,
      checklist_overall: "conditional",
      predicted_outcome: "accepted",
      predicted_severity: "High",
      final_action: "submit",
      compound: true,
      submission_ready: true
    },
    {
      id: "AR-001",
      title: "Interest accrual rounding favours borrower; cumulative drift exceeds 0.5% per epoch",
      agent: "arithmetic",
      raw_severity: "Medium",
      triage_status: "submit",
      triage_score: 27,
      recommended_severity: "High",
      calibrated_severity: "High",
      severity_ceiling: "High",
      exploitability_score: 4,
      duplicate_risk: "low",
      duplicate_probability: 0.12,
      poc_status: "proved",
      poc_level: "L3C",
      poc_runtime_level: 3,
      upgrade_required: false,
      checklist_overall: "conditional",
      predicted_outcome: "accepted",
      predicted_severity: "High",
      final_action: "submit",
      compound: false,
      submission_ready: true
    },
    {
      id: "LG-001",
      title: "Borrow cap bypass when collateral asset is added mid-block before oracle sync",
      agent: "logic",
      raw_severity: "Medium",
      triage_status: "poc_required",
      triage_score: 22,
      recommended_severity: "Medium",
      calibrated_severity: "Medium",
      severity_ceiling: "Medium",
      exploitability_score: 3,
      duplicate_risk: "medium",
      duplicate_probability: 0.34,
      poc_status: "proved",
      poc_level: "L3B",
      poc_runtime_level: 3,
      upgrade_required: false,
      checklist_overall: "conditional",
      predicted_outcome: "downgraded",
      predicted_severity: "Medium",
      final_action: "revise",
      compound: false,
      submission_ready: false
    },
    {
      id: "RE-002",
      title: "Reentrancy in repay() via ERC-777 hook permits double-credit on debt token burn",
      agent: "reentrancy",
      raw_severity: "High",
      triage_status: "submit",
      triage_score: 33,
      recommended_severity: "High",
      calibrated_severity: "High",
      severity_ceiling: "High",
      exploitability_score: 5,
      duplicate_risk: "low",
      duplicate_probability: 0.05,
      poc_status: "proved",
      poc_level: "L3C",
      poc_runtime_level: 3,
      upgrade_required: false,
      checklist_overall: "conditional",
      predicted_outcome: "accepted",
      predicted_severity: "High",
      final_action: "submit",
      compound: true,
      submission_ready: true
    }
  ],
  poc_queue: [
    { finding_id: "LG-001", poc_priority: "P2", goal: "Demonstrate borrow-cap bypass within single block", status: "completed", poc_level: "L3B" }
  ],
  submissions: ["K2-LG-005-submission.md", "K2-AR-001-submission.md", "K2-RE-002-submission.md"],
  compound_risks: [
    "LG-005 + RE-002 share the same liquidation entrypoint; if reentrancy guard is patched without addressing the partial-liquidation loop, LG-005 remains exploitable in isolation."
  ],
  // PoC validation / engagement readiness (offline preview only; live state comes from /api/state).
  // Mirrors output/dashboard/poc_validation_status.json — illustrative buckets across the main states.
  poc_validation: {
    generated_at: "2026-05-31T00:00:00+00:00",
    mode: "engagement",
    fix_list_path: "output/poc_validation/fix_list.md",
    operator_worklist_path: "output/poc_validation/operator_worklist.md",
    operator_worklist_count: 4,
    next_batch_actions: [["downgrade_severity", 1], ["write_missing_poc", 1], ["add_negative_control", 1]],
    summary: {
      total_findings_needing_poc: 5, submission_ready: 1, engagement_ready: 2,
      missing_poc: 1, missing_collected_log: 0, invalid_or_setup_only: 1,
      severity_overclaim: 1, high_critical_blocked: 2, medium_blocked: 1
    },
    buckets: {
      submission_ready: ["LG-005"], engagement_ready_but_not_submission_ready: [],
      needs_better_assertions: [], needs_negative_control: ["RE-002"], needs_fork_context: [],
      missing_poc: ["AR-001"], missing_collected_log: [], invalid_poc: [], setup_only: ["DS-003"],
      severity_overclaim: ["LG-001"], duplicate_proof: [], inconclusive: [], eval_only_not_required: []
    },
    top_next_actions: [["write_missing_poc", 1], ["downgrade_severity", 1], ["remove_invalid_setup", 1]],
    top_fix_items: [
      { finding_id: "LG-001", severity: "High", recommended_next_action: "downgrade_severity",
        shortest_next_step: "Lower the claimed severity to the demonstrated impact, or strengthen the PoC to support it." },
      { finding_id: "AR-001", severity: "High", recommended_next_action: "write_missing_poc",
        shortest_next_step: "Write a Foundry PoC that calls the real entrypoint as an unprivileged EOA and asserts the impact." },
      { finding_id: "RE-002", severity: "Medium", recommended_next_action: "add_negative_control",
        shortest_next_step: "Add a negative control: the unauthorized/patched path must behave differently." }
    ],
    submission_blockers: [
      { finding_id: "LG-001", severity: "High", reason: "demonstrated impact below claimed severity (supported: Medium)" },
      { finding_id: "AR-001", severity: "High", reason: "no PoC test exists yet" },
      { finding_id: "DS-003", severity: "High", reason: "the 'attack' is performed by test setup, not the real path" }
    ],
    closest_to_ready: [
      { finding_id: "RE-002", severity: "Medium", proof_score: 65, bucket: "needs_negative_control" }
    ],
    blocking_items: [
      { finding_id: "LG-001", severity: "High", reason: "demonstrated impact below claimed severity (supported: Medium)" },
      { finding_id: "AR-001", severity: "High", reason: "no PoC test exists yet" }
    ],
    stale_or_missing_inputs: []
  }
};

/* Per-finding detail payloads. Keyed by finding ID. Returned by
   /api/finding/{id} — same shape. */
window.MOCK_DETAIL = {
  "LG-005": {
    finding: {
      id: "LG-005",
      title: "Liquidation bonus drained via flash-loan triggered partial-liquidation loop",
      agent: "logic",
      severity: "High",
      description: "The liquidation engine grants a fixed 8% bonus on every partial-liquidation call without any anti-batching guard. An attacker can flash-loan collateral, force a vault marginally underwater, then issue ~30 consecutive partial liquidations of 0.5% of the position. Each call clears its own slippage tolerance and pays the bonus, but the aggregate health-factor recalculation is deferred to the end of the transaction — so each loop iteration sees the same underwater state. Net effect: the attacker drains 30 × 8% × 0.5% = 1.2% of the vault per block, repeated until the position is fully depleted, while liquidator gas costs remain below the bonus paid out.",
      file: "src/liquidation/LiquidationEngine.sol",
      function: "partialLiquidate(address,uint256)",
      lines: "184–231",
      code: "function partialLiquidate(address vault, uint256 repayAmount)\n    external\n    nonReentrant\n    returns (uint256 collateralOut)\n{\n    Position storage p = positions[vault];\n    require(p.healthFactor < 1e18, \"NOT_UNDERWATER\");\n    require(repayAmount <= p.debt / 200, \"ABOVE_PARTIAL_CAP\");  // 0.5% cap\n\n    collateralOut = _collateralForRepay(repayAmount);\n    collateralOut += collateralOut * BONUS_BPS / 10_000;       // 8% bonus\n\n    p.debt        -= repayAmount;\n    p.collateral  -= collateralOut;\n    // ⚠ healthFactor recomputed only on next external call\n\n    debtAsset.burn(msg.sender, repayAmount);\n    collateralAsset.transfer(msg.sender, collateralOut);\n}",
      attack_steps: [
        "Flash-loan 1,200 collateral asset from Balancer.",
        "Deposit into target vault to mint debt position just barely above threshold.",
        "Wait for next block (or use oracle freshness window) to push vault into liquidation range.",
        "Call partialLiquidate() 30 times in a single transaction, each at the 0.5% cap.",
        "Each call pays the 8% bonus against the same stale health factor.",
        "Withdraw drained collateral, repay flash loan, retain ~1.2% of vault value × 30 iterations."
      ],
      recommendation: "Recompute healthFactor inside partialLiquidate() before applying the bonus, OR collapse all partial liquidations within a transaction into a single bonus payout, OR cap aggregate liquidation per vault per block to 5%."
    },
    triage: {
      finding_id: "LG-005",
      triage_status: "submit",
      recommended_severity: "High",
      score: { total: 31, max: 35 },
      attacker_model: { realistic: true }
    },
    exploitability: { exploitability_score: 5, attacker: { type: "anyone_with_capital" }, profit_or_damage: { type: "direct_loss" } },
    duplicates: { duplicate_risk: "low", probability: 0.08, status: "novel" },
    severity: { calibrated_severity: "High", triage_severity: "High", calibration_source: "judge_simulation+poc_runtime" },
    runtime_poc: {
      finding_id: "LG-005",
      runtime_level: 3,
      poc_level: "L3C",
      status: "proved",
      run_command: "forge test --match-test test_LG005_drainViaPartialLiquidationLoop -vvv --fork-url $MAINNET_RPC"
    },
    judge: {
      predicted_outcome: "accepted",
      predicted_severity: "High",
      confidence: 0.86,
      strongest_objection: "Bonus rate of 8% may be intended liquidator incentive; argue why aggregation crosses into adversarial use.",
      likely_judge_questions: [
        "Is the 0.5% partial cap a known design choice documented elsewhere?",
        "Does the protocol's risk doc state a maximum per-block liquidation rate?",
        "What real loss to the vault depositors does this enable in the observed parameter set?"
      ],
      final_action: "submit"
    },
    checklist: {
      finding_id: "LG-005",
      overall: "conditional",
      checklist: {
        q1_level2_proved: { symbol: "✅", detail: "L2 simulation in unit test reproduces single-iteration bonus payout." },
        q2_level3_proved: { symbol: "✅", detail: "L3C fork-test drains 36% of vault value in 30 iterations within one block." },
        q3_direct_loss: { symbol: "✅", detail: "Direct collateral loss to depositors; quantified as bonus payout × iterations." },
        q4_permissionless: { symbol: "✅", detail: "No special role required; any address can call partialLiquidate()." },
        q5_victim_realistic: { symbol: "⚠️", detail: "Requires a vault to be marginally underwater — common during volatility but not constant." },
        q6_likely_duplicate: { symbol: "✅", detail: "KB search returned 0 high-similarity matches across 4,827 indexed findings." },
        q7_one_sentence_impact: { symbol: "❓", detail: "Submission draft uses 2 sentences; reviewer suggests tightening to one." }
      }
    },
    completeness: {
      finding_id: "LG-005",
      poc_level_achieved: "L3C",
      severity_ceiling: "High",
      upgrade_required: false,
      poc_supports_claimed_severity: true,
      found_steps: [
        "Setup: mainnet fork at recent block",
        "Construct flash-loan call into Balancer vault",
        "Push target vault into liquidation range via oracle nudge",
        "Loop 30× partialLiquidate calls",
        "Assert drained value ≥ claimed amount",
        "Verify health factor at end of tx"
      ],
      missing_steps: []
    }
  },

  "AR-001": {
    finding: {
      id: "AR-001",
      title: "Interest accrual rounding favours borrower; cumulative drift exceeds 0.5% per epoch",
      agent: "arithmetic",
      severity: "Medium",
      description: "The interest index update in _accrueInterest() multiplies the borrow rate per second by elapsed seconds before dividing by the ray-precision constant, but the truncating integer division rounds in the borrower's favour. Under typical mainnet block cadences this drift compounds at roughly 0.52% per 30-day epoch in stress-test parameters — sufficient to reclassify this as High under the protocol's own severity matrix once vault TVL exceeds $10M.",
      file: "src/interest/InterestRateModel.sol",
      function: "_accrueInterest()",
      lines: "92–118",
      code: "function _accrueInterest() internal {\n    uint256 dt = block.timestamp - lastAccrual;\n    if (dt == 0) return;\n\n    uint256 ratePerSec = _borrowRatePerSec();\n    // ⚠ truncating division — drift accumulates downward\n    uint256 factor    = (ratePerSec * dt) / RAY;\n\n    borrowIndex      += borrowIndex * factor / RAY;\n    lastAccrual       = block.timestamp;\n}",
      attack_steps: [
        "Open a large borrow position at epoch start.",
        "Wait for the protocol's natural accrual cycle; do not interact for 30 days.",
        "Repay debt at epoch end — note that the accrued interest is ~0.52% lower than the mathematically correct amount.",
        "Repeat across positions and epochs; net protocol revenue loss scales linearly with TVL."
      ],
      recommendation: "Use a fixed-point accumulator with WAD precision and apply round-half-up via OZ MathUpgradeable, OR pre-multiply by RAY before the division and apply rounding mode explicitly."
    },
    triage: { finding_id: "AR-001", triage_status: "submit", recommended_severity: "High", score: { total: 27, max: 35 } },
    exploitability: { exploitability_score: 4, attacker: { type: "any_borrower" }, profit_or_damage: { type: "protocol_revenue_loss" } },
    duplicates: { duplicate_risk: "low", probability: 0.12, status: "novel" },
    severity: { calibrated_severity: "High", triage_severity: "High", calibration_source: "tvl_threshold_uplift+judge" },
    runtime_poc: { finding_id: "AR-001", runtime_level: 3, poc_level: "L3C", status: "proved", run_command: "forge test --match-test test_AR001_interestDrift -vvv" },
    judge: {
      predicted_outcome: "accepted", predicted_severity: "High", confidence: 0.79,
      strongest_objection: "Rounding direction may be considered acceptable precision loss below per-tx threshold; emphasise the TVL-scaled total.",
      likely_judge_questions: [
        "What is the per-transaction drift, and at what TVL does it cross the protocol's quantitative severity threshold?",
        "Are other accrual functions in the codebase affected similarly?"
      ],
      final_action: "submit"
    },
    checklist: {
      finding_id: "AR-001", overall: "conditional",
      checklist: {
        q1_level2_proved: { symbol: "✅", detail: "Symbolic check on _accrueInterest confirms rounding direction." },
        q2_level3_proved: { symbol: "✅", detail: "Foundry test demonstrates 0.52% drift over 30-day simulation." },
        q3_direct_loss: { symbol: "✅", detail: "Protocol revenue loss; quantified per epoch." },
        q4_permissionless: { symbol: "✅", detail: "Any borrower triggers it passively." },
        q5_victim_realistic: { symbol: "✅", detail: "Protocol treasury is the victim; passive accumulation." },
        q6_likely_duplicate: { symbol: "✅", detail: "0 high-similarity matches in KB." },
        q7_one_sentence_impact: { symbol: "❓", detail: "Impact statement needs sharper TVL-scaled framing." }
      }
    },
    completeness: {
      finding_id: "AR-001", poc_level_achieved: "L3C", severity_ceiling: "High",
      upgrade_required: false, poc_supports_claimed_severity: true,
      found_steps: ["Symbolic precondition", "30-day fork simulation", "Drift quantification", "Severity-matrix mapping"],
      missing_steps: []
    }
  },

  "LG-001": {
    finding: {
      id: "LG-001",
      title: "Borrow cap bypass when collateral asset is added mid-block before oracle sync",
      agent: "logic",
      severity: "Medium",
      description: "When the asset listing flow adds a new collateral asset, the borrow cap and oracle feed are configured in separate transactions. Inside the small window where the asset is listed but the oracle has not yet returned a non-zero price, the cap check trivially passes and arbitrary borrows are permitted against a notional value of zero. The window is short, but reproducible on Anvil with a deliberately delayed price-feed callback.",
      file: "src/admin/AssetRegistry.sol",
      function: "registerAsset(address)",
      lines: "44–71",
      code: "function registerAsset(address asset, uint256 cap) external onlyAdmin {\n    require(!isListed[asset], \"ALREADY_LISTED\");\n    isListed[asset] = true;\n    borrowCap[asset] = cap;\n    // ⚠ oracle wiring happens in a follow-up tx — see ORACLE.bindFeed()\n}",
      attack_steps: [
        "Front-run the oracle.bindFeed() tx that follows registerAsset().",
        "Deposit the newly-listed asset; cap check uses notional value of 0.",
        "Borrow against the cap; protocol records non-zero debt against zero collateral value.",
        "Wait for oracle to attach; position is now severely undercollateralised and resists liquidation due to cap math."
      ],
      recommendation: "Make registerAsset() and oracle binding atomic — require both in a single multi-call, or refuse all borrows against assets whose oracle returns zero."
    },
    triage: { finding_id: "LG-001", triage_status: "poc_required", recommended_severity: "Medium", score: { total: 22, max: 35 } },
    exploitability: { exploitability_score: 3, attacker: { type: "mev_searcher" }, profit_or_damage: { type: "direct_loss" } },
    duplicates: { duplicate_risk: "medium", probability: 0.34, status: "needs_review" },
    severity: { calibrated_severity: "Medium", triage_severity: "Medium", calibration_source: "ops_dependency_downgrade" },
    runtime_poc: { finding_id: "LG-001", runtime_level: 3, poc_level: "L3B", status: "proved", run_command: "forge test --match-test test_LG001_capBypassWindow -vvv" },
    judge: {
      predicted_outcome: "downgraded", predicted_severity: "Medium", confidence: 0.71,
      strongest_objection: "Requires admin-controlled deployment ordering; likely mitigated by ops runbook rather than code.",
      likely_judge_questions: [
        "Is there a deployment script that already enforces atomicity?",
        "Can a non-admin trigger the window, or only by racing admin txs?"
      ],
      final_action: "revise"
    },
    checklist: {
      finding_id: "LG-001", overall: "conditional",
      checklist: {
        q1_level2_proved: { symbol: "✅", detail: "L2 simulation shows borrow at zero notional value." },
        q2_level3_proved: { symbol: "✅", detail: "L3B Foundry test reproduces the race window with delayed oracle." },
        q3_direct_loss: { symbol: "✅", detail: "Position is uncollateralised once oracle attaches." },
        q4_permissionless: { symbol: "⚠️", detail: "Requires racing an admin tx; permissionless but ops-dependent." },
        q5_victim_realistic: { symbol: "⚠️", detail: "Real only during asset onboarding events." },
        q6_likely_duplicate: { symbol: "⚠️", detail: "KB returned 2 medium-similarity matches; reviewer flagged for manual diff." },
        q7_one_sentence_impact: { symbol: "✅", detail: "\"Front-running oracle binding permits zero-collateral borrows.\"" }
      }
    },
    completeness: {
      finding_id: "LG-001", poc_level_achieved: "L3B", severity_ceiling: "Medium",
      upgrade_required: false, poc_supports_claimed_severity: true,
      found_steps: ["Anvil setup with delayed oracle", "registerAsset() racing", "Front-run borrow", "Assert zero-notional borrow succeeds"],
      missing_steps: ["Mainnet-equivalent timing analysis (would lift to L3C)"]
    }
  },

  "RE-002": {
    finding: {
      id: "RE-002",
      title: "Reentrancy in repay() via ERC-777 hook permits double-credit on debt token burn",
      agent: "reentrancy",
      severity: "High",
      description: "repay() transfers the repayment asset to the protocol BEFORE decrementing the borrower's recorded debt. When the repayment asset is an ERC-777, the receiver hook fires mid-execution, allowing the borrower to re-enter repay() with the same nominal value and trigger a second debt-burn against the still-stale debt mapping. The nonReentrant guard is in place on borrow() and withdraw() but is conspicuously absent on repay().",
      file: "src/lending/RepayHandler.sol",
      function: "repay(address,uint256)",
      lines: "61–95",
      code: "function repay(address asset, uint256 amount) external returns (uint256 burned) {\n    // ⚠ no nonReentrant\n    Position storage p = positions[msg.sender];\n\n    IERC20(asset).transferFrom(msg.sender, address(this), amount);\n    //                       ⤷ ERC-777 receiver hook re-enters here\n\n    burned = amount;\n    p.debt -= burned;\n    debtToken.burn(msg.sender, burned);\n    emit Repay(msg.sender, asset, burned);\n}",
      attack_steps: [
        "Use an ERC-777 token as the repayment asset (protocol whitelists at least one).",
        "Borrow 100 tokens; debt mapping = 100.",
        "Call repay(asset, 100). Inside the ERC-777 tokensReceived hook, re-enter repay(asset, 100).",
        "Inner call reads debt = 100 (still stale) and burns 100 of debt token.",
        "Outer call returns and burns another 100; debt mapping underflows or is set to 0 on a 200-debt position.",
        "Position now has full collateral with zero debt — withdraw all collateral and exit."
      ],
      recommendation: "Apply nonReentrant to repay() — and to all external state-mutating functions in the lending suite — and follow Checks-Effects-Interactions: update p.debt before transferring. Consider blacklisting ERC-777-style hook tokens outright."
    },
    triage: { finding_id: "RE-002", triage_status: "submit", recommended_severity: "High", score: { total: 33, max: 35 } },
    exploitability: { exploitability_score: 5, attacker: { type: "any_borrower" }, profit_or_damage: { type: "full_collateral_drain" } },
    duplicates: { duplicate_risk: "low", probability: 0.05, status: "novel" },
    severity: { calibrated_severity: "High", triage_severity: "High", calibration_source: "judge_simulation" },
    runtime_poc: { finding_id: "RE-002", runtime_level: 3, poc_level: "L3C", status: "proved", run_command: "forge test --match-test test_RE002_repayReentrancy -vvv" },
    judge: {
      predicted_outcome: "accepted", predicted_severity: "High", confidence: 0.91,
      strongest_objection: "Are any of the listed repayment assets actually ERC-777? If the protocol only ever uses ERC-20 in practice, severity may be argued down.",
      likely_judge_questions: [
        "Show the listed asset set and confirm at least one supports a hook.",
        "Demonstrate the attack reduces a real position's debt to zero on the fork."
      ],
      final_action: "submit"
    },
    checklist: {
      finding_id: "RE-002", overall: "conditional",
      checklist: {
        q1_level2_proved: { symbol: "✅", detail: "Static read of repay() confirms missing nonReentrant and CEI inversion." },
        q2_level3_proved: { symbol: "✅", detail: "L3C fork test drains a 100-token debt position to zero." },
        q3_direct_loss: { symbol: "✅", detail: "Borrower withdraws full collateral without repaying full debt." },
        q4_permissionless: { symbol: "✅", detail: "Any borrower with an ERC-777 asset triggers it." },
        q5_victim_realistic: { symbol: "⚠️", detail: "Depends on at least one ERC-777 being whitelisted; protocol currently lists one." },
        q6_likely_duplicate: { symbol: "✅", detail: "0 high-similarity matches; classic reentrancy pattern but call site is distinct." },
        q7_one_sentence_impact: { symbol: "❓", detail: "Current draft is dense; tighten to one sentence." }
      }
    },
    completeness: {
      finding_id: "RE-002", poc_level_achieved: "L3C", severity_ceiling: "High",
      upgrade_required: false, poc_supports_claimed_severity: true,
      found_steps: [
        "ERC-777 mock with tokensReceived hook",
        "Fork mainnet at recent block",
        "Open 100-token position",
        "Execute reentrant repay",
        "Assert debt == 0 and full collateral withdrawable"
      ],
      missing_steps: []
    }
  }
};
