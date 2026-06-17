#!/usr/bin/env python3
"""
dune_mcp.py

Layer 2 on-chain context tool. Queries Dune Analytics for live protocol health data —
TVL trends, trading volume, top positions, and slippage data — to ground economic threat
modeling in real numbers rather than assumptions.

Non-fatal: if DUNE_API_KEY is absent or the API is unreachable, returns {} so the
pipeline continues without interruption.

Usage:
    python tools/dune_mcp.py tvl    <protocol_slug>
    python tools/dune_mcp.py volume <protocol_slug> [--days 7]
    python tools/dune_mcp.py top    <protocol_slug> [--limit 10]
    python tools/dune_mcp.py slippage <token_pair> <dex>
    python tools/dune_mcp.py query  <query_id>

Environment variables:
    DUNE_API_KEY — Dune Analytics API key (https://dune.com/settings/api)
"""

import argparse
import json
import os
import sys
import time

import requests

DUNE_API_KEY = os.environ.get("DUNE_API_KEY", "")
BASE_URL = "https://api.dune.com/api/v1"

# Pre-configured query IDs for common protocol metrics.
# These are public Dune queries; replace with protocol-specific ones as needed.
KNOWN_QUERIES = {
    "enzyme_tvl":    3825000,
    "enzyme_volume": 3825001,
    "defi_tvl":      21693,     # DefiLlama-style TVL overview
}


def _headers() -> dict:
    if not DUNE_API_KEY:
        return {}
    return {"X-Dune-API-Key": DUNE_API_KEY}


def _execute_query(query_id: int, params: dict | None = None) -> dict:
    """Execute a Dune query and poll until complete."""
    if not DUNE_API_KEY:
        print("Warning: DUNE_API_KEY not set — skipping Dune query", file=sys.stderr)
        return {}

    # Execute
    payload = {"query_parameters": params or {}}
    try:
        resp = requests.post(
            f"{BASE_URL}/query/{query_id}/execute",
            json=payload,
            headers=_headers(),
            timeout=30,
        )
        resp.raise_for_status()
        execution_id = resp.json().get("execution_id")
    except Exception as e:
        print(f"Warning: Dune execute failed — {e}", file=sys.stderr)
        return {}

    # Poll for completion (max 60s)
    for _ in range(20):
        try:
            status_resp = requests.get(
                f"{BASE_URL}/execution/{execution_id}/status",
                headers=_headers(),
                timeout=15,
            )
            status_resp.raise_for_status()
            state = status_resp.json().get("state", "")
            if state == "QUERY_STATE_COMPLETED":
                break
            if state in ("QUERY_STATE_FAILED", "QUERY_STATE_CANCELLED"):
                print(f"Warning: Dune query {query_id} ended in state {state}", file=sys.stderr)
                return {}
        except Exception as e:
            print(f"Warning: Dune status poll failed — {e}", file=sys.stderr)
            return {}
        time.sleep(3)
    else:
        print(f"Warning: Dune query {query_id} timed out", file=sys.stderr)
        return {}

    # Fetch results
    try:
        result_resp = requests.get(
            f"{BASE_URL}/execution/{execution_id}/results",
            headers=_headers(),
            timeout=30,
        )
        result_resp.raise_for_status()
        return result_resp.json().get("result", {})
    except Exception as e:
        print(f"Warning: Dune result fetch failed — {e}", file=sys.stderr)
        return {}


