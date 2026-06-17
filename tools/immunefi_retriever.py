#!/usr/bin/env python3
"""
immunefi_retriever.py

Query Immunefi bug bounty reports via the GitBook MCP endpoint.
Returns top-k relevant reports for a given vulnerability type and query.

Usage (called as subprocess by agents):
    python tools/immunefi_retriever.py reentrancy "withdraw external call before state update"
    python tools/immunefi_retriever.py oracle-manipulation "chainlink staleness missing" --top-k 3
    python tools/immunefi_retriever.py --all "flash loan governance attack"

Output: JSON array printed to stdout (empty array [] on network error — non-fatal).
"""

import argparse
import json
import re
import sys

import requests

IMMUNEFI_MCP_URL = "https://reports.immunefi.com/~gitbook/mcp"
MCP_VERSION = "2024-11-05"
REQUEST_TIMEOUT = 20

# Keyword hints for inferring vuln_type from report text when the requested type
# doesn't match the content.  Longest/most-specific patterns listed first.
_VULN_PATTERNS: list[tuple[str, str]] = [
    (r"oracle.{0,20}manipulat|price.{0,20}manipulat|chainlink|twap|spot.{0,10}price", "oracle-manipulation"),
    (r"flash.{0,10}loan|flashloan|atomic.{0,10}borrow", "flash-loan"),
    (r"reentranc|re-entranc|CEI|checks.effects.interactions", "reentrancy"),
    (r"access.control|unauthorized|missing.{0,10}auth|privilege|ownership|admin.{0,10}role", "access-control"),
    (r"overflow|underflow|precision.loss|rounding.error|arithmetic|integer.{0,10}cast", "arithmetic"),
    (r"denial.of.service|\bdos\b|unbounded.{0,10}loop|gas.{0,10}limit|griefing|lock.{0,10}fund", "dos"),
    (r"logic.error|invariant|state.machine|accounting.{0,20}bug|business.logic", "logic-error"),
]


def _parse_sse(text: str) -> list[dict]:
    """Extract JSON payloads from a server-sent events stream."""
    results = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("data: ") and line[6:] not in ("", "[DONE]"):
            try:
                results.append(json.loads(line[6:]))
            except json.JSONDecodeError:
                pass
    return results


