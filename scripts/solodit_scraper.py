#!/usr/bin/env python3
"""
solodit_scraper.py — Solodit knowledge base builder with continuous learning

Modes:
    python scripts/solodit_scraper.py                        # full initial scrape
    python scripts/solodit_scraper.py --limit 100            # quick test
    python scripts/solodit_scraper.py --show-tags            # verify tag counts
    python scripts/solodit_scraper.py --refresh              # wipe DB and rebuild
    python scripts/solodit_scraper.py --learn                # update agent files + triager from existing DB
    python scripts/solodit_scraper.py --continuous           # run forever, update agents + triager
    python scripts/solodit_scraper.py --continuous --interval 60  # cycle every 60 min

--learn behaviour:
    1. Runs semantic search per vulnerability type across the full Chroma DB
    2. For each specialist agent (reentrancy.md, oracle.md, etc.) — synthesises new
       attack patterns and injects them as "## Auto-learned patterns" at the bottom
    3. For the triager (prompts/triager.md) — reads data/triage/*.jsonl decision history,
       cross-references with Solodit false-positive-flavoured findings, synthesises
       rejection/acceptance calibration rules, and injects them as
       "## Auto-learned triage patterns" at the bottom of the triager prompt
    Each synthesis cycle is persisted to kb/patterns/<vuln_type>.json and
    kb/patterns/triager.json respectively (last 20 cycles kept).

Environment variables:
    SOLODIT_API_KEY    required — your Cyfrin API key
    ANTHROPIC_API_KEY  optional — enables Claude-powered pattern synthesis in agent files
"""

import argparse
import json
import os
import re
import time
import signal
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

# Load .env into os.environ so anthropic.Anthropic() picks up ANTHROPIC_API_KEY
if Path(".env").exists():
    for _line in Path(".env").read_text().splitlines():
        if "=" in _line and not _line.startswith("#"):
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip("\"'"))

import chromadb
import requests
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────

API_ENDPOINT  = "https://solodit.cyfrin.io/api/v1/solodit/findings"
KB_DIR        = Path("kb")
PATTERNS_DIR  = KB_DIR / "patterns"
AGENTS_DIR    = Path("agents")
STATE_FILE    = KB_DIR / "scraper_state.json"
REQUEST_DELAY = 4.0        # seconds between API calls (stay under 20 req/60s)
LEARN_MARKER  = "## Auto-learned patterns"  # section injected into agent files

TRIAGER_PROMPT_PATH  = Path("prompts/triager.md")
TRIAGE_LEARN_MARKER  = "## Auto-learned triage patterns"
TRIAGE_PATTERNS_FILE = PATTERNS_DIR / "triager.json"

KB_DIR.mkdir(exist_ok=True)
PATTERNS_DIR.mkdir(exist_ok=True)

# Lazy audit-aware triage dir — gracefully falls back if no audit is active
# (allows `solodit_scraper.py --continuous` to run standalone before migration)
import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))

def _triage_data_dir() -> Path:
    try:
        from audit_context import audit_path
        return audit_path("data/triage")
    except (ImportError, RuntimeError):
        return Path("data/triage")

# ─────────────────────────────────────────────────────────────────────────────
# Tag taxonomy — corrected from official Solodit filter options reference
# ─────────────────────────────────────────────────────────────────────────────

TAG_TO_VULN_TYPE = {
    # reentrancy
    "Reentrancy":             "reentrancy",
    "Read-only Reentrancy":   "reentrancy",
    "ERC777":                 "reentrancy",
    "Withdraw Pattern":       "reentrancy",

    # access-control
    "Access Control":         "access-control",
    "Admin":                  "access-control",
    "Ownership":              "access-control",
    "Initialization":         "access-control",
    "Upgradable":             "proxy-upgrade",

    # arithmetic
    "Overflow/Underflow":     "arithmetic",
    "Wrong Math":             "arithmetic",
    "Precision Loss":         "arithmetic",
    "Rounding":               "arithmetic",
    "Type casting":           "arithmetic",
    "Decimals":               "arithmetic",

    # oracle-manipulation
    "Oracle":                 "oracle-manipulation",
    "Stale Price":            "oracle-manipulation",
    "TWAP":                   "oracle-manipulation",
    "Chainlink":              "oracle-manipulation",

    # flash-loan / mev
    "Flash Loan":             "flash-loan",
    "Sandwich Attack":        "flash-loan",
    "Front-Running":          "front-running",

    # logic-error
    "Business Logic":         "logic-error",
    "Missing-Logic":          "logic-error",
    "Validation":             "logic-error",
    "Liquidation":            "logic-error",
    "ERC4626":                "logic-error",
    "First Depositor Issue":  "logic-error",
    "Share Inflation":        "logic-error",
    "EIP-4626":               "logic-error",

    # dos
    "DOS":                    "dos",
    "Denial-Of-Service":      "dos",
    "Gas Limit":              "dos",
    "Broken Loop":            "dos",
    "Fund Lock":              "dos",
    "Grief Attack":           "dos",
    "Revert By Sending Dust": "dos",

    # snapshot / governance
    "Vote":                   "snapshot",
    "Delegate":               "snapshot",

    # signature-replay
    "Replay Attack":          "signature-replay",
    "EIP-712":                "signature-replay",

    # storage / proxy
    "storage-collision":      "storage-collision",
}

# Priority order for scraping — most valuable first
VULN_TYPE_TAGS = defaultdict(list)
for tag, vt in TAG_TO_VULN_TYPE.items():
    VULN_TYPE_TAGS[vt].append(tag)

