#!/usr/bin/env python3
"""
normalize.py — normalization helpers for the candidate author.

Pure, deterministic, stdlib-only. Every helper maps loosely-worded input onto the
exact enum / shape the submission schema expects, and falls back to a *cautious*
safe default when the input does not clearly say otherwise. Nothing here invents
evidence: an unknown severity becomes the lowest claim, an unknown scope becomes
"uncertain", an unidentifiable impact becomes "info" — never the other way around.
"""
from __future__ import annotations

import re

# --- safe defaults (cautious: never inflate, never claim) -------------------

SAFE_DEFAULTS = {
    "severity_claim": "Informational",   # lowest; the report must state higher
    "scope_status": "uncertain",         # never assume in_scope
    "impact_category": "info",           # no concrete impact identified
    "privilege_required": "none",        # most findings are permissionless
    "proof_type": "reasoning_only",      # no runnable PoC unless proven
    "poc_status": "none",
    "duplicate_check_status": "not_searched",
    "known_issue_check_status": "not_searched",
    "recommended_status": "NEEDS_MORE_PROOF",  # author never claims readiness
}

# --- severity ---------------------------------------------------------------

_SEVERITY_ALIASES = {
    "critical": "Critical",
    "crit": "Critical",
    "high": "High",
    "h": "High",
    "medium": "Medium",
    "med": "Medium",
    "m": "Medium",
    "low": "Low",
    "l": "Low",
    "informational": "Informational",
    "info": "Informational",
    "informative": "Informational",
    "qa": "Informational",
    "note": "Informational",
}


def normalize_severity(raw: str | None) -> str:
    """Map a free-text severity onto the schema enum. Unknown -> safe default.

    Preserves the *claimed* severity verbatim (after enum mapping). It never
    silently downgrades a stated severity to match impact — the gate does that.
    """
    if not raw:
        return SAFE_DEFAULTS["severity_claim"]
    key = raw.strip().lower()
    # take the first known token (handles "High (confirmed)", "Severity: High")
    for tok in re.split(r"[^a-z]+", key):
        if tok in _SEVERITY_ALIASES:
            return _SEVERITY_ALIASES[tok]
    return SAFE_DEFAULTS["severity_claim"]


# --- platform ---------------------------------------------------------------

_PLATFORM_ALIASES = {
    "immunefi": "Immunefi",
    "code4rena": "Code4rena",
    "c4": "Code4rena",
    "sherlock": "Sherlock",
    "cantina": "Cantina",
    "codehawks": "CodeHawks",
    "hackenproof": "HackenProof",
}


def normalize_platform(raw: str | None) -> str:
    """Map a platform name onto a canonical label, else pass through trimmed."""
    if not raw:
        return ""
    key = raw.strip().lower()
    for alias, canon in _PLATFORM_ALIASES.items():
        if alias in key:
            return canon
    return raw.strip()


# --- impact category --------------------------------------------------------

# ordered: the first matching family wins (more specific before generic)
_IMPACT_KEYWORDS = [
    ("governance_takeover", ["governance takeover", "governance attack", "take over governance",
                              "admin takeover", "ownership takeover", "seize control"]),
    ("fund_loss", ["theft", "steal", "stolen", "drain", "fund loss", "loss of funds",
                    "direct theft", "insolvency", "insolvent", "over-mint", "overmint",
                    "unbacked", "withdraw more", "double spend"]),
    ("reward_extraction", ["reward extraction", "unclaimed yield", "extra rewards",
                            "inflate rewards", "yield theft", "reward manipulation",
                            "claim more rewards"]),
    ("accounting_corruption", ["accounting", "incorrect accounting", "share inflation",
                                "exchange rate", "rounding", "balance corruption",
                                "incorrect shares", "miscount"]),
    ("fund_freeze", ["freeze", "frozen", "locked funds", "stuck funds", "cannot withdraw",
                      "permanently locked", "trapped"]),
    ("liveness_failure", ["liveness", "cannot progress", "stalls", "halts the protocol",
                           "protocol halt", "stuck state"]),
    ("dos", ["denial of service", "dos", "griefing", "out of gas", "gas limit",
              "revert forever", "block the function", "unbounded loop"]),
]


