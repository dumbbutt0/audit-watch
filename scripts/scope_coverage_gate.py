#!/usr/bin/env python3
"""scope_coverage_gate.py — Phase-29 RESEARCH-ONLY pre-discovery intake-completeness gate.

Closes the P28 failure: an awarded bug lived in an audited sub-package that was never intaken (Vultisig
hardhat-vultisig/contracts). Given an audit target repo + the workspace, it answers: did we ingest the WHOLE audited
source surface? It runs BEFORE discovery and (in --block mode) refuses to let discovery start when scoped contracts
are missing/ambiguous.

Matching is TIERED (not parent/basename alone): T1 exact repo-relative path · T2 normalized path after re-rooting ·
T3 content hash (sha256; path-independent) · T4 parent+basename FALLBACK (low confidence → counts as ambiguous,
never confidently present). Scope parsing is conservative: globs/dirs expanded with recorded parse_confidence;
low-confidence parse ⇒ NEEDS_SCOPE_REVIEW. Explicit scope beats default test/mock exclusions.

  is_gate:false  research_only:true  routes_in_production:false  routed_manifest_ids:[]
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from intake_contracts import SOL_EXTS  # reuse  # noqa: E402
try:
    from audit_context import _AUDITS_DIR
except Exception:  # pragma: no cover
    _AUDITS_DIR = Path(__file__).resolve().parent.parent / "audits"

FLAGS = {"is_gate": False, "research_only": True, "routes_in_production": False, "routed_manifest_ids": []}
DEFAULT_EXCLUDE = ("/lib/", "/node_modules/", "/test/", "/tests/", "/mock", "/script/", "/docs/", "/out/")
PKG_MARKERS = ("hardhat.config.js", "hardhat.config.ts", "foundry.toml", "package.json", "remappings.txt")


def _sha(p: Path):
    try:
        return hashlib.sha256(p.read_bytes()).hexdigest()
    except OSError:
        return None


def _norm(line: str) -> str:
    return line.strip().lstrip("./").strip()


def _all_sol(root: Path, apply_exclude=True):
    out = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix in SOL_EXTS:
            rel = "/" + str(p.relative_to(root)).replace("\\", "/")
            if apply_exclude and any(x in rel for x in DEFAULT_EXCLUDE):
                continue
            out.append(p)
    return out


def parse_scope(repo: Path, scope_file: Path | None):
    """Return (scoped_rel_paths[list], parse_confidence)."""
    sf = scope_file or (repo / "scope.txt")
    if not sf.exists():
        # fallback: enumerate (no authoritative scope) -> low confidence
        files = [str(p.relative_to(repo)).replace("\\", "/") for p in _all_sol(repo)]
        return sorted(set(files)), "low"
    scoped, unresolved, used_expansion = set(), 0, False
    for raw in sf.read_text(errors="replace").splitlines():
        s = _norm(raw)
        if not s or s.startswith("#") or s.startswith("//") or s.startswith("|---") or set(s) <= {"|", "-", " "}:
            continue
        s = s.split("|")[1].strip() if (s.startswith("|") and "|" in s[1:]) else s  # markdown cell
        s = _norm(s)
        ap = repo / s
        if s.endswith(tuple(SOL_EXTS)):
            # A declared .sol path is scoped whether or not it exists in this clone. If it is absent (e.g. an
            # in-scope git submodule under lib/ that was not fetched), match() will mark it MISSING — which is the
            # correct, accurate signal (vs lowering parse confidence).
            scoped.add(s)
        elif "*" in s:  # glob
            used_expansion = True
            for p in _all_sol(repo, apply_exclude=False):
                if fnmatch.fnmatch(str(p.relative_to(repo)).replace("\\", "/"), s):
                    scoped.add(str(p.relative_to(repo)).replace("\\", "/"))
        elif ap.is_dir():  # directory entry -> expand (explicit scope beats exclusions)
            used_expansion = True
            for p in _all_sol(ap, apply_exclude=False):
                scoped.add(str(p.relative_to(repo)).replace("\\", "/"))
        elif s.endswith(tuple(SOL_EXTS)):  # listed .sol that doesn't resolve
            unresolved += 1
        else:
            unresolved += 1  # package name / unresolved row
    conf = "low" if unresolved else ("medium" if used_expansion else "high")
    return sorted(scoped), conf


def _workspace_index(audit_id: str):
    cdir = _AUDITS_DIR / audit_id / "contracts"
    by_hash, by_pb, paths = {}, {}, []
    for p in cdir.rglob("*"):
        if p.is_file() and p.suffix in SOL_EXTS:
            rel = str(p.relative_to(cdir)).replace("\\", "/")
            paths.append(rel)
            h = _sha(p)
            if h:
                by_hash.setdefault(h, []).append(rel)
            by_pb.setdefault((p.parent.name, p.name), []).append(rel)
    return by_hash, by_pb, paths


def match(scoped_rel: str, repo: Path, ws_hash, ws_pb, ws_paths):
    """Tiered match. Returns (status, tier, confidence) where status in present/ambiguous/missing."""
    ap = repo / scoped_rel
    # T1 exact: a workspace path equals or ends with the full repo-relative path
    if any(wp == scoped_rel or wp.endswith("/" + scoped_rel) for wp in ws_paths):
        return "present", "T1_exact", "high"
    # T3 content hash (path-independent; handles re-rooting)
    h = _sha(ap)
    if h and h in ws_hash:
        return "present", "T3_hash", "high"
    # T2 normalized: progressively strip leading components, unique endswith.
    # If we reached here, content hash did NOT match (T3 above). So a path-tail hit with a readable repo file means
    # SAME PATH / DIFFERENT CONTENT -> ambiguous (not confidently present). Only present if repo file is unreadable.
    parts = scoped_rel.split("/")
    for i in range(1, len(parts)):
        tail = "/".join(parts[i:])
        hits = [wp for wp in ws_paths if wp == tail or wp.endswith("/" + tail)]
        if len(hits) == 1:
            return ("present", "T2_normalized_unhashable", "medium") if h is None \
                else ("ambiguous", "T2_path_match_content_differs", "low")
        if len(hits) > 1:
            break
    # T4 parent+basename fallback (low confidence)
    pb = (Path(scoped_rel).parent.name, Path(scoped_rel).name)
    hits = ws_pb.get(pb, [])
    if len(hits) == 1:
        return "ambiguous", "T4_parentbasename", "low"   # not confidently present -> review
    if len(hits) > 1:
        return "ambiguous", "T4_collision", "low"
    return "missing", None, None


def run(repo: Path, audit_id: str, scope_file: Path | None):
    scoped, parse_conf = parse_scope(repo, scope_file)
    ws_hash, ws_pb, ws_paths = _workspace_index(audit_id)
    present, ambiguous, missing = [], [], []
    for s in scoped:
        st, tier, conf = match(s, repo, ws_hash, ws_pb, ws_paths)
        rec = {"file": s, "tier": tier, "confidence": conf}
        (present if st == "present" else ambiguous if st == "ambiguous" else missing).append(rec)
    missing_roots = sorted({m["file"].split("/")[0] + ("/" + m["file"].split("/")[1] if len(m["file"].split("/")) > 1 else "")
                            for m in missing})
    # structural: package roots in repo not represented in the intaken workspace
    extra_roots = []
    for marker_dir in {p.parent for mk in PKG_MARKERS for p in repo.rglob(mk) if "/node_modules/" not in str(p)}:
        sols = _all_sol(marker_dir)
        if sols and not any(_sha(x) in ws_hash for x in sols[:25]):
            rel = str(marker_dir.relative_to(repo)).replace("\\", "/") or "."
            if rel not in ("",) and rel != ".":
                extra_roots.append(rel)
    extra_roots = sorted(set(extra_roots))

    block_reasons = []
    if missing:
        block_reasons.append(f"{len(missing)} scoped files missing (roots: {missing_roots})")
    if ambiguous:
        block_reasons.append(f"{len(ambiguous)} ambiguous-only matches (need hash/exact)")
    if parse_conf == "low":
        block_reasons.append("low-confidence scope parse")
    # Extra un-intaken source roots are a block reason only when scope is NOT high-confidence-complete:
    # if an authoritative scope file is fully satisfied (parse high, 0 missing/ambiguous), other roots are
    # legitimately out-of-scope. Flag them when parse is uncertain or something scoped is already missing.
    if extra_roots and (parse_conf != "high" or missing or ambiguous):
        block_reasons.append(f"source roots outside intake likely scoped: {extra_roots}")
    decision = "SCOPE_COMPLETE" if not block_reasons else "NEEDS_SCOPE_REVIEW"
    return {
        **FLAGS, "tool": "scope_coverage_gate.py", "audit_id": audit_id, "repo": str(repo),
        "scoped_files_total": len(scoped), "scoped_files_present": len(present),
        "scoped_files_missing": len(missing), "missing_roots": missing_roots,
        "ambiguous_matches": len(ambiguous), "parse_confidence": parse_conf,
        "extra_source_roots": extra_roots, "decision": decision,
        "block_reason": "; ".join(block_reasons) or None,
        "missing_examples": [m["file"] for m in missing[:8]],
    }


# ------------------------- self-test -------------------------

def _self_test():
    import tempfile, os
    ok = True
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        # synthetic repo: two roots (src + token/contracts); workspace intakes only src (re-rooted to contracts/src)
        repo = td / "repo"; (repo / "src" / "base").mkdir(parents=True); (repo / "token" / "contracts").mkdir(parents=True)
        (repo / "src" / "A.sol").write_text("contract A{}")
        (repo / "src" / "base" / "B.sol").write_text("contract B{}")
        (repo / "token" / "contracts" / "W.sol").write_text("contract W{}")  # un-intaken scoped root
        (repo / "token" / "package.json").write_text("{}")
        (repo / "scope.txt").write_text("./src/A.sol\n./src/base/B.sol\n./token/contracts/W.sol\n")
        # workspace: only src intaken, re-rooted under contracts/src
        ws = _AUDITS_DIR / "_selftest_scope"; (ws / "contracts" / "src" / "base").mkdir(parents=True, exist_ok=True)
        (ws / "meta.json").write_text("{}")
        (ws / "contracts" / "src" / "A.sol").write_text("contract A{}")        # hash-matches repo
        (ws / "contracts" / "src" / "base" / "B.sol").write_text("contract B{}")
        try:
            r = run(repo, "_selftest_scope", None)
            c1 = r["decision"] == "NEEDS_SCOPE_REVIEW" and "token/contracts" in r["missing_roots"] and r["parse_confidence"] == "high"
            print(f"  [{'PASS' if c1 else 'FAIL'}] multi-root: missing token/contracts -> NEEDS_SCOPE_REVIEW (missing={r['missing_roots']})")
            ok &= c1

            # single-root re-rooted: scope only src -> COMPLETE (content-hash/exact)
            (repo / "scope2.txt").write_text("./src/A.sol\n./src/base/B.sol\n")
            r2 = run(repo, "_selftest_scope", repo / "scope2.txt")
            c2 = r2["decision"] == "SCOPE_COMPLETE" and r2["scoped_files_missing"] == 0
            print(f"  [{'PASS' if c2 else 'FAIL'}] single-root re-rooted -> SCOPE_COMPLETE (present {r2['scoped_files_present']}/{r2['scoped_files_total']})")
            ok &= c2

            # collision/ambiguous: a scoped file present only by parent+basename (different content) -> ambiguous, not complete
            (repo / "src" / "base" / "C.sol").write_text("contract C_REPO{}")
            (ws / "contracts" / "src" / "base" / "C.sol").write_text("contract C_DIFFERENT{}")  # same path, different content
            # use a scope listing a DIFFERENT-content same-path file under a re-rooted name to force T4
            (repo / "scope3.txt").write_text("./other/base/C.sol\n")
            (repo / "other" / "base").mkdir(parents=True, exist_ok=True)
            (repo / "other" / "base" / "C.sol").write_text("contract C_REPO{}")
            r3 = run(repo, "_selftest_scope", repo / "scope3.txt")
            # C.sol matches workspace base/C.sol only by (parent,basename) but content differs -> ambiguous -> NEEDS_SCOPE_REVIEW
            c3 = r3["decision"] == "NEEDS_SCOPE_REVIEW" and (r3["ambiguous_matches"] >= 1 or r3["scoped_files_missing"] >= 1)
            print(f"  [{'PASS' if c3 else 'FAIL'}] collision/diff-content -> not COMPLETE (ambiguous={r3['ambiguous_matches']} missing={r3['scoped_files_missing']})")
            ok &= c3

            # low-confidence parse: no scope file -> fallback enumerate -> low -> NEEDS_SCOPE_REVIEW
            repo2 = td / "repo2"; (repo2 / "src").mkdir(parents=True)
            (repo2 / "src" / "Z.sol").write_text("contract Z{}")
            r4 = run(repo2, "_selftest_scope", None)
            c4 = r4["parse_confidence"] == "low" and r4["decision"] == "NEEDS_SCOPE_REVIEW"
            print(f"  [{'PASS' if c4 else 'FAIL'}] no scope file -> low parse -> NEEDS_SCOPE_REVIEW")
            ok &= c4
        finally:
            import shutil; shutil.rmtree(ws, ignore_errors=True)
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--audit-id")
    ap.add_argument("--scope-file")
    ap.add_argument("--out")
    ap.add_argument("--block", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    if not (args.repo and args.audit_id):
        ap.error("--repo and --audit-id required (or --self-test)")
    r = run(Path(args.repo).resolve(), args.audit_id, Path(args.scope_file).resolve() if args.scope_file else None)
    if args.out:
        Path(args.out).write_text(json.dumps(r, indent=2))
    print(f"[scope_coverage] {args.audit_id}: {r['decision']} | scoped {r['scoped_files_present']}/{r['scoped_files_total']} "
          f"present · missing {r['scoped_files_missing']} {r['missing_roots']} · ambiguous {r['ambiguous_matches']} · "
          f"parse {r['parse_confidence']}")
    if r["block_reason"]:
        print(f"   block_reason: {r['block_reason']}")
    if args.block and r["decision"] != "SCOPE_COMPLETE":
        print("   --block: discovery MUST NOT start until scope coverage is resolved.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
