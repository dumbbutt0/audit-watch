#!/usr/bin/env python3
"""
fetch_rhinofi_sources.py — Download verified Solidity source code for all
9 Rhino.fi in-scope contracts.

Primary source: Sourcify (sourcify.dev) — cross-chain, no API key required.
Fallback: chain-specific block explorer API (Etherscan-compat or zkSync).

Saves to: contracts/rhinofi/<chain>/<ContractName>/   (multi-file)
       or contracts/rhinofi/<chain>/<ContractName>.sol (single-file)
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import requests

# ── .env loader (same pattern as other scripts in this project) ───────────────
_ROOT = Path(__file__).resolve().parent.parent
if (_ROOT / ".env").exists():
    for _line in (_ROOT / ".env").read_text().splitlines():
        if "=" in _line and not _line.startswith("#"):
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip("\"'"))

ETHERSCAN_API_KEY = os.environ.get("ETHERSCAN_API_KEY", "")
OUT_ROOT = _ROOT / "contracts" / "rhinofi"

CONTRACTS = [
    {
        "name": "zkEVMBridge",
        "address": "0x65A4b8A0927c7FD899aed24356BF83810f7b9A3f",
        "chain": "zkevm",
        "chain_id": 1101,
        "explorer": "https://api-zkevm.polygonscan.com/api",
    },
    {
        "name": "OptimismBridge",
        "address": "0x0bCa65bf4b4c8803d2f0B49353ed57CAAF3d66Dc",
        "chain": "optimism",
        "chain_id": 10,
        "explorer": "https://api-optimistic.etherscan.io/api",
    },
    {
        "name": "BSCBridge",
        "address": "0xB80A582fa430645A043bB4f6135321ee01005fEf",
        "chain": "bsc",
        "chain_id": 56,
        "explorer": "https://api.bscscan.com/api",
    },
    {
        "name": "ARBMultiSig",
        "address": "0x15ca1fC728Cce7cd06151C8007e89dEe70260228",
        "chain": "arbitrum",
        "chain_id": 42161,
        "explorer": "https://api.arbiscan.io/api",
    },
    {
        "name": "MATICBridge",
        "address": "0xba4eee20f434bc3908a0b18da496348657133a7e",
        "chain": "polygon",
        "chain_id": 137,
        "explorer": "https://api.polygonscan.com/api",
    },
    {
        "name": "ARBBridge",
        "address": "0x10417734001162ea139e8b044dfe28dbb8b28ad0",
        "chain": "arbitrum",
        "chain_id": 42161,
        "explorer": "https://api.arbiscan.io/api",
    },
    {
        "name": "zkSyncBridge",
        "address": "0x1fa66e2B38d0cC496ec51F81c3e05E6A6708986F",
        "chain": "zksync",
        "chain_id": 324,
        "explorer": None,
    },
    {
        "name": "BSCMultiSig",
        "address": "0x7Af3828c0B061552AF3479806Add982eEf04f0c8",
        "chain": "bsc",
        "chain_id": 56,
        "explorer": "https://api.bscscan.com/api",
    },
    {
        "name": "MATICMultiSig",
        "address": "0x249aAbb1d67A76404Cc1197fa37ADAf358B1E212",
        "chain": "polygon",
        "chain_id": 137,
        "explorer": "https://api.polygonscan.com/api",
    },
]


def _get_json(url: str, params: dict | None = None, timeout: int = 20) -> dict | list | None:
    try:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        print(f"    [warn] GET {url[:70]}… failed: {exc}")
        return None


def _save(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fetch_sourcify(contract: dict) -> tuple[int, bool]:
    """Fetch from Sourcify.dev — returns (files_written, success)."""
    name = contract["name"]
    address = contract["address"]
    chain = contract["chain"]
    chain_id = contract["chain_id"]
    dest = OUT_ROOT / chain / name

    url = f"https://sourcify.dev/server/files/any/{chain_id}/{address}"
    data = _get_json(url)

    if not data or not isinstance(data, dict):
        return 0, False

    files = data.get("files", [])
    if not files:
        return 0, False

    files_written = 0
    for f in files:
        fname = f.get("name", "unknown.sol")
        content = f.get("content", "")
        if content:
            _save(dest / fname, content)
            files_written += 1

    status = data.get("status", "?")
    print(f"    [ok] Sourcify {status}: {files_written} files")
    return files_written, True


def fetch_zksync_explorer(contract: dict) -> tuple[int, bool]:
    """Fetch from zkSync Era block explorer (Etherscan-compat fallback)."""
    name = contract["name"]
    address = contract["address"]
    chain = contract["chain"]
    dest = OUT_ROOT / chain / name

    data = _get_json("https://block-explorer-api.mainnet.zksync.io/api", {
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
    })

    if not data or data.get("status") != "1" or not data.get("result"):
        return 0, False

    result = data["result"][0]
    src = result.get("SourceCode", "")
    contract_name = result.get("ContractName", name)

    if not src or src == "Contract source code not verified":
        return 0, False

    # Handle double-encoded Standard JSON Input
    if src.startswith("{{"):
        try:
            std = json.loads(src[1:-1])
            sources = std.get("sources", {})
            count = 0
            for fpath, fdata in sources.items():
                content = fdata.get("content", "")
                if content:
                    _save(dest / fpath, content)
                    count += 1
            print(f"    [ok] zkSync Etherscan-compat (multi-file): {count} files")
            return count, True
        except json.JSONDecodeError:
            pass

    sol_path = OUT_ROOT / chain / f"{contract_name}.sol"
    _save(sol_path, src)
    print(f"    [ok] zkSync Etherscan-compat (single-file): {contract_name}.sol")
    return 1, True


def fetch_zkevm_blockscout(contract: dict) -> tuple[int, bool]:
    """Fetch zkEVM contract via Blockscout API (alternative to Polygonscan zkEVM)."""
    name = contract["name"]
    address = contract["address"]
    dest = OUT_ROOT / "zkevm" / name

    # Try Blockscout-based zkEVM explorer
    blockscout_url = f"https://zkevm.blockscout.com/api/v2/smart-contracts/{address}"
    data = _get_json(blockscout_url)

    if not data or not isinstance(data, dict):
        return 0, False

    source = data.get("source_code") or data.get("sourcify_repo_url")
    if not source:
        # Try getting files from the additional_sources field
        additional = data.get("additional_sources", [])
        if additional:
            count = 0
            for item in additional:
                fname = item.get("file_path") or item.get("name", f"src_{count}.sol")
                content = item.get("source_code", "")
                if content:
                    _save(dest / fname, content)
                    count += 1
            if count:
                print(f"    [ok] zkEVM Blockscout (multi-file): {count} files")
                return count, True
        return 0, False

    # Single source_code field
    fname = data.get("file_path") or f"{name}.sol"
    _save(dest / fname, source)
    print(f"    [ok] zkEVM Blockscout (single-file): {fname}")
    return 1, True


def main() -> None:
    print("=" * 60)
    print("Rhino.fi Contract Source Fetcher")
    print(f"Output root: {OUT_ROOT}")
    print("Primary: Sourcify.dev | Fallback: chain-specific explorer")
    print("=" * 60)

    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    total_files = 0
    total_warnings = 0
    results = []

    for contract in CONTRACTS:
        name = contract["name"]
        chain = contract["chain"]
        address = contract["address"]
        print(f"\n  [{chain}] {name} ({address[:10]}…)")

        files_written = 0
        success = False

        # 1. Try Sourcify first (works for most chains, no key needed)
        if contract["chain_id"]:
            files_written, success = fetch_sourcify(contract)

        # 2. Fallback: zkSync Era block explorer
        if not success and chain == "zksync":
            files_written, success = fetch_zksync_explorer(contract)

        # 3. Fallback: Blockscout for zkEVM
        if not success and chain == "zkevm":
            files_written, success = fetch_zkevm_blockscout(contract)

        # 4. Record failure
        if not success:
            print(f"    [warn] Could not fetch source for {name} on {chain}")
            placeholder = OUT_ROOT / chain / f"{name}_UNVERIFIED.txt"
            _save(placeholder, f"address={address}\nchain={chain}\nstatus=source_unavailable\n")
            total_warnings += 1

        total_files += files_written
        results.append((name, chain, files_written, success))
        time.sleep(0.3)

    print("\n" + "=" * 60)
    print(f"Done: {len(CONTRACTS)} contracts processed")
    print(f"      {total_files} source files written")
    if total_warnings:
        print(f"      {total_warnings} warnings")
    print()
    for name, chain, count, ok in results:
        marker = "✓" if ok else "✗"
        print(f"  {marker} [{chain}] {name}: {count} files")
    print("=" * 60)

    if total_warnings:
        sys.exit(1)


if __name__ == "__main__":
    main()
