# P128 — Downstream state map: what forced graduation (stage 0→1) actually unlocks

Read-only; framing only. Resolves P127 C2 (downstream harm of premature graduation).

## Token / voting topology
| Element | Value / rule | Source |
|---|---|---|
| AIToken total supply | fixed `100_000_000e18`, minted to the factory at deploy, then distributed | `AIToken.sol` `INITAL_SUPPLY`; `AgentFactory.createAgent` |
| distribution | `mintToDAO%` → DAO, `mintToAgent%` → Agent, remainder `initialLiquidity` → BootstrapPool (sold to buyers) | `createAgent` |
| voting power | ERC20Votes — **requires self-delegation**; undelegated holdings (DAO/Agent) count in total supply but cast 0 votes | `AIToken` (ERC20Votes), `clock()` = timestamp |
| how an attacker gets votes | only by **buying AIToken** (bootstrap/Fraxswap) + delegating — **independent of graduation mode** | — |

## Governance parameters (measured at runtime, not assumed)
| Param | Value | Note |
|---|---|---|
| `proposalThreshold()` | `stage==0` → `type(uint256).max`; `stage>0` → **0.01% of supply** (measured **10,000e18**) | `TokenGovernor.sol:75` |
| `quorum()` | **measured 4,000,000e18 = 4% of supply** (`GovernorVotesQuorumFraction(4)`, denominator 100) | ⚠ inline comment says "25% (1/4th)" — **incidental config/comment discrepancy**, recorded neutrally; not the P128 question |
| votingDelay / votingPeriod | 2 min / 5 min | `TokenGovernor` |
| executor | the Governor itself (a proposal must **pass** to act) | `_executor()` |

## Agent surface unlocked by stage>0 (`onlyWhenAlive`)
| Function | Guard | Reachable by attacker? |
|---|---|---|
| `setProxyImplementation(addr)` | `onlyOwner`(=Governor) `onlyWhenAlive`; **impl must be in `factory.allowedProxyImplementation`** (owner-whitelisted, README-trusted) | No — governance-only + whitelist |
| `setTokenURI(id,uri)` | `onlyOwner`(=Governor) `onlyWhenAlive` | No — governance-only; cosmetic |
| `setStage` | `onlyFactory`, **monotonic** | No |

## Where forced graduation does / does not change attacker power
- Forced graduation (P126-F) is funded by a **currency donation** ⇒ the attacker receives **0 AIToken** ⇒ **0 voting power**.
- Graduation only flips `stage→1`, which *enables proposals* (threshold drops from max to 0.01%) and *makes the agent
  alive* — but **executing** any governance action still requires the **4% quorum** (4M votes).
- The attacker's voting power is set entirely by AIToken bought + delegated, which is **the same whether graduation was
  forced or organic**. Forced graduation grants **no token windfall** and **no quorum**.

⇒ The downstream-capture hypothesis reduces to: "can the attacker reach quorum (4%)?" — a mode-independent,
buy-4%-of-supply question, not something forced graduation provides.
