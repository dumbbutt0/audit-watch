# Skills (Claude Code Slash Commands)

Skills are Claude Code slash commands that execute structured audit sub-tasks from within a conversation. They are defined in `.claude/skills/<name>/SKILL.md` and invoked using `/skill-name` in a Claude Code session.

Skills are used for quick, targeted analysis without running the full pipeline. They are also how the phone control mode commands work (see `config/phone_commands.md`).

---

## Invocation

In a Claude Code session, type:
```
/reentrancy
/surface
/flash-loan
/ite-audit
```

Or as part of a message:
```
Check this for reentrancy: contracts/Vault.sol
Run /surface on the contracts/ directory
```

---

## Skill Reference

### /access-control

**Trigger:** `/access-control`, missing auth, privilege escalation, unauthorized call, signature replay, ecrecover bypass, tx.origin
**Purpose:** Targeted access control scan — missing guards, incorrect role assignment, two-step ownership, signature-based auth bypass, upgradeable contract auth gaps
**What it does:** Reads `output/attack_surface.json` to find admin-class functions and unguarded user functions first. Queries KB for signature replay, ecrecover bypass, missing chainId, and privilege escalation patterns. Produces a structured access control finding summary.

---

### /arithmetic

**Trigger:** `/arithmetic`, overflow check, precision loss, rounding error, integer cast, WAD math
**Purpose:** Arithmetic vulnerability scan — overflow, underflow, precision loss, rounding, unsafe casts
**What it does:** Focuses on mathematical operations with user-controlled inputs. Checks unchecked blocks in Solidity >=0.8, WAD/RAY unit mismatches, and truncation-before-multiplication patterns.

---

### /behavioral-state

**Trigger:** `/behavioral-state`, BSA, NatSpec mismatch, comment says but code does, semantic divergence
**Purpose:** Runs the Behavioral State Analysis agent to find semantic divergence between NatSpec/comments and actual code behavior
**What it does:** Pulls documented-but-not-enforced patterns from KB. Compares `@notice` / `@dev` documentation against actual code execution paths.

---

### /confirm

**Trigger:** `/confirm`, confirm findings, multi-pass check, validate High findings, `/confirm <ID>`
**Purpose:** Run multi-pass LLM confirmation for High/Critical findings to handle non-determinism
**What it does:** Runs `scripts/multi_pass_confirm.py` for the specified finding ID or all High/Critical findings. High = 3 passes, Critical = 5 passes. Reports confirmation_score and flags findings below 0.6 threshold for human review.

---

### /cross-chain

**Trigger:** `/cross-chain`, bridge, cross-chain, message replay, relayer, rollup, nonce reorder
**Purpose:** Cross-chain bridge specialist analysis — only activates when bridge/layer2/relayer patterns are detected
**What it does:** Pulls message replay, decimal mismatch mint, nonce reordering, and relayer griefing patterns from Solodit and Immunefi. Checks `output/findings_protocol_context.json` before activating.

---

### /dos

**Trigger:** `/dos`, denial of service, gas griefing, fund lock, unbounded loop
**Purpose:** DoS vulnerability scan — gas griefing, fund lock, unbounded loops, forced revert
**What it does:** Focuses on patterns that can permanently or temporarily block contract function.

---

### /economic-attack

**Trigger:** `/economic-attack`, MEV, liquidation arb, governance manipulation, yield drain
**Purpose:** Economic and game-theoretic attack analysis
**What it does:** Analyzes incentive design for attack opportunities that rational actors will exploit. Reads oracle and flash loan findings for compound attack surfaces.

---

### /erc4626

**Trigger:** `/erc4626`, vault inflation, first depositor, rounding direction, totalAssets
**Purpose:** ERC-4626 vault specialist — inflation attack, wrong rounding direction, totalAssets flash manipulation
**What it does:** Only activates when ERC-4626 interface is detected. Pulls inflation attack, rounding direction, and totalAssets flash manipulation patterns from Solodit and Immunefi.

---

### /flash-loan

**Trigger:** `/flash-loan`, flash loan, balanceOf accounting, governance vote manipulation, sandwich attack
**Purpose:** Flash loan attack surface analysis
**What it does:** Pulls balance-based accounting inflation, governance flash vote, price manipulation + liquidation, and sandwich attack patterns. Checks for `minAmountOut == 0` patterns.

---

### /human-queue

**Trigger:** `/human-queue`, what needs human review, show human queue, which findings need me
**Purpose:** Show findings requiring human auditor validation before submission
**What it does:** Reads `data/triage/human_review_queue.jsonl`, sorts by `human_review_score`, displays the 10% of findings in the Hadex 90/10 split that AI cannot reliably confirm. Shows each finding's routing reason and recommended human action.

---

### /immunefi

**Trigger:** `/immunefi`, immunefi search, has this been exploited before, show immunefi reports for
**Purpose:** Direct Immunefi bug bounty report search for real-world exploit precedents
**What it does:** Calls `tools/immunefi_retriever.py` with the query and optional vuln-type. Returns top-k matching bug bounty reports with descriptions and URLs. Non-fatal if MCP endpoint is unreachable.

