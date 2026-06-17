# P298 — DESIGN

## Three axes
1. **Answer-key (recall/precision)** — the finding→awarded match is the PRIOR eval2 semantic-judge result (read-only):
   81 public · HIT 15 / PARTIAL 19 / ADJACENT 9 / MISS 38 · pipeline-only 8. recall_useful=(HIT+PARTIAL)/81=0.42;
   recall_any_touch=0.53; 12 platform_confirmed accepted. P298 does NOT re-discover, so recall is the current setup's
   existing recall; P298 ADDS the next two axes.
2. **Novelty** — per merged finding, KB cosine similarity vs the 51k-finding solodit chroma (all-MiniLM-L6-v2). novel
   if sim < 0.4 (the CLAUDE.md Hermes rule). Second corroboration via the immunefi MCP on the confirmed loci.
3. **Validity** — the P294 executed-PoC verifier is the SOLE confirmer (builder self-report advisory). For each
   awarded-matched locus: Tier-C executed PoC where faithfully mockable → confirmed iff executed exploit PASS +
   L1+L2+L3 + assertion_map; evidence-bundle + needs_execution (NOT confirmed) for the entangled tail.

## Key design property surfaced by this eval
The verifier's L1+L2+L3 contract is **exploit-shaped** (L1 = attacker EOA entry, L2 = named state flip). It confirms
ATTACKER-EXPLOIT bugs strongly (theft, replay) but conservatively marks LOGIC/CORRECTNESS/ADMIN bugs (off-by-one in
migration, a wrong getter) as `setup_only` — they're real and proven by a passing differential test but have no
attacker entry to assert. This is the FP-guard erring safe (it won't call a non-attacker PoC an "exploit
confirmation"), and it's the headline improvement target: a logic-bug validity mode (validity = a passing
differential test against a corrected reference, no attacker L1 required).

## Authority / safety
Answer key + contest source read-only; no audit switch; advisory-stamped; no severity/submission; un-wired from
confirm gates; confirmed-FP=0 by construction.
