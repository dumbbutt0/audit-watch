#!/usr/bin/env python3
"""
hermes_bridge.py — Read-only adapter and memory writer for the Hermes root audit governor.

All public functions degrade silently when Hermes is disabled, misconfigured, or its
files are absent.  No function blocks for more than 2 seconds or raises to the caller.
"""
from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SCRIPTS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPTS_DIR.parent
_POLICY_PATH = _PROJECT_ROOT / "config" / "hermes_policy.json"

# Per-file write locks (keyed by resolved path string, mirrors viz/event_emitter.py pattern)
_file_locks: dict[str, threading.Lock] = {}
_locks_lock = threading.Lock()


def _get_file_lock(path: Path) -> threading.Lock:
    key = str(path.resolve())
    with _locks_lock:
        if key not in _file_locks:
            _file_locks[key] = threading.Lock()
        return _file_locks[key]


# ---------------------------------------------------------------------------
# Policy helpers
# ---------------------------------------------------------------------------

def _load_policy() -> dict:
    try:
        if not _POLICY_PATH.exists():
            return {}
        return json.loads(_POLICY_PATH.read_text())
    except Exception:
        return {}


def _get_hermes_root(policy: dict | None = None) -> Path | None:
    p = policy if policy is not None else _load_policy()
    if not p.get("hermes_enabled", False):
        return None
    root_str = p.get("hermes_root", "")
    if not root_str:
        return None
    try:
        root = (_PROJECT_ROOT / root_str).resolve()
        return root if root.exists() else None
    except Exception:
        return None


def is_hermes_enabled() -> bool:
    """Return True if Hermes is configured and enabled."""
    try:
        return _get_hermes_root() is not None
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Routing recommendation
# ---------------------------------------------------------------------------

