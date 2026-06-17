#!/usr/bin/env python3
"""static_analysis_rust.py — Rust/Solana static adapter.

Produces output/static.json in the SAME schema the Solidity path emits, so every downstream
consumer (specialists, deep-analysis, coverage manifest) stays language-blind. Two signal
sources, combined:

  1. Toolchain layer — scripts/compile_for_analysis_rust.sh runs cargo clippy / cargo check
     (+ optional cargo-audit / cargo-geiger) and normalizes diagnostics. Best-effort; absent
     toolchain degrades to layer 3 (empty) without failing.
  2. Solana source-pattern pass — a fast, always-on regex census over in-scope .rs files for
     the Anchor/Solana primitives our specialists key on (unchecked AccountInfo, init_if_needed,
     invoke_signed/PDA seeds, unwrap/panic, unchecked arithmetic, remaining_accounts). This is
     the high-value signal that routes the Solana specialist bundle and seeds attack surface.

Also sets `zk_out_of_scope` when ElGamal/Pedersen/proof-circuit patterns are detected — the
DOCUMENTED boundary (documentation/architecture/zk_boundary.md): the tool flags ZK-circuit
soundness but never adjudicates it.

This module is invoked ONLY for rust audits (dispatched from tools/static_analysis.py by
audit_language()); the Solidity path is byte-unchanged.

Usage:  python tools/static_analysis_rust.py <project_dir_or_file>
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from audit_context import audit_path  # noqa: E402

OUTPUT_DIR = audit_path("output")
COMPILE_SH = ROOT / "scripts" / "compile_for_analysis_rust.sh"

# pub fn handlers (instruction entrypoints) — mirrors build_coverage_manifest.RUST_FN_RE
RUST_FN_RE = re.compile(r"\bpub\s+fn\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:<[^>]*>)?\s*\(", re.M)

# Solana source-pattern signals: (check_id, severity, compiled regex, human message)
PATTERNS = [
    ("solana-unchecked-accountinfo", "Medium",
     re.compile(r"/// *CHECK[\s\S]{0,120}?\bAccountInfo<"),
     "AccountInfo with a /// CHECK escape — verify the account is constrained in the body (owner/key/signer)"),
    ("solana-init-if-needed", "Medium",
     re.compile(r"\binit_if_needed\b"),
     "init_if_needed — confirm a re-init guard / discriminator check (reinit risk)"),
    ("solana-invoke-signed", "Low",
     re.compile(r"\binvoke_signed\b|with_signer\s*\("),
     "PDA signer CPI — verify signer seeds include the canonical bump and are scoped to the right PDA"),
    ("solana-unwrap-panic", "Low",
     re.compile(r"\.unwrap\(\)|\.expect\("),
     "unwrap()/expect() — a panic on attacker-controlled input is a DoS surface"),
    ("solana-unchecked-arithmetic", "Low",
     re.compile(r"[^=!<>+\-*/]\s[\w.\[\]]+\s*[-+*]\s*[\w.\[\]]+", re.M),
     "arithmetic without checked_*/saturating_* — confirm overflow-checks or explicit checked math"),
    ("solana-remaining-accounts", "Medium",
     re.compile(r"\bremaining_accounts\b"),
     "remaining_accounts use — each is unvalidated; confirm owner/key/program pinning"),
    ("solana-signer-account", "Info",
     re.compile(r"\bSigner<'"),
     "Signer account present (authorization anchor)"),
]
# ZK / cryptographic-proof boundary markers — FLAG ONLY (out of adjudication scope)
ZK_MARKERS = re.compile(r"\bElGamal\b|\bPedersen\b|\bRangeProof\b|sigma[_ ]?proof|zk[_-]?elgamal|"
                        r"\bciphertext\b|confidential_transfer|proof_(generation|extraction|verification)",
                        re.I)
ANCHOR_MARKERS = re.compile(r"anchor_lang|#\[program\]|#\[derive\(Accounts\)\]|declare_id!")
CPI_MARKERS = re.compile(r"\bCpiContext\b|invoke(_signed)?\s*\(|endpoint_cpi|::cpi::")
PDA_MARKERS = re.compile(r"find_program_address|seeds\s*=|Pubkey::create_program_address")
UNSAFE_MARKERS = re.compile(r"\bunsafe\s*\{")


def _rust_files(root: Path) -> list[Path]:
    out = []
    for p in root.rglob("*.rs"):
        s = str(p)
        if "/target/" in s or "/tests/" in s or s.endswith("build.rs"):
            continue
        out.append(p)
    return out


def _run_toolchain(proj: Path) -> dict:
    try:
        res = subprocess.run(["bash", str(COMPILE_SH), str(proj)],
                             capture_output=True, text=True, timeout=900)
        m = re.search(r"RUST_STATIC_JSON=(\S+)", res.stdout)
        if m and Path(m.group(1)).exists():
            return json.loads(Path(m.group(1)).read_text())
    except Exception as e:  # noqa: BLE001
        print(f"[rust-static] toolchain layer skipped: {e}")
    return {"layer": 3, "tools": {}, "tool_findings": []}


def analyse(target: str) -> dict:
    tpath = Path(target)
    proj = tpath if tpath.is_dir() else tpath.parent
    files = _rust_files(proj)

    tool = _run_toolchain(proj)
    findings = list(tool.get("tool_findings", []))

    functions, source_findings = [], []
    is_anchor = has_cpi = has_pda = has_unsafe = zk = False
    for f in files:
        try:
            src = f.read_text(errors="ignore")
        except Exception:
            continue
        rel = str(f.relative_to(proj)) if f.is_relative_to(proj) else str(f)
        for m in RUST_FN_RE.finditer(src):
            functions.append({"name": m.group(1), "visibility": "external", "file": rel})
        is_anchor |= bool(ANCHOR_MARKERS.search(src))
        has_cpi |= bool(CPI_MARKERS.search(src))
        has_pda |= bool(PDA_MARKERS.search(src))
        has_unsafe |= bool(UNSAFE_MARKERS.search(src))
        zk |= bool(ZK_MARKERS.search(src))
        for cid, sev, rx, msg in PATTERNS:
            if rx.search(src):
                n = len(rx.findall(src))
                source_findings.append({"tool": "solana-pattern", "check": cid, "severity": sev,
                                        "message": msg, "file": rel, "count": n})

    all_findings = findings + source_findings
    static = {
        "contract_path": str(target),
        "language": "rust",
        "compiler_version": "cargo/rustc",
        "functions": functions,
        "state_variables": [],
        "external_calls": [{"file": x["file"], "kind": "cpi"} for x in source_findings
                           if x["check"] == "solana-invoke-signed"],
        "slither_findings": all_findings,   # shared key downstream consumers read
        "static_findings": all_findings,    # explicit alias
        "tainted_sinks": [],
        "delegatecall_risks": [],
        "mythril_issues": [],
        # Solana routing flags (analogous to is_erc4626/is_proxy on the Solidity side)
        "is_anchor": is_anchor,
        "has_cpi": has_cpi,
        "has_pda": has_pda,
        "has_unsafe": has_unsafe,
        "is_erc4626": False,
        "has_transient_storage": False,
        "is_proxy": False,
        # ZK boundary: FLAG, never adjudicate (documentation/architecture/zk_boundary.md)
        "zk_out_of_scope": zk,
        "zk_boundary_note": ("ZK-circuit / cryptographic-proof code detected — FLAGGED ONLY. "
                             "This architecture does not adjudicate proof soundness; route to a "
                             "ZK specialist. See documentation/architecture/zk_boundary.md.") if zk else "",
        "static_layer": tool.get("layer", 3),
        "tools_available": tool.get("tools", {}),
        "slither_available": False,
        "rust_static_available": True,
        "files_scanned": len(files),
    }
    return static


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python tools/static_analysis_rust.py <project_dir_or_file>")
        return 2
    static = analyse(sys.argv[1])
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUTPUT_DIR / "static.json"
    out.write_text(json.dumps(static, indent=2) + "\n")
    flags = [k for k in ("is_anchor", "has_cpi", "has_pda", "has_unsafe", "zk_out_of_scope") if static[k]]
    print(f"[rust-static] {static['files_scanned']} .rs files, {len(static['functions'])} pub fns, "
          f"{len(static['slither_findings'])} findings (layer {static['static_layer']}); flags: {flags or 'none'}")
    print(f"[rust-static] wrote {out}")
    if static["zk_out_of_scope"]:
        print("[rust-static] ⚠ ZK/crypto-proof code FLAGGED — out of adjudication scope (zk_boundary.md)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