IMPACT_MAP     = {"HIGH": "High", "MEDIUM": "Medium", "LOW": "Low", "GAS": "Informational"}
TARGET_IMPACTS = ["HIGH", "MEDIUM", "LOW", "GAS"]
TARGET_LANGUAGES = [
    "Solidity", "Rust", "Go", "Move", "TypeScript", "Vyper", "FunC",
    "JavaScript", "Cairo", "Dart", "Python", "Circom", "Cosmos", "Sway",
    "Yul", "Noir", "Tact",
]

# Which agent file each vuln_type maps to
VULN_TYPE_TO_AGENT = {
    "reentrancy":          "reentrancy.md",
    "access-control":      "access_control.md",
    "arithmetic":          "arithmetic.md",
    "oracle-manipulation": "oracle.md",
    "flash-loan":          "flash_loan.md",
    "front-running":       "flash_loan.md",
    "logic-error":         "logic.md",
    "dos":                 "dos.md",
    "snapshot":            "snapshot.md",
    "signature-replay":    "access_control.md",
    "proxy-upgrade":       "access_control.md",
    "storage-collision":   "logic.md",
}

# Semantic search queries used by --learn to pull relevant findings from the full DB
VULN_TYPE_SEARCH_QUERIES = {
    "reentrancy":
        "reentrancy CEI violation external call before state update re-entrancy callback reentrancy guard",
    "access-control":
        "access control missing modifier onlyOwner privilege escalation unauthorized caller role permission",
    "arithmetic":
        "integer overflow underflow precision loss rounding error wrong math division truncation decimals casting",
    "oracle-manipulation":
        "oracle price manipulation stale price TWAP chainlink price feed spot price manipulation",
    "flash-loan":
        "flash loan attack sandwich attack price manipulation within single transaction borrow repay",
    "front-running":
        "front running MEV miner extractable value transaction ordering mempool sandwich",
    "logic-error":
        "business logic error incorrect validation missing check wrong calculation invariant violation",
    "dos":
        "denial of service gas limit griefing fund lock unbounded loop failed transfer stuck funds",
    "snapshot":
        "governance vote manipulation snapshot token delegation flash loan governance attack",
    "signature-replay":
        "signature replay attack EIP-712 missing nonce domain separator reused signature",
    "proxy-upgrade":
        "proxy upgrade storage collision uninitialized implementation delegatecall slot clash",
    "storage-collision":
        "storage slot collision proxy pattern variable shadowing storage layout corruption",
}

# ─────────────────────────────────────────────────────────────────────────────
# API helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_api_key() -> str:
    key = os.environ.get("SOLODIT_API_KEY", "")
    if not key:
        for line in Path(".env").read_text().splitlines() if Path(".env").exists() else []:
            if line.startswith("SOLODIT_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"\'')
    if not key:
        raise SystemExit(
            "\nSOLODIT_API_KEY not set.\n"
            "  export SOLODIT_API_KEY=sk_your_key\n"
            "  or:  echo 'SOLODIT_API_KEY=sk_your_key' > .env"
        )
    return key


def post_findings(payload: dict, api_key: str, session: requests.Session) -> dict | None:
    headers = {"Content-Type": "application/json", "X-Cyfrin-API-Key": api_key}
    while True:
        try:
            resp = session.post(API_ENDPOINT, headers=headers, json=payload, timeout=20)
            if resp.status_code == 429:
                wait = max(int(resp.headers.get("X-RateLimit-Reset", time.time() + 65)) - time.time() + 2, 10)
                print(f"  Rate limited — sleeping {wait:.0f}s")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"  API error: {e}")
            return None


def fetch_pages(filters: dict, api_key: str, session: requests.Session,
                page_size: int = 100, max_results: int = None,
                label: str = "") -> list[dict]:
    results, page, total_pages = [], 1, "?"
    while True:
        data = post_findings({"page": page, "pageSize": page_size, "filters": filters}, api_key, session)
        if not data:
            break
        batch = data.get("findings", [])
        if not batch:
            break
        results.extend(batch)
        meta        = data.get("metadata", {})
        remaining   = data.get("rateLimit", {}).get("remaining", 20)
        total_pages = meta.get("totalPages", total_pages)
        total_res   = meta.get("totalResults", "?")
        print(f"    page {page}/{total_pages}  ({len(results)}/{total_res})  rate-limit remaining: {remaining}", end="\r")
        if max_results and len(results) >= max_results:
            results = results[:max_results]
            break
        if page >= meta.get("totalPages", 1):
            break
        page += 1
        time.sleep(REQUEST_DELAY if remaining > 5 else 9.0)
    print()  # newline after \r progress
    return results

# ─────────────────────────────────────────────────────────────────────────────
# Parsing
# ─────────────────────────────────────────────────────────────────────────────

def extract_code(md: str) -> str:
    m = re.search(r'```(?:solidity|sol|js|vyper)?\s*\n(.*?)```', md or "", re.DOTALL)
    return m.group(1).strip()[:2000] if m else ""

def extract_fix(md: str) -> str:
    for h in ["## Recommendation", "## Fix", "## Mitigation", "## Remediation", "## Suggested Fix"]:
        idx = (md or "").find(h)
        if idx != -1:
            section = md[idx + len(h):].strip()
            cut = re.search(r'\n##', section)
            return (section[:cut.start()] if cut else section)[:800]
    return ""

def extract_vuln_type(finding: dict) -> str:
    for t in finding.get("issues_issuetagscore", []):
        tag = t.get("tags_tag", {}).get("title", "")
        if tag in TAG_TO_VULN_TYPE:
            return TAG_TO_VULN_TYPE[tag]
    title = finding.get("title", "").lower()
    for kw, vt in [("reentranc","reentrancy"),("overflow","arithmetic"),("oracle","oracle-manipulation"),
                   ("flash loan","flash-loan"),("access control","access-control"),("front-run","front-running"),
                   ("dos","dos"),("vote","snapshot"),("logic","logic-error")]:
        if kw in title:
            return vt
    return "other"

