# Deduplication & Merge Policy

**Principle: link, don't collapse.** Redundant *detection* of one bug by several agents is a
confidence signal, not waste — preserve it as links. The real hazard is collapsing two
**distinct** bugs into one, which permanently hides a finding (nothing downstream re-reads the
pre-merge set).

## The merge rule

Two findings may be **merged** into one only if they match on **all five** axes:

1. **Root cause** — the same underlying defect (not just the same symptom).
2. **Affected function / state transition** — the same code location or mutation.
3. **Exploit path** — the same attacker route to trigger it.
4. **Violated invariant** — the same property broken.
5. **Impact mechanism** — the same way value/security is lost.

If **any** axis differs, **keep both findings separate** and record the relationship in
`cross_agent_refs` (and `compound_with` when they chain). Never drop the second.

### Hard guard

A merge that would collapse two findings whose `location.file` differs is **blocked** and
logged — different files are almost never the same root cause. (Same-file but different-function
or different-exploit-path is the subtle case the five-axis rule catches.)

## Why (the Beanstalk lesson)

`tools/report_generator.py` merged 70 raw findings → 44, folding **OR-001** (LibChainlinkOracle
inverted-ternary: returns spot when TWAP requested) and **OR-002** (LibUsdOracle wstETH branch
hardcodes `lookback=0`) into a single record. These share a *theme* (oracle returns instantaneous
price) but differ on root cause, function, and file. Collapsing them would have understated
detection and could have dropped a real, separately-fixable bug. The two are the canonical
regression fixture (`fixtures/dedup_distinct.json`).

## Chaining (separate from merge)

After dedup, the impact-chain pass (`run_impact_chain_escalation.py`, `synthesize_compound_findings.py`)
looks for **combinations**, asking:

- Can a low-severity bug create the precondition for a higher-severity one?
- Can a DoS/griefing issue become fund loss when combined with another state transition?
- Can an oracle bug combine with accounting logic? a migration bug with replay/missing finalization?
- Can a precision bug become economic extraction? a stale-state bug a double-claim?

Chains get a new `CC-`/`COMP-` ID with escalated severity and `compound_with` links back to the
components — the components are **not** deleted.

## Implementation

- Fixture-first (Guardrail 4): `documentation/refinement/fixtures/dedup_distinct.json` holds the
  OR-001/OR-002 shape; a check asserts both survive a merge. It must FAIL on the old logic and
  PASS on the new.
- `tools/report_generator.py`: replace exact-id-only dedup with the five-axis comparison; add the
  different-file hard guard; attach `cross_agent_refs` for linked-but-separate findings.
- `findings/raw/` retains the full pre-merge set as a human-recoverable safety net.
