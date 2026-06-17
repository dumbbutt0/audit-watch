"""
submission.author — candidate-authoring layer for the submission engine.

Converts raw, explicit finding artifacts (report.md, poc.log, scope.md, …) into a
schema-shaped submission_candidate.json. It is strictly a translator:

  - It does NOT submit anything.
  - It does NOT decide readiness (only submission_gate does).
  - It does NOT touch the detection pipeline or any runtime audit state.
  - It NEVER fabricates evidence; unknown data is represented as missing.

The submission gate remains the authority; human approval is always mandatory.
"""
