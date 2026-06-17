#!/usr/bin/env python3
"""
quicknode_mcp.py

Layer 2 on-chain context tool. Pulls live EVM data for deployed in-scope contracts
via QuickNode JSON-RPC endpoints — bytecode, transaction history, tx simulation,
and raw storage slots.

All operations are non-fatal: if the endpoint is unreachable or the API key is absent,
the tool prints a warning and returns an empty result so the pipeline continues.

Usage:
    python tools/quicknode_mcp.py bytecode 0xABCD... ethereum
    python tools/quicknode_mcp.py history  0xABCD... ethereum [--limit 50]
    python tools/quicknode_mcp.py simulate --from 0x... --to 0x... --data 0x... --chain ethereum
    python tools/quicknode_mcp.py storage  0xABCD... ethereum --slots 0,1,2

Environment variables:
    QUICKNODE_ENDPOINT_ETHEREUM   — full QuickNode HTTP endpoint URL for Ethereum
    QUICKNODE_ENDPOINT_ARBITRUM   — full QuickNode HTTP endpoint URL for Arbitrum
    QUICKNODE_ENDPOINT_BASE       — full QuickNode HTTP endpoint URL for Base
    QUICKNODE_ENDPOINT_POLYGON    — full QuickNode HTTP endpoint URL for Polygon
"""

import argparse
import json
import os
import sys
from typing import Any

import requests

ENDPOINTS = {
    "ethereum": os.environ.get("QUICKNODE_ENDPOINT_ETHEREUM", ""),
    "arbitrum": os.environ.get("QUICKNODE_ENDPOINT_ARBITRUM", ""),
    "base":     os.environ.get("QUICKNODE_ENDPOINT_BASE", ""),
    "polygon":  os.environ.get("QUICKNODE_ENDPOINT_POLYGON", ""),
}

ETHERSCAN_API_KEY = os.environ.get("ETHERSCAN_API_KEY", "")
ETHERSCAN_URLS = {
    "ethereum": "https://api.etherscan.io/api",
    "arbitrum": "https://api.arbiscan.io/api",
    "base":     "https://api.basescan.org/api",
    "polygon":  "https://api.polygonscan.com/api",
}


