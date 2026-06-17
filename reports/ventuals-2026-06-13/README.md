# Ventuals (vHYPE liquid staking, HyperEVM) — audit deliverables (2026-06-13)
Real Cantina hunt (ventuals/ventuals-contracts @3621e4d), Solidity/Foundry, local-only, nothing submitted, honest negative.
Scope = vHYPE liquid staking on HyperEVM (NOT the perps engine). Turned out TWICE-audited (Nethermind + Zenith, Oct 2025).
FINDINGS.md: exchange-rate/no-virtual-shares (Informational, live-state-contingent), decimals (conservative), linked-list
queue (battle-tested), batch/claim (protocol-favoring rounding), HyperEVM↔L1 one-block-delay guards. No permissionless H/C.
