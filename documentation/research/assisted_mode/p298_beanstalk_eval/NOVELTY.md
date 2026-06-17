# P298 — NOVELTY

Per-finding KB cosine similarity vs solodit_findings (sentence-transformers/all-MiniLM-L6-v2); novel if sim < 0.4.
Result: **0 novel / 44 known** over 44 findings.
All 44 findings match a known solodit pattern class (sim ~0.50–0.79) — beanstalk's reseed/migration/oracle/convert bug classes have prior analogues. The immunefi MCP independently corroborates the confirmed loci's classes (replay-no-nonce; unguarded-sweep) as known/awarded. No High/Critical was flagged novel-for-human-review.

| id | sev | sim | class | nearest KB |
|---|---|---|---|---|
| SC-001 | Critical | 0.5 | known_or_duplicate | [09] Necessary changes to `foundry.toml` |
| AM-020 | Low | 0.573 | known_or_duplicate | [L-03] The `unwrapAllWETH()` Function Creates |
| AM-017 | Low | 0.574 | known_or_duplicate | Migration of unripe LP from BEAN:3CRV to BEAN |
| TI-003 | High | 0.577 | known_or_duplicate | The `DepotFacet` contract uses an incorrect ` |
| AC-003 | Low | 0.581 | known_or_duplicate | Intermediate value sent by the caller can be  |
| AC-004 | Informational | 0.619 | known_or_duplicate | Missing reentrancy guard in `TokenFacet::tran |
| EA-001 | High | 0.621 | known_or_duplicate | Unfair Penalty Fees in Pipeline Convert |
| EA-002 | Medium | 0.627 | known_or_duplicate | Ability to whitelist assets uncorrelated with |
| AM-012 | Low | 0.634 | known_or_duplicate | `ReseedBarn.init()` will run out of gas due t |
| SN-001 | High | 0.638 | known_or_duplicate | User will lose the rest of their `plenty` if  |
| EA-003 | Low | 0.641 | known_or_duplicate | User will lose the rest of their `plenty` if  |
| DS-002 | Low | 0.645 | known_or_duplicate | Stealing SoP rewards by manipulating the tota |