def _rpc(chain: str, method: str, params: list) -> Any:
    endpoint = ENDPOINTS.get(chain.lower(), "")
    if not endpoint:
        print(f"Warning: QUICKNODE_ENDPOINT_{chain.upper()} not set — skipping on-chain query", file=sys.stderr)
        return None
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    try:
        resp = requests.post(endpoint, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            print(f"Warning: RPC error — {data['error']}", file=sys.stderr)
            return None
        return data.get("result")
    except Exception as e:
        print(f"Warning: QuickNode request failed — {e}", file=sys.stderr)
        return None


def get_bytecode(address: str, chain: str) -> dict:
    """Fetch deployed bytecode for a contract address."""
    code = _rpc(chain, "eth_getCode", [address, "latest"])
    if code is None:
        return {}

    result = {
        "address": address,
        "chain": chain,
        "bytecode_hex": code,
        "bytecode_size_bytes": max(0, (len(code) - 2) // 2),
        "is_contract": code != "0x" and code != "0x0",
    }

    # Heuristic: detect ERC-1967 proxy (implementation slot 0x360894...)
    if "360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc" in code:
        result["proxy_type"] = "ERC-1967"
        impl_slot = _rpc(chain, "eth_getStorageAt", [
            address,
            "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc",
            "latest",
        ])
        if impl_slot:
            result["implementation_address"] = "0x" + impl_slot[-40:]

    # Detect EIP-1167 minimal proxy (0x363d3d373d3d3d363d73 prefix)
    if code.startswith("0x363d3d373d3d3d363d73"):
        result["proxy_type"] = "EIP-1167 Minimal Proxy"
        result["implementation_address"] = "0x" + code[22:62]

    # Detect transient storage opcodes (TSTORE=0x5d, TLOAD=0x5c)
    code_body = code[2:]  # strip 0x
    has_tstore = "5d" in [code_body[i:i+2] for i in range(0, len(code_body), 2)]
    has_tload  = "5c" in [code_body[i:i+2] for i in range(0, len(code_body), 2)]
    result["has_transient_storage"] = has_tstore or has_tload

    return result


def get_transaction_history(address: str, chain: str, limit: int = 100) -> dict:
    """Fetch recent transactions (including failed) via Etherscan-compatible API."""
    base_url = ETHERSCAN_URLS.get(chain.lower())
    if not base_url:
        return {"error": f"Unsupported chain for tx history: {chain}"}

    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "page": 1,
        "offset": limit,
        "sort": "desc",
        "apikey": ETHERSCAN_API_KEY or "YourApiKeyToken",
    }
    try:
        resp = requests.get(base_url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != "1":
            return {"warning": data.get("message", "No transactions found"), "result": []}
        txs = data.get("result", [])
        return {
            "address": address,
            "chain": chain,
            "total_fetched": len(txs),
            "failed_txs": [t for t in txs if t.get("isError") == "1"],
            "unique_callers": list({t["from"] for t in txs}),
            "transactions": txs[:limit],
        }
    except Exception as e:
        print(f"Warning: tx history fetch failed — {e}", file=sys.stderr)
        return {}


def simulate_transaction(from_addr: str, to_addr: str, calldata: str, chain: str) -> dict:
    """Simulate a transaction via eth_call and return the result/revert reason."""
    result = _rpc(chain, "eth_call", [
        {"from": from_addr, "to": to_addr, "data": calldata},
        "latest",
    ])
    if result is None:
        return {}

    decoded = None
    if result.startswith("0x08c379a0"):
        # Standard Error(string) revert
        try:
            msg_hex = result[10:]  # skip selector + offset
            # 32 bytes offset + 32 bytes length + string data
            length_hex = msg_hex[64:128]
            length = int(length_hex, 16)
            msg_bytes = bytes.fromhex(msg_hex[128:128 + length * 2])
            decoded = msg_bytes.decode("utf-8", errors="replace")
        except Exception:
            decoded = result

    return {
        "from": from_addr,
        "to": to_addr,
        "calldata": calldata,
        "chain": chain,
        "raw_return": result,
        "decoded_revert": decoded,
        "reverted": result.startswith("0x08c379a0") or result == "0x",
    }


def get_storage_slots(address: str, chain: str, slots: list[int]) -> dict:
    """Read raw storage slots from a deployed contract."""
    values = {}
    for slot in slots:
        slot_hex = hex(slot)
        val = _rpc(chain, "eth_getStorageAt", [address, slot_hex, "latest"])
        values[str(slot)] = val
    return {"address": address, "chain": chain, "slots": values}


def main():
    parser = argparse.ArgumentParser(description="QuickNode EVM on-chain data tool")
    sub = parser.add_subparsers(dest="command")

    bc = sub.add_parser("bytecode", help="Fetch deployed bytecode")
    bc.add_argument("address")
    bc.add_argument("chain", choices=list(ENDPOINTS.keys()))

    hist = sub.add_parser("history", help="Fetch transaction history")
    hist.add_argument("address")
    hist.add_argument("chain", choices=list(ENDPOINTS.keys()))
    hist.add_argument("--limit", type=int, default=100)

    sim = sub.add_parser("simulate", help="Simulate a transaction")
    sim.add_argument("--from", dest="from_addr", required=True)
    sim.add_argument("--to", required=True)
    sim.add_argument("--data", default="0x")
    sim.add_argument("--chain", default="ethereum")

    stor = sub.add_parser("storage", help="Read storage slots")
    stor.add_argument("address")
    stor.add_argument("chain", choices=list(ENDPOINTS.keys()))
    stor.add_argument("--slots", default="0", help="Comma-separated slot numbers")

    args = parser.parse_args()

    if args.command == "bytecode":
        result = get_bytecode(args.address, args.chain)
    elif args.command == "history":
        result = get_transaction_history(args.address, args.chain, args.limit)
    elif args.command == "simulate":
        result = simulate_transaction(args.from_addr, args.to, args.data, args.chain)
    elif args.command == "storage":
        slots = [int(s.strip()) for s in args.slots.split(",")]
        result = get_storage_slots(args.address, args.chain, slots)
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
