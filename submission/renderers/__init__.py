"""
submission.renderers — gated platform-draft rendering.

Transforms a GATE-VALIDATED submission candidate into a platform-shaped human
draft (Immunefi / Code4rena). It is the step AFTER readiness:

  candidate -> submission_gate -> non-blocking status -> platform DRAFT -> human copy/paste

Hard guarantees:
  - Drafts ONLY. No submission, no API calls, no browser/clipboard automation.
  - A draft is emitted only when the gate status is non-blocking
    (READY_FOR_HUMAN_REVIEW or READY_TO_SUBMIT_AFTER_APPROVAL). DO_NOT_SUBMIT and
    NEEDS_MORE_PROOF can never produce a draft.
  - A gate result is REQUIRED: candidate -> draft without gate validation is refused.
  - Every draft is watermarked "DRAFT ONLY — NOT SUBMITTED"; human approval is
    always required. The gate remains the authority.
"""
