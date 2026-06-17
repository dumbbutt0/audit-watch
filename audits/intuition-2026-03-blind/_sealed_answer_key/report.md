# Intuition (Code4rena 2026-03) — Awarded Findings

> Revealed AFTER blind discovery (fetched from code4rena.com/reports/2026-03-intuition at reveal time).

# High Risk Findings (0)

# Medium Risk Findings (2)

## [[M-01] Unsigned validity window metadata](https://code4rena.com/reports/2026-03-intuition)

Signature validity windows (`validUntil`/`validAfter`) appended to signatures lack cryptographic binding,
allowing relayers to alter time restrictions without invalidating the signature.

## [[M-02] Epoch-boundary checkpoints retroactively qualify for the previous epoch's rewards](https://code4rena.com/reports/2026-03-intuition)

Voting-escrow checkpoints created at epoch boundaries are counted in the previous epoch's reward snapshots due
to inclusive timestamp lookups, enabling attackers to claim emissions without participating in that epoch.

# Low Risk and Non-Critical Issues

(excluded from reach denominator)
