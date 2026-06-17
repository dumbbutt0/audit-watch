"""
Shared helpers for candidate-validation artifact generation (Stage 1: gates 1–3).

Every artifact carries a common header (candidate_id, audit_id, candidate_hash, generated_at, tool, source_root,
source_hash, evidence_refs, status, reasons, unresolved_assumptions) plus research flags. Writes are confined to
documentation/research/candidates/<audit_id>/<candidate_hash>/ and overwrite-per-candidate. Never touches detector
outputs, the frozen corpus, submission/report paths, or the PoC engine.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
CANDIDATES_ROOT = ROOT / "documentation/research/candidates"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def candidate_hash_of(candidate_id: str) -> str:
    return candidate_id.split(":")[-1] if candidate_id else ""


def candidate_dir(audit_id: str, candidate_hash: str) -> Path:
    return CANDIDATES_ROOT / audit_id / candidate_hash


def md5_file(path: Path) -> Optional[str]:
    try:
        return "md5:" + hashlib.md5(Path(path).read_bytes()).hexdigest()
    except (FileNotFoundError, OSError):
        return None


def source_roots() -> List[Path]:
    roots = [ROOT]
    aud = ROOT / "audits"
    if aud.is_dir():
        roots += sorted(d for d in aud.glob("*") if d.is_dir())
    return roots


def common_header(*, candidate_id: str, audit_id: str, candidate_hash: str, tool: str,
                  source_root: Optional[str] = None, source_hash: Optional[str] = None,
                  evidence_refs: Optional[List[str]] = None, status: str = "PASS",
                  reasons: Optional[List[str]] = None,
                  unresolved_assumptions: Optional[List[str]] = None) -> Dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "audit_id": audit_id,
        "candidate_hash": candidate_hash,
        "generated_at": now(),
        "tool": tool,
        "source_root": source_root,
        "source_hash": source_hash,
        "evidence_refs": evidence_refs or [],
        "status": status,
        "reasons": reasons or [],
        "unresolved_assumptions": unresolved_assumptions or [],
        "routing_allowed": False,
        "research_only": True,
    }


def dir_is_illustrative(folder: Path) -> bool:
    """True if the folder already holds illustrative demo artifacts (protect them from overwrite)."""
    if not folder.is_dir():
        return False
    for p in folder.glob("*.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if isinstance(d, dict) and d.get("_illustrative"):
            return True
    return False


def write_json(folder: Path, name: str, obj: Dict[str, Any]) -> Path:
    _assert_under_candidates(folder)
    folder.mkdir(parents=True, exist_ok=True)
    p = folder / name
    p.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    return p


def load_existing(folder: Path, name: str) -> Optional[Dict[str, Any]]:
    """Read an already-written artifact (read-only). Returns None if absent/unparseable."""
    p = folder / name
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def write_text(folder: Path, name: str, text: str) -> Path:
    _assert_under_candidates(folder)
    folder.mkdir(parents=True, exist_ok=True)
    p = folder / name
    p.write_text(text, encoding="utf-8")
    return p


def _assert_under_candidates(folder: Path) -> None:
    f = folder.resolve()
    if CANDIDATES_ROOT.resolve() not in f.parents:
        raise ValueError(f"refusing to write outside candidates root: {folder}")