def _mcp_post(session: requests.Session, payload: dict, session_id: str | None = None) -> dict:
    """POST a JSON-RPC 2.0 payload; handle both JSON and SSE responses."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    resp = session.post(IMMUNEFI_MCP_URL, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()

    ct = resp.headers.get("Content-Type", "")
    if "text/event-stream" in ct:
        events = _parse_sse(resp.text)
        return events[0] if events else {}
    return resp.json()


def _initialize(session: requests.Session) -> None:
    """MCP handshake (required by spec; server does not return a session ID)."""
    _mcp_post(session, {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "initialize",
        "params": {
            "protocolVersion": MCP_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "smart-contract-auditor", "version": "1.0.0"},
        },
    })


def _search(session: requests.Session, query: str) -> dict:
    """Call the Immunefi GitBook `searchDocumentation` tool."""
    return _mcp_post(session, {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "searchDocumentation",
            "arguments": {"query": query},
        },
    })


def _infer_severity(text: str) -> str:
    t = text.lower()
    for label in ("critical", "high", "medium", "low"):
        if label in t:
            return label.capitalize()
    return "Unknown"


def _infer_vuln_type(text: str, fallback: str) -> str:
    t = text.lower()
    for pattern, vtype in _VULN_PATTERNS:
        if re.search(pattern, t):
            return vtype
    return fallback


def _extract_protocol(title: str, url: str = "") -> str:
    """
    Extract protocol name from an Immunefi report title or URL.

    Immunefi titles look like:
      "#43314 [SC-Insight] Oracle functions mislead integrators..."  → from URL path
      "57596 sc low reentrancy in distributepromoterpayments..."     → from URL path
      "29513 - [SC - Insight] Critical reentrancy..."               → from URL path
    URL path first segment after the domain is the protocol name.
    """
    # Prefer URL: first path segment after the domain is the protocol slug
    # e.g. https://reports.immunefi.com/alchemix-v3/56798-... → "alchemix-v3"
    if url:
        url_path = re.sub(r"^https?://[^/]+", "", url)  # strip scheme + host
        segments = [s for s in url_path.split("/") if s]
        if segments:
            slug = segments[0]
            # Skip pure-numeric or finding-id-style slugs
            if not re.match(r"^\d+", slug):
                return " ".join(w.capitalize() for w in slug.split("-"))

    # Fallback: conventional separators
    for sep in (" — ", " - ", ": ", " | "):
        if sep in title:
            candidate = title.split(sep)[0].strip()
            # Skip if candidate looks like a finding ID (all digits or starts with #)
            if candidate and not re.match(r"^#?\d+$", candidate):
                return candidate

    return "Unknown"


def _parse_text_block(text: str) -> list[dict]:
    """
    Parse a single content block from the Immunefi searchDocumentation tool.

    The endpoint returns one text block per result, formatted as:
        Title: <title>
        Link: <url>
        Content: <description text...>

    Fallback: attempt JSON parse, then treat the whole block as one entry.
    """
    text = text.strip()

    # Attempt 1: structured "Title: / Link: / Content:" format (actual endpoint format)
    title_m = re.search(r"^Title:\s*(.+)", text, re.MULTILINE)
    link_m = re.search(r"^Link:\s*(https?://\S+)", text, re.MULTILINE)
    content_m = re.search(r"^Content:\s*([\s\S]+)", text, re.MULTILINE)
    if title_m:
        return [{
            "title": title_m.group(1).strip(),
            "url": link_m.group(1).strip() if link_m else "",
            "description": content_m.group(1).strip()[:600] if content_m else "",
        }]

    # Attempt 2: embedded JSON array
    if text.startswith("[") or text.startswith("{"):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                parsed = [parsed]
            return [p for p in parsed if isinstance(p, dict)]
        except json.JSONDecodeError:
            pass

    # Attempt 3: markdown bold headings or numbered sections
    pages: list[dict] = []
    sections = re.split(r"\n(?=\d+\.\s|\*\*[A-Z])", text)
    for section in sections:
        section = section.strip()
        if not section:
            continue
        title_match = re.search(r"\*\*(.+?)\*\*|##\s+(.+)", section)
        title = (title_match.group(1) or title_match.group(2)).strip() if title_match else section[:60]
        url_match = re.search(r"https?://\S+", section)
        url = url_match.group(0) if url_match else ""
        body = re.sub(r"\*\*.+?\*\*|##\s+.+|\bhttps?://\S+", "", section).strip()
        pages.append({"title": title, "description": body[:600], "url": url})
    if pages:
        return pages

    # Fallback: treat the whole block as one finding
    return [{"title": "Immunefi report", "description": text[:600], "url": ""}]


def normalize_results(raw: dict, vuln_type: str, top_k: int) -> list[dict]:
    """Convert an MCP tools/call response to our standard findings list."""
    findings: list[dict] = []

    result = raw.get("result", {}) if isinstance(raw, dict) else {}
    content_blocks = result.get("content", []) if isinstance(result, dict) else []

    for block in content_blocks:
        if not isinstance(block, dict) or block.get("type") != "text":
            continue
        raw_text = block.get("text", "")
        if not raw_text:
            continue

        for item in _parse_text_block(raw_text):
            title = item.get("title") or item.get("name", "")
            description = item.get("description") or item.get("body") or item.get("excerpt", "")
            url = item.get("url") or item.get("href", "")

            description = (description or "")[:600]
            combined = f"{title} {description}"

            findings.append({
                "title": title,
                "severity": _infer_severity(combined),
                "vuln_type": _infer_vuln_type(combined, vuln_type),
                "protocol": _extract_protocol(title, url),
                "source": "immunefi",
                "description": description,
                "url": url,
            })

    return findings[:top_k]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Query Immunefi bug bounty reports via the GitBook MCP endpoint"
    )
    parser.add_argument(
        "vuln_type", nargs="?", default="other",
        help="Vulnerability type filter (e.g. reentrancy, oracle-manipulation)"
    )
    parser.add_argument(
        "query", nargs="?", default="",
        help="Natural language query describing the pattern to search for"
    )
    parser.add_argument(
        "--all", dest="all_types", action="store_true",
        help="Ignore vuln_type filter; search across all categories"
    )
    parser.add_argument(
        "--top-k", type=int, default=5, dest="top_k",
        help="Maximum number of results to return (default: 5)"
    )
    args = parser.parse_args()

    if not args.query:
        print("[]")
        sys.exit(0)

    # Enrich the query with the vuln_type for better relevance when not in --all mode
    search_query = args.query if args.all_types else f"{args.vuln_type} {args.query}"

    with requests.Session() as session:
        try:
            _initialize(session)
        except requests.RequestException:
            pass  # Non-fatal; proceed without handshake

        try:
            raw = _search(session, search_query)
        except requests.RequestException as exc:
            print(f"# Immunefi MCP unreachable: {exc}", file=sys.stderr)
            print("[]")
            sys.exit(0)

    findings = normalize_results(raw, args.vuln_type, args.top_k)
    print(json.dumps(findings, indent=2))


if __name__ == "__main__":
    main()