def get_routing_recommendation(stage: str, context: dict) -> dict:
    """
    Return a routing recommendation dict for the given pipeline stage.

    Keys always present in return value:
      stage, recommendation, priority, confidence, source,
      priority_agents, escalate_to_human, escalation_reason, commands
    """
    _default = {
        "stage": stage,
        "recommendation": "",
        "priority": "NORMAL",
        "confidence": 0.0,
        "source": "default",
        "priority_agents": [],
        "escalate_to_human": False,
        "escalation_reason": "",
        "commands": [],
    }
    try:
        policy = _load_policy()
        if not policy.get("hermes_enabled", False):
            return _default
        if not policy.get("integration", {}).get("read_routing", True):
            return _default

        hermes_root = _get_hermes_root(policy)
        if hermes_root is None:
            return _default

        routing_path = hermes_root / "routing_policy.yaml"
        if not routing_path.exists():
            return _default

        try:
            import yaml  # optional dependency; graceful fallback
        except ImportError:
            return _default

        docs = list(yaml.safe_load_all(routing_path.read_text()))
        routing = next((d for d in docs if d and isinstance(d, dict) and "audit_priority_rules" in d), {})

        rec = dict(_default)
        rec["source"] = "routing_policy"

        # --- deadline-based audit priority rules ---
        deadline_days = context.get("deadline_days")
        submit_count = context.get("submit_count", 1)

        if deadline_days is not None:
            audit_rules = routing.get("audit_priority_rules", [])
            for rule in audit_rules:
                if not isinstance(rule, dict):
                    continue
                cond = rule.get("condition", "")
                if "days_to_deadline <= 5" in cond and deadline_days <= 5 and submit_count == 0:
                    rec["recommendation"] = rule.get("action", "")
                    rec["priority"] = rule.get("priority", "CRITICAL")
                    rec["confidence"] = 0.9
                    rec["commands"] = rule.get("commands", [])
                    break
                if "days_to_deadline <= 14" in cond and deadline_days <= 14:
                    rec["recommendation"] = rule.get("action", "")
                    rec["priority"] = rule.get("priority", "HIGH")
                    rec["confidence"] = 0.75
                    rec["commands"] = rule.get("commands", [])
                    break

        # --- stage-specific overrides ---
        stage_rules = routing.get("stage_routing_rules", {})
        budget_rules = routing.get("budget_mode_routing", {})
        active_mode = context.get("budget_mode", "normal")

        if stage == "pre_deep_analysis":
            if not rec["recommendation"] and stage_rules:
                layer_rule = stage_rules.get("layer_0", {})
                if layer_rule:
                    rec["recommendation"] = layer_rule.get("next_action", "")
                    rec["commands"] = layer_rule.get("commands", [])
                    rec["confidence"] = max(rec["confidence"], 0.6)

            # agent priority from memory
            protocol_type = context.get("protocol_type", "")
            audit_id = context.get("audit_id", "")
            if protocol_type:
                ap = get_agent_priority(protocol_type, audit_id)
                rec["priority_agents"] = ap.get("high_value_agents", [])

        elif stage == "pre_triage":
            mode_rule = budget_rules.get(active_mode, {})
            if mode_rule:
                forbidden = mode_rule.get("forbidden_stages", [])
                if "spawn_specialist_agents" in forbidden or "run_deep_analysis" in forbidden:
                    rec["recommendation"] = mode_rule.get("hermes_behavior", "")
                    rec["priority"] = "NORMAL"
                    rec["confidence"] = 0.8

            # check human escalation triggers relevant to triage
            human_triggers = routing.get("human_escalation_triggers", [])
            for trigger in human_triggers:
                if not isinstance(trigger, dict):
                    continue
                if trigger.get("name") == "triage_all_on_existing_audit":
                    if context.get("triage_all_on_existing"):
                        rec["escalate_to_human"] = True
                        rec["escalation_reason"] = trigger.get("action", "STOP. triage_findings.py --all on existing audit.")
                        rec["confidence"] = 1.0
                        break

        elif stage in ("pre_poc_escalation", "pre_submission_gate", "post_exploit_proved", "post_session"):
            # advisory pass-through: surface relevant stage rule if confidence still 0
            if rec["confidence"] == 0.0:
                layer_key = {
                    "pre_poc_escalation": "layer_5",
                    "pre_submission_gate": "layer_3",
                    "post_exploit_proved": "layer_6",
                    "post_session": "layer_9",
                }.get(stage)
                if layer_key and stage_rules.get(layer_key):
                    rule = stage_rules[layer_key]
                    rec["recommendation"] = rule.get("next_action", "")
                    rec["commands"] = rule.get("commands", [])
                    rec["confidence"] = 0.5

        return rec

    except Exception:
        return _default


# ---------------------------------------------------------------------------
# Agent priority (cross-audit memory)
# ---------------------------------------------------------------------------

