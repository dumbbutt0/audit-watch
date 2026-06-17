#!/usr/bin/env python3
"""
chainlist_mcp.py — Fetch public RPC endpoints from chainid.network (same data as chainlist.org).

Commands:
  rpc <chain_id>    Best public HTTP RPC for chain_id
  list              All chains (id, name, rpc count)
  find <name>       Search chains by name (case-insensitive)
  env               Emit shell export statements for MAINNET_RPC, ARBITRUM_RPC, BASE_RPC
"""

import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

CHAINS_URL = "https://chainid.network/chains.json"
CACHE_PATH = Path(__file__).parent.parent / "kb" / "chainlist_cache.json"
CACHE_TTL = 86400  # 24 hours


def _load_cache():
    if CACHE_PATH.exists():
        data = json.loads(CACHE_PATH.read_text())
        if time.time() - data.get("timestamp", 0) < CACHE_TTL:
            return data["chains"]
    return None


def _save_cache(chains):
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps({"timestamp": time.time(), "chains": chains}, indent=2))


def _fetch_chains():
    cached = _load_cache()
    if cached is not None:
        return cached
    try:
        req = urllib.request.Request(CHAINS_URL, headers={"User-Agent": "audit-watch/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            chains = json.loads(resp.read())
        _save_cache(chains)
        return chains
    except urllib.error.URLError as e:
        # If cache exists but stale, return it rather than failing
        if CACHE_PATH.exists():
            return json.loads(CACHE_PATH.read_text())["chains"]
        sys.exit(f"error: cannot fetch chain list: {e}")


def _best_rpc(rpcs):
    # Exclude API-key-required URLs (contain ${)
    public = [r for r in rpcs if "${" not in r]
    # Prefer https
    https_rpcs = [r for r in public if r.startswith("https://")]
    candidates = https_rpcs if https_rpcs else [r for r in public if r.startswith("http://")]
    return candidates[0] if candidates else None


def cmd_rpc(chain_id_str):
    chain_id = int(chain_id_str)
    chains = _fetch_chains()
    for chain in chains:
        if chain.get("chainId") == chain_id:
            rpc = _best_rpc(chain.get("rpc", []))
            if rpc:
                print(rpc)
                return
            sys.exit(f"error: no public RPC found for chain {chain_id}")
    sys.exit(f"error: chain {chain_id} not found")


def cmd_list():
    chains = _fetch_chains()
    for chain in sorted(chains, key=lambda c: c.get("chainId", 0)):
        public = [r for r in chain.get("rpc", []) if "${" not in r]
        print(f"{chain.get('chainId', '?'):>8}  {len(public):>3} rpcs  {chain.get('name', '?')}")


def cmd_find(name):
    name_lower = name.lower()
    chains = _fetch_chains()
    hits = [c for c in chains if name_lower in c.get("name", "").lower()]
    if not hits:
        print("No chains found.")
        return
    for chain in sorted(hits, key=lambda c: c.get("chainId", 0)):
        public = [r for r in chain.get("rpc", []) if "${" not in r]
        print(f"{chain.get('chainId', '?'):>8}  {len(public):>3} rpcs  {chain.get('name', '?')}")


def cmd_env():
    targets = {
        "MAINNET_RPC": 1,       # Ethereum mainnet
        "ARBITRUM_RPC": 42161,  # Arbitrum One
        "BASE_RPC": 8453,       # Base
    }
    chains = _fetch_chains()
    by_id = {c.get("chainId"): c for c in chains}
    for var, cid in targets.items():
        chain = by_id.get(cid)
        if not chain:
            print(f"# {var}: chain {cid} not found")
            continue
        rpc = _best_rpc(chain.get("rpc", []))
        if rpc:
            print(f'export {var}="{rpc}"')
        else:
            print(f"# {var}: no public RPC for chain {cid}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "rpc":
        if len(sys.argv) < 3:
            sys.exit("usage: chainlist_mcp.py rpc <chain_id>")
        cmd_rpc(sys.argv[2])
    elif cmd == "list":
        cmd_list()
    elif cmd == "find":
        if len(sys.argv) < 3:
            sys.exit("usage: chainlist_mcp.py find <name>")
        cmd_find(sys.argv[2])
    elif cmd == "env":
        cmd_env()
    else:
        sys.exit(f"unknown command: {cmd}")


if __name__ == "__main__":
    main()
