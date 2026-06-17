# P156 — Gate 3: Severity Finalization

## Ladder placement
- **High?** No — no protocol-fund loss and no broad user-fund loss independent of a trusted role.
- **Medium?** Ladder def: "unprivileged user can extract a zero-sum reward redistribution from honest
  stakers, with concrete runtime proof, but magnitude depends on operator delay/trusted maintenance." H5
  matches this *shape* exactly (P154 runtime proof, zero-sum 175e18).
- **Low?** Ladder def: "real unfairness exists but requires unlikely or short operator delay, limited
  impact, or **accepted liveness dependency**." The new external fact — de-boost is performed by an
  **automated Gelato keeper** "once a `rewardDuration`" — makes the exploit window an **unlikely/short
  keeper-failure exception** and an **accepted liveness dependency**, which is precisely the Low tier.

## Final recommendation: **Low candidate (bounded; rises to Medium under sustained keeper failure)**
A downgrade from P155's Medium, justified by the P156 external evidence (automated keeper) that P155 lacked.

### Downgrade arguments (Medium → Low)
- De-boost is **automated** (Gelato), so operator delay is an exception, not the norm → small expected window.
- **No protocol-fund loss**; strictly zero-sum reward redistribution among stakers.
- Inherited, **publicly-known** Convex/Curve lazy-expiry design; wardens examined this contract's reward
  accounting (M-07) and did **not** award this → market signal that it is at most low-impact here.

### Upgrade arguments (keeps it off QA / could reach Medium)
- Honest third-party stakers bear the loss and have **no self-remediation** (no user unlock).
- Loss for elapsed windows is **permanent** once claimed/vested (not retroactively corrected).
- **Unbounded** if the keeper is ever down for a sustained period; scales with reward rate × delay ×
  expired-locked size × multiplier (up to 3× here, configurable higher).

### Assumptions
- Gelato keeper normally runs ~each epoch (per contest docs).
- `lockingBoostMultiplerInBips` materially > BIPS (3× in PoC).

### Unresolved questions (for the target program, not resolvable here)
- The program's stance on keeper-liveness reward-fairness issues (in-scope Low/Med vs out-of-scope).
- Whether a non-awarded/QA warden submission of this exists (raw-issue set not exhausted).

**final_severity_recommendation = low_candidate_bounded_medium_under_sustained_keeper_failure**
