# Specialist Chain Selection — Why Access-Control + Signature-Replay Next

Research-only planning. Selects the next **two** research-track specialist chains from the P54/P55 out-of-charter
evidence. **No detector built here.** These chains **complement** (do not replace) the production access-control /
reentrancy / DoS specialists; they are research-only precision lanes like the value-flow chain.

## Evidence (P54 / P55 out-of-charter families)
From the analyzed clean-abstain subjects (P54 `aggregate_tables.json`, P55 `metric_4_scope`), the awarded H/M that the
value-flow chain is *not* built for break down (top families):
- **access-control: 3** (P55) / **3** (P54 incl. access-control-validation)
- **DoS/griefing: 3**
- **signature/replay: 2**
- reentrancy: 1 · governance/process: 1 · input-validation: 1 · (AMM-invariant, external-integration: 1 each)
82.4% of awarded H/M on those subjects were out-of-charter — dominated by access-control and signature/replay (the two
most *source-verifiable* of the high-frequency families).

## The two chosen
1. **Access Control / Authorization / Caller Surface** (config `access_control_chain_draft.json`).
2. **Signature Replay / Permit / Domain Separation / Nonce Integrity** (config `signature_replay_chain_draft.json`).

## Why these beat DoS / governance / oracle / AMM
| family | frequency (P54/P55) | source-verifiable? | tight-gateable? | needs economic/market assumptions? | verdict |
|---|---|---|---|---|---|
| **access-control** | high (3) | **yes** (modifier / caller / role at the call site) | **yes** (privileged mutation + reachable + missing check + protected sibling) | no | **SELECT** |
| **signature-replay** | high (2) | **yes** (signed fields / nonce-consume / domain in source) | **yes** (recovered signer + missing nonce/domain/deadline + reachable replay) | no | **SELECT** |
| DoS/griefing | high (3) | partial | **no** — needs cost/gas/economic modelling; noisy | often | defer |
| governance/process | low (1) | partial | no — "should be pausable/upgradable" is a design judgement | no but judgement-heavy | defer |
| oracle manipulation | (1, AMM/emissions) | partial | no — needs market/oracle economic assumptions | **yes** | defer |
| AMM invariant | (1) | partial | no — needs protocol-specific math/economics | yes | defer |

**Rationale (explicit, per the failure-condition guardrail):**
- **Frequency:** access-control (3) and signature-replay (2) are among the most common out-of-charter misses; DoS (3) is
  also frequent but fails the next two tests.
- **Source-verifiability:** AC and replay are decidable from *source at the call/verify site* (modifier present? signer
  bound? nonce consumed? domain includes chainId+verifyingContract?). DoS/oracle/AMM need cost models, market state, or
  protocol-specific economics that are not source-local.
- **Tight gating / low noise:** AC and replay have crisp positive-evidence + rejection criteria (see configs), so they
  can be FP-tight like the value-flow gates. Generic DoS is intrinsically noisy (every loop/external call "could" DoS).
- **Impact clarity:** AC = privileged value/authority/control change; replay = repeated value/authority/claim/approval
  state change — both have concrete, bounded impact, unlike "griefing" or "manipulation" which need economic argument.
- **Pairs with value-flow:** AC governs *who* may move value; replay governs *how many times* a signed value action runs;
  value-flow governs *whether the amount/recipient is right*. Together they cover the who/how-often/how-much of value
  movement with source-local evidence.

## Non-replacement note
Audit-Watch's production pipeline already has access_control / reentrancy / dos specialists (CLAUDE.md Step 2). The new
chains are **research-only precision lanes** (REVIEW_ONLY candidate generators), validated under the same freeze-before-
findings + holdout discipline as the value-flow arc; they do not change or replace the production specialists.
