"""
viz/graph_state.py — In-memory reasoning graph state manager.

Replays VizEvents to maintain the live graph. Provides snapshot() and diff()
for WebSocket broadcasting.
"""

from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Any


class GraphState:
    """
    Maintains the complete in-memory reasoning graph for one audit session.
    Thread-safe: uses a single lock for all mutations.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._nodes: dict[str, dict] = {}   # node_id → node dict
        self._edges: list[dict] = []
        self._event_count = 0
        self._hyp_counter = 0
        self._branch_counter = 0
        self._evidence_counter = 0
        self._edge_counter = 0

    # ──────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────

    def apply_event(self, event: dict) -> dict:
        """
        Mutate graph state based on a VizEvent.
        Returns a diff dict: {changed: [...], added: [...], edges_added: [...]}
        """
        with self._lock:
            self._event_count += 1
            return self._dispatch(event)

    def snapshot(self) -> dict:
        """Return full graph as JSON-serialisable dict."""
        with self._lock:
            return {
                "nodes": list(self._nodes.values()),
                "edges": list(self._edges),
                "metrics": self._compute_metrics(),
                "event_count": self._event_count,
            }

    def diff(self, changed: list[str]) -> dict:
        """Return only the listed node IDs plus current metrics."""
        with self._lock:
            return {
                "nodes": [self._nodes[nid] for nid in changed if nid in self._nodes],
                "edges": [],
                "metrics": self._compute_metrics(),
            }

    def metrics(self) -> dict:
        with self._lock:
            return self._compute_metrics()

    def suppress_node(self, node_id: str) -> bool:
        """Human-in-the-loop: mark a branch/hypothesis as PRUNED."""
        with self._lock:
            if node_id not in self._nodes:
                return False
            node = self._nodes[node_id]
            node["status"] = "PRUNED"
            return True

    def annotate_node(self, node_id: str, annotation: str) -> bool:
        """Attach a human annotation to a node."""
        with self._lock:
            if node_id not in self._nodes:
                return False
            self._nodes[node_id]["annotation"] = annotation
            return True

    # ──────────────────────────────────────────────────────────────
    # Event dispatch
    # ──────────────────────────────────────────────────────────────

    def _dispatch(self, event: dict) -> dict:
        etype = event.get("event_type", "")
        handlers = {
            "HYPOTHESIS_BORN":   self._on_hypothesis_born,
            "BRANCH_CREATED":    self._on_branch_created,
            "EVIDENCE_ATTACHED": self._on_evidence_attached,
            "CONFIDENCE_SHIFT":  self._on_confidence_shift,
            "BRANCH_INVALIDATED": self._on_branch_invalidated,
            "EXPLOIT_PROVED":    self._on_exploit_proved,
            "EXPLOIT_FAILED":    self._on_exploit_failed,
            "KB_MATCH":          self._on_kb_match,
            "AGENT_SPAWNED":     self._on_agent_spawned,
            "TRIAGER_DECISION":  self._on_triager_decision,
            "NODE_SUPPRESSED":   self._on_node_suppressed,
            "HUMAN_ANNOTATE":    self._on_human_annotate,
            # Intercept gate events — tracked in audit trail, no graph mutation
            "GATE_OPENED":       self._on_gate_event,
            "GATE_RELEASED":     self._on_gate_event,
            "GATE_MODIFIED":     self._on_gate_event,
            "GATE_DROPPED":      self._on_gate_dropped,
        }
        handler = handlers.get(etype)
        if handler:
            return handler(event)
        return {"changed": [], "added": [], "edges_added": []}

    # ──────────────────────────────────────────────────────────────
    # Event handlers
    # ──────────────────────────────────────────────────────────────

    def _on_hypothesis_born(self, event: dict) -> dict:
        p = event.get("payload") or {}
        target_id = event.get("target_node_id") or self._next_hyp_id()

        if target_id in self._nodes:
            # Already exists — treat as update
            node = self._nodes[target_id]
            old_conf = node.get("confidence", 0.5)
            new_conf = p.get("confidence", old_conf)
            if new_conf != old_conf:
                node["confidence"] = new_conf
                node["confidence_history"].append(self._conf_event(
                    old_conf, new_conf, "re-seen by agent", event.get("source_agent", "")))
            return {"changed": [target_id], "added": [], "edges_added": []}

        node = {
            "id": target_id,
            "node_type": "hypothesis",
            "label": p.get("label", p.get("hypothesis_text", "")[:60] or target_id),
            "hypothesis_text": p.get("hypothesis_text", ""),
            "agent_origin": event.get("source_agent", "unknown"),
            "born_at": event.get("timestamp", _now()),
            "status": "LIVE",
            "confidence": float(p.get("confidence", 0.5)),
            "severity_ceiling": p.get("severity_ceiling", "UNKNOWN"),
            "attacker_reachable": p.get("attacker_reachable", None),
            "exploit_class": p.get("exploit_class", ""),
            "linked_contracts": p.get("linked_contracts", []),
            "assumptions": [],
            "blockers": [],
            "kb_matches": [],
            "invalidation_reason": None,
            "confidence_history": [],
            "annotation": None,
        }
        self._nodes[target_id] = node
        return {"changed": [], "added": [target_id], "edges_added": []}

    def _on_branch_created(self, event: dict) -> dict:
        p = event.get("payload") or {}
        branch_id = event.get("target_node_id") or self._next_branch_id()
        parent_id = p.get("parent_hypothesis", "")

        node = {
            "id": branch_id,
            "node_type": "branch",
            "parent_hypothesis": parent_id,
            "branch_trigger": p.get("branch_trigger", ""),
            "branch_type": p.get("branch_type", "EXPLOIT_PATH"),
            "status": "LIVE",
            "depth": int(p.get("depth", 1)),
            "spawned_by": event.get("source_agent", "unknown"),
            "children": [],
            "label": p.get("label", p.get("branch_trigger", branch_id)[:60]),
            "born_at": event.get("timestamp", _now()),
            "annotation": None,
        }
        self._nodes[branch_id] = node

        edges_added = []
        if parent_id and parent_id in self._nodes:
            edge = self._make_edge(parent_id, branch_id, "SPAWNED")
            self._edges.append(edge)
            edges_added.append(edge["id"])

        return {"changed": [], "added": [branch_id], "edges_added": edges_added}

    def _on_evidence_attached(self, event: dict) -> dict:
        p = event.get("payload") or {}
        ev_id = event.get("target_node_id") or self._next_evidence_id()
        attached_to = p.get("attached_to", "")

        node = {
            "id": ev_id,
            "node_type": "evidence",
            "attached_to": attached_to,
            "evidence_type": p.get("evidence_type", "AGENT_REASONING"),
            "content": p.get("content", ""),
            "source": p.get("source", event.get("source_agent", "")),
            "confidence_delta": float(p.get("confidence_delta", 0.0)),
            "timestamp": event.get("timestamp", _now()),
        }
        self._nodes[ev_id] = node

        edges_added = []
        if attached_to and attached_to in self._nodes:
            # Apply confidence delta to parent
            parent = self._nodes[attached_to]
            delta = node["confidence_delta"]
            if delta != 0.0:
                old_conf = parent.get("confidence", 0.5)
                new_conf = max(0.0, min(1.0, old_conf + delta))
                parent["confidence"] = new_conf
                parent.setdefault("confidence_history", []).append(
                    self._conf_event(old_conf, new_conf, "evidence attached", ev_id))

            edge = self._make_edge(attached_to, ev_id, "EVIDENCE")
            self._edges.append(edge)
            edges_added.append(edge["id"])

        return {"changed": [attached_to] if attached_to in self._nodes else [],
                "added": [ev_id], "edges_added": edges_added}

    def _on_confidence_shift(self, event: dict) -> dict:
        p = event.get("payload") or {}
        target_id = event.get("target_node_id", "")

        node = self._nodes.get(target_id)
        if not node:
            # Create a minimal hypothesis node to hold the shift
            node = self._make_minimal_hypothesis(target_id, event)
            self._nodes[target_id] = node

        old_conf = float(p.get("old_confidence", node.get("confidence", 0.5)))
        new_conf = float(p.get("new_confidence", old_conf))
        node["confidence"] = new_conf
        node.setdefault("confidence_history", []).append(
            self._conf_event(old_conf, new_conf,
                             p.get("reason", "confidence updated"),
                             event.get("source_agent", "")))

        # Update severity_ceiling if provided
        if p.get("calibrated_severity"):
            node["severity_ceiling"] = p["calibrated_severity"].upper()

        return {"changed": [target_id], "added": [], "edges_added": []}

    def _on_branch_invalidated(self, event: dict) -> dict:
        p = event.get("payload") or {}
        target_id = event.get("target_node_id", "")

        node = self._nodes.get(target_id)
        if not node:
            node = self._make_minimal_hypothesis(target_id, event)
            self._nodes[target_id] = node

        node["status"] = "INVALIDATED"
        node["invalidation_reason"] = p.get("reason", "rejected by triage")

        # Drive confidence to near-zero
        old_conf = node.get("confidence", 0.5)
        node["confidence"] = 0.05
        node.setdefault("confidence_history", []).append(
            self._conf_event(old_conf, 0.05, "invalidated: " + node["invalidation_reason"],
                             event.get("source_agent", "")))

        return {"changed": [target_id], "added": [], "edges_added": []}

    def _on_exploit_proved(self, event: dict) -> dict:
        p = event.get("payload") or {}
        target_id = event.get("target_node_id", "")

        node = self._nodes.get(target_id)
        if not node:
            node = self._make_minimal_hypothesis(target_id, event)
            self._nodes[target_id] = node

        node["status"] = "CONVERGED"
        node["confidence"] = 1.0
        node.setdefault("confidence_history", []).append(
            self._conf_event(node.get("confidence", 0.5), 1.0, "PoC PROVED",
                             event.get("source_agent", "")))

        # Attach PoC evidence node
        ev_id = self._next_evidence_id()
        evidence = {
            "id": ev_id,
            "node_type": "evidence",
            "attached_to": target_id,
            "evidence_type": "POC_RESULT",
            "content": p.get("evidence_summary", f"PoC proved at level {p.get('runtime_level', '?')}"),
            "source": p.get("test_file", ""),
            "confidence_delta": 0.5,
            "timestamp": event.get("timestamp", _now()),
        }
        self._nodes[ev_id] = evidence
        edge = self._make_edge(target_id, ev_id, "EVIDENCE")
        self._edges.append(edge)

        return {"changed": [target_id], "added": [ev_id], "edges_added": [edge["id"]]}

    def _on_exploit_failed(self, event: dict) -> dict:
        p = event.get("payload") or {}
        target_id = event.get("target_node_id", "")

        node = self._nodes.get(target_id)
        if not node:
            node = self._make_minimal_hypothesis(target_id, event)
            self._nodes[target_id] = node

        node["status"] = "PRUNED"
        old_conf = node.get("confidence", 0.5)
        node["confidence"] = max(0.1, old_conf - 0.3)
        node.setdefault("confidence_history", []).append(
            self._conf_event(old_conf, node["confidence"],
                             "PoC FAILED: " + (p.get("failure_reason") or p.get("status", "")),
                             event.get("source_agent", "")))

        return {"changed": [target_id], "added": [], "edges_added": []}

    def _on_kb_match(self, event: dict) -> dict:
        p = event.get("payload") or {}
        target_id = event.get("target_node_id", "")

        kb_match = {
            "solodit_id": p.get("solodit_id", ""),
            "title": p.get("title", ""),
            "similarity_score": float(p.get("similarity_score", 0.0)),
            "exploit_pattern": p.get("exploit_pattern", p.get("query", "")),
            "historical_severity": p.get("historical_severity", ""),
            "protocol_type": p.get("protocol_type", ""),
        }

        # Create a KB evidence node
        ev_id = self._next_evidence_id()
        ev_node = {
            "id": ev_id,
            "node_type": "evidence",
            "attached_to": target_id,
            "evidence_type": "SOLODIT_MATCH",
            "content": f"{kb_match['title']} (similarity: {kb_match['similarity_score']:.2f})",
            "source": kb_match["solodit_id"],
            "confidence_delta": round((kb_match["similarity_score"] - 0.5) * 0.4, 3),
            "timestamp": event.get("timestamp", _now()),
        }
        self._nodes[ev_id] = ev_node

        edges_added = []
        if target_id and target_id in self._nodes:
            node = self._nodes[target_id]
            node.setdefault("kb_matches", []).append(kb_match)
            # Boost confidence
            old_conf = node.get("confidence", 0.5)
            delta = ev_node["confidence_delta"]
            new_conf = max(0.0, min(1.0, old_conf + delta))
            node["confidence"] = new_conf
            node.setdefault("confidence_history", []).append(
                self._conf_event(old_conf, new_conf,
                                 f"KB_MATCH: {kb_match['title'][:40]}",
                                 "retriever"))
            edge = self._make_edge(target_id, ev_id, "KB_MATCH")
            self._edges.append(edge)
            edges_added.append(edge["id"])

        return {"changed": [target_id] if target_id in self._nodes else [],
                "added": [ev_id], "edges_added": edges_added}

    def _on_agent_spawned(self, event: dict) -> dict:
        p = event.get("payload") or {}
        parent_id = event.get("target_node_id") or p.get("parent_hypothesis", "")
        branch_id = self._next_branch_id()

        node = {
            "id": branch_id,
            "node_type": "branch",
            "parent_hypothesis": parent_id,
            "branch_trigger": p.get("branch_trigger", p.get("thread_id", "")),
            "branch_type": "EXPLOIT_PATH",
            "status": "LIVE",
            "depth": 1,
            "spawned_by": event.get("source_agent", "unknown"),
            "children": [],
            "label": p.get("spawned_agent", "sub-agent")[:60],
            "born_at": event.get("timestamp", _now()),
            "annotation": None,
        }
        self._nodes[branch_id] = node

        edges_added = []
        if parent_id and parent_id in self._nodes:
            edge = self._make_edge(parent_id, branch_id, "SPAWNED")
            self._edges.append(edge)
            edges_added.append(edge["id"])

        return {"changed": [], "added": [branch_id], "edges_added": edges_added}

    def _on_triager_decision(self, event: dict) -> dict:
        p = event.get("payload") or {}
        target_id = event.get("target_node_id", "")
        decision = p.get("decision", "")

        node = self._nodes.get(target_id)
        if not node:
            node = self._make_minimal_hypothesis(target_id, event)
            self._nodes[target_id] = node

        if decision == "submit":
            node["status"] = "ESCALATED"
            old_conf = node.get("confidence", 0.5)
            node["confidence"] = max(old_conf, 0.75)
            node.setdefault("confidence_history", []).append(
                self._conf_event(old_conf, node["confidence"],
                                 "triage: SUBMIT", "triage"))
        elif decision in ("rejected", "reject"):
            node["status"] = "INVALIDATED"
            node["invalidation_reason"] = p.get("reason", "triage rejected")
            old_conf = node.get("confidence", 0.5)
            node["confidence"] = 0.05
            node.setdefault("confidence_history", []).append(
                self._conf_event(old_conf, 0.05, "triage: REJECTED", "triage"))
        elif decision == "poc_required":
            node["status"] = "LIVE"
            old_conf = node.get("confidence", 0.5)
            node["confidence"] = max(old_conf, 0.6)
            node.setdefault("confidence_history", []).append(
                self._conf_event(old_conf, node["confidence"],
                                 "triage: POC_REQUIRED", "triage"))

        return {"changed": [target_id], "added": [], "edges_added": []}

    def _on_node_suppressed(self, event: dict) -> dict:
        target_id = event.get("target_node_id", "")
        if target_id in self._nodes:
            self._nodes[target_id]["status"] = "PRUNED"
            return {"changed": [target_id], "added": [], "edges_added": []}
        return {"changed": [], "added": [], "edges_added": []}

    def _on_human_annotate(self, event: dict) -> dict:
        p = event.get("payload") or {}
        target_id = event.get("target_node_id", "")
        if target_id in self._nodes:
            self._nodes[target_id]["annotation"] = p.get("annotation", "")
            return {"changed": [target_id], "added": [], "edges_added": []}
        return {"changed": [], "added": [], "edges_added": []}

    def _on_gate_event(self, event: dict) -> dict:
        # Gate events are audit-trail only — no graph state mutation
        return {"changed": [], "added": [], "edges_added": []}

    def _on_gate_dropped(self, event: dict) -> dict:
        # A dropped event: mark the target node as PRUNED if it exists
        p = event.get("payload") or {}
        target_id = event.get("target_node_id", "")
        node = self._nodes.get(target_id)
        if node:
            node["status"] = "PRUNED"
            node["invalidation_reason"] = "dropped by intercept"
            return {"changed": [target_id], "added": [], "edges_added": []}
        return {"changed": [], "added": [], "edges_added": []}

    # ──────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────

    def _next_hyp_id(self) -> str:
        self._hyp_counter += 1
        return f"HYP-{self._hyp_counter:03d}"

    def _next_branch_id(self) -> str:
        self._branch_counter += 1
        return f"BR-{self._branch_counter:03d}"

    def _next_evidence_id(self) -> str:
        self._evidence_counter += 1
        return f"EV-{self._evidence_counter:03d}"

    def _make_edge(self, source: str, target: str, edge_type: str) -> dict:
        self._edge_counter += 1
        return {
            "id": f"E-{self._edge_counter:04d}",
            "source": source,
            "target": target,
            "edge_type": edge_type,
            "strength": 0.5,
        }

    def _make_minimal_hypothesis(self, node_id: str, event: dict) -> dict:
        p = event.get("payload") or {}
        return {
            "id": node_id,
            "node_type": "hypothesis",
            "label": node_id,
            "hypothesis_text": p.get("hypothesis_text", ""),
            "agent_origin": event.get("source_agent", "unknown"),
            "born_at": event.get("timestamp", _now()),
            "status": "LIVE",
            "confidence": float(p.get("confidence", 0.5)),
            "severity_ceiling": p.get("severity_ceiling", "UNKNOWN"),
            "attacker_reachable": None,
            "exploit_class": p.get("exploit_class", ""),
            "linked_contracts": [],
            "assumptions": [],
            "blockers": [],
            "kb_matches": [],
            "invalidation_reason": None,
            "confidence_history": [],
            "annotation": None,
        }

    @staticmethod
    def _conf_event(old: float, new: float, reason: str, triggered_by: str) -> dict:
        return {
            "timestamp": _now(),
            "old_confidence": round(old, 3),
            "new_confidence": round(new, 3),
            "reason": reason,
            "triggered_by": triggered_by,
        }

    def _compute_metrics(self) -> dict:
        nodes = list(self._nodes.values())
        hyps = [n for n in nodes if n.get("node_type") == "hypothesis"]
        branches = [n for n in nodes if n.get("node_type") == "branch"]
        evidences = [n for n in nodes if n.get("node_type") == "evidence"]

        live = sum(1 for n in hyps + branches if n.get("status") == "LIVE")
        invalidated = sum(1 for n in hyps + branches if n.get("status") == "INVALIDATED")
        converged = sum(1 for n in hyps if n.get("status") == "CONVERGED")
        escalated = sum(1 for n in hyps if n.get("status") == "ESCALATED")
        pruned = sum(1 for n in branches if n.get("status") == "PRUNED")

        confs = [n.get("confidence", 0.5) for n in hyps]
        conf_dist = {
            "high": sum(1 for c in confs if c >= 0.7),
            "medium": sum(1 for c in confs if 0.4 <= c < 0.7),
            "low": sum(1 for c in confs if c < 0.4),
        }

        kb_total = sum(len(n.get("kb_matches", [])) for n in hyps)

        return {
            "total_hypotheses": len(hyps),
            "active_branches": len([b for b in branches if b.get("status") == "LIVE"]),
            "pruned_branches": pruned,
            "proved_exploits": converged,
            "live_count": live,
            "invalidated_count": invalidated,
            "converged_count": converged,
            "escalated_count": escalated,
            "confidence_distribution": conf_dist,
            "kb_matches_total": kb_total,
            "total_events_processed": self._event_count,
            "evidence_nodes": len(evidences),
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
