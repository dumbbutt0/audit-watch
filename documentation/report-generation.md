# Report Generation

---

## Submission Format

Every finding submitted to a contest must follow this structure.

### Title

Format: `<Vulnerability Classification> — <Concrete Impact>`

Examples:
- `Missing Access Control on setManagerOf Allows Revoked Manager to Self-Reinstall`
- `ERC-4626 Rounding Direction Error in convertToShares Enables Inflation Attack`
- `Reentrancy in withdraw() Allows Full Vault Drain via Re-entrant Callback`

Avoid vague titles like "Incorrect Access Control" or "Reentrancy Vulnerability". The title must convey both the mechanism and the impact.

### Description Sections

**Brief/Introduction** (2-3 sentences): What the protocol does in the affected area. What the bug is, stated plainly.

**Vulnerability Details**: Technical description. File, function, line. Missing check or incorrect logic. Exact code snippet. Why existing defenses do not cover this path.

**Impact Details**: What happens if exploited. Who is the victim. What assets or invariants are affected. Bounded or unbounded? Reversible?

**References** (optional): Links to related Solodit or Immunefi findings. Relevant EIPs.

### Proof of Concept

Separate top-level section. Must include: step-by-step attack scenario, test file name and run command, expected output, PoC level achieved.

### Recommended Fix

Concrete code change showing before and after. Not a suggestion to "consider adding a check".

---

## What NOT to Include in Submissions

Do not include: Severity Justification section, Quality Checklist answers, internal pipeline scores (triage score, confirmation_score, exploitability_score), internal finding IDs (RE-001, AC-003), draft notes, pipeline reasoning, comments about AI-generated analysis, or mentions of this framework.

---

## Report Gate

Answer all 8 questions before writing any submission:

1. What exact state did the attacker corrupt?
2. What protocol function consumes that state?
3. Did the PoC reach that consumer?
4. Did the consumer perform a real protocol action?
5. What impact was directly proven?
6. What impact was only plausible?
7. What severity is justified only by the direct proof?
8. What would be needed to increase severity?

If questions 2 or 3 are unanswered: do not write the report. Continue consumer tracing. Spawn `agents/impact_chain_escalation.md` or check `output/ice_manual_review.jsonl`.

---

## Pipeline Report Generation Commands

### Generate merged report (Step 3)

```bash
python tools/report_generator.py
```

Reads all `output/findings_*.json`, deduplicates, calls `agents/report_synthesis.md` for narrative. Writes `output/merged_findings.json`, `output/audit_report.md`, `output/audit_report.json`.

The output validation gate (`scripts/validate_agent_output.py`) runs automatically. Fix schema violations or injection artifacts before continuing.

### Generate submission pack (Step 4)

```bash
python scripts/final_submission_pack.py
```

Reads `data/triage/submit.jsonl`, generates per-finding submission reports using `prompts/submission_writer.md`. Writes `output/submission_pack.md`, `output/submission_pack.json`, and `output/submissions/<ID>.md` for each finding.

### Populate finding definitions

Run after `report_generator.py` — required before `generate_status.py` can display per-finding detail:

```bash
python - << 'EOF'
import json, sys
from pathlib import Path
sys.path.insert(0, 'scripts')
from audit_context import audit_path
merged = json.loads((audit_path('output') / 'merged_findings.json').read_text())
d = audit_path('data/findings')
d.mkdir(parents=True, exist_ok=True)
for f in merged.get('findings', []):
    fid = f.get('id')
    if fid:
        (d / f'{fid}.json').write_text(json.dumps({
            'finding_id': fid, 'title': f.get('title',''),
            'severity': f.get('severity','Medium'), 'vuln_type': f.get('vuln_type',''),
            'bug_class': f.get('vuln_type','logic_error'), 'claimed_severity': f.get('severity','Medium'),
            'file': f.get('location',{}).get('file',''), 'function': f.get('location',{}).get('function',''),
            'confidence': f.get('confidence','Medium'), 'duplicate_of': f.get('duplicate_of'),
            'agent': f.get('agent',''),
        }, indent=2))
print(f"Written {len(merged.get('findings',[]))} definitions to data/findings/")
EOF
```

---

## Glider Variant Analysis

For Critical or High findings, scan the ecosystem for the same pattern:

```bash
python tools/glider_tool.py search "<pattern_name>" --limit 20
python tools/glider_tool.py register "<name>" "<query_string>" <vuln_type>
```

Set `GLIDER_API_KEY` in `.env` to enable cross-repo scanning. Without the key, falls back to local Chroma KB similarity search.

---

## Recording Contest Results

After judging completes:

```bash
python scripts/ingest_judging_results.py \
  --finding-id XTR-001 --claimed-severity high --judged-severity medium \
  --contest xterio-immunefi-2026-05 --reason "..."

python scripts/ingest_ground_truth.py \
  --finding-id XTR-001 --outcome accepted --severity medium \
  --assumption-count 1 --assumptions "attacker must act during grace period"

python scripts/evaluate_pipeline_accuracy.py
```