def get_agent_priority(protocol_type: str, audit_id: str = "") -> dict:
    """
    Return agents ranked by historical confirmation rate for this protocol type.

    Return dict keys: high_value_agents, low_value_agents, data_points
    """
    _empty = {"high_value_agents": [], "low_value_agents": [], "data_points": 0}
    try:
        hermes_root = _get_hermes_root()
        if hermes_root is None:
            return _empty

        outcomes_path = hermes_root / "memory" / "agent_outcomes.jsonl"
        if not outcomes_path.exists():
            return _empty

        lines = [l.strip() for l in outcomes_path.read_text().splitlines() if l.strip()]
        if not lines:
            return _empty

        agent_stats: dict[str, dict] = {}
        for line in lines:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if protocol_type and rec.get("protocol_type", "") != protocol_type:
                continue
            agent = rec.get("agent", "")
            if not agent:
                continue
            s = agent_stats.setdefault(agent, {"confirmed": 0, "total": 0})
            s["total"] += 1
            if rec.get("outcome") == "confirmed":
                s["confirmed"] += 1

        if not agent_stats:
            return _empty

        ranked = sorted(
            agent_stats.items(),
            key=lambda kv: (kv[1]["confirmed"] / max(kv[1]["total"], 1)),
            reverse=True,
        )
        midpoint = max(1, len(ranked) // 2)
        return {
            "high_value_agents": [a for a, _ in ranked[:midpoint]],
            "low_value_agents": [a for a, _ in ranked[midpoint:]],
            "data_points": sum(s["total"] for _, s in agent_stats.items()),
        }
    except Exception:
        return _empty


# ---------------------------------------------------------------------------
# Skill recommendation
# ---------------------------------------------------------------------------

def get_skill_recommendation(protocol_type: str, static_json_path: str = "") -> dict:
    """
    Return skills ranked by historical effectiveness for this protocol type.

    Return dict keys: recommended_skills, data_points
    """
    _empty = {"recommended_skills": [], "data_points": 0}
    try:
        hermes_root = _get_hermes_root()
        if hermes_root is None:
            return _empty

        outcomes_path = hermes_root / "memory" / "skill_outcomes.jsonl"
        if not outcomes_path.exists():
            return _empty

        lines = [l.strip() for l in outcomes_path.read_text().splitlines() if l.strip()]
        if not lines:
            return _empty

        skill_stats: dict[str, dict] = {}
        for line in lines:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if protocol_type and rec.get("protocol_type", "") != protocol_type:
                continue
            skill = rec.get("skill", "")
            if not skill:
                continue
            s = skill_stats.setdefault(skill, {"confirmed": 0, "total": 0})
            s["total"] += 1
            if rec.get("outcome") == "confirmed":
                s["confirmed"] += 1

        if not skill_stats:
            return _empty

        ranked = sorted(
            skill_stats.items(),
            key=lambda kv: (kv[1]["confirmed"] / max(kv[1]["total"], 1)),
            reverse=True,
        )
        return {
            "recommended_skills": [s for s, _ in ranked],
            "data_points": sum(s["total"] for _, s in skill_stats.items()),
        }
    except Exception:
        return _empty


# ---------------------------------------------------------------------------
# Human escalation check
# ---------------------------------------------------------------------------

_EVENT_TO_TRIGGER = {
    "sandbox_flag": "sandbox_flags_raised",
    "novel_pattern": "novel_pattern_no_kb_precedent",
    "critical_no_poc": "critical_without_l2_poc",
    "ground_truth_write": "ground_truth_write_attempted",
    "submission_ready_first": "submission_ready_first_time",
    "gate_override_requested": "invalidation_tag_override_requested",
    "triage_all_on_existing": "triage_all_on_existing_audit",
}


def should_escalate_to_human(event_type: str, context: dict) -> tuple[bool, str]:
    """
    Return (should_escalate: bool, reason: str).

    Uses human_escalation_triggers from routing_policy.yaml when available;
    falls back to hardcoded safety defaults for the seven critical triggers.
    """
    trigger_name = _EVENT_TO_TRIGGER.get(event_type, "")

    # Always-on safety defaults (independent of YAML loading)
    _always_escalate = {
        "sandbox_flags_raised": "sandbox_check.py returned non-zero — stop and report flags to human.",
        "ground_truth_write_attempted": "ground_truth.jsonl is human-only write path — stop.",
        "triage_all_on_existing_audit": "triage_findings.py --all overwrites submit.jsonl — stop.",
        "invalidation_tag_override_requested": "Invalidation tag override requires human reviewer — stop.",
    }
    if trigger_name in _always_escalate:
        return True, _always_escalate[trigger_name]

    try:
        hermes_root = _get_hermes_root()
        if hermes_root is None:
            return False, ""

        try:
            import yaml
        except ImportError:
            return False, ""

        routing_path = hermes_root / "routing_policy.yaml"
        if not routing_path.exists():
            return False, ""

        docs = list(yaml.safe_load_all(routing_path.read_text()))
        routing = next((d for d in docs if d and isinstance(d, dict) and "human_escalation_triggers" in d), {})
        triggers = routing.get("human_escalation_triggers", [])

        for trigger in triggers:
            if not isinstance(trigger, dict):
                continue
            if trigger.get("name") != trigger_name:
                continue
            action = trigger.get("action", "Escalate to human.")

            # Context-dependent checks for non-always triggers
            if trigger_name == "novel_pattern_no_kb_precedent":
                kb_sim = context.get("kb_similarity", 1.0)
                severity = context.get("severity", "Low")
                if kb_sim < 0.4 and severity in ("High", "Critical"):
                    return True, action
                return False, ""

            if trigger_name == "critical_without_l2_poc":
                if context.get("severity") == "Critical" and context.get("poc_level", 2) < 2:
                    return True, action
                return False, ""

            if trigger_name == "submission_ready_first_time":
                if context.get("first_submission"):
                    return True, action
                return False, ""

            if trigger_name == "compound_chain_no_comp_match":
                if context.get("is_compound") and not context.get("comp_pattern_matched"):
                    return True, action
                return False, ""

            return True, action

        return False, ""

    except Exception:
        return False, ""


# ---------------------------------------------------------------------------
# Memory writer
# ---------------------------------------------------------------------------

def write_memory_event(event_type: str, payload: dict) -> None:
    """
    Append one JSON line to ../hermes/memory/events.jsonl.

    Thread-safe; never raises; no-ops when Hermes is disabled.
    """
    try:
        policy = _load_policy()
        if not policy.get("hermes_enabled", False):
            return
        if not policy.get("integration", {}).get("write_memory", True):
            return

        hermes_root = _get_hermes_root(policy)
        if hermes_root is None:
            return

        events_path = hermes_root / "memory" / "events.jsonl"
        events_path.parent.mkdir(parents=True, exist_ok=True)

        record = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **payload,
        }
        line = json.dumps(record, default=str) + "\n"

        lock = _get_file_lock(events_path)
        with lock:
            with events_path.open("a", encoding="utf-8") as fh:
                fh.write(line)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Audit recap writer
