#!/usr/bin/env python3
"""
build_coverage_manifest.py — Enumerate the COMPLETE review denominator (deterministic, no LLM).

Produces output/coverage_manifest.json: every reviewable item (functions, constructors/initializers,
state variables, constants, immutables, hardcoded addresses, scoped magic numbers) across the in-scope
contracts, each with a stable id, a deterministic attack-surface score, tags, and an in_scope flag.

Primary enumeration is a source regex pass (accurate file paths + line spans + mutability + constants/
addresses, which static.json lacks). static.json supplies SIGNALS keyed by function name: tainted
sinks, external-call sites, slither hits, and the proxy/erc4626 flags. Optional enrichment from
output/coverage_gaps.json (risk_score) and notes/points_of_interest.jsonl (attacker-reachable kind)
is folded in when present.

Usage:
    python scripts/build_coverage_manifest.py [--contract <path_or_dir>]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from fnmatch import fnmatch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path, audit_language  # noqa: E402

try:  # cross-chain taxonomy is best-effort: the builder still works if config/module is absent
    import cross_chain_taxonomy as _xchain
except Exception:  # pragma: no cover
    _xchain = None

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_VERSION = 1

DEFAULT_EXCLUDE_GLOBS = ["**/mocks/**", "**/Mock*.sol", "**/test/**", "**/tests/**", "**/*.t.sol"]

# --- tag keyword maps (lowercased substring match against name+file+signature) ---
TAG_KEYWORDS = {
    "accounting": ("stalk", "root", "bdv", "balance", "deposit", "withdraw", "mint", "burn",
                   "supply", "debt", "pod", "fertiliz", "silo", "convert", "earned", "germinat",
                   "harvest", "sow", "plot", "season", "flood", "sop", "shipment"),
    "oracle":     ("oracle", "price", "twap", "chainlink", "deltab", "pump", "reserve", "usd",
                   "uniswap", "wsteth", "lookback", "cumulativeprice", "pricecumulative", "spot",
                   "getreserves", "slot0", "latestrounddata", "quote", "validateprice"),
    # AMM / protocol-owned-liquidity / swap machinery — the value-at-risk price surface.
    # (Olas recall-lab lesson: most awarded Highs lived in BalancerPriceOracle / UniswapPriceOracle /
    #  LiquidityManager / BuyBackBurner, a cluster that was deprioritized. Tag it explicitly so it ranks top.)
    "amm_pol":    ("swap", "liquidity", "pool", "tick", "slippage", "amountout", "amountin", "slipstream",
                   "balancer", "univ3", "uniswapv3", "rebalance", "buyback", "buyandburn", "pol", "sqrtprice",
                   "concentrated", "range", "changeranges", "addliquidity", "removeliquidity", "minamount",
                   "deadline", "swapexact"),
    "token":      ("transfer", "approve", "erc20", "erc1155", "erc721", "token", "safetransfer",
                   "permit", "allowance"),
    "permissions":("onlyowner", "enforceis", "onlyrole", "auth", "owner", "grant", "whitelist",
                   "pause", "diamondcut", "admin"),
    "migration":  ("reseed", "migrat", "bridge", "recieve", "receivel1", "l1", "l2", "xdomain"),
    "config":     ("registry", "address", "constant", "immutable", "pipeline", "weth", "factory"),
    "decimals":   ("decimal", "1e6", "1e18", "1e24", "precision", "scale"),
}
ADDRESS_RE  = re.compile(r"0x[a-fA-F0-9]{40}\b")
FUNC_RE     = re.compile(r"\bfunction\s+([A-Za-z_]\w*)\s*\(")
CTOR_RE     = re.compile(r"\bconstructor\s*\(")
TYPE_DECL   = re.compile(r"\b(contract|interface|library|abstract\s+contract)\s+([A-Za-z_]\w*)")
VIS_TOKENS  = {"public", "external", "internal", "private"}
MUT_TOKENS  = {"view", "pure", "payable"}
INIT_NAMES  = {"initialize", "init", "initializer", "setupinitialdiamond"}

# --- Rust / Solana (Anchor) taxonomy + extraction (cross-language; selected by audit language) ---------------
# Tag names deliberately REUSE the Solidity scoring names where the concept maps (accounting/token/permissions/
# config/decimals/migration) and add Solana-native ones (account_validation/cpi/pda/serialization). The
# value-at-risk score in add() rewards these so signer/owner/CPI/PDA-touching handlers rank to the top.
RUST_TAG_KEYWORDS = {
    "permissions":        ("signer", "is_signer", "owner", "authority", "admin", "has_one", "onlyowner",
                           "access_control", "require_keys_eq", "constraint", "only_owner"),
    "account_validation": ("account", "accountinfo", "discriminator", "try_borrow", "deserialize", "unpack",
                           "load", "zero_copy", "realloc", "key()", "to_account_info", "checked"),
    "cpi":                ("invoke", "invoke_signed", "cpi", "cross_program", "system_program", "token::",
                           "program::", "remaining_accounts"),
    "pda":                ("seeds", "find_program_address", "create_program_address", "bump", "pda", "canonical"),
    "accounting":         ("lamports", "balance", "amount", "transfer", "mint", "burn", "supply", "deposit",
                           "withdraw", "stake", "reward", "fee", "debt", "collateral"),
    "token":              ("spl", "token", "mint", "ata", "associated", "metadata", "transfer_checked"),
    "config":             ("pubkey", "sysvar", "clock", "rent", "const ", "constant"),
    "decimals":           ("decimals", "lamports", "rent", "scale", "precision"),
    "migration":          ("bridge", "cross", "wormhole", "layerzero", "relay", "message"),
    "serialization":      ("borsh", "serialize", "try_from_slice", "bytemuck", "pod", "zerocopy"),
}
RUST_FN_RE    = re.compile(r"\bfn\s+([A-Za-z_]\w*)\s*[(<]")
RUST_TYPE_DECL = re.compile(r"\b(struct|enum|mod|trait)\s+([A-Za-z_]\w*)")
RUST_INIT_NAMES = {"initialize", "init", "new", "create", "setup"}

# --- Move / Sui taxonomy + extraction (cross-language; selected by audit language) ---------------------------
# Tag names REUSE the Solidity scoring names where the concept maps (accounting/token/permissions/config/decimals/
# migration/amm_pol/oracle) and add Move/Sui-native ones (capability/object_model/arithmetic). The value-at-risk
# score in add() rewards these so capability/object/coin/liquidity-math-touching functions rank to the top.
# Cetus-class lesson: the $220M Sui CLMM drain lived in the integer/liquidity math (checked_shlw/full_math),
# so 'arithmetic' + 'amm_pol' are tagged aggressively.
MOVE_TAG_KEYWORDS = {
    "permissions":  ("signer", "txcontext", "sender", "capability", "_cap", "admincap", "witness", "acl",
                     "authority", "admin", "owner", "is_admin", "assert_", "only", "versioned", "version"),
    "object_model": ("uid", "object::", "shared", "share_object", "transfer", "public_transfer", "dynamic_field",
                     "dynamic_object_field", "df::", "dof::", "borrow_mut", "borrow", "key", "store"),
    "amm_pol":      ("swap", "liquidity", "pool", "tick", "sqrt_price", "sqrtprice", "position", "flash",
                     "compute_swap", "add_liquidity", "remove_liquidity", "mint", "burn", "fee_growth",
                     "reward", "delta", "range", "slippage", "amount_in", "amount_out"),
    "arithmetic":   ("full_math", "checked_shl", "checked_shlw", "math_u128", "math_u256", "math_u64", "overflow",
                     "shlw", "<<", ">>", "mul_div", "muldiv", "math_liquidity", "math_sqrt", "math_tick", "carry"),
    "accounting":   ("balance", "coin", "amount", "deposit", "withdraw", "collect", "fee", "supply", "debt",
                     "reserve", "protocol_fee", "split", "join", "value"),
    "token":        ("coin", "balance", "treasury", "treasurycap", "supply", "mint", "burn", "metadata"),
    "config":       ("const ", "constant", "registry", "config", "package", "published"),
    "decimals":     ("decimal", "scale", "precision", "q64", "q128", "1u64", "1u128", "fixed_point"),
    "migration":    ("bridge", "wormhole", "cross_chain", "migrate", "relay", "message"),
    "oracle":       ("oracle", "price", "twap", "observation", "cumulative"),
}
# Move declarations: `public fun`, `public(friend) fun`, `entry fun`, `public entry fun`, plain `fun`.
MOVE_FN_RE    = re.compile(r"\bfun\s+([A-Za-z_]\w*)\s*[(<]")
MOVE_TYPE_DECL = re.compile(r"\b(module|struct)\s+([A-Za-z_][\w:]*)")
MOVE_CONST_RE = re.compile(r"\bconst\s+([A-Z][A-Za-z0-9_]*)\s*:")
MOVE_INIT_NAMES = {"init", "initialize", "new", "create", "create_pool", "open_position"}

# Active taxonomy — defaults to Solidity; main() swaps to RUST_TAG_KEYWORDS for a rust audit. _tags_for() and
# add() read this so the Solidity path is byte-behavior-unchanged when language is solidity.
ACTIVE_TAG_KEYWORDS = TAG_KEYWORDS


def _short_id(kind: str, contract: str, name: str, file: str, line: int) -> str:
    slug = f"{kind}:{contract}:{name}"
    h = hashlib.sha256(f"{slug}:{file}:{line}".encode()).hexdigest()[:8]
    return f"{slug}#{h}"


def _sol_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root] if root.suffix == ".sol" else []
    return sorted(p for p in root.rglob("*.sol") if p.is_file())


def _rust_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root] if root.suffix == ".rs" else []
    skip = ("/target/", "/tests/", "/.git/")
    return sorted(p for p in root.rglob("*.rs")
                  if p.is_file() and not any(s in p.as_posix() for s in skip)
                  and not p.name.endswith("_test.rs") and p.name != "build.rs")


def _move_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root] if root.suffix == ".move" else []
    skip = ("/tests/", "/build/", "/.git/", "/target/")
    return sorted(p for p in root.rglob("*.move")
                  if p.is_file() and not any(s in p.as_posix() for s in skip)
                  and not p.name.endswith("_test.move") and not p.name.endswith("_tests.move"))


def _source_files(root: Path, lang: str) -> list[Path]:
    """Language-dispatched source enumeration. Solidity default keeps _sol_files byte-identical."""
    if lang == "rust":
        return _rust_files(root)
    if lang == "move":
        return _move_files(root)
    return _sol_files(root)


def _infer_language(root: Path) -> str:
    """Infer audit language from the source tree (used when meta.language is unset/solidity but the tree is
    Rust/Move). Conservative: only returns a non-Solidity language when there are NO .sol files and there ARE
    files of that language. Solidity remains the default."""
    if root.is_file():
        if root.suffix == ".rs":
            return "rust"
        if root.suffix == ".move":
            return "move"
        return "solidity"
    if not _sol_files(root):
        if _rust_files(root):
            return "rust"
        if _move_files(root):
            return "move"
    return "solidity"


def _rel(p: Path, root: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def _norm_scope_entry(line: str) -> str:
    """Normalize a scope.txt line to a comparable relative suffix: strip comments, ./ and leading /."""
    s = line.split("#", 1)[0].strip()
    if not s:
        return ""
    s = s.lstrip("./").lstrip("/")
    return s


def _load_scope_allowlist(croot: Path) -> tuple[set[str] | None, set[str]]:
    """
    Look for scope.txt / out_of_scope.txt at the contract root (or its parent if a file), and at the
    repo root. Returns (allow, deny) of normalized relative path suffixes/globs, or (None, deny) when no
    scope.txt is found (→ legacy exclude-glob behavior). Only reads scope files — never the findings report.
    """
    search_dirs = []
    base = croot if croot.is_dir() else croot.parent
    for d in (base, base.parent, ROOT):
        if d not in search_dirs:
            search_dirs.append(d)

    def _read(name: str) -> set[str]:
        for d in search_dirs:
            f = d / name
            if f.exists():
                return {e for e in (_norm_scope_entry(ln) for ln in f.read_text().splitlines()) if e}
        return set()

    allow = _read("scope.txt")
    deny = _read("out_of_scope.txt")
    return (allow or None), deny


def _matches_scope(rel_path: str, entries: set[str]) -> bool:
    """A file matches a scope entry if its path ends with the entry or fnmatches it (glob support)."""
    for e in entries:
        if rel_path == e or rel_path.endswith("/" + e) or rel_path.endswith(e) or fnmatch(rel_path, e) or fnmatch(rel_path, "*/" + e):
            return True
    return False


def _in_scope(rel_path: str, is_pure_interface: bool, exclude_globs: list[str],
              scope_allow: set[str] | None = None, scope_deny: set[str] | None = None) -> tuple[bool, str]:
    # Explicit scope-file ingestion takes precedence when a scope.txt is present (kills manual staging:
    # point analyze at the repo contracts/ dir and the contest scope file restricts the denominator).
    if scope_deny and _matches_scope(rel_path, scope_deny):
        return False, "listed in out_of_scope.txt"
    if scope_allow is not None:
        if not _matches_scope(rel_path, scope_allow):
            return False, "not listed in scope.txt"
        if is_pure_interface:
            return False, "pure interface (no implementation)"
        return True, "in scope.txt"
    for g in exclude_globs:
        if fnmatch(rel_path, g) or fnmatch("/" + rel_path, g):
            return False, f"path matches exclude glob '{g}'"
    if is_pure_interface:
        return False, "pure interface (no implementation)"
    return True, "in-scope production contract"


def _tags_for(text: str, extra: set[str]) -> list[str]:
    t = text.lower()
    tags = set(extra)
    for tag, kws in ACTIVE_TAG_KEYWORDS.items():
        if any(k in t for k in kws):
            tags.add(tag)
    return sorted(tags)


def _signature_block(lines: list[str], start_idx: int) -> tuple[str, int, int, str]:
    """From a 'function ...' line, gather the signature until '{' or ';', then brace-match the body.

    Returns (signature_text, end_line_1based, body_end_1based, span_method).
    """
    sig_parts = []
    i = start_idx
    n = len(lines)
    opened = False
    while i < n:
        sig_parts.append(lines[i])
        if "{" in lines[i]:
            opened = True
            break
        if ";" in lines[i]:  # interface / abstract declaration, no body
            return " ".join(s.strip() for s in sig_parts), i + 1, i + 1, "regex_start_only"
        i += 1
        if i - start_idx > 25:  # runaway guard
            break
    sig_text = " ".join(s.strip() for s in sig_parts)
    if not opened:
        return sig_text, start_idx + 1, start_idx + 1, "regex_start_only"
    # brace match from the line that opened the body
    depth = 0
    j = i
    while j < n:
        depth += lines[j].count("{") - lines[j].count("}")
        if depth <= 0:
            return sig_text, start_idx + 1, j + 1, "regex_brace_match"
        j += 1
        if j - i > 4000:
            break
    return sig_text, start_idx + 1, min(j, n) + 1, "regex_brace_match_truncated"


def _parse_visibility_mutability(sig: str) -> tuple[str, str, list[str]]:
    # tokens between ')' and '{'/'returns'
    after = sig.split(")", 1)[1] if ")" in sig else sig
    after = re.split(r"\breturns\b|\{", after, 1)[0]
    toks = re.findall(r"[A-Za-z_]\w*", after)
    vis = next((t for t in toks if t in VIS_TOKENS), "internal")
    mut = next((t for t in toks if t in MUT_TOKENS), "")
    mods = [t for t in toks if t not in VIS_TOKENS and t not in MUT_TOKENS
            and t not in {"returns", "virtual", "override", "memory", "calldata", "storage"}]
    return vis, mut, mods


def _load_static() -> dict:
    p = audit_path("output") / "static.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _git_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, timeout=5).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


_MOCK_PATH_SEGMENTS = ("/mock", "/mocks/", "/test/", "/tests/", "/fixture")
# A single trivial return whose value carries no logic. ALL-CAPS bare identifier = a named constant.
_TRIVIAL_RETURN_RE = re.compile(
    r"^return\s+(?:new\s+\w+\[\]\(\s*0\s*\)|address\(\s*0\s*\)|0|1|true|false|\"\"|''|[A-Z_][A-Z0-9_]*)\s*;$"
)


def _is_mock_item(item: dict) -> bool:
    """P132: boost-exclude mocks/tests by STRUCTURE (file/contract/path), never by comments or strings.

    Catches `Mock*.sol` and `*Mock*.sol` (e.g. `ConnectorMock2.sol`), `contract *Mock*` even when the file
    name is not Mock-prefixed, and obvious test/mock/fixture path segments. Boost-local only — it does not
    change global scope membership.
    """
    fname = (item.get("file") or "").rsplit("/", 1)[-1].lower()
    contract = (item.get("contract") or "").lower()
    path = (item.get("file") or "").lower()
    if "mock" in fname or "mock" in contract:
        return True
    return any(seg in path for seg in _MOCK_PATH_SEGMENTS)


def _is_trivial_body(body_src: str) -> bool:
    """P132: True iff the function body is empty or a single non-informative `return <trivial-expr>;`.

    Trivial-expr ∈ {new T[](0), address(0), 0, 1, true, false, "", '', ALL_CAPS constant}. Comments are
    stripped first. ANYTHING else — any call, internal call, arithmetic, indexing, loop/conditional,
    assignment, member access, multiple statements, or value/oracle/TVL logic — is non-trivial (kept).
    Conservative: when in doubt, return False (do not trim) so recall is preserved.
    """
    if "{" not in body_src or "}" not in body_src:
        return False
    inner = body_src[body_src.find("{") + 1: body_src.rfind("}")]
    inner = re.sub(r"/\*.*?\*/", "", inner, flags=re.S)   # block comments
    inner = re.sub(r"//[^\n]*", "", inner)                # line comments
    stmts = [s.strip() for s in inner.split(";") if s.strip()]
    if not stmts:
        return True
    if len(stmts) == 1:
        st = re.sub(r"\s+", " ", stmts[0]).strip() + ";"
        if _TRIVIAL_RETURN_RE.match(st):
            return True
    return False


def _apply_library_surface_boost(items: list[dict], pol: dict) -> int:
    """P130: rescue risk-tagged computation/helper logic that under-scores at the manifest stage.

    General source-resolution repair for library/Diamond-heavy protocols, where value/oracle/accounting
    logic lives in `view`/`internal` helpers and `library`/`*Facet` code. Such functions get only the
    risk-tag +2 (they miss the external-state-changing +2) and sit just below the deep-pass cutoff, so the
    awarded bug's contract is never inspected at depth (the P129 "wrong contract inspected" miss class).

    Two-signal, FP-tight, capped, reversible. A function is boosted to the cutoff (score=3) ONLY if it
    BOTH (a) carries a risk tag the scorer already rewards {accounting,token,oracle,migration,config}
    AND (b) is computation/helper logic (internal/private OR view/pure OR contract_type==library OR a
    *Facet contract). At most `cap` per contract (highest-signal first) to bound deep-pass inflation.
    Keys only off generic structure/tags — NO contract names, issue ids, or answer-key labels.
    """
    if not pol.get("library_internal_surface_boost", True):
        return 0
    cutoff = int(pol.get("deep_pass_attack_surface_score_min", 3))
    cap = int(pol.get("library_internal_surface_boost_cap_per_contract", 3))
    RISK = {"accounting", "token", "oracle", "migration", "config", "amm_pol"}
    STRONG = {"oracle", "accounting", "migration", "amm_pol"}

    def is_helper(it: dict) -> bool:
        return (it.get("visibility") in ("internal", "private")
                or it.get("mutability") in ("view", "pure")
                or it.get("contract_type") == "library"
                or str(it.get("contract", "")).endswith("Facet"))

    def eligible(it: dict) -> bool:
        return (it.get("kind") == "function" and it.get("in_scope")
                and it.get("attack_surface_score", 0) < cutoff
                and bool(RISK & set(it.get("tags", []))) and is_helper(it)
                # P132 noise trims: never boost mock/test helpers or trivial-bodied helpers
                and not _is_mock_item(it) and not it.get("trivial_body", False))

    def rank(it: dict):
        t = set(it.get("tags", []))
        return (len(STRONG & t), len(RISK & t),
                int(bool(it.get("external_calls"))) + int(bool(it.get("in_tainted_sink"))))

    by_contract: dict[str, list[dict]] = {}
    for it in items:
        if eligible(it):
            by_contract.setdefault(it.get("contract"), []).append(it)
    boosted = 0
    for _c, its in by_contract.items():
        its.sort(key=rank, reverse=True)
        for it in its[:cap]:
            it["attack_surface_score"] = cutoff
            it["surface_boost"] = "library_internal_risk"  # provenance: measurable + one-flag reversible
            boosted += 1
    return boosted


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the coverage manifest (deterministic, no LLM).")
    ap.add_argument("--contract", help="Contract file or dir (default: static.json contract_path)")
    ap.add_argument("--out", help="Output path (default: output/coverage_manifest.json). Use a sandbox "
                                  "path to preview a rebuild without touching the live/frozen manifest.")
    args = ap.parse_args()

    static = _load_static()
    contract = args.contract or static.get("contract_path")
    if not contract:
        raise SystemExit("[build_coverage_manifest] No --contract and no contract_path in static.json.")
    croot = Path(contract)
    if not croot.exists():
        croot = ROOT / contract
    if not croot.exists():
        raise SystemExit(f"[build_coverage_manifest] contract path not found: {contract}")

    # Cross-language: the manifest is about the --contract tree, so the tree wins when it is UNAMBIGUOUSLY a
    # single language. Prefer the audit's declared language otherwise (incl. mixed trees, where _infer_language is
    # conservative and returns "solidity"). This keeps a real run byte-behavior-unchanged (declared==inferred) while
    # making `--contract <other-language-tree>` correct even when the active audit is a different language.
    global ACTIVE_TAG_KEYWORDS
    lang = audit_language()
    inferred = _infer_language(croot)
    if inferred in ("rust", "move") and inferred != lang:
        # the targeted tree is clearly rust/move and differs from the active audit -> trust the tree
        lang = inferred
    elif lang not in ("rust", "move"):
        lang = inferred
    # set explicitly so the swap is idempotent if main() is called more than once in-process
    if lang == "rust":
        ACTIVE_TAG_KEYWORDS = RUST_TAG_KEYWORDS
    elif lang == "move":
        ACTIVE_TAG_KEYWORDS = MOVE_TAG_KEYWORDS
    else:
        ACTIVE_TAG_KEYWORDS = TAG_KEYWORDS

    # config (exclude globs + scope-file ingestion toggle)
    exclude_globs = DEFAULT_EXCLUDE_GLOBS
    scope_ingestion = True
    try:
        pol = json.loads((ROOT / "config" / "agent_policy.json").read_text()).get("coverage_policy", {})
        exclude_globs = pol.get("exclude_globs") or DEFAULT_EXCLUDE_GLOBS
        scope_ingestion = pol.get("scope_file_ingestion_enabled", True)
    except Exception:
        pass

    # contest scope-file ingestion (scope.txt / out_of_scope.txt). When present, it overrides exclude-glob
    # scoping so the manifest denominator == the contest scope without manual file staging.
    scope_allow, scope_deny = (None, set())
    if scope_ingestion:
        scope_allow, scope_deny = _load_scope_allowlist(croot)

    # static signals keyed by function name
    ext_call_fns = {c.get("function") for c in static.get("external_calls", []) if c.get("function")}
    sink_fns = {s.get("function") for s in static.get("tainted_sinks", []) if s.get("function")}
    slither_by_file: dict[str, int] = {}
    for f in static.get("slither_findings", []):
        fn = (f.get("file") or "").split("/")[-1]
        slither_by_file[fn] = slither_by_file.get(fn, 0) + 1

    # optional enrichment
    risk_by_key: dict[tuple, int] = {}
    cg = audit_path("output") / "coverage_gaps.json"
    if cg.exists():
        try:
            for r in json.loads(cg.read_text()).get("all_untested", []):
                risk_by_key[(r.get("contract"), r.get("name"))] = r.get("risk_score", 0)
        except Exception:
            pass

    items: list[dict] = []
    seen_ids: set[str] = set()

    def add(kind, contract_name, name, file_rel, line_start, line_end, span_method,
            visibility="", mutability="", modifiers=None, signature="", extra_tags=None):
        iid = _short_id(kind, contract_name or "?", name, file_rel, line_start)
        # ensure uniqueness even on collision
        base = iid
        k = 1
        while iid in seen_ids:
            iid = f"{base}~{k}"; k += 1
        seen_ids.add(iid)
        tags = _tags_for(f"{name} {file_rel} {signature}", set(extra_tags or []))
        is_state_changing = kind in ("function", "constructor", "initializer") and mutability not in ("view", "pure")
        has_ext = name in ext_call_fns or kind == "function" and bool(re.search(r"\.(call|delegatecall|transfer|send)\b", signature))
        in_sink = name in sink_fns
        has_loop = "loop" in tags
        is_perm = bool(modifiers) and any(m.lower() in ACTIVE_TAG_KEYWORDS.get("permissions", ()) for m in (modifiers or [])) or "permissions" in tags
        # deterministic attack-surface score (spec heuristic)
        score = 0
        if kind in ("function", "constructor", "initializer") and visibility in ("external", "public") and is_state_changing:
            score += 2
        if any(t in tags for t in ("accounting", "token", "oracle", "migration", "config", "amm_pol",
                                    "cpi", "account_validation", "pda", "arithmetic", "object_model")):
            score += 2
        # Value-at-risk boost: price/oracle/AMM/POL machinery (Solidity), account-validation/CPI/PDA
        # machinery (Solana), and integer/liquidity math + object/capability surface (Move/Sui — the
        # Cetus-class drain lived in the liquidity math) are where loss-of-funds concentrates. Rank ABOVE
        # generic state-changing functions so the cold pass / specialists hit it first (recall-lab coverage fix).
        if any(t in tags for t in ("oracle", "amm_pol", "cpi", "account_validation", "pda", "arithmetic")):
            score += 1
        if has_ext:
            score += 1
        if has_loop:
            score += 1
        if is_perm:
            score += 1
        if kind in ("constant", "immutable", "magic_number", "address") and any(
                t in tags for t in ("accounting", "token", "oracle", "config", "decimals", "amm_pol")):
            score += 1
        if kind in ("constructor", "initializer") or "migration" in tags:
            score += 1
        if in_sink:
            score += 2
        rel_for_scope = file_rel
        item = {
            "id": iid, "kind": kind, "contract": contract_name, "file": file_rel,
            "name": name, "signature": signature[:300], "visibility": visibility,
            "mutability": mutability, "modifiers": modifiers or [],
            "external_calls": bool(has_ext), "in_tainted_sink": bool(in_sink),
            "has_loop": bool(has_loop), "slither_hits_in_file": slither_by_file.get(file_rel.split("/")[-1], 0),
            "risk_score": risk_by_key.get((contract_name, name), 0),
            "source_span": {"start_line": line_start, "end_line": line_end, "method": span_method},
            "tags": tags, "attack_surface_score": score,
        }
        # Cross-chain-sensitive tagging (focused: constants/immutables/addresses + any taxonomy
        # name match). Harmless literals match nothing and stay untagged — no manifest explosion.
        if _xchain is not None and kind in ("constant", "immutable", "address", "magic_number"):
            cls = _xchain.classify(name, signature, file_rel)
            if cls and cls.get("cross_chain_sensitive"):
                item["cross_chain_sensitive"] = True
                item["cross_chain_category"] = cls["category"]
                item.update(_xchain.risk_flags(cls))
                if cls.get("severity_ceiling_hint"):
                    item["cross_chain_severity_hint"] = cls["severity_ceiling_hint"]
                if "cross_chain" not in item["tags"]:
                    item["tags"] = sorted(item["tags"] + ["cross_chain"])
                if _xchain.is_high_risk(cls) and score < 3:
                    item["attack_surface_score"] = 3  # ensure high-risk x-chain constants are high-surface
        return item, rel_for_scope

    # --- Rust / Solana parse path (cross-language). Produces the same item schema via add(); the value-at-risk
    # score rewards signer/owner/CPI/PDA/account-validation tags so handlers rank to the top. ---
    _RUST_CONTAINER = re.compile(r"\b(mod|impl|struct|enum|trait)\s+(?:<[^>]*>\s*)?([A-Za-z_]\w*)")
    _RUST_CONST = re.compile(r"\b(?:const|static)\s+([A-Z][A-Z0-9_]*)\s*:")
    for fpath in (_rust_files(croot) if lang == "rust" else []):
        src = fpath.read_text(encoding="utf-8", errors="replace")
        lines = src.splitlines()
        file_rel = _rel(fpath, ROOT)
        in_scope, scope_reason = _in_scope(file_rel, False, exclude_globs, scope_allow, scope_deny)
        # attribute items to the enclosing mod/impl/struct/trait (Rust "contract" analog)
        mod_at: list[str] = []
        cur = fpath.stem
        for ln in lines:
            if not ln.lstrip().startswith("//"):
                mm = _RUST_CONTAINER.search(ln)
                if mm:
                    cur = mm.group(2)
            mod_at.append(cur)
        produced: list[dict] = []
        for idx, ln in enumerate(lines):
            s = ln.lstrip()
            if s.startswith("//"):
                continue
            cname = mod_at[idx]
            fm = RUST_FN_RE.search(ln)
            if fm:
                name = fm.group(1)
                is_pub = ("pub fn" in ln) or ("pub(" in ln and " fn " in ln) or s.startswith("pub ")
                vis = "external" if is_pub else "internal"
                kind = "initializer" if name.lower() in RUST_INIT_NAMES else "function"
                it, _ = add(kind, cname, name, file_rel, idx + 1, idx + 1, "regex_start_only",
                            vis, "", [], ln.strip())
                produced.append(it)
            cm = _RUST_CONST.search(ln)
            if cm:
                it, _ = add("constant", cname, cm.group(1), file_rel, idx + 1, idx + 1,
                            "regex_start_only", signature=ln.strip(), extra_tags={"constant"})
                produced.append(it)
            for am in ADDRESS_RE.finditer(ln):
                it, _ = add("address", cname, am.group(0), file_rel, idx + 1, idx + 1,
                            "regex_start_only", signature=ln.strip(), extra_tags={"config"})
                produced.append(it)
        for it in produced:
            it["in_scope"] = in_scope
            it["scope_reason"] = scope_reason
            it["contract_type"] = "rust_module"
            items.append(it)

    # --- Move / Sui parse path (cross-language). Produces the same item schema via add(); the value-at-risk
    # score rewards capability/object/coin/liquidity-math (arithmetic/amm_pol) tags so handlers rank to the top.
    for fpath in (_move_files(croot) if lang == "move" else []):
        src = fpath.read_text(encoding="utf-8", errors="replace")
        lines = src.splitlines()
        file_rel = _rel(fpath, ROOT)
        in_scope, scope_reason = _in_scope(file_rel, False, exclude_globs, scope_allow, scope_deny)
        # attribute items to the enclosing module (Move "contract" analog)
        mod_at: list[str] = []
        cur = fpath.stem
        for ln in lines:
            s = ln.lstrip()
            if not s.startswith("//"):
                mm = MOVE_TYPE_DECL.search(ln)
                if mm and mm.group(1) == "module":
                    # module addr::name { ... }  -> use the trailing name
                    cur = mm.group(2).split("::")[-1]
            mod_at.append(cur)
        produced: list[dict] = []
        for idx, ln in enumerate(lines):
            s = ln.lstrip()
            if s.startswith("//") or s.startswith("*") or s.startswith("/*"):
                continue
            cname = mod_at[idx]
            fm = MOVE_FN_RE.search(ln)
            if fm:
                name = fm.group(1)
                # Move visibility: `public`, `public(friend)`/`public(package)`, `entry`. Treat public/entry as
                # the externally-reachable attack surface (analogous to Solidity external/public).
                is_entry = bool(re.search(r"\bentry\b", ln))
                is_public = bool(re.search(r"\bpublic\b", ln))
                vis = "external" if (is_entry or is_public) else "internal"
                mods = []
                if is_entry:
                    mods.append("entry")
                if "public(friend)" in ln or "public(package)" in ln:
                    mods.append("restricted_public")
                kind = "initializer" if name.lower() in MOVE_INIT_NAMES else "function"
                it, _ = add(kind, cname, name, file_rel, idx + 1, idx + 1, "regex_start_only",
                            vis, "", mods, ln.strip())
                produced.append(it)
            cm = MOVE_CONST_RE.search(ln)
            if cm:
                it, _ = add("constant", cname, cm.group(1), file_rel, idx + 1, idx + 1,
                            "regex_start_only", signature=ln.strip(), extra_tags={"constant"})
                produced.append(it)
        for it in produced:
            it["in_scope"] = in_scope
            it["scope_reason"] = scope_reason
            it["contract_type"] = "move_module"
            items.append(it)

    for fpath in (_sol_files(croot) if lang not in ("rust", "move") else []):
        src = fpath.read_text(encoding="utf-8", errors="replace")
        lines = src.splitlines()
        file_rel = _rel(fpath, ROOT)
        # detect contracts in file + whether file is pure interface
        decls = TYPE_DECL.findall(src)
        kinds_decl = {d[0].replace("abstract contract", "contract") for d in decls}
        is_pure_interface = bool(decls) and kinds_decl == {"interface"}
        in_scope, scope_reason = _in_scope(file_rel, is_pure_interface, exclude_globs, scope_allow, scope_deny)

        # track current contract by line for attribution
        contract_at: list[str] = []
        cur = "?"
        for ln in lines:
            stripped = ln.lstrip()
            # Skip comment lines so prose like "* ... this contract on L2 ..." can't flip attribution.
            if not stripped.startswith(("//", "*", "/*")):
                m = TYPE_DECL.search(ln)
                if m:
                    cur = m.group(2)
            contract_at.append(cur)

        produced: list[dict] = []
        # functions + constructors
        for idx, ln in enumerate(lines):
            # Skip comment lines: NatSpec '@param foo(...)' prose and commented-out (// ...) constants
            # must not be captured as real items (regex would otherwise misread doc signatures).
            stripped = ln.lstrip()
            if stripped.startswith(("//", "*", "/*", "///")):
                continue
            cname = contract_at[idx]
            fm = FUNC_RE.search(ln)
            if fm:
                sig, end_decl, body_end, method = _signature_block(lines, idx)
                vis, mut, mods = _parse_visibility_mutability(sig)
                name = fm.group(1)
                kind = "initializer" if name.lower() in INIT_NAMES or "initializer" in [m.lower() for m in mods] else "function"
                it, _ = add(kind, cname, name, file_rel, idx + 1, body_end, method,
                            vis, mut, mods, sig)
                it["trivial_body"] = _is_trivial_body("\n".join(lines[idx:body_end]))
                produced.append(it)
            elif CTOR_RE.search(ln):
                sig, end_decl, body_end, method = _signature_block(lines, idx)
                vis, mut, mods = _parse_visibility_mutability(sig)
                it, _ = add("constructor", cname, "constructor", file_rel, idx + 1, body_end, method,
                            vis or "public", mut, mods, sig)
                produced.append(it)
            # constants / immutables (declaration lines)
            if re.search(r"\bconstant\b", ln) and "=" in ln and "function" not in ln:
                nm = re.search(r"(\w+)\s*=", ln)
                it, _ = add("constant", cname, nm.group(1) if nm else "const", file_rel, idx + 1, idx + 1,
                            "regex_start_only", signature=ln.strip(), extra_tags={"constant"})
                produced.append(it)
            elif re.search(r"\bimmutable\b", ln) and "function" not in ln:
                nm = re.search(r"(\w+)\s*(=|;)", ln)
                it, _ = add("immutable", cname, nm.group(1) if nm else "immutable", file_rel, idx + 1, idx + 1,
                            "regex_start_only", signature=ln.strip(), extra_tags={"constant"})
                produced.append(it)
            # hardcoded addresses
            for am in ADDRESS_RE.finditer(ln):
                it, _ = add("address", cname, am.group(0), file_rel, idx + 1, idx + 1,
                            "regex_start_only", signature=ln.strip(), extra_tags={"config"})
                produced.append(it)

        # contract_type per declared name (general signal; no protocol-specific strings)
        file_decl_kind = {d[1]: d[0].replace("abstract contract", "abstract_contract") for d in decls}
        for it in produced:
            it["in_scope"] = in_scope
            it["scope_reason"] = scope_reason
            it["contract_type"] = file_decl_kind.get(it.get("contract"), "contract")
            items.append(it)

    n_boosted = _apply_library_surface_boost(items, pol)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "source": {
            "static_json": "output/static.json",
            "contracts_root": str(croot),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "git_commit": _git_commit(),
            "exclude_globs": exclude_globs,
            "scope_file": ("scope.txt" if scope_allow is not None else None),
            "scope_allow_count": (len(scope_allow) if scope_allow is not None else 0),
            "out_of_scope_count": len(scope_deny or []),
        },
        "items": items,
    }
    out = Path(args.out) if args.out else audit_path("output") / "coverage_manifest.json"
    out.write_text(json.dumps(manifest, indent=2))

    in_scope_n = sum(1 for i in items if i["in_scope"])
    xchain_n = sum(1 for i in items if i.get("cross_chain_sensitive"))
    by_kind: dict[str, int] = {}
    for i in items:
        by_kind[i["kind"]] = by_kind.get(i["kind"], 0) + 1
    print(f"[ok] coverage manifest → {out}")
    print(f"     items: {len(items)} ({in_scope_n} in-scope) · by kind: {by_kind}")
    print(f"     high-surface (score>=3, in-scope): {sum(1 for i in items if i['in_scope'] and i['attack_surface_score']>=3)}")
    print(f"     cross-chain-sensitive: {xchain_n}")
    print(f"     library/internal risk-logic boosted (P130): {sum(1 for i in items if i.get('surface_boost')=='library_internal_risk')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