def normalise(raw: dict, vuln_type: str = None) -> dict:
    content = raw.get("content", "")
    return {
        "id":            f"solodit-{raw['id']}",
        "title":         raw.get("title", "Untitled")[:200],
        "severity":      IMPACT_MAP.get(raw.get("impact"), "Low"),
        "vuln_type":     vuln_type or extract_vuln_type(raw),
        "description":   (raw.get("summary") or content)[:1500],
        "code_snippet":  extract_code(content),
        "fix":           extract_fix(content),
        "protocol":      (raw.get("protocol_name") or raw.get("sponsor_name") or "unknown")[:100],
        "audit_firm":    (raw.get("firm_name") or "unknown")[:80],
        "quality_score": raw.get("quality_score", 0),
        "year":          (raw.get("report_date") or "")[:4] or str(datetime.now().year),
        "url":           (raw.get("source_link") or raw.get("github_link") or "")[:300],
        "tags":          [t.get("tags_tag", {}).get("title", "") for t in raw.get("issues_issuetagscore", [])],
    }

# ─────────────────────────────────────────────────────────────────────────────
# Chroma
# ─────────────────────────────────────────────────────────────────────────────

def init_chroma(refresh: bool = False) -> chromadb.Collection:
    client = chromadb.PersistentClient(path=str(KB_DIR / "chroma"))
    if refresh:
        try:
            client.delete_collection("solodit_findings")
            print("Cleared existing collection.")
        except Exception:
            pass
        # Clear batch checkpoints so the full scrape runs from scratch
        if STATE_FILE.exists():
            state = json.loads(STATE_FILE.read_text())
            state["completed_batches"] = []
            STATE_FILE.write_text(json.dumps(state, indent=2))
    return client.get_or_create_collection("solodit_findings", metadata={"hnsw:space": "cosine"})

def get_existing_ids(collection: chromadb.Collection) -> set[str]:
    try:
        result = collection.get(include=[])
        return set(result["ids"])
    except Exception:
        return set()

def index_findings(findings: list[dict], model: SentenceTransformer,
                   collection: chromadb.Collection, batch_size: int = 64) -> int:
    if not findings:
        return 0
    indexed = 0
    for i in range(0, len(findings), batch_size):
        batch = findings[i:i + batch_size]
        texts = [f"{f['title']} {f['description']} {f['code_snippet']}"[:4000] for f in batch]
        embeddings = model.encode(texts, show_progress_bar=False).tolist()
        collection.upsert(
            ids=[f["id"] for f in batch],
            embeddings=embeddings,
            metadatas=[{
                "title":         f["title"],
                "severity":      f["severity"],
                "vuln_type":     f["vuln_type"],
                "protocol":      f["protocol"],
                "audit_firm":    f["audit_firm"],
                "quality_score": str(f["quality_score"]),
                "year":          f["year"],
                "url":           f["url"],
                "tags":          ", ".join(f["tags"]),
            } for f in batch],
            documents=[json.dumps({k: f[k] for k in
                ("title","description","code_snippet","fix","severity","vuln_type")
            }) for f in batch],
        )
        indexed += len(batch)
    return indexed

# ─────────────────────────────────────────────────────────────────────────────
# Agent learning — updates agent .md files with patterns from new findings
# ─────────────────────────────────────────────────────────────────────────────

def synthesize_patterns_with_claude(findings: list[dict], vuln_type: str) -> str:
    """Use Claude Haiku to synthesize patterns from new findings. Requires ANTHROPIC_API_KEY."""
    try:
        import anthropic
        client = anthropic.Anthropic()
        by_quality = sorted(findings, key=lambda x: -x.get("quality_score", 0))
        # Top 20 by quality + 20 sampled evenly from the rest for diversity
        top        = by_quality[:20]
        rest       = by_quality[20:]
        step       = max(1, len(rest) // 20)
        diverse    = rest[::step][:20]
        sample     = {f["title"]: f for f in top + diverse}.values()  # dedupe by title
        samples = "\n\n".join(
            f"[{f['severity']}] {f['title']}\n"
            f"Protocol: {f['protocol']} | Firm: {f['audit_firm']}\n"
            f"Description: {f['description'][:400]}\n"
            f"Code: {f['code_snippet'][:300]}"
            for f in sample
        )
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=800,
            messages=[{"role": "user", "content":
                f"You are updating a smart contract auditing agent specialising in {vuln_type}.\n\n"
                f"Here are {len(findings)} new findings sourced from real audits:\n\n{samples}\n\n"
                "Extract and summarise:\n"
                "1. New attack patterns or variants seen in these findings\n"
                "2. Specific protocols, standards, or contract types frequently affected\n"
                "3. Code patterns that reliably indicate this vulnerability\n"
                "4. Any edge cases or bypass techniques the agent should watch for\n\n"
                "Write as concise bullet points for an experienced auditor. 150 words max. "
                "No preamble, just the bullets."
            }]
        )
        return resp.content[0].text.strip()
    except ImportError:
        return _heuristic_patterns(findings, vuln_type)
    except Exception as e:
        print(f"  Claude synthesis failed ({e}), falling back to heuristic extraction.")
        return _heuristic_patterns(findings, vuln_type)


