#!/usr/bin/env python3
"""
onchain_mcp_server.py — MCP server exposing on-chain context tools.

Consolidates four CLI tools into a single MCP server:
  quicknode_mcp.py  → get_bytecode, get_tx_history, simulate_tx, get_storage
  dune_mcp.py       → get_tvl, get_volume
  graph_mcp.py      → query_subgraph, detect_anomaly
  chainlist_mcp.py  → resolve_rpc

Auto-registered via .mcp.json when Claude Code opens this project.
All tools degrade gracefully if API keys are absent.

Usage (standalone test):
    python tools/onchain_mcp_server.py
    # Then send MCP JSON-RPC messages via stdin

Manual CLI equivalents (still work for backward compat):
    python tools/quicknode_mcp.py bytecode <address> <chain>
    python tools/dune_mcp.py tvl <slug>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# ── Try to import mcp; emit a clear error if not installed ───────────────────
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print(
        "ERROR: 'mcp' package not installed. Run: pip install mcp>=1.0.0",
        file=sys.stderr,
    )
    sys.exit(1)

# ── Add tools/ to path so sibling modules are importable ─────────────────────
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "tools"))
sys.path.insert(0, str(_ROOT / "scripts"))

# ── Lazy imports of sibling tool modules (non-fatal) ─────────────────────────
def _import(name: str):
    try:
        import importlib
        return importlib.import_module(name)
    except Exception:
        return None

_qn      = _import("quicknode_mcp")
_dune    = _import("dune_mcp")
_graph   = _import("graph_mcp")
_chain   = _import("chainlist_mcp")

# ── MCP server ────────────────────────────────────────────────────────────────
mcp = FastMCP("onchain-context")


@mcp.tool()
def get_bytecode(address: str, chain: str = "ethereum") -> str:
    """
    Fetch the deployed bytecode for a contract address.
    Use to verify that deployed code matches the audited source.

    Args:
        address: Contract address (0x-prefixed)
        chain: Chain name (ethereum, arbitrum, base, polygon)
    """
    if _qn is None:
        return json.dumps({"error": "quicknode_mcp not available"})
    try:
        return json.dumps(_qn.get_bytecode(address, chain))
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_tx_history(address: str, chain: str = "ethereum", limit: int = 20) -> str:
    """
    Fetch recent transaction history for an address.
    Use to detect anomalous activity patterns or confirm exploit attempts.

    Args:
        address: Contract or EOA address (0x-prefixed)
        chain: Chain name
        limit: Number of recent transactions to return (max 100)
    """
    if _qn is None:
        return json.dumps({"error": "quicknode_mcp not available"})
    try:
        return json.dumps(_qn.get_transaction_history(address, chain, min(limit, 100)))
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def simulate_tx(from_addr: str, to_addr: str, calldata: str, chain: str = "ethereum") -> str:
    """
    Simulate a transaction call without broadcasting to the network.
    Use to verify exploit feasibility or check return values.

    Args:
        from_addr: Sender address
        to_addr: Target contract address
        calldata: ABI-encoded calldata (0x-prefixed hex)
        chain: Chain name
    """
    if _qn is None:
        return json.dumps({"error": "quicknode_mcp not available"})
    try:
        return json.dumps(_qn.simulate_transaction(from_addr, to_addr, calldata, chain))
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_storage(address: str, slots: str, chain: str = "ethereum") -> str:
    """
    Read raw storage slots from a deployed contract.
    Use to verify proxy implementation address, admin slot, or state variables.

    Args:
        address: Contract address
        slots: Comma-separated slot indices (e.g. "0,1,2" or "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc")
        chain: Chain name
    """
    if _qn is None:
        return json.dumps({"error": "quicknode_mcp not available"})
    try:
        slot_list = [int(s.strip(), 16) if s.strip().startswith("0x") else int(s.strip())
                     for s in slots.split(",")]
        return json.dumps(_qn.get_storage_slots(address, chain, slot_list))
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_tvl(protocol_slug: str) -> str:
    """
    Fetch Total Value Locked for a protocol (Dune / DefiLlama fallback).
    Use for severity calibration — higher TVL raises impact of critical bugs.

    Args:
        protocol_slug: Protocol identifier (e.g. "aave", "compound", "uniswap")
    """
    if _dune is None:
        return json.dumps({"error": "dune_mcp not available"})
    try:
        return json.dumps(_dune.get_protocol_tvl(protocol_slug))
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_volume(protocol_slug: str, days: int = 7) -> str:
    """
    Fetch trading volume for a protocol over a period.
    Use for severity calibration and economic impact estimation.

    Args:
        protocol_slug: Protocol identifier
        days: Lookback window in days (default 7)
    """
    if _dune is None:
        return json.dumps({"error": "dune_mcp not available"})
    try:
        return json.dumps(_dune.get_volume(protocol_slug, days))
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def query_subgraph(subgraph: str, graphql_query: str) -> str:
    """
    Execute a GraphQL query against a known protocol subgraph on The Graph.
    Known subgraphs: enzyme, uniswap-v3, aave-v3, compound-v3, curve

    Args:
        subgraph: Protocol slug or full subgraph endpoint URL
        graphql_query: GraphQL query string
    """
    if _graph is None:
        return json.dumps({"error": "graph_mcp not available"})
    try:
        return json.dumps(_graph.query_subgraph(subgraph, graphql_query))
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def detect_anomaly(protocol_slug: str, field: str = "totalValueLockedUSD") -> str:
    """
    Detect statistical anomalies in historical on-chain data for a protocol.
    Use to flag unusual TVL drops, volume spikes, or state changes.

    Args:
        protocol_slug: Protocol identifier
        field: The metric to analyse (e.g. totalValueLockedUSD, volumeUSD)
    """
    if _graph is None:
        return json.dumps({"error": "graph_mcp not available"})
    try:
        return json.dumps(_graph.find_anomalies(protocol_slug, field))
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def resolve_rpc(chain_id: str) -> str:
    """
    Resolve the best public RPC endpoint for a given EVM chain.
    Use to set up local simulation or direct RPC calls.

    Args:
        chain_id: Chain ID as integer string or chain name (e.g. "1", "42161", "ethereum")
    """
    if _chain is None:
        return json.dumps({"error": "chainlist_mcp not available"})
    try:
        return json.dumps(_chain.cmd_rpc(chain_id))
    except Exception as e:
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    mcp.run()