---

### /ite-audit

**Trigger:** `/ite-audit`, run ite audit, hadex audit, full audit with ITE, start the methodology pipeline
**Purpose:** Full Jason Hadex ITE audit pipeline from sandbox check through human review routing
**What it does:** Runs the full pipeline in order: sandbox check → attacker mindset map → static analysis + supply chain → parallel specialist agents → compound synthesis → multi-pass confirmation → triage → human-AI routing. Implements the ITE (Intent/Technique/Evasion) framework at every stage.

---

### /kb-patterns

**Trigger:** `/kb-patterns`, show KB patterns, what patterns exist for X, solodit patterns
**Purpose:** Surface real-world attack patterns from the Solodit/Immunefi KB without running an agent
**What it does:** Calls `tools/retriever.py` with the specified vuln-type. Returns top patterns from past audits. Useful for intelligence gathering before deciding which specialist agent to invoke.

---

### /logic

**Trigger:** `/logic`, business logic error, invariant violation, state machine bug
**Purpose:** Business logic vulnerability scan
**What it does:** Reads protocol context to understand what the protocol is supposed to do, then finds where the code deviates. Checks for broken invariants and incorrect state machine transitions.

---

### /oracle

**Trigger:** `/oracle`, price oracle, TWAP manipulation, Chainlink staleness, spot price
**Purpose:** Oracle manipulation vulnerability analysis
**What it does:** Pulls spot price manipulation, TWAP weakness, oracle staleness, and missing heartbeat patterns. Cross-references with flash loan findings.

---

### /reentrancy

**Trigger:** `/reentrancy`, reentrancy check, CEI violations, nonReentrant missing, ERC-777 hooks, read-only reentrancy
**Purpose:** Reentrancy vulnerability scan — CEI violations, ERC-777, read-only reentrancy, cross-function reentrancy
**What it does:** Pulls real-world CEI violation, ERC-777 hook, and read-only reentrancy patterns from Solodit and Immunefi. Checks Curve virtual price patterns for read-only reentrancy.

---

### /semantic-guard

**Trigger:** `/semantic-guard`, modifier asymmetry, guard inconsistency, role granting unprotected, whenNotPaused missing
**Purpose:** Semantic guard analysis — asymmetric and incomplete access control across function groups
**What it does:** Pulls modifier shadowing, role-granting unguarded, and whenNotPaused missing patterns from KB. Audits the symmetry of the entire guard system, not just individual functions.

---

### /snapshot

**Trigger:** `/snapshot`, snapshot bug, voting power, balanceOf not checkpoint, governance manipulation
**Purpose:** Snapshot and checkpoint vulnerability analysis
**What it does:** Pulls flash loan vote, buy-before-snapshot, delegation front-running, and missing epoch snapshot patterns. Covers ERC20Votes, ERC20Snapshot, governance checkpointing.

---

### /supply-chain

**Trigger:** `/supply-chain`, check dependencies, audit build chain, check imports, patient zero check
**Purpose:** Supply chain security check — ffi=true, unpinned forge deps, suspicious npm packages, build script RCE, unsigned GitHub Actions
**What it does:** Implements the Jason Hadex "patient zero" threat model. Reads foundry.toml, package.json, .gitmodules, Makefile, and GitHub Actions workflows. Returns `output/findings_supply_chain.json` with SC- prefix findings.

---

### /surface

**Trigger:** `/surface`, map attack surface, ITE analysis, show attack surface, where should I look first
**Purpose:** Map attack surface using ITE framework before specialist agents run
**What it does:** Spawns the `attacker_mindset` agent (Step 0.25). Produces `output/attack_surface.json` with all functions scored 1–5 by attacker relevance, plus per-agent priority hints. If `attack_surface.json` already exists, displays the current map.

---

### /token-integration

**Trigger:** `/token-integration`, fee-on-transfer, rebasing, ERC-777, blacklist, decimals
**Purpose:** Non-standard ERC-20 token integration vulnerability analysis
**What it does:** Finds bugs where protocol logic is correct but breaks with non-standard tokens. Covers fee-on-transfer, rebasing, ERC-777 callbacks, blacklists, and decimal mismatches.

---

### /transient-storage

**Trigger:** `/transient-storage`, TSTORE, TLOAD, EIP-1153, ReentrancyGuardTransient, transient reentrancy
**Purpose:** EIP-1153 transient storage vulnerability analysis — only activates when TSTORE/TLOAD opcodes are detected
**What it does:** Pulls cross-function reentrancy bypass, delegatecall namespace collision, and flash loan unlock patterns from Solodit and Immunefi.

---

### /upgrade-storage

**Trigger:** `/upgrade-storage`, proxy, UUPS, storage collision, implementation upgrade
**Purpose:** Proxy and upgradeable contract vulnerability analysis
**What it does:** Checks storage slot collisions, initialization gaps, authorization on upgrade paths, and storage layout drift. Only activates when proxy patterns are detected.