def _heuristic_patterns(findings: list[dict], vuln_type: str) -> str:
    """Fallback: extract patterns by frequency analysis when no Anthropic key is set."""
    protocols  = Counter(f["protocol"] for f in findings if f["protocol"] != "unknown")
    firms      = Counter(f["audit_firm"] for f in findings)
    # Extract keyword phrases from titles
    words = Counter()
    for f in findings:
        for w in re.findall(r'\b[A-Za-z][\w-]{3,}\b', f["title"].lower()):
            if w not in {"this","that","with","from","when","have","been","will","can","the"}:
                words[w] += 1

    top_protocols = ", ".join(f"{p} ({n})" for p, n in protocols.most_common(5))
    top_firms     = ", ".join(f"{f} ({n})" for f, n in firms.most_common(3))
    top_words     = ", ".join(w for w, _ in words.most_common(10))

    return (
        f"- Most affected protocols: {top_protocols or 'varied'}\n"
        f"- Most active auditing firms for this category: {top_firms or 'varied'}\n"
        f"- Common title keywords: {top_words or 'varied'}\n"
        f"- Total findings in knowledge base for this type: {len(findings)}\n"
        f"- Set ANTHROPIC_API_KEY for richer Claude-powered pattern synthesis."
    )


def update_agent_file(vuln_type: str, new_findings: list[dict], all_findings: list[dict]):
    """Inject a live-learned patterns section into the relevant agent .md file."""
    agent_filename = VULN_TYPE_TO_AGENT.get(vuln_type)
    if not agent_filename:
        return
    agent_file = AGENTS_DIR / agent_filename
    if not agent_file.exists():
        return

    patterns_file = PATTERNS_DIR / f"{vuln_type}.json"
    history = json.loads(patterns_file.read_text()) if patterns_file.exists() else {"cycles": []}

    # Synthesise patterns from new findings
    synthesis = synthesize_patterns_with_claude(new_findings, vuln_type) if new_findings else ""

    # Persist to history
    history["cycles"].append({
        "timestamp":     datetime.now(timezone.utc).isoformat(),
        "new_findings":  len(new_findings),
        "total_in_db":   len(all_findings),
        "synthesis":     synthesis,
    })
    # Keep last 20 cycles
    history["cycles"] = history["cycles"][-20:]
    patterns_file.write_text(json.dumps(history, indent=2))

    # Build the injected section from the last 3 cycles
    recent = [c for c in reversed(history["cycles"]) if c.get("synthesis")][:3]
    if not recent:
        return

    section_lines = [
        "",
        "---",
        "",
        LEARN_MARKER,
        f"> Auto-updated from Solodit · {datetime.now().strftime('%Y-%m-%d %H:%M')} "
        f"· {len(all_findings)} total findings in KB",
        "",
    ]
    for i, cycle in enumerate(recent):
        ts = cycle["timestamp"][:10]
        n  = cycle["new_findings"]
        section_lines.append(f"### Cycle {ts} (+{n} new findings)")
        section_lines.append("")
        section_lines.append(cycle["synthesis"])
        section_lines.append("")
    section = "\n".join(section_lines)

    # Replace existing auto-learned section or append
    content = agent_file.read_text()
    if LEARN_MARKER in content:
        cut = content.index(LEARN_MARKER)
        # Go back two lines (the --- and blank line before the marker)
        pre = content[:cut].rstrip()
        if pre.endswith("---"):
            pre = pre[:-3].rstrip()
        content = pre + section
    else:
        content = content.rstrip() + "\n" + section

    agent_file.write_text(content)
    print(f"  ✓ Updated {agent_file.name} with learned patterns")


def run_agent_learning(new_by_type: dict[str, list[dict]], all_by_type: dict[str, list[dict]]):
    """Update all agent files that received new findings this cycle."""
    if not new_by_type:
        return
    print("\nUpdating agent files with learned patterns...")
    for vuln_type, new_findings in new_by_type.items():
        if new_findings:
            update_agent_file(vuln_type, new_findings, all_by_type.get(vuln_type, new_findings))


# ─────────────────────────────────────────────────────────────────────────────
# Triager learning — updates prompts/triager.md with learned rejection/acceptance patterns
# ─────────────────────────────────────────────────────────────────────────────

def load_triage_decisions() -> dict[str, list[dict]]:
    """Load all triage decision buckets from data/triage/*.jsonl."""
    buckets: dict[str, list[dict]] = {}
    for bucket in ["submit", "poc_required", "downgraded", "merged", "rejected"]:
        path = _triage_data_dir() / f"{bucket}.jsonl"
        if not path.exists():
            buckets[bucket] = []
            continue
        items = []
        for line in path.read_text().splitlines():
            line = line.strip()
            if line:
                try:
                    items.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        buckets[bucket] = items
    return buckets


