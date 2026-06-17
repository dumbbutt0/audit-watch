# False Positive Rejection

---

## Hard Invalidation Tags

Hard invalidation tags prevent a finding from reaching `submit.jsonl` without explicit human override. They are set by deterministic logic (not AI judgment) and represent structural impossibilities or known-invalid patterns.

| Tag | Set by | Meaning |
|-----|--------|---------|
| `already_guarded` | `defense_mapper.py`, Gate 4 | Modifier provides full coverage; no CFG evasion path |
| `admin_only` | Gate 3 | Only attack path requires trusted admin compromise |
| `impossible_state` | Gate 2 | Required contract state is structurally impossible |
| `non_exploitable` | Gate 1 | Auth blocker present; no realistic trigger path |
| `no_profitability` | Gate 5 | No profit or damage; or attack cost exceeds potential gain |
| `duplicate_finding` | Gate 8 | Same root cause and fix as another finding in the batch |
| `duplicate_pattern` | Step 3.6 / Gate 8 | Matches known-invalid FP pattern at > 0.85 similarity |
| `requires_compromised_key` | Gate 3 | Private key compromise required as a precondition |
| `unverifiable_assumption` | Gate 2 | Core assumption cannot be confirmed |
| `unrealistic_liquidity` | Gate 5 | Attack requires impossible market conditions |

Tags are set at **trust level 5** (historical report). AI-generated hypotheses have trust level 7 and cannot remove them. Human override requires setting `"invalidation_tag_override": {"reviewer": "<name>", "reason": "<specific reason>"}` in the finding record.

---

## FP Pattern Matching

`scripts/fp_pattern_check.py` (Step 3.6) compares each finding against rejection rules accumulated from past audits.

### Similarity Score Calculation

```
similarity = vuln_type_match (0.3) + agent_match (0.2) + keyword_overlap (0.0–0.5)
```

- `vuln_type_match`: 0.3 if finding's vuln_type matches the rule's vuln_type
- `agent_match`: 0.2 if finding's agent matches the rule's agent
- `keyword_overlap`: word overlap between finding description and rule's rejection keywords (capped at 0.5)

**Thresholds:**
- `similarity > 0.85` AND `rule.confidence > 0.8` → `recommended_action: reject`
- `similarity > 0.6` → `recommended_action: warn` (review before submitting)
- `similarity <= 0.6` → `recommended_action: proceed`

### Rejection Rule Format

```json
{
  "rule_id": "FP-RULE-007",
  "vuln_type": "reentrancy",
  "agent": "reentrancy",
  "rejection_keywords": ["nonReentrant", "ReentrancyGuard", "inherited", "all functions"],
  "rejection_reason": "nonReentrant applied via ReentrancyGuard inheritance covers all external functions",
  "confidence": 0.92,
  "source_finding_id": "GL-001",
  "contest": "gearbox-2026-05",
  "created_at": "2026-05-21T10:00:00Z"
}
```

Rules live in two places:
- `audits/<id>/data/fp_autopsies/rejection_rules.jsonl` — per-audit rules
- `data/fp_autopsies/rejection_rules.jsonl` — project-level (accumulated across all audits)

`fp_pattern_check.py` reads both and deduplicates by `rule_id`. Both files are written when `record_fp_autopsy.py` runs.

---

## Recording FP Autopsies

After a finding is judged invalid (by a contest judge or by your own review), record an autopsy to prevent the same false positive in future audits:

```bash
python scripts/record_fp_autopsy.py \
  --finding-id RE-001 \
  --judge-outcome rejected \
  --rejection-reason "nonReentrant applied via ReentrancyGuard inheritance"
```

This writes:
- A rejection rule to `data/fp_autopsies/rejection_rules.jsonl` (both per-audit and project-level)
- An autopsy record to `data/fp_autopsies/<ID>_autopsy.json`

The rule becomes active in Step 3.6 on the next audit run.

---

## Common FP Patterns

### 1. already_guarded — nonReentrant / inherited modifier

The most common false positive. Agent finds a function that looks vulnerable to reentrancy but does not check whether `nonReentrant` is inherited from `ReentrancyGuard` in a parent contract.

**Detection:** `defense_mapper.py` resolves inherited modifiers before any agent runs. Findings tagged `already_guarded` by the defense mapper are hard-rejected before the triage API call.

**Autopsy trigger:** Judge rejects with "nonReentrant applied via inheritance".

---

### 2. admin_only — trusted admin assumed to be attacker

Agent identifies a function that only admin can call and claims the admin could misuse it. When the audit scope says "admin is trusted", this is not a valid finding.

**Detection:** Gate 3 checks for admin attacker type + `realistic=False` + no untrusted-admin argument.

**Legitimate exception:** When the finding argues admin is untrusted (e.g., "admin is a multisig whose signers can be bribed"), include the phrase "untrusted admin" or "admin is untrusted" in the description.

---

### 3. mocked-only impact — PoC only proves impact against mock contracts

PoC uses a mock ERC-20 that returns incorrect values to demonstrate loss, but the real protocol would only interact with tokens on a whitelist that all behave correctly.

**Detection:** PoC completeness gate flags this when PoC level is high but assertions are against mock balances.

---

### 4. no protocol consumer — corrupted state never read

State can be set incorrectly but no trusted protocol function ever reads it to make a security-relevant decision. ICE marks this as `consumers = []` and routes to `ice_manual_review.jsonl`.

---

### 5. duplicate root cause — same missing check as another finding

Two findings in the same batch both identify the same missing guard. Only the one that describes the most valuable attack path should be submitted; the other is a duplicate.

**Detection:** Gate 8 checks `duplicate_risk` model. `duplicate_risk_agent.md` identifies same root cause + same fix.

---

### 6. unrealistic attacker model — requires victim to grant allowance first

ERC-20 `transferFrom` requires the victim to have previously called `approve`. If the protocol does not standard-flow force users to approve the contract, this is not a permissionless attack.

**Detection:** Exploitability modeler marks `allowance_blocker: true`. Gate 1 fails if no permissionless trigger path.

---

## Supply Chain Note

Findings from `agents/supply_chain_check.md` (SC- prefix) may flag `ffi = true` in `foundry.toml` as a supply chain concern. This is a legitimate security concern for CI/CD environments. However, for most smart contract bounty programs, supply chain vulnerabilities are explicitly out of scope unless the program specifically includes "build infrastructure" or "CI/CD pipelines" in scope.

Check the bounty scope definition before submitting SC- findings. They typically route to `downgraded.jsonl` unless the program explicitly includes build chain in scope.
