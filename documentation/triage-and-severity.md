# Triage and Severity

---

## Severity Scale

| Level | Meaning | Typical Immunefi bounty range |
|-------|---------|------------------------------|
| Critical | Direct loss of funds with no preconditions; or complete protocol takeover | Maximum bounty |
| High | Loss of funds or broken core invariant under realistic conditions; or permanent DoS of a safety mechanism | High tier |
| Medium | Incorrect behavior, significant griefing, temporary DoS, or loss requiring multiple steps | Medium tier |
| Low | Best-practice violations, minor logic issues, bounded griefing | Low tier |
| Informational | Gas optimizations, code quality, documentation | No reward |

**Critical requires:** A direct asset loss path that does not require trusted admin, victim allowances not standard to the protocol, or oracle/market conditions that cannot exist in production.

**High requires:** A confirmed consumer path (via ICE) that performs a real protocol action on the corrupted state. The PoC must call the consumer, not just show the corrupted state.

---

## The 7-Component Triage Score

The triage agent evaluates each finding on 7 dimensions (0–5 each, 35 maximum).

| Component | What it measures | Score 5 | Score 0 |
|-----------|-----------------|---------|---------|
| `attacker_control` | How much the attacker controls the trigger | Fully permissionless, any address | Requires owner key |
| `sensitive_sink` | How valuable the target is | Direct fund theft | Gas cost only |
| `missing_check_clarity` | How clear the missing defense is | Obvious, one-line fix | Speculative design issue |
| `impact_realism` | How realistic the victim/market conditions are | Normal protocol use | Impossible market state |
| `poc_feasibility` | How feasible a PoC is | Already proved at Level 3 | Requires mainnet fork + market timing |
| `scope_safety` | How confident we are it's in scope | Core contract, explicitly in scope | Gray area or test file |
| `duplicate_risk` | Inverse duplicate risk (5 = unique, 0 = exact known duplicate) | Novel pattern | Exact root cause match |

**Bucket thresholds:**
- **Submit** (>= 28): Strong finding, submit directly
- **PoC Required** (22–27): Good candidate, needs proof before submission
- **Downgraded** (16–21): Submit at lower severity or drop
- **Rejected** (< 16): Not worth submitting

---

## The 8 Pre-Submission Gates

Gates run in `scripts/pre_submission_gate.py` before any triage API call. A FAIL assigns a hard invalidation tag and bypasses the Claude triage call entirely.

| Gate | Name | FAIL condition | Tag applied |
|------|------|----------------|-------------|
| 1 | Reachability | `blocked_by_auth=True` AND `can_trigger=False` in exploitability model | `non_exploitable` |
| 2 | State Realism | Impossible-state keywords in description (e.g., "100% of supply", "oracle down", "zero liquidity") | `impossible_state` |
| 3 | Privilege | Admin attacker type AND `realistic=False` AND no untrusted-admin argument in description | `admin_only` |
| 4 | Defense | `coverage == "full"` in defense_map AND `evasion_path == ""` | `already_guarded` |
| 5 | Economics | `profit_or_damage.type == "none"` AND bounded = true, OR attack cost > estimated profit | `no_profitability` |
| 6 | PoC | Critical or High severity AND `needs_poc=True` AND `runtime_poc_level == 0` | — (routes to poc_required) |
| 7 | Severity | Judge simulation `predicted_outcome == "rejected"` with confidence >= 4 | — (routes to human review) |
| 8 | Duplicate | `duplicate_risk == "high"` in duplicate risk model OR FP pattern similarity > 0.85 | `duplicate_finding` / `duplicate_pattern` |

**WARN behavior:** 3 or more WARNs (not FAILs) routes the finding to `human_review_queue.jsonl` rather than automatic rejection.

---

## Invalidation Tags

| Tag | Meaning | How to override |
|-----|---------|-----------------|
| `already_guarded` | Existing modifier fully covers the attack path with no evasion | Set `invalidation_tag_override` with reviewer name and reason |
| `admin_only` | Only attack path requires trusted admin | Add untrusted-admin argument to finding description; human override |
| `impossible_state` | Required contract state cannot exist in production | Remove impossible-state keywords; provide evidence state is reachable |
| `non_exploitable` | Auth blocker present, no realistic trigger path identified | Show permissionless trigger path; human override |
| `no_profitability` | No profit or damage, or attack cost exceeds gain | Identify asset at risk; show damage path |
| `duplicate_finding` | Same root cause and fix as another finding in the batch | Differentiate root cause or fix; document unique angle |
| `duplicate_pattern` | Matches known-invalid FP pattern at > 0.85 similarity | Human override with specific reason this instance is different |
| `requires_compromised_key` | Private key compromise required | Show permissionless alternative path |
| `unverifiable_assumption` | Core assumption cannot be verified | Remove assumption or provide on-chain evidence |
| `unrealistic_liquidity` | Attack requires market conditions that cannot exist | Document real historical liquidity that meets condition |

Human override requires setting `"invalidation_tag_override": {"reviewer": "<name>", "reason": "<specific reason>"}` in the finding record. AI-generated hypotheses cannot remove invalidation tags.

---

## Severity Ceiling vs. Claimed Severity

Claimed severity is what the specialist agent asserts. Severity ceiling is the maximum severity the evidence can support at the current PoC level.

The final calibrated severity is `min(claimed_severity, severity_ceiling)`.

Ceiling is constrained by:
- **ICE**: `severity_ceiling` in the ice block based on confirmed consumer and PoC level
- **PoC completeness gate**: L3A/L3B/L3C ceiling per bug class
- **Severity calibrator rules**: admin-only → Medium, harness-only PoC → no High claim, etc.

See [poc-development.md](poc-development.md) for the full severity-ceiling table by PoC level and bug class.

---

## Multi-Pass Confirmation

Implements the Jason Hadex principle: LLM reasoning is non-deterministic. A finding that passes once but fails four times is not ready to submit.

| Severity | Number of passes | Confirmation threshold |
|----------|-----------------|----------------------|
| High | 3 | 0.6 (must pass at least 2/3 times) |
| Critical | 5 | 0.6 (must pass at least 3/5 times) |

`confirmation_score = passes_that_confirmed / total_passes`

Findings with `confirmation_score < 0.6` have `human_review_required = true` set automatically. They are NOT removed from the pipeline — they route to `human_review_queue.jsonl` at Step 4.5.

**Configuration:** `config/agent_policy.json` `multi_pass` section. `skip_in_fast_mode: true` (fast mode skips this step entirely).

---

## Human Review Routing (Step 4.5)

A finding is routed to `human_review_queue.jsonl` if **2 or more** of these criteria trigger:

| # | Criterion | Threshold |
|---|-----------|-----------|
| 1 | KB similarity below threshold | < 0.4 (novel pattern) |
| 2 | Confirmation score below threshold | < 0.6 |
| 3 | Trace depth | >= 3 hops cross-contract |
| 4 | Compound claim with no COMP-* pattern match | — |
| 5 | Category | `cross_chain` or `upgrade_storage` |
| 6 | Critical claim without Level 2+ PoC | — |
| 7 | BSA finding | Behavioral divergence needs human intent judgment |
| 8 | Already flagged by multi_pass_confirm.py | `human_review_required = true` |

**Do not submit human_review_queue findings based on AI-generated PoC alone.** Personally inspect the exploit path before submission.