def synthesize_triage_patterns_with_claude(
    buckets: dict[str, list[dict]],
    solodit_false_positives: list[dict],
) -> str:
    """Use Claude Haiku to synthesize triage decision patterns for the triager prompt."""
    try:
        import anthropic
        client = anthropic.Anthropic()

        accepted   = buckets.get("submit", []) + buckets.get("poc_required", [])
        rejected   = buckets.get("rejected", [])
        downgraded = buckets.get("downgraded", [])

        def fmt_decisions(items: list[dict], label: str, limit: int = 8) -> str:
            if not items:
                return f"{label}: none\n"
            lines = [f"{label} ({len(items)} total, showing {min(len(items), limit)}):"]
            for t in items[:limit]:
                fid    = t.get("finding_id", "?")
                sev    = t.get("recommended_severity", "?")
                score  = t.get("score", {}).get("total", "?")
                reason = t.get("decision_reason", "")[:120]
                lines.append(f"  {fid} [{sev}] score={score}: {reason}")
            return "\n".join(lines)

        def fmt_fp_patterns(findings: list[dict], limit: int = 10) -> str:
            if not findings:
                return "No Solodit false-positive patterns available.\n"
            lines = [f"Common false-positive-flavoured findings from Solodit ({len(findings)} sampled):"]
            for f in findings[:limit]:
                lines.append(f"  [{f.get('severity','?')}] {f.get('title','')[:80]}")
                lines.append(f"    {f.get('description','')[:200]}")
            return "\n".join(lines)

        context = "\n\n".join([
            fmt_decisions(accepted,   "ACCEPTED (submit/poc_required)"),
            fmt_decisions(rejected,   "REJECTED"),
            fmt_decisions(downgraded, "DOWNGRADED"),
            fmt_fp_patterns(solodit_false_positives),
        ])

        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=800,
            messages=[{"role": "user", "content":
                "You are calibrating a smart contract audit triage agent.\n\n"
                "Below are triage decisions from recent audit runs and Solodit false-positive patterns:\n\n"
                f"{context}\n\n"
                "Extract:\n"
                "1. Patterns that reliably indicate REJECTION "
                "(specific attacker types, language, preconditions seen in past rejects)\n"
                "2. Patterns that reliably indicate ACCEPTANCE "
                "(what makes findings score ≥28 in practice)\n"
                "3. Common severity inflation patterns to correct\n"
                "4. Recurring false-positive signatures (words, claim types, attacker roles)\n\n"
                "Write as concise bullet points for an experienced auditor/triager. "
                "150 words max. No preamble."
            }]
        )
        return resp.content[0].text.strip()
    except ImportError:
        return _heuristic_triage_patterns(buckets)
    except Exception as e:
        print(f"  Claude triage synthesis failed ({e}), falling back to heuristic.")
        return _heuristic_triage_patterns(buckets)


def _heuristic_triage_patterns(buckets: dict[str, list[dict]]) -> str:
    accepted   = buckets.get("submit", []) + buckets.get("poc_required", [])
    rejected   = buckets.get("rejected", [])
    downgraded = buckets.get("downgraded", [])
    lines = []

    if rejected:
        reject_attackers = Counter(
            t.get("attacker_model", {}).get("attacker_type", "unknown")
            for t in rejected
        )
        lines.append(
            f"- Most-rejected attacker types: "
            f"{', '.join(f'{a} ({n})' for a, n in reject_attackers.most_common(3))}"
        )

    if downgraded:
        down_sevs = Counter(t.get("recommended_severity", "?") for t in downgraded)
        lines.append(
            f"- Common downgrade targets: "
            f"{', '.join(f'{s} ({n})' for s, n in down_sevs.most_common(3))}"
        )

    if accepted:
        accept_sevs = Counter(t.get("recommended_severity", "?") for t in accepted)
        avg_score   = sum(t.get("score", {}).get("total", 0) for t in accepted) / len(accepted)
        lines.append(
            f"- Accepted severity distribution: "
            f"{', '.join(f'{s} ({n})' for s, n in accept_sevs.most_common())}"
        )
        lines.append(f"- Average accepted score: {avg_score:.1f}/35")

    if not lines:
        lines.append("- No triage history yet — run a full audit + triage_findings.py first.")
        lines.append("- Set ANTHROPIC_API_KEY for richer Claude-powered pattern synthesis.")

    return "\n".join(lines)


def update_triager_prompt(by_type: dict[str, list[dict]]):
    """
    Inject a live-learned patterns section into prompts/triager.md.

    Draws from two sources:
    1. Past triage decisions in data/triage/*.jsonl (actual accept/reject history)
    2. False-positive-flavoured findings from the Solodit KB (admin, future, speculative)
    """
    if not TRIAGER_PROMPT_PATH.exists():
        print(f"  [skip] {TRIAGER_PROMPT_PATH} not found — skipping triager learning")
        return

    buckets        = load_triage_decisions()
    total_decisions = sum(len(v) for v in buckets.values())

    # Pull false-positive-flavoured Solodit findings as negative examples
    FP_KEYWORDS = ["admin", "trusted", "future", "consider", "could potentially",
                   "owner", "governance", "timelocked", "migration"]
    solodit_fp: list[dict] = []
    seen_titles: set[str]  = set()
    for findings in by_type.values():
        for f in findings:
            desc = (f.get("description", "") + " " + f.get("title", "")).lower()
            if any(kw in desc for kw in FP_KEYWORDS):
                title = f.get("title", "")
                if title not in seen_titles:
                    seen_titles.add(title)
                    solodit_fp.append(f)
        if len(solodit_fp) >= 20:
            break

    synthesis = synthesize_triage_patterns_with_claude(buckets, solodit_fp[:20])

    # Persist to history
    history = (json.loads(TRIAGE_PATTERNS_FILE.read_text())
               if TRIAGE_PATTERNS_FILE.exists() else {"cycles": []})
    history["cycles"].append({
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "total_decisions": total_decisions,
        "by_bucket":       {k: len(v) for k, v in buckets.items()},
        "synthesis":       synthesis,
    })
    history["cycles"] = history["cycles"][-20:]
    TRIAGE_PATTERNS_FILE.write_text(json.dumps(history, indent=2))

    # Build injected section from last 3 cycles
    recent = [c for c in reversed(history["cycles"]) if c.get("synthesis")][:3]
    if not recent:
        return

    section_lines = [
        "",
        "---",
        "",
        TRIAGE_LEARN_MARKER,
        f"> Auto-updated from Solodit KB + triage history · "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M')} · "
        f"{total_decisions} past decisions",
        "",
    ]
    for cycle in recent:
        ts          = cycle["timestamp"][:10]
        n           = cycle["total_decisions"]
        buckets_str = ", ".join(
            f"{k}:{v}" for k, v in cycle.get("by_bucket", {}).items() if v > 0
        )
        section_lines.append(f"### Cycle {ts} ({n} decisions — {buckets_str})")
        section_lines.append("")
        section_lines.append(cycle["synthesis"])
        section_lines.append("")
    section = "\n".join(section_lines)

    # Replace existing auto-learned section or append
    content = TRIAGER_PROMPT_PATH.read_text()
    if TRIAGE_LEARN_MARKER in content:
        cut = content.index(TRIAGE_LEARN_MARKER)
        pre = content[:cut].rstrip()
        if pre.endswith("---"):
            pre = pre[:-3].rstrip()
        content = pre + section
    else:
        content = content.rstrip() + "\n" + section

    TRIAGER_PROMPT_PATH.write_text(content)
    print(f"  ✓ Updated {TRIAGER_PROMPT_PATH} with learned triage patterns")

