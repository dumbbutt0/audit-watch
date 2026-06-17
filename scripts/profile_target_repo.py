#!/usr/bin/env python3
"""
profile_target_repo.py — Detect language, framework, test structure of an audit target repo.

Usage:
    python scripts/profile_target_repo.py --repo contracts/2026-04-k2 --out data/poc_queue/repo_profile.json
    python scripts/profile_target_repo.py --repo contracts/2026-04-k2  # prints to stdout
"""

import argparse
import json
import re
import sys
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# Language / framework detection
# ─────────────────────────────────────────────────────────────────────────────

def detect_language(root: Path) -> str:
    # Move (Sui/Aptos): Move.toml is unambiguous; check before Cargo.toml since some Move repos vendor Rust tools.
    if (root / "Move.toml").exists() or list(root.rglob("Move.toml"))[:1]:
        return "move"
    if (root / "Cargo.toml").exists():
        return "rust"
    if (root / "foundry.toml").exists() or list(root.rglob("*.sol"))[:1]:
        return "solidity"
    if (root / "Anchor.toml").exists():
        return "rust"  # Anchor is Rust
    if (root / "package.json").exists():
        content = (root / "package.json").read_text(errors="ignore")
        return "typescript" if '"typescript"' in content or '"ts-node"' in content else "javascript"
    if list(root.rglob("*.py"))[:1]:
        return "python"
    return "unknown"


def detect_framework(root: Path, language: str) -> str:
    if language == "rust":
        # Check all Cargo.toml files for soroban-sdk
        for cargo in root.rglob("Cargo.toml"):
            try:
                content = cargo.read_text(errors="ignore")
                if "soroban-sdk" in content:
                    return "soroban"
                if "anchor-lang" in content:
                    return "anchor"
                if "cosmwasm-std" in content:
                    return "cosmwasm"
            except Exception:
                pass
    if language == "solidity":
        if (root / "foundry.toml").exists():
            return "foundry"
        for f in ["hardhat.config.js", "hardhat.config.ts"]:
            if (root / f).exists():
                return "hardhat"
        if (root / "truffle-config.js").exists():
            return "truffle"
    if language == "move":
        # Distinguish Sui from Aptos by the framework dependency / address conventions.
        for mt in ([root / "Move.toml"] + list(root.rglob("Move.toml")))[:6]:
            try:
                c = mt.read_text(errors="ignore").lower()
                if "sui" in c or "0x2" in c:
                    return "sui"
                if "aptos" in c:
                    return "aptos"
            except Exception:
                pass
        return "sui"
    return "other"


# ─────────────────────────────────────────────────────────────────────────────
# Test discovery
# ─────────────────────────────────────────────────────────────────────────────

def find_test_dirs(root: Path, language: str, framework: str) -> list[str]:
    dirs: set[str] = set()

    if language == "rust":
        # Dedicated test crates (Cargo.toml in a tests/ directory)
        for cargo in root.rglob("Cargo.toml"):
            try:
                content = cargo.read_text(errors="ignore")
                if "#[test]" in content or "dev-dependencies" in content:
                    dirs.add(str(cargo.parent.relative_to(root)))
            except Exception:
                pass
        # Directories named test, tests, or containing *_test.rs files
        for rs_file in root.rglob("*_test.rs"):
            dirs.add(str(rs_file.parent.relative_to(root)))
        for test_dir in root.rglob("tests"):
            if test_dir.is_dir():
                dirs.add(str(test_dir.relative_to(root)))

    elif framework == "foundry":
        for test_dir in root.rglob("test"):
            if test_dir.is_dir() and list(test_dir.glob("*.sol")):
                dirs.add(str(test_dir.relative_to(root)))
        for sol in root.rglob("*.t.sol"):
            dirs.add(str(sol.parent.relative_to(root)))

    return sorted(dirs)


def find_helper_files(root: Path, test_dirs: list[str]) -> list[str]:
    helpers: list[str] = []
    helper_patterns = [
        "*mock*", "*helper*", "*fixture*", "*testutils*", "*testutil*",
        "*setup*", "*util*", "*common*",
    ]
    search_roots = [root / d for d in test_dirs] + [root]

    seen: set[str] = set()
    for search_root in search_roots:
        if not search_root.exists():
            continue
        for pattern in helper_patterns:
            for f in search_root.rglob(pattern):
                rel = str(f.relative_to(root))
                if rel not in seen and f.is_file():
                    seen.add(rel)
                    helpers.append(rel)

    return sorted(helpers)[:20]


# ─────────────────────────────────────────────────────────────────────────────
# Contract discovery
# ─────────────────────────────────────────────────────────────────────────────

