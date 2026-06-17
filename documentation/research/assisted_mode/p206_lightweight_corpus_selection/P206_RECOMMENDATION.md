# P206 — recommendation

## Decision: `FALLBACK_TO_VULTISIG_DEPENDENCY_ASSEMBLY`

The lightweight-corpus hunt did its job and produced a clear negative answer: **no firewall-clean (sealed, unused),
dependency-light corpus supplies an L3 positive-control High.** Therefore, for the *positive* control specifically,
fall back to assembling Vultisig's solc-0.7.6 + Uniswap-V3 dependency env (finishing P205) rather than introducing a
new corpus.

### Why no lightweight positive control exists
JSON-only firewall screening (two runs, agreeing; prose discarded) of the two eligible lightweight corpora:
- **munchables-2024-05** (2H/4M, solc 0.8.25, **compiles cleanly** against local OZ v5): both Highs are
  **permissionless DoS/griefing with no value transfer** → demote-class, **not** positive controls.
- **pooltogether-2024-03** (1H/8M, lightest deps): its single High is **`trusted_prereq` permanent-loss** →
  explicitly disfavored as a *main* positive control (criteria: "no trusted-admin-only Highs as the main positive
  control").
- badger / kleidi: 0 High → `REJECT_TOO_THIN`. All other sealed holdouts: `REJECT_ALREADY_USED`.

The decisive point: for munchables the harness is **trivial** (94 files, 0.8.25, OZ v5 local) — the blocker is
**finding content**, not deps. The lightweight pool is content-poor for *positive* controls, exactly inverse to
Vultisig (rich positive content, poor dep availability).

## Recommended P207 plan
1. **Positive control → Vultisig dependency assembly** (the fallback): build the solc-0.7.6 V3 harness env
   (forge-install or vendor canonical OZ-3.4 + Uniswap v3-core/v3-periphery) and build **H-01 claim-fee-loss
   (positive, awarded High, permissionless material)** + **M-03 cap-bypass (negative, awarded Medium)** — converting
   P205's `L3_STANDARD_PARTIAL` → `VALIDATED` on a corpus already mapped post-freeze. (M-03's `buy()` needs no live
   pool; H-01's `claim` needs a faithful V3 position fee-growth mock — the harder of the two.)
2. **Strong secondary (cheap, high-value): munchables as an executable DEMOTION-side 3rd corpus.** Its 2 **awarded**
   permissionless DoS/griefing Highs are exactly the over-rated class L3 should demote, and it compiles in seconds at
   0.8.25 against local OZ v5. This would fill a real P205 gap: P205's executed negative control (`ILOWhitelist`) was
   a *by-design, non-awarded* feature, whereas munchables would let L3 **demote a genuine AWARDED High executably** —
   the cleanest demotion validation yet. (Negative side only; does not supply the positive control.)

## Caveats / integrity
- **Firewall contamination (logged):** the run-2 firewall subagent leaked mechanism hints in its prose preamble
  (lock griefing/timing; fee-share permanent lock), contaminating the orchestrator re munchables/pooltogether
  mechanisms — the PCS failure mode recurring. Persisted JSON is clean and agrees with run 1. **Mitigation:** if
  munchables/pooltogether is used in P207, the threat-ceiling run **must** use fresh key-blind blind subagents with
  the orchestrator scoring only post-freeze (as in P202/P205). Process fix for future screening: subagents must be
  forced to first-char `{` / last-char `}`; preamble → void + rerun (the JSON-only instruction alone was insufficient
  — the model kept prepending a sentence).
- This phase did **no** production change; hashes byte-identical START==END; sealed keys accessed read-only
  (count-only by orchestrator; bodies only by firewall subagents); smoke-test artifacts trimmed.

## Decision space mapping
Not `ACCEPT_LIGHTWEIGHT_POSITIVE_CONTROL_CORPUS` (no lightweight positive High exists). Not `DATASET_TOO_THIN` (clean
positive content DOES exist — in Vultisig — just dep-heavy; and lightweight negative content is abundant). Not
`FIREWALL_COMPROMISED` as a run-invalidating verdict (leak logged + mitigated; JSON corroborated across two runs).
→ **`FALLBACK_TO_VULTISIG_DEPENDENCY_ASSEMBLY`.**