# ─────────────────────────────────────────────────────────────────────────────
# State persistence
# ─────────────────────────────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        s = json.loads(STATE_FILE.read_text())
        s.setdefault("completed_batches", [])
        return s
    return {"last_run": None, "total_indexed": 0, "cycles": 0, "completed_batches": []}

def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))

# ─────────────────────────────────────────────────────────────────────────────
# Core scrape cycle
# ─────────────────────────────────────────────────────────────────────────────

def run_cycle(api_key: str, session: requests.Session, model: SentenceTransformer,
              collection: chromadb.Collection, incremental: bool = False,
              limit: int = None, full_mode: bool = False) -> tuple[int, dict]:
    """
    Run one scrape cycle. Returns (n_new_findings, new_by_type).

    full_mode=True : fetch all findings by impact (no tag filter) — gets everything.
    full_mode=False: fetch findings matching the tag taxonomy only.
    incremental=True: restrict to last 30 days (continuous mode).
    Checkpoints each batch so Ctrl+C + re-run skips already-finished batches.
    """
    state = load_state()
    done_batches = set(state.get("completed_batches", []))

    existing_ids = get_existing_ids(collection)
    all_new: list[dict] = []
    new_by_type: dict[str, list[dict]] = defaultdict(list)

    if incremental:
        date_filter = {"reported": {"value": "30"}}
    else:
        date_filter = {}

    if full_mode:
        # ── Full scrape: iterate by impact only, no tag filter ──────────────
        # Covers all ~49k findings, not just those with recognised tags.
        for impact in TARGET_IMPACTS:
            if limit and len(all_new) >= limit:
                break

            batch_key = f"full:{impact}"
            if batch_key in done_batches:
                n_done = sum(1 for b in done_batches if b.startswith("full:"))
                print(f"  [full] {impact}: already done, skipping")
                continue

            print(f"  [full] {impact}: fetching all pages...")
            raw = fetch_pages(
                filters={
                    "impact":        [impact],
                    "sortField":     "Recency" if incremental else "Quality",
                    "sortDirection": "Desc",
                    "languages":     [{"value": lang} for lang in TARGET_LANGUAGES],
                    **date_filter,
                },
                api_key=api_key,
                session=session,
                max_results=limit,
            )

            new_for_batch = []
            for r in raw:
                fid = f"solodit-{r['id']}"
                if fid not in existing_ids:
                    f = normalise(r)  # vuln_type auto-detected from tags/title
                    new_for_batch.append(f)
                    all_new.append(f)
                    existing_ids.add(fid)
                    new_by_type[f["vuln_type"]].append(f)

            print(f"  [full] {impact}: +{len(new_for_batch)} new  (fetched {len(raw)} total)")

            done_batches.add(batch_key)
            state["completed_batches"] = list(done_batches)
            save_state(state)

    else:
        # ── Tag-filtered scrape: only findings matching the tag taxonomy ─────
        vuln_types_ordered = [
            "reentrancy", "logic-error", "oracle-manipulation", "access-control",
            "arithmetic", "flash-loan", "dos", "snapshot", "front-running",
            "signature-replay", "proxy-upgrade",
        ]

        for vuln_type in vuln_types_ordered:
            if limit and len(all_new) >= limit:
                break

            tags = VULN_TYPE_TAGS[vuln_type]
            if not tags:
                continue

            per_type_limit = min((limit - len(all_new)) if limit else 300, 300)
            label = f"[{vuln_type}]"

            for impact in TARGET_IMPACTS:
                if limit and len(all_new) >= limit:
                    break

                batch_key = f"{vuln_type}:{impact}"
                if batch_key in done_batches:
                    print(f"  {label} {impact}: already done, skipping")
                    continue

                raw = fetch_pages(
                    filters={
                        "tags":          [{"value": t} for t in tags],
                        "impact":        [impact],
                        "sortField":     "Recency" if incremental else "Quality",
                        "sortDirection": "Desc",
                        "qualityScore":  2,
                        "languages":     [{"value": lang} for lang in TARGET_LANGUAGES],
                        **date_filter,
                    },
                    api_key=api_key,
                    session=session,
                    max_results=per_type_limit // 2,
                )

                new_for_batch = []
                for r in raw:
                    fid = f"solodit-{r['id']}"
                    if fid not in existing_ids:
                        f = normalise(r, vuln_type=vuln_type)
                        new_for_batch.append(f)
                        all_new.append(f)
                        existing_ids.add(fid)
                        new_by_type[vuln_type].append(f)

                if new_for_batch:
                    print(f"  {label} {impact}: +{len(new_for_batch)} new")

                done_batches.add(batch_key)
                state["completed_batches"] = list(done_batches)
                save_state(state)

    # Index all new findings
    if all_new:
        print(f"\nIndexing {len(all_new)} new findings...")
        for i in tqdm(range(0, len(all_new), 64), desc="Embedding"):
            index_findings(all_new[i:i+64], model, collection)

    return len(all_new), dict(new_by_type)


