# P141 — Review-Gate Rendering

Each architecture's `generate_review_gate.py` output (saved as `{noya,blackhole,size}_review_gate.md`) was checked
for the same isolation guarantees.

| Arch | VP subsection present | findings tagged "NOT confirmed" | strong_clear as "cleared advisory context" | in Validated Findings | Confirmed findings count |
|---|---|---|---|---|---|
| noya | yes | yes (NoyaValueOracle._getValue) | yes (SolvencyV2) | **no** | **0** |
| blackhole | yes | yes (claim_many) | yes (claim, claimable) | **no** | **0** |
| size | yes | n/a (no finding) | yes (debtToken…); needs_human shown verbatim | **no** | **0** |

## Rendering rules confirmed (from `_value_provenance_section`)
- Section header: "### Value Provenance Deep-Pass Results — advisory only" + the disclaimer "Advisory only —
  prompt-derived review evidence, NOT proof, NOT confirmed, NOT submission-ready… Requires human review and PoC…
  Excluded from Validated Findings and the confirmed count."
- `finding`/`likely_exploitable` → "<decision> — NOT confirmed"; `strong_clear` → "strong_clear (cleared advisory
  context)"; `needs_human`/`completed` shown verbatim.
- Columns: Status · Location · Decision · Confidence · Next step · Mechanism · Job.
- Completed entries are **never** added to `findings`, so the Validated Findings table and the confirmed-findings
  count are mathematically unaffected (all three audits printed `Confirmed findings: 0`).
