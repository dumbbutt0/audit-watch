#!/usr/bin/env python3
"""
graph_mcp.py

Layer 2 on-chain context tool. Queries The Graph Protocol subgraphs for historical
protocol state — useful for verifying that state variable invariants hold over real
historical data, detecting historical anomalies, and confirming that no invariant
violations have already occurred in production.

Non-fatal: if the endpoint is unreachable or returns an error, returns {} so the
pipeline continues without interruption.

Usage:
    python tools/graph_mcp.py query  <subgraph_url> "<graphql_query>"
    python tools/graph_mcp.py history <subgraph_url> <entity> <field> [--from-block N] [--to-block N]
    python tools/graph_mcp.py anomaly <subgraph_url> <entity> <field> --threshold <float>
    python tools/graph_mcp.py known   <protocol_slug>

Environment variables:
    GRAPH_API_KEY — The Graph Network gateway API key (optional; public subgraphs work without)
"""

import argparse
import json
import os
import sys

import requests

GRAPH_API_KEY = os.environ.get("GRAPH_API_KEY", "")

# Known subgraph endpoints for common protocols (public, no key required).
KNOWN_SUBGRAPHS = {
    "enzyme":       "https://api.thegraph.com/subgraphs/name/enzymefinance/enzyme-core",
    "uniswap-v3":   "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3",
    "aave-v3":      "https://api.thegraph.com/subgraphs/name/aave/protocol-v3",
    "compound-v3":  "https://api.thegraph.com/subgraphs/name/messari/compound-v3-ethereum",
    "curve":        "https://api.thegraph.com/subgraphs/name/messari/curve-finance-ethereum",
}


def _gql_request(endpoint: str, query: str, variables: dict | None = None) -> dict:
    """Execute a GraphQL query against a subgraph endpoint."""
    headers = {"Content-Type": "application/json"}
    if GRAPH_API_KEY:
        headers["Authorization"] = f"Bearer {GRAPH_API_KEY}"

    payload = {"query": query, "variables": variables or {}}
    try:
        resp = requests.post(endpoint, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if "errors" in data:
            print(f"Warning: GraphQL errors — {data['errors']}", file=sys.stderr)
            return {"errors": data["errors"]}
        return data.get("data", {})
    except Exception as e:
        print(f"Warning: The Graph request failed — {e}", file=sys.stderr)
        return {}


def query_subgraph(endpoint: str, graphql_query: str) -> dict:
    """Run an arbitrary GraphQL query against a subgraph and return results."""
    return _gql_request(endpoint, graphql_query)


def get_historical_state(
    endpoint: str,
    entity: str,
    field: str,
    from_block: int = 0,
    to_block: int | None = None,
    limit: int = 100,
) -> dict:
    """
    Fetch a timeseries of a field value for an entity across block range.
    Constructs a generic query; the entity must have a 'blockNumber' field.
    """
    block_filter = f"blockNumber_gte: {from_block}"
    if to_block:
        block_filter += f", blockNumber_lte: {to_block}"

    query = f"""
    {{
      {entity}s(
        first: {limit},
        orderBy: blockNumber,
        orderDirection: asc,
        where: {{ {block_filter} }}
      ) {{
        id
        blockNumber
        {field}
      }}
    }}
    """
    data = _gql_request(endpoint, query)
    items = data.get(f"{entity}s", [])
    return {
        "endpoint": endpoint,
        "entity": entity,
        "field": field,
        "from_block": from_block,
        "to_block": to_block,
        "data_points": len(items),
        "timeseries": items,
    }


def find_anomalies(
    endpoint: str,
    entity: str,
    field: str,
    threshold: float,
    limit: int = 200,
) -> dict:
    """
    Fetch all historical values of a field and flag any that exceed the threshold
    or fall below zero (potential invariant violations in production data).
    """
    query = f"""
    {{
      {entity}s(first: {limit}, orderBy: blockNumber, orderDirection: asc) {{
        id
        blockNumber
        {field}
      }}
    }}
    """
    data = _gql_request(endpoint, query)
    items = data.get(f"{entity}s", [])

    anomalies = []
    for item in items:
        val = item.get(field)
        try:
            v = float(val)
            if v > threshold or v < 0:
                anomalies.append({**item, "flagged_value": v, "threshold": threshold})
        except (TypeError, ValueError):
            pass

    return {
        "endpoint": endpoint,
        "entity": entity,
        "field": field,
        "threshold": threshold,
        "total_records_checked": len(items),
        "anomalies_found": len(anomalies),
        "anomalies": anomalies,
    }


def get_known_protocol(protocol_slug: str, custom_query: str | None = None) -> dict:
    """Query a known protocol subgraph for basic health metrics."""
    endpoint = KNOWN_SUBGRAPHS.get(protocol_slug.lower())
    if not endpoint:
        available = ", ".join(KNOWN_SUBGRAPHS.keys())
        return {"error": f"Unknown protocol slug. Available: {available}"}

    if custom_query:
        return query_subgraph(endpoint, custom_query)

    # Default health query — generic across most DeFi subgraphs
    default_q = """
    {
      protocols(first: 1) {
        id
        name
        totalValueLockedUSD
        cumulativeVolumeUSD
        totalPoolCount
      }
    }
    """
    result = _gql_request(endpoint, default_q)
    return {"protocol": protocol_slug, "endpoint": endpoint, "data": result}


def main():
    parser = argparse.ArgumentParser(description="The Graph subgraph query tool")
    sub = parser.add_subparsers(dest="command")

    q = sub.add_parser("query", help="Run an arbitrary GraphQL query")
    q.add_argument("endpoint", help="Subgraph endpoint URL or known protocol slug")
    q.add_argument("gql_query", help="GraphQL query string")

    h = sub.add_parser("history", help="Fetch field value timeseries for an entity")
    h.add_argument("endpoint", help="Subgraph endpoint URL")
    h.add_argument("entity", help="Entity name (singular, e.g. 'vault')")
    h.add_argument("field", help="Field to track (e.g. 'totalAssets')")
    h.add_argument("--from-block", type=int, default=0)
    h.add_argument("--to-block", type=int, default=None)
    h.add_argument("--limit", type=int, default=100)

    an = sub.add_parser("anomaly", help="Flag historical values exceeding a threshold")
    an.add_argument("endpoint")
    an.add_argument("entity")
    an.add_argument("field")
    an.add_argument("--threshold", type=float, required=True)
    an.add_argument("--limit", type=int, default=200)

    kn = sub.add_parser("known", help="Query a known protocol by slug")
    kn.add_argument("protocol_slug", choices=list(KNOWN_SUBGRAPHS.keys()))
    kn.add_argument("--query", default=None, help="Custom GraphQL query")

    args = parser.parse_args()

    if args.command == "query":
        endpoint = KNOWN_SUBGRAPHS.get(args.endpoint, args.endpoint)
        result = query_subgraph(endpoint, args.gql_query)
    elif args.command == "history":
        result = get_historical_state(
            args.endpoint, args.entity, args.field,
            from_block=args.from_block, to_block=args.to_block, limit=args.limit,
        )
    elif args.command == "anomaly":
        result = find_anomalies(args.endpoint, args.entity, args.field, args.threshold, args.limit)
    elif args.command == "known":
        result = get_known_protocol(args.protocol_slug, args.query)
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