def get_all_by_type(collection: chromadb.Collection) -> dict[str, list[dict]]:
    """Pull all findings from Chroma grouped by vuln_type, in batches to avoid memory issues."""
    by_type: dict[str, list] = defaultdict(list)
    n          = collection.count()
    batch_size = 500
    for offset in range(0, n, batch_size):
        try:
            result = collection.get(
                include=["metadatas", "documents"],
                limit=batch_size,
                offset=offset,
            )
            for meta, doc in zip(result["metadatas"], result["documents"]):
                try:
                    f = json.loads(doc)
                    f["protocol"]      = meta.get("protocol", "")
                    f["audit_firm"]    = meta.get("audit_firm", "")
                    f["quality_score"] = float(meta.get("quality_score", 0))
                    by_type[meta.get("vuln_type", "other")].append(f)
                except Exception:
                    pass
        except Exception as e:
            print(f"  Warning: error loading batch at offset {offset}: {e}")
    return dict(by_type)


def get_findings_for_vuln_type(collection: chromadb.Collection,
                                vuln_type: str, limit: int = 200) -> list[dict]:
    """Fetch up to `limit` findings for a specific vuln_type using metadata filtering."""
    try:
        result = collection.get(
            where={"vuln_type": {"$eq": vuln_type}},
            include=["metadatas", "documents"],
            limit=limit,
        )
        findings = []
        for meta, doc in zip(result["metadatas"], result["documents"]):
            try:
                f = json.loads(doc)
                f["protocol"]      = meta.get("protocol", "")
                f["audit_firm"]    = meta.get("audit_firm", "")
                f["quality_score"] = float(meta.get("quality_score", 0))
                findings.append(f)
            except Exception:
                pass
        return findings
    except Exception as e:
        print(f"  Warning: could not load findings for {vuln_type}: {e}")
        return []

# ─────────────────────────────────────────────────────────────────────────────
# Commands
# ─────────────────────────────────────────────────────────────────────────────

def cmd_show_tags(api_key: str, session: requests.Session):
    print("Finding counts per tag (all impacts, all languages):\n")
    tags_seen = set()
    for vt, tags in VULN_TYPE_TAGS.items():
        for tag in tags:
            if tag in tags_seen:
                continue
            tags_seen.add(tag)
            data = post_findings({
                "page": 1, "pageSize": 1,
                "filters": {"tags": [{"value": tag}], "impact": TARGET_IMPACTS,
                            "languages": [{"value": lang} for lang in TARGET_LANGUAGES]}
            }, api_key, session)
            n = data.get("metadata", {}).get("totalResults", "?") if data else "error"
            print(f"  {tag:40s}  {n:>6}  → {vt}")
            time.sleep(REQUEST_DELAY)


def cmd_scrape(api_key: str, limit: int, refresh: bool, full: bool = False):
    """Initial scrape — tag-filtered by default, or --full to grab everything."""
    session = requests.Session()
    print("Loading embedding model...")
    model      = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    collection = init_chroma(refresh=refresh)
    print(f"Existing findings: {collection.count()}")
    if full:
        print("Mode: FULL (all findings, no tag filter — ~49k findings, ~30-40 min)\n")
    else:
        print("Mode: tag-filtered (use --full to scrape everything)\n")

    state = load_state()
    n_new, new_by_type = run_cycle(
        api_key, session, model, collection,
        incremental=False, limit=limit, full_mode=full,
    )

    print(f"\n{'─'*50}")
    print(f"Scrape complete. {n_new} new findings indexed. Total: {collection.count()}")

    if n_new > 0:
        all_by_type = get_all_by_type(collection)
        run_agent_learning(new_by_type, all_by_type)
        update_triager_prompt(all_by_type)

    state["last_run"]           = datetime.now(timezone.utc).isoformat()
    state["total_indexed"]      = collection.count()
    state["cycles"]             = state.get("cycles", 0) + 1
    state["completed_batches"]  = []  # reset so next run starts fresh
    save_state(state)

    print("\nRun agent learning on the full DB:")
    print("  python scripts/solodit_scraper.py --learn")
    print("\nNext steps:")
    print("  python tools/retriever.py reentrancy 'withdraw before state update'")
    print("  python tools/verify_setup.py")


