#!/usr/bin/env python3
"""
glider_tool.py

Layer 3 variant analysis tool. After the specialist agents isolate a vulnerability pattern
in the target contract, Glider scans the broader Ethereum ecosystem for the same pattern —
enabling variant analysis across thousands of contracts and expanding blast radius assessment.

Glider (by Hexens) is a query-based Solidity code analysis framework. This tool wraps the
Glider API. If the API key is absent, it falls back to searching the local Chroma KB via
retriever.py for structurally similar code patterns.

Usage:
    python tools/glider_tool.py search  <pattern_name> [--limit 20]
    python tools/glider_tool.py check   <address> [--chain ethereum]
    python tools/glider_tool.py register <name> <query_file> <vuln_type>
    python tools/glider_tool.py list

Environment variables:
    GLIDER_API_KEY — Glider API key (https://glide.r.xyz/)
    GLIDER_BIN     — Path to local Glider binary (alternative to API)
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import requests

GLIDER_API_KEY = os.environ.get("GLIDER_API_KEY", "")
GLIDER_BIN = os.environ.get("GLIDER_BIN", "glider")
GLIDER_BASE_URL = "https://api.glide.r.xyz/v1"

PATTERNS_FILE = Path(__file__).resolve().parent.parent / "kb" / "glider_patterns.json"


def _load_patterns() -> dict:
    if PATTERNS_FILE.exists():
        return json.loads(PATTERNS_FILE.read_text())
    return {}


def _save_patterns(patterns: dict):
    PATTERNS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PATTERNS_FILE.write_text(json.dumps(patterns, indent=2))


def _api_headers() -> dict:
    if not GLIDER_API_KEY:
        return {}
    return {"Authorization": f"Bearer {GLIDER_API_KEY}", "Content-Type": "application/json"}


def _kb_fallback(query_name: str, limit: int) -> list[dict]:
    """Fallback: search local Chroma KB for similar vulnerability patterns."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import retriever  # noqa: F401
        result = subprocess.run(
            [sys.executable, "tools/retriever.py", "other", query_name],
            capture_output=True, text=True, cwd=Path(__file__).resolve().parent.parent,
        )
        if result.returncode == 0 and result.stdout.strip():
            kb_results = json.loads(result.stdout)
            return [
                {
                    "source": "local_kb",
                    "title": r.get("title", ""),
                    "similarity": r.get("score", 0),
                    "description": r.get("description", "")[:300],
                }
                for r in kb_results[:limit]
            ]
    except Exception as e:
        print(f"Warning: KB fallback failed — {e}", file=sys.stderr)
    return []


def search_pattern(pattern_name: str, limit: int = 20) -> list[dict]:
    """
    Search for contracts matching a named vulnerability pattern.
    Uses the Glider API if available, falls back to local KB.
    """
    patterns = _load_patterns()
    pattern = patterns.get(pattern_name)

    if not pattern:
        print(f"Warning: Pattern '{pattern_name}' not registered. Using name as raw query.", file=sys.stderr)
        query_str = pattern_name
        vuln_type = "other"
    else:
        query_str = pattern.get("query", pattern_name)
        vuln_type = pattern.get("vuln_type", "other")

    # Try Glider API
    if GLIDER_API_KEY:
        try:
            resp = requests.post(
                f"{GLIDER_BASE_URL}/search",
                json={"query": query_str, "limit": limit},
                headers=_api_headers(),
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            return [
                {
                    "source": "glider",
                    "address": r.get("address"),
                    "chain": r.get("chain", "ethereum"),
                    "contract_name": r.get("name"),
                    "function": r.get("function"),
                    "snippet": r.get("snippet", "")[:500],
                    "similarity_score": r.get("similarity", 1.0),
                    "vuln_type": vuln_type,
                }
                for r in data.get("results", [])
            ]
        except Exception as e:
            print(f"Warning: Glider API search failed — {e}. Falling back to local KB.", file=sys.stderr)

    # Try local Glider binary
    if GLIDER_BIN != "glider":  # custom path set
        try:
            result = subprocess.run(
                [GLIDER_BIN, "search", "--query", query_str, "--limit", str(limit), "--json"],
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception as e:
            print(f"Warning: Glider binary failed — {e}. Falling back to local KB.", file=sys.stderr)

    # Fallback
    print("Using local KB fallback (install Glider or set GLIDER_API_KEY for cross-repo scanning)", file=sys.stderr)
    return _kb_fallback(query_str, limit)


def check_contract(address: str, chain: str = "ethereum") -> dict:
    """Run all registered Glider patterns against a single deployed contract."""
    patterns = _load_patterns()
    if not patterns:
        return {"warning": "No patterns registered. Use 'register' to add patterns first."}

    results = {}
    for pattern_name, pattern_data in patterns.items():
        matches = search_pattern(pattern_name, limit=5)
        contract_matches = [m for m in matches if m.get("address", "").lower() == address.lower()]
        if contract_matches:
            results[pattern_name] = {
                "matched": True,
                "vuln_type": pattern_data.get("vuln_type"),
                "matches": contract_matches,
            }
        else:
            results[pattern_name] = {"matched": False}

    return {
        "address": address,
        "chain": chain,
        "patterns_checked": len(patterns),
        "matches": {k: v for k, v in results.items() if v.get("matched")},
        "clean": not any(v.get("matched") for v in results.values()),
    }


def register_pattern(name: str, query_file_or_string: str, vuln_type: str) -> dict:
    """Register a new vulnerability pattern for future Glider scans."""
    patterns = _load_patterns()

    # Accept either a file path or inline query string
    query_path = Path(query_file_or_string)
    if query_path.exists():
        query_str = query_path.read_text().strip()
    else:
        query_str = query_file_or_string

    patterns[name] = {
        "query": query_str,
        "vuln_type": vuln_type,
        "registered_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
    }
    _save_patterns(patterns)

    return {
        "registered": name,
        "vuln_type": vuln_type,
        "query_length": len(query_str),
        "total_patterns": len(patterns),
    }


def list_patterns() -> dict:
    patterns = _load_patterns()
    return {
        "total_patterns": len(patterns),
        "patterns": [
            {"name": k, "vuln_type": v.get("vuln_type"), "registered_at": v.get("registered_at")}
            for k, v in patterns.items()
        ],
    }


def main():
    parser = argparse.ArgumentParser(description="Glider variant analysis tool")
    sub = parser.add_subparsers(dest="command")

    s = sub.add_parser("search", help="Search for contracts matching a pattern")
    s.add_argument("pattern_name", help="Registered pattern name or raw query string")
    s.add_argument("--limit", type=int, default=20)

    c = sub.add_parser("check", help="Run all patterns against one contract")
    c.add_argument("address")
    c.add_argument("--chain", default="ethereum")

    r = sub.add_parser("register", help="Register a new vulnerability pattern")
    r.add_argument("name")
    r.add_argument("query", help="Query string or path to .py query file")
    r.add_argument("vuln_type", help="Vulnerability type (e.g. erc4626, reentrancy)")

    sub.add_parser("list", help="List all registered patterns")

    args = parser.parse_args()

    if args.command == "search":
        result = search_pattern(args.pattern_name, args.limit)
    elif args.command == "check":
        result = check_contract(args.address, args.chain)
    elif args.command == "register":
        result = register_pattern(args.name, args.query, args.vuln_type)
    elif args.command == "list":
        result = list_patterns()
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
