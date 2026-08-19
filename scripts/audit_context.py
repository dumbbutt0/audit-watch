#!/usr/bin/env python3
"""
audit_context.py — Central audit workspace path resolution and shared utilities.

All pipeline scripts import from this module instead of constructing paths
directly. The shared knowledge base (kb/), agents/, prompts/, schemas/, and
templates/ stay at the project root and are NOT managed here.

Shared utilities (import to avoid duplication across 24+ scripts):
    load_env()       — load .env into os.environ (idempotent)
    load_jsonl(path) — parse a JSONL file into list[dict]
    DEFAULT_MODEL    — canonical Claude model for all pipeline scripts
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_CONFIG_DIR = _PROJECT_ROOT / "config"
_ACTIVE_FILE = _CONFIG_DIR / "active_audit.json"
_AUDITS_DIR = _PROJECT_ROOT / "audits"
_REGISTRY_FILE = _AUDITS_DIR / "registry.json"

# ─── Shared constants ─────────────────────────────────────────────────────────

DEFAULT_MODEL = "claude-sonnet-4-6"

# ─── Shared utilities ─────────────────────────────────────────────────────────

_env_loaded = False


def load_env(env_file: str = ".env") -> None:
    """Load a .env file into os.environ (idempotent; skips already-set keys)."""
    global _env_loaded
    p = Path(env_file)
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip("\"'"))
    _env_loaded = True


def load_jsonl(path: "Path | str") -> list[dict]:
    """Parse a JSONL file. Returns [] on missing file or parse errors (non-fatal)."""
    p = Path(path)
    if not p.exists():
        return []
    records: list[dict] = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return records


def load_jsonl_by_id(
    path: "Path | str",
    id_field: str = "finding_id",
) -> dict[str, dict]:
    """Load a JSONL file into a dict keyed by id_field."""
    return {r[id_field]: r for r in load_jsonl(path) if id_field in r}

_AUDIT_SUBDIRS = [
    # ── Human-facing layer (added 2026-05 refinement; views over the substrate) ──
    "contracts",            # primary audited source (intake)
    "contracts/_sources",   # extra downloaded repos/dirs (non-primary)
    "notes",                # contract_context.md, static_analysis.md, points_of_interest.jsonl
    "findings/raw",         # human view: copy of output/findings_*.json
    "findings/validated",   # human view: copy of data/triage/<id>.md
    "status",               # human view: status.json, session.json
    # ── Machine substrate (canonical for scripts; do not relocate) ──
    "output",
    "output/poc_completeness",
    "output/poc_upgrade_tasks",
    "output/submissions",
    "data/triage",
    "data/poc_queue",
    "data/exploitability",
    "data/duplicates",
    "data/severity",
    "data/runtime_poc",
    "data/judge_simulation",
    "data/quality_checklist",
    "data/invariants",
    "data/interactions",
    "data/threads",
    "data/findings",
    "data/learning",
    "data/fp_autopsies",
    "data/evaluation",
    "pocs",
    "reports",
]


# ─── Registry helpers ────────────────────────────────────────────────────────

def _read_registry() -> dict:
    if not _REGISTRY_FILE.exists():
        return {"audits": [], "updated_at": _now()}
    try:
        return json.loads(_REGISTRY_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {"audits": [], "updated_at": _now()}


def _write_registry(reg: dict) -> None:
    _AUDITS_DIR.mkdir(parents=True, exist_ok=True)
    reg["updated_at"] = _now()
    _REGISTRY_FILE.write_text(json.dumps(reg, indent=2))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─── Active audit ────────────────────────────────────────────────────────────

def get_active_audit() -> dict:
    """Return the active audit config dict.

    Returns {"audit_id": None} if no audit is set — never raises.
    This allows solodit_scraper.py to import without failure before migration.
    """
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not _ACTIVE_FILE.exists():
        return {"audit_id": None, "audit_root": None}
    try:
        data = json.loads(_ACTIVE_FILE.read_text())
        if not data.get("audit_id"):
            return {"audit_id": None, "audit_root": None}
        return data
    except (json.JSONDecodeError, OSError):
        return {"audit_id": None, "audit_root": None}


def get_audit_root() -> Path:
    """Return the Path to the active audit workspace.

    Raises RuntimeError with an actionable message when no audit is active.
    """
    cfg = get_active_audit()
    audit_id = cfg.get("audit_id")
    if not audit_id:
        raise RuntimeError(
            "No active audit. Run:\n"
            "  python scripts/migrate_to_audit.py      (first time, migrates K2 data)\n"
            "  python scripts/audit_manager.py new <id>  (create a fresh audit)"
        )
    return _AUDITS_DIR / audit_id


def audit_path(*parts: str) -> Path:
    """Resolve a path relative to the active audit workspace.

    Creates parent directories automatically so callers can open files
    immediately after calling this function.

    Examples:
        audit_path("output")                       -> audits/k2-.../output
        audit_path("data/triage")                  -> audits/k2-.../data/triage
        audit_path("data/triage", "submit.jsonl")  -> audits/k2-.../data/triage/submit.jsonl
    """
    root = get_audit_root()
    p = root.joinpath(*parts)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


# ─── Audit metadata ──────────────────────────────────────────────────────────

def get_audit_meta() -> dict:
    """Read meta.json for the active audit. Returns {} on failure."""
    try:
        root = get_audit_root()
    except RuntimeError:
        return {}
    meta_path = root / "meta.json"
    if not meta_path.exists():
        return {}
    try:
        return json.loads(meta_path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


_KNOWN_LANGUAGES = {"solidity", "rust", "vyper", "move", "ton"}


def audit_language(audit_id: str | None = None) -> str:
    """Normalized language of an audit ('solidity' default). Cross-language routing spine: the coverage manifest,
    full-coverage gate, static step, and ite-audit specialist routing branch on this. Reads meta.json's
    `language` field (set by create_audit_workspace / ingest_contest). Falls back to 'solidity' for any
    unknown/missing value so the Solidity path is byte-behavior-unchanged when language is unset."""
    meta = {}
    if audit_id is None:
        meta = get_audit_meta()
    else:
        try:
            p = Path(__file__).resolve().parents[1] / "audits" / audit_id / "meta.json"
            if p.exists():
                meta = json.loads(p.read_text())
        except (json.JSONDecodeError, OSError):
            meta = {}
    lang = str(meta.get("language", "") or "").strip().lower()
    return lang if lang in _KNOWN_LANGUAGES else "solidity"


def get_contract_path() -> Path | None:
    """Return the path to the contract source for this audit.

    Prefers the workspace-local primary contract dir (set by intake_contracts.py);
    falls back to the legacy meta.contract_path for audits created before the
    2026-05 refinement. Backward-compatible.
    """
    primary = get_primary_contract_dir()
    if primary is not None and primary.exists():
        return primary
    meta = get_audit_meta()
    cp = meta.get("contract_path")
    if not cp:
        return None
    p = Path(cp)
    if not p.is_absolute():
        p = _PROJECT_ROOT / p
    return p


def get_primary_contract_dir() -> Path | None:
    """Return the workspace-local primary contract directory, or None if unset.

    Resolves meta.primary_contract_dir (a path relative to the audit root, e.g.
    'contracts/protocol') against the active audit workspace.
    """
    meta = get_audit_meta()
    rel = meta.get("primary_contract_dir")
    if not rel:
        return None
    try:
        root = get_audit_root()
    except RuntimeError:
        return None
    return root / rel


def set_primary_contract_dir(rel_path: str) -> None:
    """Record the primary contract directory in meta.json (relative to audit root).

    Example: set_primary_contract_dir("contracts/protocol").
    """
    root = get_audit_root()
    meta_path = root / "meta.json"
    meta: dict = {}
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text())
        except (json.JSONDecodeError, OSError):
            meta = {}
    meta["primary_contract_dir"] = rel_path
    meta_path.write_text(json.dumps(meta, indent=2))


# ─── List / switch / create ──────────────────────────────────────────────────

def list_audits() -> list[dict]:
    """Return all audits from registry.json."""
    return _read_registry().get("audits", [])


def _update_output_symlink(audit_id: str) -> None:
    """Keep the root output/ symlink pointed at the active audit's output directory.

    This lets agent templates use the bare path 'output/' without knowing
    which audit is active — the symlink always resolves to the right workspace.
    """
    symlink = _PROJECT_ROOT / "output"
    target = Path("audits") / audit_id / "output"  # relative — stays valid after moves
    if symlink.is_symlink():
        symlink.unlink()
    elif symlink.exists():
        return  # real directory present; don't clobber it
    symlink.symlink_to(target)


def switch_audit(audit_id: str) -> dict:
    """Set the active audit. Raises ValueError if audit_id not in registry."""
    reg = _read_registry()
    known_ids = {a["audit_id"] for a in reg.get("audits", [])}
    if audit_id not in known_ids:
        raise ValueError(
            f"Audit '{audit_id}' not found in registry. "
            f"Known: {sorted(known_ids) or '(none)'}"
        )
    audit_root = _AUDITS_DIR / audit_id
    cfg = {"audit_id": audit_id, "audit_root": str(audit_root), "switched_at": _now()}
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    _ACTIVE_FILE.write_text(json.dumps(cfg, indent=2))
    # Update last_active in registry
    for entry in reg.get("audits", []):
        if entry["audit_id"] == audit_id:
            entry["last_active"] = _now()
            break
    _write_registry(reg)
    _update_output_symlink(audit_id)
    return cfg


def create_audit_workspace(audit_id: str, meta: dict) -> Path:
    """Create a new audit workspace with all required subdirectories.

    Writes meta.json and registers the audit in registry.json.
    Does NOT switch the active audit.
    Raises ValueError if the workspace already exists.
    """
    audit_root = _AUDITS_DIR / audit_id
    if audit_root.exists():
        raise ValueError(f"Workspace already exists: {audit_root}")

    for subdir in _AUDIT_SUBDIRS:
        (audit_root / subdir).mkdir(parents=True, exist_ok=True)

    full_meta = {
        "audit_id":       audit_id,
        "name":           meta.get("name", audit_id),
        "contest":        meta.get("contest", ""),
        "platform":       meta.get("platform", ""),
        "language":       meta.get("language", ""),
        "framework":      meta.get("framework", ""),
        "contract_path":  meta.get("contract_path", ""),
        "status":         meta.get("status", "active"),
        "start_date":     meta.get("start_date", _now()),
        "deadline":       meta.get("deadline", ""),
        "created_at":     _now(),
    }
    (audit_root / "meta.json").write_text(json.dumps(full_meta, indent=2))

    reg = _read_registry()
    reg.setdefault("audits", [])
    reg["audits"] = [a for a in reg["audits"] if a["audit_id"] != audit_id]
    reg["audits"].append({
        "audit_id":    audit_id,
        "name":        full_meta["name"],
        "contest":     full_meta["contest"],
        "status":      full_meta["status"],
        "start_date":  full_meta["start_date"],
        "deadline":    full_meta["deadline"],
        "submit_count": 0,
        "poc_count":   0,
        "last_active": _now(),
    })
    _write_registry(reg)
    return audit_root


def update_audit_status(status: str) -> None:
    """Update status in meta.json and registry for the active audit."""
    root = get_audit_root()
    meta_path = root / "meta.json"
    meta: dict = {}
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    meta["status"] = status
    meta_path.write_text(json.dumps(meta, indent=2))

    audit_id = get_active_audit().get("audit_id")
    reg = _read_registry()
    for entry in reg.get("audits", []):
        if entry["audit_id"] == audit_id:
            entry["status"] = status
            break
    _write_registry(reg)


# ─── Session tracking ────────────────────────────────────────────────────────

def write_session(updates: dict) -> None:
    """Merge updates into audits/<id>/session.json (creates if missing).

    Standard fields: audit_id, target_contract_dir, scope_files,
                     active_step, findings_count, last_updated.
    """
    audit_id = get_active_audit().get("audit_id")
    if not audit_id:
        return
    session_path = _AUDITS_DIR / audit_id / "session.json"
    session: dict = {}
    if session_path.exists():
        try:
            session = json.loads(session_path.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    session.update(updates)
    session["audit_id"] = audit_id
    session["last_updated"] = _now()
    session_path.write_text(json.dumps(session, indent=2))


def read_session() -> dict:
    """Read audits/<id>/session.json for the active audit. Returns {} on failure."""
    audit_id = get_active_audit().get("audit_id")
    if not audit_id:
        return {}
    session_path = _AUDITS_DIR / audit_id / "session.json"
    if not session_path.exists():
        return {}
    try:
        return json.loads(session_path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def update_registry_stats() -> None:
    """Recompute submit_count and poc_count for the active audit from JSONL files."""
    audit_id = get_active_audit().get("audit_id")
    if not audit_id:
        return
    root = _AUDITS_DIR / audit_id

    def _count(path: Path) -> int:
        if not path.exists():
            return 0
        return sum(1 for ln in path.read_text().splitlines() if ln.strip())

    submit_count = _count(root / "data/triage/submit.jsonl")
    poc_count = _count(root / "data/poc_queue/results.jsonl")

    reg = _read_registry()
    for entry in reg.get("audits", []):
        if entry["audit_id"] == audit_id:
            entry["submit_count"] = submit_count
            entry["poc_count"] = poc_count
            entry["last_active"] = _now()
            break
    _write_registry(reg)