def cmd_continuous(api_key: str, interval: int):
    """Run forever, fetching new reports and updating agents each cycle."""
    session = requests.Session()
    print("Loading embedding model...")
    model      = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    collection = init_chroma(refresh=False)
    state      = load_state()

    # Graceful shutdown
    shutdown = {"flag": False}
    def _handle_signal(sig, frame):
        print("\n\nShutdown requested — finishing current cycle then exiting.")
        shutdown["flag"] = True
    signal.signal(signal.SIGINT,  _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    cycle_n = state.get("cycles", 0)
    print(f"\n{'═'*60}")
    print(f"  Continuous mode  |  interval: {interval} min  |  Ctrl+C to stop")
    print(f"  DB size: {collection.count()} findings")
    print(f"{'═'*60}\n")

    # If DB is empty, do a full initial scrape first
    if collection.count() == 0:
        print("DB is empty — running full initial scrape first (~49k findings)...\n")
        state["completed_batches"] = []
        save_state(state)
        n_new, new_by_type = run_cycle(
            api_key, session, model, collection, incremental=False, full_mode=True
        )
        if n_new > 0:
            all_by_type = get_all_by_type(collection)
            run_agent_learning(new_by_type, all_by_type)
            update_triager_prompt(all_by_type)
        cycle_n += 1
        state.update({"last_run": datetime.now(timezone.utc).isoformat(),
                      "total_indexed": collection.count(), "cycles": cycle_n})
        save_state(state)

    while not shutdown["flag"]:
        cycle_n += 1
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'─'*60}")
        print(f"  Cycle #{cycle_n}  |  {now}  |  DB: {collection.count()} findings")
        print(f"{'─'*60}")

        try:
            # Clear checkpoints so this cycle runs all batches fresh
            state["completed_batches"] = []
            save_state(state)

            n_new, new_by_type = run_cycle(
                api_key, session, model, collection,
                incremental=True,     # only last 30 days each cycle
            )

            if n_new > 0:
                print(f"\n  +{n_new} new findings this cycle")
                all_by_type = get_all_by_type(collection)
                run_agent_learning(new_by_type, all_by_type)
                update_triager_prompt(all_by_type)
            else:
                print("  No new findings this cycle.")

        except Exception as e:
            print(f"  Cycle error: {e} — will retry next cycle")

        state.update({"last_run": datetime.now(timezone.utc).isoformat(),
                      "total_indexed": collection.count(), "cycles": cycle_n})
        save_state(state)

        if shutdown["flag"]:
            break

        # Countdown to next cycle
        wait_secs = interval * 60
        print(f"\n  Next cycle in {interval} min. Press Ctrl+C to stop.")
        for remaining in range(wait_secs, 0, -30):
            if shutdown["flag"]:
                break
            time.sleep(min(30, remaining))
            if remaining > 30:
                print(f"  ... {remaining // 60}m {remaining % 60}s remaining", end="\r")

    print("\nContinuous mode stopped. Final DB size:", collection.count())

def cmd_learn(n_results: int = 2000):
    """Update agent files and the triager prompt using semantic search — no scraping needed.

    For each vulnerability type, embeds a descriptive query and retrieves the
    n_results most semantically similar findings from the entire DB, regardless
    of how they were tagged at scrape time.  Surfaces relevant findings even
    when classified as 'other'.

    After updating specialist agents, also updates prompts/triager.md:
      - Reads past triage decisions from data/triage/*.jsonl
      - Pulls false-positive-flavoured Solodit findings as negative examples
      - Synthesises rejection/acceptance calibration rules via Claude Haiku
      - Injects result as "## Auto-learned triage patterns" into the triager prompt
    """
    print("Loading embedding model...")
    model      = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    collection = init_chroma(refresh=False)
    n = collection.count()
    if n == 0:
        print("DB is empty — run a scrape first.")
        return
    print(f"DB has {n} findings. Running semantic search per vulnerability type...\n")

    by_type: dict[str, list] = {}
    for vuln_type in sorted(VULN_TYPE_SEARCH_QUERIES.keys()):
        query = VULN_TYPE_SEARCH_QUERIES[vuln_type]
        query_embedding = model.encode([query]).tolist()
        try:
            result = collection.query(
                query_embeddings=query_embedding,
                n_results=min(n_results, n),
                include=["metadatas", "documents"],
            )
            metas = result["metadatas"][0] if result["metadatas"] else []
            docs  = result["documents"][0]  if result["documents"]  else []
            findings = []
            for meta, doc in zip(metas, docs):
                try:
                    f = json.loads(doc)
                    f["protocol"]      = meta.get("protocol", "")
                    f["audit_firm"]    = meta.get("audit_firm", "")
                    f["quality_score"] = float(meta.get("quality_score", 0))
                    findings.append(f)
                except Exception:
                    pass
            if findings:
                by_type[vuln_type] = findings
                print(f"  {vuln_type}: {len(findings)} findings (top semantic matches)")
        except Exception as e:
            print(f"  {vuln_type}: error — {e}")

    print(f"\nRunning agent learning for {len(by_type)} types...")
    run_agent_learning(by_type, by_type)

    print("\nUpdating triager prompt with learned patterns...")
    update_triager_prompt(by_type)

    print("\nDone. Agent files and triager prompt updated.")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Solodit knowledge base builder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python scripts/solodit_scraper.py --show-tags               # verify tag counts
  python scripts/solodit_scraper.py --limit 100               # quick test
  python scripts/solodit_scraper.py --full --refresh          # wipe DB and grab ALL ~49k findings
  python scripts/solodit_scraper.py --full                    # resume grabbing all findings
  python scripts/solodit_scraper.py --learn                   # update agent files from existing DB
  python scripts/solodit_scraper.py                           # tag-filtered scrape only
  python scripts/solodit_scraper.py --refresh                 # wipe and rebuild (tag-filtered)
  python scripts/solodit_scraper.py --continuous              # run forever (30 min cycles)
  python scripts/solodit_scraper.py --continuous --interval 60  # 60 min cycles
"""
    )
    parser.add_argument("--limit",      type=int,  default=None,  help="Max findings to collect")
    parser.add_argument("--refresh",    action="store_true",       help="Clear DB before scraping")
    parser.add_argument("--full",       action="store_true",       help="Scrape ALL findings (no tag filter, ~49k)")
    parser.add_argument("--learn",      action="store_true",       help="Update agent files from existing DB (no scraping)")
    parser.add_argument("--show-tags",  action="store_true", dest="show_tags")
    parser.add_argument("--continuous", action="store_true",       help="Run continuously, updating agents")
    parser.add_argument("--interval",   type=int,  default=30,    help="Continuous cycle interval in minutes (default: 30)")
    args = parser.parse_args()

    api_key = get_api_key()
    session = requests.Session()

    if args.learn:
        cmd_learn()
    elif args.show_tags:
        cmd_show_tags(api_key, session)
    elif args.continuous:
        cmd_continuous(api_key, args.interval)
    else:
        cmd_scrape(api_key, limit=args.limit, refresh=args.refresh, full=args.full)