# ---------------------------------------------------------------------------

def write_audit_recap(session_summary: dict) -> None:
    """
    Write a session recap JSON to ../hermes/verdicts/<audit_id>_recap.json.

    Never raises; no-ops when Hermes is disabled or write_recap is false.
    """
    try:
        policy = _load_policy()
        if not policy.get("hermes_enabled", False):
            return
        if not policy.get("integration", {}).get("write_recap", True):
            return

        hermes_root = _get_hermes_root(policy)
        if hermes_root is None:
            return

        verdicts_dir = hermes_root / "verdicts"
        verdicts_dir.mkdir(parents=True, exist_ok=True)

        audit_id = session_summary.get("audit_id", "unknown")
        recap_path = verdicts_dir / f"{audit_id}_recap.json"

        record = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            **session_summary,
        }
        recap_path.write_text(json.dumps(record, indent=2, default=str))
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Context loader (for Hermes orientation, read-only)
# ---------------------------------------------------------------------------

def load_hermes_context() -> dict:
    """
    Return a lightweight dict with role summary and routing rule names.

    Used at session start to orient a new Claude session as Hermes.
    """
    _empty: dict[str, Any] = {"role_summary": "", "routing_rule_names": [], "loaded": False}
    try:
        hermes_root = _get_hermes_root()
        if hermes_root is None:
            return _empty

        role_path = hermes_root / "role.md"
        role_summary = ""
        if role_path.exists():
            role_summary = role_path.read_text()[:500]

        routing_path = hermes_root / "routing_policy.yaml"
        rule_names: list[str] = []
        if routing_path.exists():
            try:
                import yaml
                docs = list(yaml.safe_load_all(routing_path.read_text()))
                routing = next((d for d in docs if d and isinstance(d, dict) and "audit_priority_rules" in d), {})
                for rule in routing.get("audit_priority_rules", []):
                    if isinstance(rule, dict) and "name" in rule:
                        rule_names.append(rule["name"])
            except Exception:
                pass

        return {"role_summary": role_summary, "routing_rule_names": rule_names, "loaded": True}
    except Exception:
        return _empty
