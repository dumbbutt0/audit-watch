# P280 — EVIDENCE_QUALITY_AUDIT

Machine: `outputs/evidence_quality_audit.json`. All 3 READY packages inspected against the real source + PoC result.

| candidate | attacker_path correct? | assertion implementable? | source_basis sufficient? | placeholder leak? | hallucinated? | should've been READY? | class |
|---|---|---|---|---|---|---|---|
| V3Vault.transform | **NO** (inline-guarded) | yes | **NO** (missed inline guard) | no | no | **NO** | READY_OVERCLAIMED |
| IBeanstalk.cancelPodListing | **NO** (inline ownership) | yes | **NO** | no | no | **NO** | READY_OVERCLAIMED |
| L2Governor.execute | **NO** (permissionless by design; real bug is state-machine) | yes | **NO** | no | no | **NO** | READY_OVERCLAIMED |

Summary: READY_CONFIRMED 0 · **READY_OVERCLAIMED 3** · READY_WRONG/TOO_WEAK/INCONCLUSIVE 0 · hallucinated core 0 ·
placeholder leaks 0 · severe FP 0 · evidence sufficient to BUILD all 3 = yes.

## Root cause (one, specific)
The P279 deriver assigns attacker_path HIGH/MEDIUM from the manifest `modifiers` field, so it is **blind to**:
1. **inline guards** — `require(msg.sender == owner)` / `require(plots[lister][index]>0)` are not modifiers
   (transform, cancelPodListing). The deriver saw `modifiers=[]` and concluded "no auth" → overclaimed HIGH/MEDIUM.
2. **state-machine semantics** — L2Governor.execute is permissionless *by design*; the real anomaly is the status-set
   it accepts (Defeated/Expired). The ACCESS template's "unauthorized caller" framing is the wrong mechanism.
No fabrication and no placeholder leak — the evidence was *structurally true but mechanistically mis-framed*.
