# SOPH-04 — boost inflates pool.amount reward denominator (likely intended)
- **Severity recommendation:** Low/Medium or by-design (ceiling High; L3 NEEDS_HARNESS / spec check)
- **Affected:** SophonFarming.sol `_deposit`/`increaseBoost` (L598-617, L640-674)
- **Root cause:** boost adds `boost*boosterMultiplier/1e18` synthetic weight to `pool.amount` (reward denominator)
  without matching custody; dilutes honest depositors' point share. This is plausibly the INTENDED paid-boost amplifier.
- **Attacker model:** permissionless (pay to boost). **Fund theft:** none. **L3:** blocked / pending spec confirmation.
- **Mitigation:** none if intended; document the boost economics. **Human review:** confirm against protocol spec.