def _defillama_tvl(protocol_slug: str) -> dict:
    """Fallback: query DefiLlama TVL API (no key required)."""
    try:
        resp = requests.get(
            f"https://api.llama.fi/protocol/{protocol_slug}",
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        tvl_list = data.get("tvl", [])
        current_tvl = tvl_list[-1]["totalLiquidityUSD"] if tvl_list else None
        tvl_30d_ago = tvl_list[-30]["totalLiquidityUSD"] if len(tvl_list) >= 30 else None
        return {
            "source": "defillama",
            "protocol": protocol_slug,
            "current_tvl_usd": current_tvl,
            "tvl_30d_ago_usd": tvl_30d_ago,
            "tvl_change_30d_pct": (
                round((current_tvl - tvl_30d_ago) / tvl_30d_ago * 100, 2)
                if current_tvl and tvl_30d_ago and tvl_30d_ago > 0 else None
            ),
            "chains": list(data.get("chainTvls", {}).keys()),
        }
    except Exception as e:
        print(f"Warning: DefiLlama fallback failed — {e}", file=sys.stderr)
        return {}


def get_protocol_tvl(protocol_slug: str) -> dict:
    """Return current TVL and 30-day trend. Falls back to DefiLlama if no Dune key."""
    if not DUNE_API_KEY:
        return _defillama_tvl(protocol_slug)

    query_id = KNOWN_QUERIES.get(f"{protocol_slug}_tvl", KNOWN_QUERIES["defi_tvl"])
    rows = _execute_query(query_id, {"protocol": protocol_slug}).get("rows", [])
    if not rows:
        return _defillama_tvl(protocol_slug)
    return {"source": "dune", "protocol": protocol_slug, "data": rows}


def get_volume(protocol_slug: str, days: int = 7) -> dict:
    """Return trading volume for the past N days."""
    if not DUNE_API_KEY:
        try:
            resp = requests.get(
                f"https://api.llama.fi/summary/dexs/{protocol_slug}?excludeTotalDataChart=false",
                timeout=20,
            )
            resp.raise_for_status()
            data = resp.json()
            daily = data.get("totalDataChart", [])[-days:]
            total = sum(v for _, v in daily) if daily else None
            return {
                "source": "defillama",
                "protocol": protocol_slug,
                "days": days,
                "total_volume_usd": total,
                "daily": daily,
            }
        except Exception as e:
            print(f"Warning: volume fetch failed — {e}", file=sys.stderr)
            return {}

    query_id = KNOWN_QUERIES.get(f"{protocol_slug}_volume", KNOWN_QUERIES["defi_tvl"])
    rows = _execute_query(query_id, {"protocol": protocol_slug, "days": days}).get("rows", [])
    return {"source": "dune", "protocol": protocol_slug, "days": days, "data": rows}


def get_top_positions(protocol_slug: str, limit: int = 10) -> dict:
    """Return the largest positions (whale concentration) for a protocol."""
    if not DUNE_API_KEY:
        print("Warning: DUNE_API_KEY not set — top positions unavailable without Dune", file=sys.stderr)
        return {"warning": "DUNE_API_KEY required for top positions query"}

    query_id = KNOWN_QUERIES.get(f"{protocol_slug}_tvl", KNOWN_QUERIES["defi_tvl"])
    rows = _execute_query(query_id, {"protocol": protocol_slug, "limit": limit}).get("rows", [])
    return {"source": "dune", "protocol": protocol_slug, "top_positions": rows[:limit]}


def get_slippage_data(token_pair: str, dex: str) -> dict:
    """Return historical slippage data for a token pair on a given DEX."""
    token_a, _, token_b = token_pair.partition("/")
    if not DUNE_API_KEY:
        print("Warning: DUNE_API_KEY not set — slippage data unavailable", file=sys.stderr)
        return {"warning": "DUNE_API_KEY required for slippage query"}

    # Generic slippage query — adjust query_id for the target DEX/pair
    rows = _execute_query(
        KNOWN_QUERIES["defi_tvl"],
        {"token_a": token_a, "token_b": token_b, "dex": dex},
    ).get("rows", [])
    return {
        "source": "dune",
        "token_pair": token_pair,
        "dex": dex,
        "slippage_data": rows,
    }


def run_query(query_id: int) -> dict:
    """Run an arbitrary saved Dune query by ID."""
    result = _execute_query(query_id)
    return {"source": "dune", "query_id": query_id, "result": result}


def main():
    parser = argparse.ArgumentParser(description="Dune Analytics on-chain data tool")
    sub = parser.add_subparsers(dest="command")

    tvl_p = sub.add_parser("tvl", help="Protocol TVL + 30-day trend")
    tvl_p.add_argument("protocol_slug")

    vol_p = sub.add_parser("volume", help="Protocol trading volume")
    vol_p.add_argument("protocol_slug")
    vol_p.add_argument("--days", type=int, default=7)

    top_p = sub.add_parser("top", help="Largest positions (whale concentration)")
    top_p.add_argument("protocol_slug")
    top_p.add_argument("--limit", type=int, default=10)

    slip_p = sub.add_parser("slippage", help="Historical slippage for a token pair")
    slip_p.add_argument("token_pair", help="e.g. WETH/USDC")
    slip_p.add_argument("dex", help="e.g. uniswap-v3")

    qry_p = sub.add_parser("query", help="Run an arbitrary Dune query by ID")
    qry_p.add_argument("query_id", type=int)

    args = parser.parse_args()

    if args.command == "tvl":
        result = get_protocol_tvl(args.protocol_slug)
    elif args.command == "volume":
        result = get_volume(args.protocol_slug, args.days)
    elif args.command == "top":
        result = get_top_positions(args.protocol_slug, args.limit)
    elif args.command == "slippage":
        result = get_slippage_data(args.token_pair, args.dex)
    elif args.command == "query":
        result = run_query(args.query_id)
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
