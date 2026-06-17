#!/usr/bin/env python3
"""Stage 1+2 (v2): build scope artifacts from the AUTHORITATIVE README scope list.

The repo README has an explicit `## Scope (contracts)` section. The contest scope is a
SPECIFIC subset of src/ (the Market Making Engine subsystem + 3 keepers + referral +
dex-adapters + 2 utils + ZlpVault + exactly two perpetuals functions), NOT all of src/.
This script encodes that allowlist, verifies every entry exists, classifies the rest of
src/ as out-of-scope, and writes program_scope.json/md, contract_source_manifest.json,
and output/pre_audit_snapshot/MANIFEST.json. Deterministic, read-only on the repo.
"""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path("/home/dummy/clones/audit-watch/smart-contract-auditor")
REPO = PROJECT / "audit_downloads/2025-01-zaros-part-2"
WS = PROJECT / "audits/zaros-2025-01-part-2-eval"
SCOPE = WS / "scope"
SNAP = WS / "output/pre_audit_snapshot"
REPO_URL = "https://github.com/Cyfrin/2025-01-zaros-part-2"
COMMIT = "35deb3e92b2a32cd304bf61d27e6071ef36e446d"
BRANCH = "main"
SOURCE_URL = (SCOPE / "source_url.txt").read_text().strip()
NOW = datetime.now(timezone.utc).isoformat()

# ── AUTHORITATIVE in-scope list (from README ## Scope (contracts)) ──────────────
IN_SCOPE = [
    # external/chainlink keepers
    "src/external/chainlink/keepers/debt-settlement-keeper/DebtSettlementKeeper.sol",
    "src/external/chainlink/keepers/fee-conversion-keeper/FeeConversionKeeper.sol",
    "src/external/chainlink/keepers/usd-token-swap-keeper/UsdTokenSwapKeeper.sol",
    # market-making/branches
    "src/market-making/branches/CreditDelegationBranch.sol",
    "src/market-making/branches/FeeDistributionBranch.sol",
    "src/market-making/branches/MarketMakingEngineConfigurationBranch.sol",
    "src/market-making/branches/StabilityBranch.sol",
    "src/market-making/branches/VaultRouterBranch.sol",
    # market-making/interfaces
    "src/market-making/interfaces/IEngine.sol",
    # market-making/leaves
    "src/market-making/leaves/AssetSwapPath.sol",
    "src/market-making/leaves/Collateral.sol",
    "src/market-making/leaves/CreditDelegation.sol",
    "src/market-making/leaves/DexSwapStrategy.sol",
    "src/market-making/leaves/Distribution.sol",
    "src/market-making/leaves/LiveMarkets.sol",
    "src/market-making/leaves/Market.sol",
    "src/market-making/leaves/MarketMakingEngineConfiguration.sol",
    "src/market-making/leaves/StabilityConfiguration.sol",
    "src/market-making/leaves/Swap.sol",
    "src/market-making/leaves/UsdTokenSwapConfig.sol",
    "src/market-making/leaves/Vault.sol",
    "src/market-making/leaves/WithdrawalRequest.sol",
    # market-making engine root
    "src/market-making/MarketMakingEngine.sol",
    # perpetuals (FUNCTION-LEVEL scope; whole file included, scope noted)
    "src/perpetuals/branches/LiquidationBranch.sol",
    "src/perpetuals/branches/SettlementBranch.sol",
    # referral
    "src/referral/Referral.sol",
    "src/referral/interfaces/IReferral.sol",
    "src/referral/leaves/CustomReferralConfiguration.sol",
    "src/referral/leaves/ReferralConfiguration.sol",
    # utils dex-adapters
    "src/utils/dex-adapters/BaseAdapter.sol",
    "src/utils/dex-adapters/CurveAdapter.sol",
    "src/utils/dex-adapters/UniswapV2Adapter.sol",
    "src/utils/dex-adapters/UniswapV3Adapter.sol",
    # utils interfaces
    "src/utils/interfaces/ICurveSwapRouter.sol",
    "src/utils/interfaces/IDexAdapter.sol",
    "src/utils/interfaces/ISwapAssetConfig.sol",
    "src/utils/interfaces/IUniswapV2Router01.sol",
    "src/utils/interfaces/IUniswapV2Router02.sol",
    "src/utils/interfaces/IUniswapV3RouterInterface.sol",
    "src/utils/interfaces/IUniswapV3SwapCallback.sol",
    # utils
    "src/utils/EngineAccessControl.sol",
    "src/utils/Whitelist.sol",
    # zlp
    "src/zlp/ZlpVault.sol",
]
# function-level scope notes
FUNC_SCOPE = {
    "src/perpetuals/branches/LiquidationBranch.sol": "ONLY liquidateAccounts in scope",
    "src/perpetuals/branches/SettlementBranch.sol": "ONLY _fillOrder in scope",
}

def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

# verify every in-scope file exists
missing = [r for r in IN_SCOPE if not (REPO / r).exists()]
if missing:
    raise SystemExit("MISSING in-scope files:\n  " + "\n  ".join(missing))
in_scope_set = set(IN_SCOPE)

