# Reasoning Graph Dashboard

The reasoning graph is a live cognitive debugger for the audit pipeline. It shows how hypotheses were born, how evidence shifted confidence, which branches converged to findings, and which were invalidated — all in real time as pipeline stages execute.

---

## Purpose

Standard audit dashboards show outcomes (findings count, severity distribution). The reasoning graph shows process: which agent spawned which hypothesis, what KB precedent it matched, what confidence shifts occurred, and why the final triage decision was made. This is useful for:

- Reviewing agent reasoning quality
- Identifying where the pipeline diverged from expected paths
- Understanding why a finding was invalidated (trace the branch to its INVALIDATED node)
- Auditing the audit — verifying that the AI followed the correct methodology

---

## Launching

```bash
python viz/server.py
# or with a specific session:
python viz/server.py --session <session_id>
```

Port: **8766** (port 8765 is the main audit dashboard)

---

## Session Management

Sessions tie all VizEvents from one pipeline run together. The session ID is stored in the `VIZ_SESSION_ID` environment variable so all pipeline subprocesses share it.

```bash
# Create a new session before starting a pipeline run
python -c "from viz.session import create_session; print(create_session('MyProtocol.sol'))"
export VIZ_SESSION_ID=<output>

# List all sessions
python -c "from viz.session import list_sessions; import json; print(json.dumps(list_sessions(), indent=2))"
```

Session data is stored in `data/sessions/{session_id}/`:
- `manifest.json` — session metadata (target, audit_id, created_at, status)
- `events.jsonl` — all VizEvents in chronological order

If `VIZ_SESSION_ID` is not set, events are silently skipped (graceful degradation).

---

## Event Types

| Event type | Emitted by | Meaning |
|------------|-----------|---------|
| `SESSION_START` | Pipeline orchestrator | Audit session begun |
| `SESSION_END` | Pipeline orchestrator | Audit session complete |
| `AGENT_SPAWNED` | Step 2 spawn | A specialist agent was launched |
| `HYPOTHESIS_BORN` | Agent | A new vulnerability hypothesis was created |
| `BRANCH_CREATED` | Agent | An exploit path branch was spawned under a hypothesis |
| `EVIDENCE_ATTACHED` | Agent | Evidence (code ref, KB match, static finding) attached to a node |
| `KB_MATCH` | `retriever.py` / `immunefi_retriever.py` | Knowledge base precedent found for a hypothesis |
| `CONFIDENCE_SHIFT` | Any agent | Confidence score for a node updated (with old/new values and reason) |
| `BRANCH_INVALIDATED` | Agent, gate | An exploit path was ruled out |
| `EXPLOIT_PROVED` | `run_poc_tests.py` | PoC test confirmed the exploit |
| `EXPLOIT_FAILED` | `run_poc_tests.py` | PoC test failed to prove the exploit |
| `TRIAGER_DECISION` | `triage_findings.py` | Triage agent made a submit/reject/downgrade decision |
| `HUMAN_ANNOTATE` | Human (via REST API) | Human auditor added an annotation to a node |
| `NODE_SUPPRESSED` | Human (via REST API) | Human suppressed a branch from display |

---

## Instrumenting Pipeline Scripts

```python
from viz.event_emitter import emit

# Born a hypothesis
emit("HYPOTHESIS_BORN", source_agent="reentrancy_agent", payload={
    "hypothesis_text": "Collateral desync via reentrancy in withdraw()",
    "linked_contracts": ["LendingPool.sol"],
    "severity_ceiling": "CRITICAL",
    "confidence": 0.6,
    "exploit_class": "reentrancy",
})

# Attach KB evidence
emit("KB_MATCH", source_agent="reentrancy_agent", target_node_id="HYP-001", payload={
    "solodit_id": "SOL-12345",
    "title": "Reentrancy in withdraw() causes collateral desync",
    "similarity_score": 0.87,
})

# Shift confidence after evidence
emit("CONFIDENCE_SHIFT", source_agent="reentrancy_agent", target_node_id="HYP-001", payload={
    "old_confidence": 0.6,
    "new_confidence": 0.85,
    "reason": "KB precedent found; attack path confirmed via CFG",
    "triggered_by": "EVIDENCE_ATTACHED",
})
```

The emitter never blocks (fire-and-forget), never raises exceptions, and gracefully skips if `VIZ_SESSION_ID` is not set.

---

## Graph Node Types

### HypothesisNode

Represents one vulnerability claim from a specialist agent.