def normalize_impact_category(text: str | None) -> str:
    """Derive an impact_category enum from explicit impact text.

    Returns the safe default 'info' when no concrete impact keyword is present —
    this deliberately lets the impact/severity gate flag a high-severity claim
    that has no identifiable impact, rather than inventing one.
    """
    if not text:
        return SAFE_DEFAULTS["impact_category"]
    low = text.lower()
    for category, keywords in _IMPACT_KEYWORDS:
        if any(k in low for k in keywords):
            return category
    return SAFE_DEFAULTS["impact_category"]


# --- privilege --------------------------------------------------------------

_GOVERNANCE_KEYWORDS = ["governance", "timelock vote", "dao vote", "onlygovernance",
                        "governor", "proposal execution"]
_ADMIN_KEYWORDS = ["onlyowner", "only owner", "admin only", "onlyadmin", "only admin",
                   "owner-only", "owner only", "privileged role", "default_admin_role",
                   "onlyrole", "access-controlled admin", "trusted owner", "the owner can",
                   "owner can set", "as owner", "multisig"]
_PRIVILEGED_KEYWORDS = ["operator role", "keeper", "minter role", "pauser",
                        "only operator", "manager role", "whitelisted caller"]


def normalize_privilege(text: str | None) -> str:
    """Derive the privilege level required from explicit role language.

    Default 'none' (permissionless) unless the text clearly names a privileged
    role. This is a derivation from explicit evidence, not a guess: only role
    keywords promote the level.
    """
    if not text:
        return SAFE_DEFAULTS["privilege_required"]
    low = text.lower()
    if any(k in low for k in _GOVERNANCE_KEYWORDS):
        return "governance"
    if any(k in low for k in _ADMIN_KEYWORDS):
        return "admin"
    if any(k in low for k in _PRIVILEGED_KEYWORDS):
        return "privileged"
    return SAFE_DEFAULTS["privilege_required"]


# --- file / line references -------------------------------------------------

# matches Foo.sol:123, path/to/Foo.sol:123-145, Foo.sol#L123
_FILE_LINE_RE = re.compile(
    r"(?P<path>[\w./-]+\.(?:sol|vy|rs|cairo|move|fe))"
    r"(?:[:#]L?(?P<start>\d+)(?:[-–]L?(?P<end>\d+))?)?",
    re.IGNORECASE,
)


def normalize_file_line(ref: str) -> str:
    """Normalize a single 'file:line' reference to 'file:start' / 'file:start-end'.

    If no line number is present, returns just the file path (line evidence is
    left missing rather than invented)."""
    m = _FILE_LINE_RE.search(ref)
    if not m:
        return ref.strip()
    path = m.group("path")
    start = m.group("start")
    end = m.group("end")
    if start and end:
        return f"{path}:{start}-{end}"
    if start:
        return f"{path}:{start}"
    return path


def extract_file_line_refs(text: str | None) -> list[str]:
    """Return all explicit file[:line] references found in text (deduped, ordered)."""
    if not text:
        return []
    seen: list[str] = []
    for m in _FILE_LINE_RE.finditer(text):
        path = m.group("path")
        start = m.group("start")
        end = m.group("end")
        if start and end:
            ref = f"{path}:{start}-{end}"
        elif start:
            ref = f"{path}:{start}"
        else:
            ref = path
        if ref not in seen:
            seen.append(ref)
    return seen


# --- address / hash tagging (tag, never invent) -----------------------------

_ADDRESS_RE = re.compile(r"\b0x[a-fA-F0-9]{40}\b")
_TXHASH_RE = re.compile(r"\b0x[a-fA-F0-9]{64}\b")


def tag_addresses_and_hashes(text: str | None) -> dict:
    """Report addresses / tx hashes that explicitly appear in the input.

    This only surfaces what is literally present so a human can sanity-check it;
    it never fabricates an address or a transaction hash.
    """
    if not text:
        return {"addresses": [], "tx_hashes": []}
    hashes = sorted(set(_TXHASH_RE.findall(text)))
    # exclude 64-hex (tx hashes) from the 40-hex address scan
    addresses = sorted({a for a in _ADDRESS_RE.findall(text)})
    return {"addresses": addresses, "tx_hashes": hashes}


# --- misc -------------------------------------------------------------------

def slugify(text: str, max_len: int = 48) -> str:
    """Deterministic kebab-case slug for finding ids. Always returns non-empty."""
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    s = s[:max_len].strip("-")
    return s or "finding"
