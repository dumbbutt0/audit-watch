---
name: supply-chain
description: "Check the build dependency chain for supply chain compromise vectors: ffi=true in foundry.toml, unpinned forge dependencies, suspicious npm packages, build script remote code execution, unsigned GitHub Actions. Implements the Jason Hadex 'patient zero' threat model. Activate when user says: /supply-chain, check dependencies, audit build chain, check imports, patient zero check, are our deps safe."
---

# Supply Chain Security Check

Implements the Jason Hadex "patient zero" threat model: before auditing
contract logic, verify the build chain itself has not been compromised.

Threat model: a threat actor targets a developer's machine or a shared
dependency to inject malicious code before the protocol ships. The injected
code passes code review because it was inserted after the review was complete,
and it passes audits because auditors focus on the contract source, not the
build environment.

## Instructions

### 1. Collect build files

Read each of the following files if they exist in the project root or audit scope:

```bash
cat foundry.toml 2>/dev/null
cat hardhat.config.js 2>/dev/null || cat hardhat.config.ts 2>/dev/null
cat package.json 2>/dev/null
cat .gitmodules 2>/dev/null
cat Makefile 2>/dev/null || cat justfile 2>/dev/null
find .github/workflows -name "*.yml" 2>/dev/null | head -10
```

Also extract all Solidity import statements:
```bash
grep -r "^import" contracts/ src/ --include="*.sol" 2>/dev/null | head -100
```

### 2. Spawn supply_chain_check agent

Spawn `agents/supply_chain_check.md` as a Task. Provide all collected file contents
as context. The agent performs five checks:
1. Solidity import path analysis (non-standard, raw GitHub URLs, test-in-production)
2. foundry.toml: `ffi=true`, unpinned deps, unknown registry URLs
3. npm: `file:`, `git+https:` specifiers, custom registries, typosquats
4. Build scripts: `curl | bash`, `eval`, `wget` patterns
5. Git submodules: unknown URL sources, paths outside `lib/`

### 3. Validate output

```bash
python scripts/validate_agent_output.py output/findings_supply_chain.json
```

### 4. Display results

Read `output/findings_supply_chain.json` and print:

**If issues found:**
```
Supply chain check: N issues found ⚠️

[SC-001]  ffi=true in foundry.toml                        Critical
  Build scripts can execute arbitrary shell commands during compilation.
  Fix: Remove ffi=true unless strictly required. If required, document
       why and audit all Makefile/shell scripts that leverage it.
  File: foundry.toml

[SC-002]  @openzeppelin pinned to branch "main"            High
  Unpinned branch dependency — any push by the dependency author changes
  what gets compiled, breaking reproducibility and introducing untrusted code.
  Fix: Pin to a specific commit hash: rev = "8f4b7f84864484a..."
  File: foundry.toml

[SC-003]  GitHub Action uses mutable tag @v3               High
  Tag references can be moved by the action author. Pin to commit SHA.
  Fix: uses: actions/checkout@8f4b7f84864484a7bf31766abe9204da3cbe65b3
  File: .github/workflows/ci.yml

Clean checks: ✅ npm packages  ✅ import paths  ✅ build scripts  ✅ submodules
```

**If clean:**
```
Supply chain: clean ✅

All dependencies pinned, imports verified, build scripts safe.
  ✅ foundry.toml: all deps pinned to commit hashes
  ✅ npm packages: no file:/git+https: specifiers, no typosquats
  ✅ import paths: all from standard trusted sources
  ✅ build scripts: no remote code execution patterns
  ✅ GitHub Actions: all pinned to SHA
  ✅ Git submodules: all from known sources in lib/

No supply chain action required. Proceed with contract audit.
```

### 5. Note on human review

All SC-* findings are automatically flagged `human_review_required: true`.
Supply chain issues require human judgment about developer intent and actual risk.
A `ffi=true` setting may be intentional and documented — the finding flags it;
the human auditor decides whether it is acceptable.
