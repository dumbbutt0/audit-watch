# P235 — Answer key (revealed AFTER freeze)

**Source:** Code4rena reNFT findings report — https://code4rena.com/reports/2024-01-renft (report page >10MB; the
deduped High set was cross-verified via the code-423n4/2024-01-renft-findings issues and two independent searches).
**Fetched:** Phase 3, 2026-06-08, after the freeze marker was written (FROZEN_HUNT.md hashes predate this file).

> Retrieval note (honesty): the High set below is high-confidence and consistent across all sources. The complete
> Medium enumeration could not be fully retrieved (report.md exceeds WebFetch's 10MB limit; AuditHub timed out), so
> the Medium list is REPRESENTATIVE (titles recovered from search + the findings repo), and total Medium count is
> approximate (~14). Recall is scored primarily against the authoritative High set; Medium recall is reported as a
> lower-confidence estimate.

## Awarded HIGH findings (deduped) — 5
| ID | Title | Root cause |
|---|---|---|
| H-01 | All orders can be hijacked to lock rental assets forever by tipping a malicious ERC20 | settlement/stop path reverts on a malicious payment token → permanent lock |
| H-02 | Attacker hijacks any borrowed ERC721/ERC1155 — guard missing validation on `setFallbackHandler()` | guard selector-blocklist is incomplete (Safe self-management) |
| H-03 | Attacker hijacks any rented ERC1155 via reentrancy (rental not registered before token swap) | create-time ordering / reentrancy |
| **H-04** | **Incorrect `gnosis_safe_disable_module_offset` → removing the rental safe's module without verification** | **guard reads prevModule not module** |
| H-05 | Malicious actor can steal any actively rented NFT and freeze rental payments in escrow | theft + escrow freeze |

## Awarded MEDIUM findings (representative; full set ~14, not exhaustively retrieved)
| ID | Title |
|---|---|
| M-01 | Malicious lender freezes borrower's ERC1155 indefinitely (guard can't differentiate rented vs non-rented ERC1155) |
| M-03 | DoS stopping large rental orders (block gas limit) |
| M-07 | Upgrading modules via `executeAction()` bricks all existing rentals |
| M-14 | Lender of a PAY order can grief renter of the payment |
| (others) | e.g. blacklist-on-`stopRent` permanent freeze (#605); partial-offer lock (#203); + further mediums |

## Direct mapping to my frozen candidates
| My candidate | Awarded? | Match quality |
|---|---|---|
| **RENFT-01** (disableModule offset → remove Stop) | **= H-04 (High)** | **EXACT** — same root cause, same mechanism; I CONFIRMED it with a runtime L3 PoC, blind. Severity predicted High = awarded High. |
| RENFT-04 (guard blocklist incomplete; renter calls non-transfer fns) | ~ H-02 (High) | PARTIAL — same root-cause family ("incomplete guard selector blocklist"), but I did NOT identify the specific `setFallbackHandler` hijack vector. |
| RENFT-02 (active hook bypasses guard) | not awarded (as framed) | none/QA |
| RENFT-03 (whitelisted delegatecall escape) | not awarded (NatSpec-acknowledged) | none/QA |
| RENFT-05 (CREATE_SIGNER replay) | not in recovered awarded set | none (unconfirmed) |
| RENFT-06..10 (low/info) | not in recovered awarded set | QA at best |
| — | H-01 malicious-ERC20 lock | **MISSED** (reasoned the reentrancy/settlement path but dismissed the malicious-token-revert lock) |
| — | H-03 ERC1155 reentrancy hijack | **MISSED** (checked reentrancy, wrongly concluded mitigated) |
| — | H-05 NFT theft + payment freeze | **MISSED** |
| — | M-01/M-03/M-07/M-14 ... | **MISSED** (most mediums) |