# enumerate all repo .sol
all_sol = sorted(str(p.relative_to(REPO)) for p in REPO.rglob("*.sol") if ".git" not in p.parts)
manifest_files = []
counts = {"in_scope": 0, "src_out": 0, "test": 0, "script": 0, "other": 0}
for rel in all_sol:
    p = REPO / rel
    if rel in in_scope_set:
        inscope, reason = True, "README contest scope" + (f" — {FUNC_SCOPE[rel]}" if rel in FUNC_SCOPE else "")
        counts["in_scope"] += 1
    elif rel.startswith("src/"):
        inscope, reason = False, "Under src/ but NOT in README contest scope list"
        counts["src_out"] += 1
    elif rel.startswith("test/"):
        inscope, reason = False, "Test suite (out of scope)"; counts["test"] += 1
    elif rel.startswith("script/"):
        inscope, reason = False, "Deployment/util scripts (out of scope)"; counts["script"] += 1
    else:
        inscope, reason = False, "Out of scope"; counts["other"] += 1
    manifest_files.append({"path": rel, "sha256": sha256(p), "size": p.stat().st_size,
                            "in_scope": inscope, "reason": reason})

manifest = {
    "generated_at": NOW, "program": "Zaros Part 2", "repo_url": REPO_URL, "commit": COMMIT,
    "branch_or_tag": BRANCH, "local_path": str(REPO),
    "package_manager": "npm/pnpm (package.json) + forge git submodules (lib/)",
    "framework": "Foundry", "solidity_versions": ["0.8.25"],
    "build_command": "make install && forge build", "test_command": "forge test",
    "scope_rule": "in_scope = explicit README ## Scope (contracts) allowlist (43 files; 2 of them function-level)",
    "counts": {"total_sol": len(all_sol), **counts},
    "function_level_scope": FUNC_SCOPE,
    "files": manifest_files,
}
(SCOPE / "contract_source_manifest.json").write_text(json.dumps(manifest, indent=2))

program_scope = {
    "program": "Zaros Part 2", "platform": "CodeHawks", "contest_slug": "2025-01-zaros-part-2",
    "source_url": SOURCE_URL, "repo_url": REPO_URL, "commit": COMMIT, "branch_or_tag": BRANCH,
    "contest_date": "2025-01-20 to 2025-02-06 (CodeHawks)", "sponsor": "Zaros",
    "scope_pages": ["https://codehawks.cyfrin.io/c/2025-01-zaros-part-2",
                    "README.md ## Scope (contracts) — authoritative explicit allowlist"],
    "in_scope_contracts": IN_SCOPE,
    "in_scope_count": counts["in_scope"],
    "function_level_scope": FUNC_SCOPE,
    "out_of_scope_contracts": [
        f"src/** NOT in the README list ({counts['src_out']} files: most of perpetuals/, usd/, tree-proxy/, trading-account-nft/, utils/Constants.sol, non-keeper external/)",
        f"test/** ({counts['test']} files)", f"script/** ({counts['script']} files)",
    ],
    "out_of_scope_summary": counts,
    "docs": ["README.md (scope + actors + known issues)", "https://docs.zaros.fi/",
             "Known issues incl. LightChaser: github.com/Cyfrin/2025-01-zaros-part-2/issues/1 (NOT eligible findings)"],
    "known_bounty_rules": [
        "Pool $70k (H/M $66.5k, Low $3.5k).",
        "Severity: High / Medium / Low.",
        "Answer key = selected-for-report AND validated findings only.",
        "Known issues (README) are out-of-scope for credit.",
        "Assumption: 1 usdToken = usdc = 1 usd. Chainlink verification fees waived. Centralization risk excluded.",
    ],
    "severity_categories": ["High", "Medium", "Low"],
    "compatibilities": {"chains": ["Arbitrum", "Monad"],
                        "tokens": ["ETH","WETH","WEETH","WSTETH","WBTC","USDC","USDT","USDE","SUSDE","ERC721"]},
    "judging_result_page": "https://codehawks.cyfrin.io/c/2025-01-zaros-part-2/results",
    "selected_for_report_page": SOURCE_URL, "validated_findings_page": SOURCE_URL,
    "answer_key_url": SOURCE_URL, "answer_key_access_status": "not_accessed_before_freeze",
    "scope_resolution_note": (
        "Scope is the explicit README allowlist (43 files), NOT all of src/. Perpetuals is out of scope "
        "except LiquidationBranch.liquidateAccounts and SettlementBranch._fillOrder. usd/, tree-proxy/, "
        "trading-account-nft/ are out of scope. This is the Market-Making-Engine-centric 'Part 2' scope."
    ),
    "generated_at": NOW,
}
(SCOPE / "program_scope.json").write_text(json.dumps(program_scope, indent=2))

# pre-audit snapshot
SNAP.mkdir(parents=True, exist_ok=True)
snap = []
def add(label, p):
    if p.exists() and p.is_file():
        st = p.stat()
        snap.append({"label": label, "path": str(p.relative_to(PROJECT)), "sha256": sha256(p),
                     "size": st.st_size, "mtime": datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat()})
for f in ["source_url.txt", "program_scope.json", "program_scope.md", "contract_source_manifest.json"]:
    add("scope", SCOPE / f)
add("eval_plan", WS / "eval_plan.md")
for rel in IN_SCOPE:
    add("contract_src", REPO / rel)
for f in ["foundry.toml","remappings.txt","package.json","package-lock.json","pnpm-lock.yaml",".gitmodules",".env.example","Makefile","slither.config.json"]:
    add("config", REPO / f)
(SNAP / "MANIFEST.json").write_text(json.dumps(
    {"generated_at": NOW, "note": "pre-audit snapshot — repo state frozen before the blind pipeline run",
     "repo_url": REPO_URL, "commit": COMMIT, "file_count": len(snap), "files": snap}, indent=2))

print(f"OK in_scope={counts['in_scope']} src_out={counts['src_out']} test={counts['test']} "
      f"script={counts['script']} total_sol={len(all_sol)} snapshot_files={len(snap)}")
