# P280 — LIMITATIONS

- **Tier C reproductions, not full deploys.** Each PoC faithfully reproduces the exact guard/state-transition the auto
  claim targets; it does not stand up the full Beanstalk diamond / governance / lending stack. Sufficient to
  refute/qualify the auto *mechanism*, not to prove a full end-to-end exploit.
- **The L2Governor "Defeated/Expired executable" anomaly is a human finding**, not auto-derived — recorded as
  SAME_AREA_WRONG_MECHANISM to show what the deriver missed; it is a validation hypothesis, not a confirmed bug.
- **n=3** (the only 3 P279 auto-READY). The conclusion (READY overclaims via inline-guard blindness) is specific to
  this deriver's manifest-modifiers signal, demonstrated on 3 clean cases — not a statistical rate.
- Supervised diagnostic, not blind; not production authority; nothing here is reportable/confirmed.