| Field | Description |
|-------|-------------|
| `id` | Pattern: `HYP-NNN` |
| `node_type` | `"hypothesis"` |
| `label` | One-line hypothesis title (max 80 chars) |
| `hypothesis_text` | Full statement |
| `agent_origin` | Which agent created it |
| `status` | LIVE / INVALIDATED / CONVERGED / PRUNED / ESCALATED |
| `confidence` | 0.0–1.0, updated over time |
| `severity_ceiling` | CRITICAL / HIGH / MEDIUM / LOW / INFO / UNKNOWN |
| `exploit_class` | reentrancy, arithmetic, storage_shadow, etc. |
| `kb_matches` | Array of KBMatch objects (solodit_id, similarity_score) |
| `assumptions` | Preconditions required for the exploit |
| `blockers` | ACCESS_CONTROL / GAS / LOGIC / GOVERNANCE / EXTERNAL_DEP |
| `confidence_history` | Timeline of confidence shifts |
| `annotation` | Human auditor annotation (null if none) |

### BranchNode

Represents one exploit path under a hypothesis.

| Field | Description |
|-------|-------------|
| `id` | Pattern: `BR-NNN-A` |
| `parent_hypothesis` | HypothesisNode.id |
| `branch_trigger` | What caused this branch to spawn |
| `branch_type` | EXPLOIT_PATH / CONSTRAINT_RELAXATION / VARIANT / COUNTERFACTUAL |
| `status` | LIVE / PRUNED / CONVERGED |
| `depth` | Hops from root hypothesis |

### EvidenceNode

Attached to a HypothesisNode or BranchNode.

| Field | Description |
|-------|-------------|
| `evidence_type` | CODE_REF / SOLODIT_MATCH / STATIC_ANALYSIS / POC_RESULT / AGENT_REASONING |
| `content` | Evidence text or code snippet |
| `confidence_delta` | How much this shifted confidence (+/-) |

---

## Node Status Colors

| Status | Color | Meaning |
|--------|-------|---------|
| LIVE | `#00d4aa` (teal) | Active, being investigated |
| CONVERGED | `#00ff88` (green) | Confirmed finding, submitted |
| INVALIDATED | `#ff3355` (red) | Gate failure or disproved |
| PRUNED | `#3d4458` (dark gray) | Low confidence, dropped |
| ESCALATED | `#ffaa00` (amber) | Combined into compound finding |

---

## Swimlane Columns

The frontend displays hypotheses in a timeline swimlane:

```
BORN → KB MATCH → EVIDENCE → CONFIDENCE → TRIAGE → POC → OUTCOME
```

Each column corresponds to a pipeline phase. Hypotheses flow left-to-right as evidence accumulates. Hypotheses that get pruned or invalidated stop at the column where the decision was made.

---

## REST API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Frontend HTML (serves `viz/frontend/index.html`) |
| `/api/session/{id}/graph` | GET | Full graph snapshot as JSON |
| `/api/session/{id}/graph?at=N` | GET | Graph state at event index N (replay) |
| `/api/session/{id}/metrics` | GET | Graph metrics (hypothesis counts, confidence distribution) |
| `/api/sessions` | GET | List all historical sessions |
| `/ws/live` | WS | Real-time event stream |
| `/api/session/{id}/branch/{bid}/suppress` | POST | Human-in-loop: suppress a branch from display |
| `/api/session/{id}/hypothesis/{hid}/annotate` | POST | Add human annotation to a node |

---

## Session Replay Mode

To replay a historical session:

```
http://localhost:8766/?session=<session_id>&replay=1
```

Replay steps through events sequentially, showing the graph state at each step. Useful for post-audit review of how the pipeline reached its conclusions.

---

## WebSocket Event Stream

Connect to `/ws/live` to receive real-time events. Each message is a JSON object with the VizEvent structure plus a `diff` field showing which nodes changed.

Example message:
```json
{
  "event_type": "CONFIDENCE_SHIFT",
  "target_node_id": "HYP-003",
  "source_agent": "reentrancy_agent",
  "payload": {
    "old_confidence": 0.5,
    "new_confidence": 0.82,
    "reason": "CFG confirms no nonReentrant modifier on withdraw()"
  },
  "diff": {
    "changed": ["HYP-003"],
    "added": [],
    "edges_added": []
  }
}
```

---

## Detail Panel

Clicking a node in the frontend opens a detail panel showing:
- Full hypothesis text
- All evidence attached (code refs, KB matches, static analysis)
- Confidence history timeline
- Assumptions and blockers
- Human annotation (editable)
- Triage decision and reason (if CONVERGED or INVALIDATED)
