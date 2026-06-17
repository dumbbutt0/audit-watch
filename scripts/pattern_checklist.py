#!/usr/bin/env python3
"""pattern_checklist.py — the CHECKLIST PASS.

Addresses the empirically-measured "having the class != applying it" weakness (a reincorporated mechanism
pattern existed but the cold pass still missed its instance, e.g. secondswap M-13 = the particle-M-05
global-param-change pattern). The recall lab proved (5 full-coverage Solidity contests) that recall is
reasoning-bound and the gap is the LONG TAIL of known patterns not being mechanically applied.

This turns the reincorporated mechanism classes + their `Anchor:` tells (in agents/*.md §-sections) into:
  1. a language-filtered, per-specialist CHECKLIST (every reincorporated pattern, its anchor, a checkbox), and
  2. an ACTIVE SCAN — high-signal grep tokens (derived from the anchors) run over the audit's in-scope source,
     reporting candidate sites (file:line) so the cold pass is pointed at concrete loci, not just told a pattern.

Writes audits/<id>/output/pattern_checklist.md. Read-only on source; advisory (never gates/relabels).

  python scripts/pattern_checklist.py <audit_id>
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from audit_context import audit_language  # noqa: E402

MECH = ROOT / "config" / "mechanism_classes.json"
AGENTS = ROOT / "agents"

# Curated HIGH-SIGNAL grep signals derived from reincorporated anchors. Each is (pattern_label, regex).
# Kept high-precision (concrete code tells) so the active scan points at real loci, not noise.
# language: "sol" | "rust" | "any"
SCAN_SIGNALS = [
    # --- Solidity (from neobase/init-capital/particle/iq-ai/secondswap reincorporations) ---
    ("deadline-blocktimestamp-noop", "sol", r"deadline\s*:\s*block\.timestamp"),
    ("missing-liquidity-slippage", "sol", r"amount0Min\s*:\s*0|amount1Min\s*:\s*0|amountOutMinimum\s*:\s*0|amountAMin\s*:\s*0|amountBMin\s*:\s*0"),
    ("oz-quorum-fraction-percent-misuse", "sol", r"GovernorVotesQuorumFraction\s*\("),
    ("memory-copy-state-write-lost", "sol", r"\b\w+\s+memory\s+\w+\s*=\s*\w+\[[^\]]+\]\s*;"),
    ("strict-equality-balance-dos", "sol", r"require\([^;]*\.balanceOf\([^)]*\)\s*==|==\s*[^;]*amountOut\b"),
    ("ported-uni-0.8-underflow-revert", "sol", r"feeGrowthGlobal[01]?X128|feeGrowthInside[01]?LastX128"),
    ("unconditional-native-refund-dos", "sol", r"\.withdraw\(.*balanceOf|call\{value:\s*(address\(this\)\.balance|wNativeBal|nativeBal)\}"),
    ("blacklist-token-push-refund-dos", "sol", r"safeTransfer\((?:USDC|USDT|usdt|usdc)\b|\.safeTransfer\([^,]+,\s*(?:recipient|to|seller|borrower)\b"),
    ("global-param-change-affects-open-positions", "sol", r"function\s+(set|update)[A-Z]\w*\s*\([^)]*\)\s*external[^{]*\bon(ly)?(Owner|Governor|Admin|Governance)"),
    ("slope-underflow-dos", "sol", r"\.slope\s*-=|slope\s*-=\s*\w"),
    ("masterchef-rewarddebt-rounding", "sol", r"rewardDebt\s*[-+]?=|accCantoPerShare|accRewardPerShare|acc\w*PerShare"),
    ("missing-token-validation", "sol", r"function\s+addCoin|function\s+addToken|function\s+whitelistToken|isTokenSupport\["),
    ("wrong-mapping-key-ownership", "sol", r"_tokenOwner\[|tokenOwner\[|owners?\[\s*(_?owner|msg\.sender)\s*\]\s*="),
    ("tx-initiator-not-verified", "sol", r"address\s+(userAddress|beneficiary)\b"),
    ("aa-wallet-cross-chain-address", "sol", r"function\s+(\w*[Rr]eallocat\w*|\w*[Cc]rossChain\w*|handleReallocation)\s*\("),
    ("division-as-percentage-fee", "sol", r"/\s*(taxCut|feePercent|taxRate|feeCut|feePercentage)\b"),
    ("stale-owner-snapshot-reward-attribution", "sol", r"initialOwners?\[|\bfirstMinter\b|\bfirstDepositor\b|\boriginalOwner\b"),
    # --- Rust/Solana (from woofi/orderly/pyth/lz/drift reincorporations) ---
    ("solana-unchecked-accountinfo", "rust", r"/// *CHECK"),
    ("solana-init-if-needed", "rust", r"\binit_if_needed\b"),
    ("solana-pda-signer-seeds-missing-bump", "rust", r"with_signer\(|invoke_signed\("),
    ("solana-remaining-accounts-trust", "rust", r"\bremaining_accounts\b"),
    ("solana-ed25519-introspection-data-unbound", "rust", r"ed25519|load_instruction_at_checked|message_offset"),
    ("solana-anchor-idl-instructions-enabled", "rust", r"#\[program\]"),
    ("lz-ordered-execution-option-missing", "rust", r"addExecutorLzReceiveOption|inbound_nonce|OrderedExecution"),
]


def _classes(lang: str) -> dict:
    c = json.loads(MECH.read_text())["classes"]
    want = "rust" if lang == "rust" else "solidity"
    return {k: v for k, v in c.items()
            if v.get("status") == "reincorporated" and v.get("language", "solidity") == want}


def _agent_anchors() -> dict[str, list[tuple[str, str, str]]]:
    """Parse agents/*.md §-sections -> {agent_file: [(title, anchor, provenance)]}."""
    out: dict[str, list] = {}
    for md in sorted(AGENTS.glob("*.md")):
        txt = md.read_text()
        blocks = re.split(r"\n###\s+", txt)
        rows = []
        for b in blocks[1:]:
            title = b.splitlines()[0].strip()
            am = re.search(r"Anchor:\s*([^\n]+)", b)
            prov = re.search(r"\(((?:p\d+|p\d+\w*)[^)]*)\)", title)
            if am:
                rows.append((title, am.group(1).strip(), prov.group(1) if prov else ""))
        if rows:
            out[md.stem] = rows
    return out


def _in_scope_files(adir: Path, lang: str) -> list[Path]:
    sp = adir / "scope.json"
    exts = (".rs",) if lang == "rust" else (".sol",)
    files: list[Path] = []
    if sp.exists():
        for f in json.loads(sp.read_text()).get("in_scope_files", []):
            rel = f["file"]
            hits = list((adir / "contracts").rglob(Path(rel).name))
            if hits:
                files.append(hits[0])
    return files


def _scan(files: list[Path], lang: str) -> dict[str, list[str]]:
    sig_lang = "rust" if lang == "rust" else "sol"
    sigs = [(n, re.compile(rx)) for (n, l, rx) in SCAN_SIGNALS if l in (sig_lang, "any")]
    hits: dict[str, list[str]] = {}
    for f in files:
        try:
            lines = f.read_text(errors="ignore").splitlines()
        except Exception:
            continue
        rel = f.name
        for i, line in enumerate(lines, 1):
            for name, rx in sigs:
                if rx.search(line):
                    hits.setdefault(name, []).append(f"{rel}:{i}: {line.strip()[:100]}")
    return hits


def build(aid: str) -> Path:
    adir = ROOT / "audits" / aid
    lang = audit_language(aid)
    classes = _classes(lang)
    anchors = _agent_anchors()
    files = _in_scope_files(adir, lang)
    hits = _scan(files, lang)

    L = [f"# Pattern checklist pass — {aid}  (language: {lang})", "",
         "> Mechanical application of the reincorporated mechanism-class library. Addresses 'having the class "
         "!= applying it'. For EACH in-scope file/function, tick every applicable box. The AUTO-SCAN section "
         "lists concrete candidate sites — DO NOT skip a flagged site without an evidence-anchored reason.", "",
         f"Reincorporated {lang} classes to apply: **{len(classes)}**.", ""]

    # 1. Active scan results first (the actionable part)
    L.append("## AUTO-SCANNED CANDIDATE SITES (apply the matching pattern at each)")
    if not files:
        L.append("\n_(no in-scope source resolved — generate scope.json + source first)_")
    elif not hits:
        L.append("\n_(no high-signal anchor tokens matched — still run the manual checklist below)_")
    else:
        for name in sorted(hits):
            cls = classes.get(name)
            desc = (cls["description"].split(".")[0] if cls else name)
            L.append(f"\n### `{name}` — {desc}")
            for site in hits[name][:25]:
                L.append(f"- [ ] {site}")
            if len(hits[name]) > 25:
                L.append(f"- … +{len(hits[name]) - 25} more")
    L.append("")

    # 2. Full per-specialist checklist (every reincorporated pattern's anchor)
    L.append("## FULL CHECKLIST — every reincorporated pattern (apply per file/function)")
    # map agent->classes
    by_agent: dict[str, list] = {}
    for k, v in classes.items():
        by_agent.setdefault(v.get("agent", "?"), []).append((k, v))
    for agent in sorted(by_agent):
        L.append(f"\n### {agent}")
        for slug, v in sorted(by_agent[agent]):
            tell = v["description"].split(".")[0]
            L.append(f"- [ ] **{slug}** — {tell}.")
    L.append("")

    out = adir / "output" / "pattern_checklist.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + "\n")
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/pattern_checklist.py <audit_id>")
        return 2
    aid = sys.argv[1]
    out = build(aid)
    lang = audit_language(aid)
    n = len(_classes(lang))
    hits = _scan(_in_scope_files(ROOT / "audits" / aid, lang), lang)
    print(f"[checklist] {aid} ({lang}): {n} reincorporated patterns; "
          f"{sum(len(v) for v in hits.values())} candidate sites across {len(hits)} patterns -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
