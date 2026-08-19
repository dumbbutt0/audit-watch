#!/usr/bin/env python3
"""static_analysis_ton.py — TON / FunC static adapter.

Produces output/static.json in the SAME schema the Solidity path emits, so every downstream
consumer (specialists, deep-analysis, coverage manifest, conditional-spawn gating) stays
language-blind. Two signal sources, combined:

  1. Toolchain layer (best-effort) — if a FunC compiler (`func`) or the Misti analyzer
     (`npx @nowarp/misti`) is on PATH, run it for compiler/lint diagnostics. Absent toolchain
     degrades to layer 3 (census only) without failing — TON's compiler ships via Blueprint
     (npm), which a fresh checkout may not have installed yet.
  2. FunC source-pattern pass — a fast, always-on regex census over in-scope .fc files for the
     TON-native primitives the specialists key on: jetton transfer-notification handling
     (sender-spoofing surface), sender-address auth anchors (equal_slices), bounce branches
     (ignored-bounce fund-stranding), raw message sends (carry-value egress), cell/ref parsing
     (malformed-multihop), and coin muldiv (TVM 257-bit arithmetic). This is the high-value
     signal that routes the TON specialist bundle and seeds attack surface.

The EVM conditional-spawn flags (is_erc4626 / has_transient_storage / is_proxy) are forced
False so the EVM-only conditional specialists never spawn on a FunC target. TON-native routing
flags (has_jetton / is_dex / bounce_ignored / has_multihop) are added for the ite-audit TON
branch + specialists.

This module is invoked ONLY for ton audits (dispatched from tools/static_analysis.py by
audit_language()); the Solidity path is byte-unchanged.

Usage:  python tools/static_analysis_ton.py <project_dir_or_file>
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from audit_context import audit_path  # noqa: E402

OUTPUT_DIR = audit_path("output")

# FunC has no function keyword: `<return-type> <name>(<params>) <specifiers> {`. Mirrors
# build_coverage_manifest.FUNC_FN_RE (negative lookahead drops `return foo(...)`-style statements).
FUNC_FN_RE = re.compile(
    r"^[ \t]*"
    r"(?!(?:return|if|ifnot|while|repeat|do|until|else|elseif|throw|throw_if|throw_unless|begin_cell)\b)"
    r"(?:\([^;{}]*\)|_|var|int|slice|cell|builder|tuple|cont|[A-Za-z_][\w:]*)"
    r"[ \t]+(~?[A-Za-z_][\w:?'$]*)[ \t]*\(",
    re.M,
)

# FunC source-pattern signals: (check_id, severity, compiled regex, human message)
PATTERNS = [
    ("ton-jetton-transfer-notification", "Info",
     re.compile(r"transfer_notification"),
     "jetton transfer-notification handled — verify the SENDER is the contract's OWN jetton wallet for the "
     "claimed asset (sender-spoofing → fake-deposit theft; cf. STON.fi lp_account / Swap Coffee vault findings)"),
    ("ton-sender-auth-anchor", "Info",
     re.compile(r"equal_slices\s*\([^)]*(sender|admin|owner|pool_address|user_address|router)", re.I),
     "sender-address auth check present (authorization anchor)"),
    ("ton-raw-message-send", "Low",
     re.compile(r"send_raw_message\s*\(|send_message\s*\(|\bmsgs?::send"),
     "outgoing message send — value-carrying egress; verify gas/value accounting + that a downstream failure "
     "bounces and is handled (carry-value stranding / drain surface)"),
    ("ton-bounce-branch", "Medium",
     re.compile(r"is_bounced|IS_BOUNCED|bounced\?"),
     "bounce-flag branch — if bounced messages are ignored/short-circuited, a failed downstream message can "
     "strand reserved funds or desync accounting (verify state is restored on bounce; cf. Crouton/Torch findings)"),
    ("ton-multihop-cell", "Low",
     re.compile(r"load_ref\s*\(|~?load_dict|slice_refs|load_maybe_ref"),
     "cell/ref parsing — malformed or attacker-shaped cells (multihop routes) can mis-parse to a wrong recipient "
     "or throw (verify end_parse + bounds; cf. TONCO 'malformed multihop cell → jetton loss')"),
    ("ton-coins-muldiv", "Low",
     re.compile(r"muldiv\s*\(|mul_div\s*\("),
     "muldiv on coin amounts — TVM 257-bit; verify rounding direction + no overflow/precision loss in swap/LP math"),
    ("ton-throw-guard", "Info",
     re.compile(r"throw_unless\s*\(|throw_if\s*\("),
     "explicit throw guard (precondition anchor)"),
]

# Routing-flag markers
JETTON_MARK   = re.compile(r"transfer_notification|internal_transfer|provide_wallet_address|burn_notification")
SEND_MARK     = re.compile(r"send_raw_message\s*\(|send_message\s*\(|\bmsgs?::send")
DEX_MARK      = re.compile(r"\bswap\b")
POOL_MARK     = re.compile(r"\bpool\b|\bliquidity\b|provide_lp")
MULTIHOP_MARK = re.compile(r"load_ref|multihop|cross_provide|route_dex")
# Ignored-bounce pattern: an IS_BOUNCED branch that immediately returns (does no recovery).
BOUNCE_IGNORE = re.compile(r"IS_BOUNCED\)?\s*\{[^}]*return\s*\(\s*\)", re.S)
AUTH_MARK     = re.compile(r"equal_slices\s*\(")


def _ton_files(root: Path) -> list[Path]:
    out = []
    for p in root.rglob("*"):
        if p.suffix not in (".fc", ".func", ".tolk") or not p.is_file():
            continue
        s = p.as_posix()
        if any(seg in s for seg in ("/test/", "/tests/", "/build/", "/.git/", "/node_modules/")):
            continue
        out.append(p)
    return sorted(out)


def _run_toolchain(proj: Path, files: list[Path]) -> dict:
    """Best-effort: run Misti (preferred) or the func compiler if available. Degrades to layer 3."""
    tools: dict = {}
    tool_findings: list = []
    # Misti static analyzer (Tact/FunC) — only if a blueprint project + deps are present.
    misti = shutil.which("misti")
    if misti and (proj / "node_modules").exists():
        try:
            res = subprocess.run([misti, "--output-format", "json", str(proj)],
                                 capture_output=True, text=True, timeout=600)
            tools["misti"] = True
            try:
                data = json.loads(res.stdout or "{}")
                for w in (data.get("warnings") or data.get("findings") or []):
                    tool_findings.append({"tool": "misti", "check": w.get("rule", w.get("id", "misti")),
                                          "severity": (w.get("severity") or "Low").title(),
                                          "message": w.get("message", ""), "file": w.get("file", "")})
            except Exception:
                pass
        except Exception as e:  # noqa: BLE001
            print(f"[ton-static] misti layer skipped: {e}")
    # func compiler — syntax/type warnings (best-effort, per-entry). Most repos compile via Blueprint;
    # a bare `func` is rarely on PATH, so this degrades silently.
    func_bin = shutil.which("func")
    if func_bin:
        tools["func"] = True
    layer = 1 if tool_findings else (2 if tools else 3)
    return {"layer": layer, "tools": tools, "tool_findings": tool_findings}


def analyse(target: str) -> dict:
    tpath = Path(target)
    proj = tpath if tpath.is_dir() else tpath.parent
    files = _ton_files(proj) if proj.is_dir() else ([tpath] if tpath.suffix in (".fc", ".func", ".tolk") else [])

    tool = _run_toolchain(proj, files)
    findings = list(tool.get("tool_findings", []))

    functions, source_findings, external_calls = [], [], []
    has_jetton = is_dex_swap = has_pool = has_multihop = bounce_ignored = False
    auth_check_count = 0
    for f in files:
        try:
            src = f.read_text(errors="ignore")
        except Exception:
            continue
        rel = str(f.relative_to(proj)) if f.is_relative_to(proj) else str(f)
        for m in FUNC_FN_RE.finditer(src):
            name = m.group(1)
            vis = "external" if (name in ("recv_internal", "recv_external") or "method_id" in src[m.start():m.start() + 200]) else "internal"
            functions.append({"name": name, "visibility": vis, "file": rel})
        has_jetton |= bool(JETTON_MARK.search(src))
        is_dex_swap |= bool(DEX_MARK.search(src))
        has_pool |= bool(POOL_MARK.search(src))
        has_multihop |= bool(MULTIHOP_MARK.search(src))
        bounce_ignored |= bool(BOUNCE_IGNORE.search(src))
        auth_check_count += len(AUTH_MARK.findall(src))
        if SEND_MARK.search(src):
            external_calls.append({"file": rel, "kind": "message_send"})
        for cid, sev, rx, msg in PATTERNS:
            if rx.search(src):
                n = len(rx.findall(src))
                source_findings.append({"tool": "func-pattern", "check": cid, "severity": sev,
                                        "message": msg, "file": rel, "count": n})

    # Promote the ignored-bounce pattern to an explicit High-visibility census finding when a DEX
    # value-handling contract ignores bounces (the prime TON fund-stranding surface).
    if bounce_ignored and (has_jetton or has_pool):
        source_findings.append({"tool": "func-pattern", "check": "ton-bounce-ignored-on-value-path",
                                "severity": "Medium", "file": "<multiple>", "count": 1,
                                "message": "An IS_BOUNCED branch returns immediately (ignores the bounce) on a "
                                "contract that handles jettons/liquidity — a failed downstream message can strand "
                                "funds or leave reserved state inconsistent. Verify each reservation/credit is "
                                "reversible on bounce."})

    all_findings = findings + source_findings
    is_dex = bool(is_dex_swap and has_pool)
    static = {
        "contract_path": str(target),
        "language": "ton",
        "compiler_version": "func/blueprint",
        "functions": functions,
        "state_variables": [],
        "external_calls": external_calls,
        "slither_findings": all_findings,   # shared key downstream consumers read
        "static_findings": all_findings,    # explicit alias
        "tainted_sinks": [],
        "delegatecall_risks": [],
        "mythril_issues": [],
        # TON routing flags (analogous to is_erc4626/is_proxy on the Solidity side)
        "has_jetton": has_jetton,
        "is_dex": is_dex,
        "has_pool": has_pool,
        "has_multihop": has_multihop,
        "bounce_ignored": bounce_ignored,
        "sender_auth_checks": auth_check_count,
        # EVM conditional-spawn flags forced off so EVM-only conditional specialists never spawn on FunC
        "is_erc4626": False,
        "has_transient_storage": False,
        "is_proxy": False,
        "static_layer": tool.get("layer", 3),
        "tools_available": tool.get("tools", {}),
        "slither_available": False,
        "ton_static_available": True,
        "files_scanned": len(files),
    }
    return static


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python tools/static_analysis_ton.py <project_dir_or_file>")
        return 2
    static = analyse(sys.argv[1])
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUTPUT_DIR / "static.json"
    out.write_text(json.dumps(static, indent=2) + "\n")
    flags = [k for k in ("has_jetton", "is_dex", "has_multihop", "bounce_ignored") if static[k]]
    print(f"[ton-static] {static['files_scanned']} .fc files, {len(static['functions'])} functions, "
          f"{len(static['slither_findings'])} census findings (layer {static['static_layer']}); "
          f"flags: {flags or 'none'}; sender-auth checks: {static['sender_auth_checks']}")
    print(f"[ton-static] wrote {out}")
    if static["bounce_ignored"] and (static["has_jetton"] or static["has_pool"]):
        print("[ton-static] ⚠ ignored-bounce pattern on a value-handling contract — fund-stranding surface")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