def find_contracts(root: Path, language: str) -> list[str]:
    names: list[str] = []

    if language == "rust":
        for cargo in root.rglob("Cargo.toml"):
            # Skip workspace roots and test crates
            try:
                text = cargo.read_text(errors="ignore")
                if "[workspace]" in text:
                    continue
                m = re.search(r'\[package\][^\[]*name\s*=\s*"([^"]+)"', text, re.DOTALL)
                if m:
                    pkg_name = m.group(1)
                    # Skip test packages
                    if any(kw in pkg_name for kw in ["test", "fuzz", "bench"]):
                        continue
                    names.append(pkg_name)
            except Exception:
                pass

    elif language == "solidity":
        for sol in root.rglob("*.sol"):
            # Skip test and interface files
            if any(kw in sol.name.lower() for kw in ["test", "mock", "interface", "i_"]):
                continue
            m = re.search(r'contract\s+(\w+)', sol.read_text(errors="ignore"))
            if m:
                names.append(m.group(1))

    return sorted(set(names))


# ─────────────────────────────────────────────────────────────────────────────
# Test command
# ─────────────────────────────────────────────────────────────────────────────

def find_test_command(root: Path, language: str, framework: str) -> str:
    if language == "rust" and framework == "soroban":
        # Look for a test workspace package
        for cargo in root.rglob("Cargo.toml"):
            try:
                text = cargo.read_text(errors="ignore")
                m = re.search(r'\[package\][^\[]*name\s*=\s*"([^"]+)"', text, re.DOTALL)
                if m and "unit-test" in m.group(1):
                    return f"cargo test -p {m.group(1)}"
            except Exception:
                pass
        return "cargo test"
    if framework == "foundry":
        return "forge test"
    if framework == "anchor":
        return "anchor test"
    if framework == "hardhat":
        return "npx hardhat test"
    if language == "rust":
        return "cargo test"
    return "make test"


# ─────────────────────────────────────────────────────────────────────────────
# Build command detection
# ─────────────────────────────────────────────────────────────────────────────

def find_build_command(root: Path, framework: str) -> str:
    if framework == "soroban":
        if (root / "build.sh").exists():
            return "bash build.sh"
        return "stellar contract build"
    if framework == "foundry":
        return "forge build"
    if framework == "anchor":
        return "anchor build"
    return "cargo build"


# ─────────────────────────────────────────────────────────────────────────────
# Workspace packages (for import paths)
# ─────────────────────────────────────────────────────────────────────────────

def find_workspace_packages(root: Path) -> dict[str, str]:
    """Map package-name → relative path for workspace members."""
    packages: dict[str, str] = {}
    root_cargo = root / "Cargo.toml"
    if not root_cargo.exists():
        return packages
    try:
        text = root_cargo.read_text(errors="ignore")
        members = re.findall(r'"([^"]+)"', text[text.find("[workspace]"):] if "[workspace]" in text else "")
        for member in members:
            member_cargo = root / member / "Cargo.toml"
            if member_cargo.exists():
                m = re.search(r'name\s*=\s*"([^"]+)"', member_cargo.read_text(errors="ignore"))
                if m:
                    packages[m.group(1)] = member
    except Exception:
        pass
    return packages


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def profile_repo(repo_path: Path) -> dict:
    root = repo_path.resolve()
    if not root.exists():
        raise SystemExit(f"Repo path does not exist: {root}")

    language  = detect_language(root)
    framework = detect_framework(root, language)
    test_dirs = find_test_dirs(root, language, framework)
    helpers   = find_helper_files(root, test_dirs)
    contracts = find_contracts(root, language)
    test_cmd  = find_test_command(root, language, framework)
    build_cmd = find_build_command(root, framework)
    packages  = find_workspace_packages(root)

    # Detect if tests require pre-built WASMs (Soroban integration tests)
    needs_build = False
    for d in test_dirs:
        src_dir = root / d / "src"
        if src_dir.exists():
            for rs in src_dir.glob("*.rs"):
                if "contractimport!" in rs.read_text(errors="ignore"):
                    needs_build = True
                    break

    return {
        "repo_path":    str(root),
        "language":     language,
        "framework":    framework,
        "test_command": test_cmd,
        "build_command": build_cmd,
        "needs_build_before_test": needs_build,
        "test_dirs":    test_dirs,
        "helper_files": helpers,
        "contracts":    contracts,
        "workspace_packages": packages,
    }


def main():
    parser = argparse.ArgumentParser(description="Profile a smart contract repository")
    parser.add_argument("--repo", required=True, help="Path to the repository root")
    parser.add_argument("--out",  default=None,  help="Output JSON file path (default: stdout)")
    args = parser.parse_args()

    profile = profile_repo(Path(args.repo))

    out_json = json.dumps(profile, indent=2)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(out_json)
        print(f"Profile written to {args.out}")
        # Also print summary
        print(f"  Language:  {profile['language']}")
        print(f"  Framework: {profile['framework']}")
        print(f"  Contracts: {len(profile['contracts'])}")
        print(f"  Test dirs: {len(profile['test_dirs'])}")
        print(f"  Needs build: {profile['needs_build_before_test']}")
    else:
        print(out_json)

    return 0


if __name__ == "__main__":
    sys.exit(main())
