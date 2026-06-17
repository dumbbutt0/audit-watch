# Deep-Pass Depth-Trace (Phase-16, RESEARCH-ONLY, optional)

A structured **reasoning checklist** that composes ON TOP OF the baseline value-provenance pass
(`prompts/deep_pass_value_provenance.md`). It targets the subtle accounting bugs the baseline misses on
functions that are **already in the candidate queue**: missing penalty/scale/fee/profit terms, wrong
share-conversion direction, and identity/basis errors hidden in internal callees.

**This is NOT a detector.** It asks generic accounting-reasoning *questions*; it must not encode known bug
patterns or protocol-specific names. It must be able to conclude **"no vulnerability found"**.

## Run this per candidate (after the baseline pass)

For each candidate function, reconstruct and STATE explicitly:

1. **Accounting identity / invariant** this function claims to preserve (one line).
2. **Intended formula** (what the math *should* be) vs **implemented formula** (what the code does) — and the
   **diff** (a term/operand/conversion present in one but not the other).
3. **Per-term unit ledger** — for every operand/term in the formula:
   | term | role (principal/fee/penalty/profit/discount/scale/index) | **expected units** | **actual units** | present? |
   Flag any term whose expected≠actual units, or that is **missing/zeroed**.
4. **Internal-callee trace** — for each internal callee touching value/identity/units: does it preserve the
   same **owner/actor · asset · share/asset basis · units**? State **which callee, if any, changed your
   conclusion** (and cite its `file:line`).
5. **Conversion check** — every assets↔shares (or any X↔Y) conversion: **direction** and **rounding** correct
   for who benefits?
6. **Order-of-operations** — is the invariant checked **before or after** the mutation it guards?

## Two-sided evidence (MANDATORY for any suspected issue)
State BOTH, with `file:line`:
- **why-wrong:** the concrete term/conversion/identity divergence and the economic effect if exploited.
- **why-safe/intended:** the strongest reason it could be deliberate (e.g. the term is handled elsewhere, is a
  treasury cut not user-owed, rounding is protocol-favorable by design).
Decide by weighing the two. If why-safe dominates or is unresolved → **do NOT emit a finding**.

## Decision (per candidate)
- `finding` — formula diff yields a concrete, evidenced, exploitable divergence (why-wrong clearly outweighs
  why-safe). `confidence: high`.
- `likely_exploitable` — evidenced divergence, but why-safe not fully excluded. **MANDATORY:**
  attacker_entrypoint + divergence_point + claimed_effect + a `repro_hint`. `confidence: medium`.
- `strong_clear` — **"No vulnerability found; formula appears internally consistent"** — carry the identity,
  the unit ledger showing all terms present/consistent, and why no attacker benefits.
- `needs_human` — genuine uncertainty after two-sided weighing.

## Depth-only annotation fields (added to each decision, for contribution analysis)
- `via_callee`: true/false — did tracing an **internal callee** change the conclusion?
- `depth_class`: one of `missing_term | wrong_conversion | scale_mismatch | excluded_fee | callee_identity |
  none` — the failure class (step from the taxonomy) that produced the decision.

## Output
Append to `output/deep_pass/_decisions.json` with the same schema as the baseline pass PLUS `via_callee` and
`depth_class`. Then `deep_pass_write.py --eval`. **"More findings" is a liability** — an extra suspicious note
that isn't a concrete formula diff is noise, not recall; prefer `strong_clear`/`needs_human` over a weak flag.

## Discipline
- Same candidate queue, same source snapshot, same decision schema (+ the 2 annotation fields) as baseline.
- No hallucinated recall: every `finding`/`likely_exploitable` cites a real `file:line` formula diff.
- Research-only: sets `family`/`shape`/`confidence` + a hypothesis only; no severity/submission/routing.
