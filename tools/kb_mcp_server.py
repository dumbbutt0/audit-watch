#!/usr/bin/env python3
"""
kb_mcp_server.py — MCP server exposing the local knowledge base and attack primitives.

Tools exposed:
  search_findings(vuln_type, query, top_k=5)      → Chroma semantic search (Solodit/C4/Sherlock)
  search_immunefi(vuln_type, query, top_k=5)      → Immunefi bug-bounty reports via GitBook MCP
  get_primitives(category)                         → attack primitives by category
  get_primitive_compounds(primitive_id)            → primitives that compound with a given ID

Auto-registered via .mcp.json when Claude Code opens this project.

Usage (standalone test):
    python tools/kb_mcp_server.py
    # Then send MCP JSON-RPC messages via stdin

Manual CLI equivalents (still work for backward compat):
    python tools/retriever.py reentrancy "flash loan callback"
    python tools/immunefi_retriever.py reentrancy "flash loan callback"
    python tools/primitives_retriever.py reentrancy
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print(
        "ERROR: 'mcp' package not installed. Run: pip install mcp>=1.0.0",
        file=sys.stderr,
    )
    sys.exit(1)

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "tools"))
sys.path.insert(0, str(_ROOT / "scripts"))

_KB_DIR = _ROOT / "kb"
_PRIMITIVES_FILE = _KB_DIR / "attack_primitives.json"


def _import(name: str):
    try:
        import importlib
        return importlib.import_module(name)
    except Exception:
        return None


_retriever = _import("retriever")
_immunefi = _import("immunefi_retriever")

mcp = FastMCP("kb-search")


@mcp.tool()
def search_findings(vuln_type: str = "other", query: str = "", top_k: int = 5) -> str:
    """
    Search the local Solodit/Code4rena/Sherlock knowledge base for relevant audit findings.
    Returns the top-k most similar findings for a given vulnerability type and query.

    Args:
        vuln_type: Vulnerability category — one of: reentrancy, access-control, arithmetic,
                   oracle-manipulation, flash-loan, logic-error, gas-griefing, dos,
                   signature-replay, storage-collision, proxy-upgrade, front-running, other
        query: Natural language description of the pattern you're investigating
        top_k: Number of results to return (default 5, max 20)
    """
    if not query:
        return json.dumps({"error": "query is required"})
    if _retriever is None:
        return json.dumps({"error": "retriever module not available — check chromadb/sentence-transformers install"})
    try:
        results = _retriever.query_kb(
            vuln_type=vuln_type,
            query=query,
            top_k=min(top_k, 20),
            all_types=(vuln_type == "other"),
        )
        return json.dumps(results)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def search_immunefi(vuln_type: str = "other", query: str = "", top_k: int = 5) -> str:
    """
    Search Immunefi bug-bounty reports via the GitBook MCP endpoint.
    Returns top-k relevant reports. Returns [] if the endpoint is unreachable — non-fatal.

    Args:
        vuln_type: Vulnerability type hint for relevance scoring (e.g. reentrancy, oracle-manipulation)
        query: Natural language query describing the vulnerability pattern
        top_k: Maximum number of results (default 5)
    """
    if not query:
        return json.dumps([])
    if _immunefi is None:
        return json.dumps({"error": "immunefi_retriever module not available"})
    try:
        import requests as _req
        search_query = f"{vuln_type} {query}"
        with _req.Session() as session:
            try:
                _immunefi._initialize(session)
            except Exception:
                pass
            try:
                raw = _immunefi._search(session, search_query)
            except Exception as exc:
                return json.dumps({"error": f"Immunefi MCP unreachable: {exc}"})
        findings = _immunefi.normalize_results(raw, vuln_type, top_k)
        return json.dumps(findings)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_primitives(category: str = "") -> str:
    """
    Return attack primitives from the local knowledge base, optionally filtered by category.
    Categories: reentrancy, flash-loan, oracle-manipulation, access-control,
                arithmetic, logic-error, dos, upgrade-storage, front-running

    Args:
        category: Category to filter by. Leave empty to return all primitives.
    """
    if not _PRIMITIVES_FILE.exists():
        return json.dumps({"error": "attack_primitives.json not found — run kb setup"})
    try:
        data = json.loads(_PRIMITIVES_FILE.read_text())
        primitives = data if isinstance(data, list) else data.get("primitives", [])
        if category:
            primitives = [p for p in primitives if p.get("category", "") == category]
        return json.dumps(primitives)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_primitive_compounds(primitive_id: str) -> str:
    """
    Return all attack primitives that are known to compound with the given primitive ID.
    Useful for discovering multi-primitive compound vulnerabilities.

    Args:
        primitive_id: Primitive ID (e.g. "PRIM-006") to find compounds for
    """
    if not _PRIMITIVES_FILE.exists():
        return json.dumps({"error": "attack_primitives.json not found"})
    try:
        data = json.loads(_PRIMITIVES_FILE.read_text())
        primitives = data if isinstance(data, list) else data.get("primitives", [])

        # Find the compound IDs listed for this primitive
        source = next((p for p in primitives if p.get("id") == primitive_id), None)
        if source is None:
            return json.dumps({"error": f"Primitive {primitive_id} not found"})

        compound_ids: set[str] = set(source.get("known_compounds", []))

        # Also find any primitive that lists this ID in its own known_compounds
        for p in primitives:
            if primitive_id in p.get("known_compounds", []):
                compound_ids.add(p["id"])

        compound_ids.discard(primitive_id)
        compounds = [p for p in primitives if p.get("id") in compound_ids]
        return json.dumps({"source": source, "compounds": compounds})
    except Exception as e:
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    mcp.run()
