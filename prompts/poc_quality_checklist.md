# PoC Quality Checklist

After every finding reaches Level 3, answer all 8 questions before submitting.
A finding that cannot answer ✅ or ⚠️ on questions 1–4 should not be submitted as High/Critical.

---

## The 8 Questions

### Q1 — L1 Entry: Is the entry point permissionless?

**Passes when:** `test_L1_entryReachable()` passes AND the test uses only an EOA with no privileged keys or pre-existing allowances.

L1 proves the attacker transaction is crafted from an unpermissioned address — if a privileged role is required, the finding is `ICE_E = Privileged` and must be flagged.

**Why it matters:** An entry point gated behind `onlyOwner` or a multisig is not exploitable without that key. L1 is the access-control sanity check.

---

### Q2 — L2 State Flip: Are storage changes proven?

**Passes when:** `test_L2_stateFlip()` passes AND the test uses `vm.load()` (or equivalent) to assert specific storage slot values before and after the exploit.

L2 proves the specific state change occurs — named slots, named balances, named flags. Vague before/after descriptions do not pass L2.

**Why it matters:** Judges dispute impact without evidence of what actually changes. L2 eliminates "theoretical" objections.

---

### Q3 — L3 Outcome: Is the final consequence proven?

**Passes when:** `test_L3_fullChain()` passes AND the final assert names the economic or security consequence (e.g., `assertGt(attacker.balance, INITIAL + THRESHOLD)`, `assertEq(protocolFunds, 0)`).

L3 = full chain from external entry point to outcome. Mock only contracts genuinely outside scope. All in-scope contract logic must run.

**Why it matters:** Judges are more skeptical of tests that call internal functions directly. L3 demonstrates the vulnerability exists in the actual on-chain call path.

---

### Q4 — Is there direct loss?

**Passes (✅) when:** The exploit causes one of:
- Theft of funds from a user's balance or allowance
- Over-seizure of collateral (more than protocol guarantees)
- Permanent blocking of a core safety mechanism (liquidation, redemption) causing
  uncoverable bad debt
- Forced liquidation of a solvent position

**Conditional (⚠️) when:** The loss requires a secondary precondition such as:
- A victim having an open token allowance to the protocol
- A specific market state (price at a certain level)
- An admin action to enable the attack vector

**Fails (❌) when:** The impact is only griefing, event log corruption, or denial of
a non-critical function with no downstream financial impact.

**Why it matters:** "Direct loss" is the primary driver of High vs Medium severity.
A finding with no direct loss path and no broken safety mechanism is at most Medium
regardless of how technically interesting the bug is.

---

### Q5 — Is the exploit permissionless?

**Passes (✅) when:** Any EOA or contract can trigger the exploit without:
- A privileged private key (admin, owner, operator)
- A special role that must be granted
- A pre-existing arrangement with the victim

Flash loans count as permissionless (they require capital but no permission).
Victim's open approvals count as a condition (see Q6), not a permission.

**Conditional (⚠️) when:** The attacker needs something realistic but not
universally present:
- Victim's aToken allowance (common but not universal)
- A minimum capital threshold (e.g., enough to borrow before attacking)

**Why it matters:** Permissionless exploits have much higher severity than those
requiring privileged access. A privileged-only exploit may be downgraded to Medium
or Low depending on the trust model.

---

### Q6 — Is the victim condition realistic?

**Passes (✅) when:** The condition that makes a user vulnerable arises naturally
from:
- Normal protocol use (supplying collateral, taking a loan, approving a router)
- Normal market conditions (price dropping, position becoming underwater)

**Conditional (⚠️) when:** The victim must be in an unusual state:
- Position already deeply underwater (may be rare in normal markets)
- Very specific collateral ratio or asset combination

**Fails (❌) when:** The victim must have made an unusual configuration error or
done something no normal user would do.

**Why it matters:** A finding that requires a very unusual victim state will be
rated lower by judges even if the technical exploit is clean. Assessing realism
prevents over-claiming.

---

### Q7 — Is this likely a duplicate?

**Check:**
1. Search Solodit for the same root cause pattern
2. Check `data/duplicates/clusters.jsonl` for this finding's cluster
3. Ask: is this the same root cause as another finding already in this audit's
   `data/triage/submit.jsonl`?

**Flag as ❓ (investigate) when:**
- A similar function has the same bug (e.g., same missing normalization in multiple
  entrypoints)
- The root cause exists in a widely-forked protocol (Aave, Compound, Uniswap v3)
  and has been reported before

**Why it matters:** Duplicate findings split the reward pool and can result in
rejection. Better to merge root-cause duplicates into one finding or flag the risk.

---

### Q8 — Can I write the impact in one sentence?

**Passes (✅) when:** You can write one clear sentence that:
- Names the victim ("borrower", "liquidator", "protocol treasury")
- States the harm ("loses X", "is permanently blocked from Y", "has Z seized")
- Requires no hedging or conditions to be true

**Example that passes:**
> Liquidating any position where collateral < debt + bonus panics with a u128
> underflow, permanently blocking that position's liquidation and allowing bad
> debt to accumulate.

**Example that fails (too hedged):**
> Under certain conditions involving specific oracle precisions and token decimals,
> liquidations might potentially allow more collateral than intended.

**Why it matters:** If you cannot write this sentence, the finding is either not
well-understood or the impact is not as severe as claimed. Judges read the summary
line first. A crisp one-sentence impact signals a well-evidenced finding.

---

## Checklist Status Symbols

| Symbol | Meaning |
|--------|---------|
| ✅ | Clearly satisfied — no further investigation needed |
| ⚠️ | Conditional — satisfies but requires a precondition; document it |
| ❌ | Not satisfied — consider downgrading severity |
| ❓ | Unknown — must investigate before submitting |

---

## Embedding in Test Files

Add a checklist comment block directly above each Level 3 test function:

```rust
// Checklist:
//   ✅ Q1 L1 entry reachable: <EOA can call entrypoint with no privileged setup>
//   ✅ Q2 L2 state flip: <slots/balances asserted before/after with vm.load()>
//   ✅ Q3 L3 full chain: <outcome proven — e.g. assertGt(attacker.balance, ...)>
//   ✅/⚠️/❌  Q4 Direct loss: <description>
//   ✅/⚠️/❌  Q5 Permissionless: <description>
//   ✅/⚠️/❌  Q6 Victim condition realistic: <description>
//   ✅/❓/❌  Q7 Likely duplicate: <result of check or "no known duplicate">
//   ✅  Q8 One-sentence impact: <the sentence>
```

---

## Embedding in Submission Markdown

Add a Quality Checklist section near the top of each submission (after Summary,
before Vulnerability Detail):

```markdown
## Quality Checklist

| # | Question | Answer |
|---|----------|--------|
| 1 | L1 entry reachable (permissionless EOA)? | ✅ `test_L1_entryReachable()` passes |
| 2 | L2 state flip proven (vm.load slots)? | ✅ `test_L2_stateFlip()` passes |
| 3 | L3 full chain outcome asserted? | ✅ `test_L3_fullChain()` passes |
| 4 | Direct loss? | ✅/⚠️/❌ `<one line>` |
| 5 | Permissionless? | ✅/⚠️/❌ `<one line>` |
| 6 | Victim condition realistic? | ✅/⚠️/❌ `<one line>` |
| 7 | Likely duplicate? | ✅/❓/❌ `<one line>` |
| 8 | One-sentence impact? | ✅ `<the sentence>` |
```
