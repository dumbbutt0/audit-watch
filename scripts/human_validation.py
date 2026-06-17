"""
Human Validation — pure logic for the research-corpus validation console.

This module holds the testable core behind the dashboard's /validation surface. It lets a human
reviewer label frozen research-track evidence bundles for *coherence / investigation-worthiness /
PoC-follow-up-worthiness / review-effort / missing-info / counter-signals / notes / reviewer-confidence*.

CORE INVARIANT: **human validation, not routing.** Nothing here decides a bug, a severity, an
exploitability score, a submission, or a routing action. Every label row is research_only:true and
routing_allowed:false, and the set of label keys is a fixed allowlist — forbidden verdict fields are
structurally impossible to emit, and `assert_no_forbidden_fields` is a belt-and-suspenders guard.

No FastAPI here (kept import-light + unit-testable). The corpus is read-only; the ONLY thing this
module writes is the human-labels JSONL (append-only).
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Union

LABEL_SCHEMA_VERSION = "hv-1"

# --------------------------------------------------------------- allowed labels
ALLOWED: Dict[str, set] = {
    "coherence": {"coherent", "partially_coherent", "weak", "incoherent"},
    "investigation_worthiness": {"investigate", "maybe", "skip"},
    "poc_followup_worthiness": {"yes", "maybe", "no"},
    "expected_review_effort": {"low", "medium", "high"},
    "reviewer_confidence": {"high", "medium", "low"},
}

# Verdict / routing concepts that MUST NEVER appear on a research label row.
FORBIDDEN_KEYS: set = {
    "is_bug", "bug", "valid", "validity", "invalid", "severity", "predicted_severity",
    "exploitability", "exploitability_score", "submit", "reject", "rejected", "bounty",
    "bounty_worthy", "verdict", "final_verdict", "predicted_outcome", "final_action",
    "route", "routing", "routes_in_production", "is_gate",
}

# The exact, complete set of keys a label row may contain.
_ALLOWED_ROW_KEYS = {
    "label_schema_version", "timestamp", "reviewer_alias", "candidate_id", "source_corpus_hash",
    "detector", "candidate_surface", "coherence", "investigation_worthiness",
    "poc_followup_worthiness", "expected_review_effort", "missing_information", "counter_signals",
    "reviewer_notes", "reviewer_confidence", "routing_allowed", "research_only",
}


class LabelValidationError(ValueError):
    """Raised when a submitted label violates an enum, the allowlist, or carries a forbidden field."""


# ------------------------------------------------------------------ corpus load
def _read_json(path: Path) -> Optional[Any]:
    try:
        with Path(path).open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    try:
        with Path(path).open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except (FileNotFoundError, OSError):
        return []
    return out


def _bundle_content_hash(b: Dict[str, Any]) -> str:
    """Stable per-bundle content hash, used when a bundle lacks corpus_bundle_hash
    (e.g. a raw evidence_bundles.json)."""
    key = json.dumps(
        {k: b.get(k) for k in
         ("candidate_id", "detector", "candidate_surface", "code_snippet",
          "evidence_signals", "rationale", "confidence")},
        sort_keys=True,
    )
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def _workspace_of(b: Dict[str, Any]) -> str:
    """Derive a target/workspace label. Frozen corpus carries corpus_source_slug; a raw
    evidence_bundles.json only has source_audit_path — derive a best-effort slug from it."""
    if b.get("corpus_source_slug"):
        return str(b["corpus_source_slug"])
    sap = b.get("source_audit_path") or ""
    parts = Path(sap).parts
    if "audits" in parts:
        i = parts.index("audits")
        if i + 1 < len(parts):
            return parts[i + 1]
    if "_runs" in parts:
        i = parts.index("_runs")
        if i + 1 < len(parts):
            return parts[i + 1]
    return "unknown"


def compute_corpus_hash(bundles: List[Dict[str, Any]]) -> str:
    """Deterministic hash over (candidate_id, per-bundle content hash), order-independent.
    Changes iff bundle content changes; identical across reloads of the same corpus."""
    items = sorted(
        (str(b.get("candidate_id")), b.get("corpus_bundle_hash") or _bundle_content_hash(b))
        for b in bundles
    )
    return hashlib.sha256(json.dumps(items, sort_keys=True).encode("utf-8")).hexdigest()


def load_corpus(path: Union[str, Path]) -> Dict[str, Any]:
    """Load a frozen_corpus.json OR a raw evidence_bundles.json. Normalizes to a common record list,
    annotating each bundle with `workspace` and a stable `bundle_hash`. Read-only."""
    path = Path(path)
    data = _read_json(path)
    if not isinstance(data, dict) or not isinstance(data.get("bundles"), list):
        raise LabelValidationError(f"not a corpus/evidence-bundle file: {path}")
    bundles: List[Dict[str, Any]] = []
    for b in data["bundles"]:
        if not isinstance(b, dict):
            continue
        rec = dict(b)
        rec["workspace"] = _workspace_of(b)
        rec["bundle_hash"] = b.get("corpus_bundle_hash") or _bundle_content_hash(b)
        bundles.append(rec)
    return {
        "source_path": str(path),
        "corpus_version": data.get("corpus_version") or data.get("schema_version"),
        "generated_at": data.get("generated_at"),
        "corpus_hash": compute_corpus_hash(bundles),
        "bundle_count": len(bundles),
        "bundles": bundles,
    }


def abs_source(file_rel: Optional[str], roots: Union[str, Path, Iterable]) -> Optional[str]:
    """Resolve a corpus-relative source path to an absolute path for an editor 'open at line' link.

    `roots` may be a single root or a list of allowed source roots (repo root + known eval workspace roots,
    so paths that are relative to a workspace rather than the repo root still resolve). Tries each root in
    order and returns the first resolved path that BOTH stays under that root (no traversal) AND exists;
    otherwise None. Read-only; nothing outside an allowed root is ever emitted."""
    if not file_rel:
        return None
    if isinstance(roots, (str, Path)):
        roots = [roots]
    for r in roots:
        try:
            root = Path(r).resolve()
            p = (root / file_rel).resolve()
        except (OSError, ValueError):
            continue
        if (p == root or root in p.parents) and p.is_file():
            return str(p)
    return None


# ------------------------------------------------------------------- statistics
def _count_by(bundles: List[Dict[str, Any]], key: str) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for b in bundles:
        k = str(b.get(key, "?"))
        out[k] = out.get(k, 0) + 1
    return out


def overview_stats(bundles: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "total_bundles": len(bundles),
        "by_detector": _count_by(bundles, "detector"),
        "by_confidence": _count_by(bundles, "confidence"),
        "by_declared_severity_potential": _count_by(bundles, "declared_severity_potential"),
        "by_bundle_status": _count_by(bundles, "bundle_status"),
        "by_workspace": _count_by(bundles, "workspace"),
    }


# ------------------------------------------------------------------- label rows
def assert_no_forbidden_fields(row: Dict[str, Any]) -> None:
    """Raise if a row carries any forbidden verdict/routing field, or any key outside the allowlist."""
    bad = FORBIDDEN_KEYS & set(row.keys())
    if bad:
        raise LabelValidationError(f"forbidden verdict/routing fields present: {sorted(bad)}")
    extra = set(row.keys()) - _ALLOWED_ROW_KEYS
    if extra:
        raise LabelValidationError(f"non-allowlisted label keys present: {sorted(extra)}")


def _as_text_or_list(v: Any) -> Union[str, List[str]]:
    if v is None:
        return ""
    if isinstance(v, list):
        return [str(x) for x in v]
    return str(v)


def build_label_row(
    bundle: Dict[str, Any],
    reviewer_alias: str,
    form: Dict[str, Any],
    corpus_hash: str,
) -> Dict[str, Any]:
    """Build a single label row from a fixed allowlist of keys ONLY. Validates enums. Forbidden
    verdict fields are structurally impossible (we never copy arbitrary form keys)."""
    if not reviewer_alias or not str(reviewer_alias).strip():
        raise LabelValidationError("reviewer_alias is required")
    for field, allowed in ALLOWED.items():
        val = form.get(field)
        if val is None or val == "":
            raise LabelValidationError(f"missing required label: {field}")
        if val not in allowed:
            raise LabelValidationError(f"invalid {field}={val!r}; allowed: {sorted(allowed)}")
    row = {
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "reviewer_alias": str(reviewer_alias).strip(),
        "candidate_id": bundle.get("candidate_id"),
        "source_corpus_hash": corpus_hash,
        "detector": bundle.get("detector"),
        "candidate_surface": bundle.get("candidate_surface"),
        "coherence": form["coherence"],
        "investigation_worthiness": form["investigation_worthiness"],
        "poc_followup_worthiness": form["poc_followup_worthiness"],
        "expected_review_effort": form["expected_review_effort"],
        "missing_information": _as_text_or_list(form.get("missing_information")),
        "counter_signals": _as_text_or_list(form.get("counter_signals")),
        "reviewer_notes": str(form.get("reviewer_notes") or ""),
        "reviewer_confidence": form["reviewer_confidence"],
        "routing_allowed": False,
        "research_only": True,
    }
    assert_no_forbidden_fields(row)
    return row


# ------------------------------------------------------------- persistence (append-only)
def append_label(row: Dict[str, Any], labels_path: Union[str, Path]) -> None:
    """Append one label row as a JSONL line. NEVER rewrites or overwrites existing rows.
    Creates the file (and parent dir) if absent. This is the only write this module performs."""
    assert_no_forbidden_fields(row)
    labels_path = Path(labels_path)
    labels_path.parent.mkdir(parents=True, exist_ok=True)
    with labels_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


def read_labels(labels_path: Union[str, Path]) -> List[Dict[str, Any]]:
    return _read_jsonl(Path(labels_path))


def latest_by_candidate(rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """The 'current' label per candidate = the row with the newest timestamp (append-only history)."""
    out: Dict[str, Dict[str, Any]] = {}
    for r in sorted(rows, key=lambda x: str(x.get("timestamp", ""))):
        cid = r.get("candidate_id")
        if cid is not None:
            out[cid] = r  # later (newer) rows overwrite in-memory only; file is untouched
    return out


# --------------------------------------------------------------------- progress
def label_progress(
    bundles: List[Dict[str, Any]],
    rows: List[Dict[str, Any]],
    corpus_hash: Optional[str] = None,
) -> Dict[str, Any]:
    latest = latest_by_candidate(rows)
    total = len(bundles)
    labeled_ids = {b.get("candidate_id") for b in bundles} & set(latest.keys())
    labeled = len(labeled_ids)
    drift = False
    if corpus_hash is not None:
        for cid in labeled_ids:
            if latest[cid].get("source_corpus_hash") not in (None, corpus_hash):
                drift = True
                break

    def _dist(field: str) -> Dict[str, int]:
        d: Dict[str, int] = {}
        for cid in labeled_ids:
            v = str(latest[cid].get(field, "?"))
            d[v] = d.get(v, 0) + 1
        return d

    return {
        "total": total,
        "labeled": labeled,
        "unlabeled": total - labeled,
        "percent_complete": round(100.0 * labeled / total, 1) if total else 0.0,
        "by_coherence": _dist("coherence"),
        "by_investigation_worthiness": _dist("investigation_worthiness"),
        "by_poc_followup_worthiness": _dist("poc_followup_worthiness"),
        "corpus_drift": drift,
    }
