# Phase 2 — Rejected / False-Positive Candidates (preserved, not hidden)

These are pipeline-emitted items that do **not** map to a valid public finding. **Zero are
hallucinations** — every one corresponds to real source code. The cost is noise and scope, not
invented bugs. Each is tagged with the validation improvement that should catch it earlier.

## Class A — Attacker-mindset hypotheses leaked into the findings corpus (22, highest cost)
`AM-001, AM-003, AM-004, AM-008, AM-010, AM-011, AM-012, AM-014, AM-015, AM-017, AM-018, AM-019,
AM-020, AM-021` (+ others) — "potential <X> entry point (score N)" surface hints, e.g. AM-001
`sunrise: potential oracle-manipulation entry point (score 5)`.
- **Why plausible:** high attack-surface scores on real entrypoints.
- **Why invalid as findings:** no traced exploit path; they are pre-analysis hints, not findings.
- **Validation fix:** `attacker_mindset` must write to `attack_surface.json` only; schema/
  `validate_agent_output.py` should reject Speculative entries with no path from the corpus. **This
  single fix removes ~45% of the emitted count with zero recall loss.**
- **Source:** agent reasoning (Step 0.25).

## Class B — Out-of-scope but valid (supply chain) (6)
`SC-001` (Critical: `foundry.toml ffi=true` + shell hooks), `SC-002..006` (unpinned deps, CI curl, etc.).
- **Why plausible / why FP here:** real build-security issues, but the contest scope is the Solidity
  contracts — none of the 81 valid findings is supply-chain. Emitting a **Critical** into the same
  corpus distorts severity and precision.
- **Validation fix:** route to `reports/build_security_annex.md`; exclude from precision/recall scoring.
- **Source:** supply_chain_check (Step 1).

## Class C — Real but non-exploitable / over-flagged (4)
`RE-001 (Medium), RE-002 (Low), RE-003 (Low)` — CEI smells on a hookless Bean ERC-20 already covered
by the diamond nonReentrant lock; `AC-003 (Low)` — UnwrapAndSendETH sweeps WETH but holds no resting
protocol funds.
- **Validation fix:** exploitability gate on emit — reentrancy may not exceed Low without a named
  in-scope hooked/reentrant token; "no resting funds" contracts cap at Info.
- **Source:** agent reasoning (reentrancy / access_control).

## Class D — Informational filed as a finding (2)
`AR-003 (Info)` — `addMigratedUnderlying` trusts the amount (FoT pattern), but no FoT token is a
whitelisted unripe underlying → unreachable. `AC-004 (Info)` — actually a *clearing* ("arbitrary-send
sinks non-exploitable"), should not hold a finding ID (and it masked High #279 — Tractor refund pivot).
- **Validation fix:** confidence floor; clearings belong in a `resolved_flags` section, not findings.
- **Source:** agent reasoning (arithmetic / access_control).

## Class E — Unmatched but source-confirmed (likely NOT FPs — verify, don't suppress) (2)
`SG-001 (High)` — `transferPlots` transposes args to `decrementAllowancePods` so the pod allowance is
never consumed (an approved spender can drain pods). Verified in source; clusters near public #505 but
is arguably a **distinct, worse** bug. `EA-002 (Medium)` — SOP swap with `minAmountOut=0, deadline=max`.
- **Verdict:** real code; route to human review. SG-001 is plausibly a genuine win the public board
  taxonomy didn't separately list — counted as ADJACENT to #505, not as an FP.
- **Source:** semantic_guard / economic_attack.

## Net read
Excluding Class A hypotheses and the Class D clearing, the genuinely-wrong exploitable-claim rate is
**≈ 0**. The two highest-ROI precision fixes are: (1) keep attacker-mindset out of the corpus, (2)
annex supply-chain. Together they roughly halve triage load without dropping a single real finding.
