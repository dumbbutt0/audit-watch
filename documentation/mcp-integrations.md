# MCP Integrations

Audit-Watch uses MCP (Model Context Protocol) servers to provide external context to agents. All MCP tools are **non-fatal**: if the API key is absent or the endpoint is unreachable, the tool returns `{}` or `[]` and the pipeline continues without interruption.

MCP servers are registered in `.mcp.json` at the project root.

> **Important:** MCPs are context providers, not proof engines. All MCP data must be verified through code, tests, or independent on-chain reads before use in a finding. A TVL figure from Dune or a bytecode match from QuickNode may be stale, cached, or based on an incorrect subgraph. Never claim a finding is Critical based solely on MCP-provided data.

---

## Registered MCP Servers (.mcp.json)

```json
{
  "mcpServers": {
    "onchain-context":              "tools/onchain_mcp_server.py",
    "kb-search":                    "tools/kb_mcp_server.py",
    "immunefi-audit-competitions":  "https://reports.immunefi.com/~gitbook/mcp"
  }
}
```

---

## kb_mcp_server.py — Local Knowledge Base

**File:** `tools/kb_mcp_server.py`
**Purpose:** Serves the local Chroma vector database of Solodit/Code4rena/Sherlock/Immunefi findings as an MCP tool. Agents query this to find historical precedent for their hypotheses.
**Environment variable:** None required (local file access)
**Failure behavior:** Returns `[]` if Chroma DB is not built. Build with `python scripts/solodit_scraper.py`.

Agents call `tools/retriever.py` (CLI subprocess) rather than the MCP directly. The MCP server allows Claude Code's tool-use API to call the KB from within agent reasoning.

```bash
# Build the KB (required once):
python scripts/solodit_scraper.py

# Direct query:
python tools/retriever.py reentrancy "withdraw external call before state update"
```

---

## immunefi_retriever.py — Immunefi Bug Bounty Reports

**File:** `tools/immunefi_retriever.py`
**MCP endpoint:** `https://reports.immunefi.com/~gitbook/mcp`
**Registered as:** `immunefi-audit-competitions` in `.mcp.json`
**Purpose:** Queries the Immunefi GitBook for real-world bug bounty reports matching a vulnerability type and query. Returns actual exploit descriptions and report URLs.
**Environment variable:** None (public endpoint, no key required)
**Failure behavior:** Returns `[]` on network error or MCP timeout. Non-fatal.

```bash
# Direct CLI usage:
python tools/immunefi_retriever.py reentrancy "withdraw before state update"
python tools/immunefi_retriever.py oracle-manipulation "chainlink staleness" --top-k 3
python tools/immunefi_retriever.py --all "flash loan governance attack"
```

Output format: JSON array of `{title, severity, vuln_type, protocol, source, description, url}` objects.

All specialist agents call `immunefi_retriever.py` alongside `retriever.py`. Immunefi bounty reports often contain exploit PoCs that sharpen severity calibration.

---

## onchain_mcp_server.py — General On-Chain Data

**File:** `tools/onchain_mcp_server.py`
**Registered as:** `onchain-context` in `.mcp.json`
**Purpose:** General on-chain data aggregator wrapping QuickNode, Etherscan, Dune, and The Graph. Used by agents working on deployed contracts with known addresses.
**Environment variables (all optional):**
- `QUICKNODE_ENDPOINT_ETHEREUM`
- `QUICKNODE_ENDPOINT_ARBITRUM`
- `QUICKNODE_ENDPOINT_BASE`
- `QUICKNODE_ENDPOINT_POLYGON`
- `ETHERSCAN_API_KEY`
- `DUNE_API_KEY`
- `GRAPH_API_KEY`

**Failure behavior:** Returns `{}` if all keys absent. Each sub-tool degrades independently.

---

## quicknode_mcp.py — Bytecode Verification

**File:** `tools/quicknode_mcp.py`
**Purpose:** Pulls live EVM data for deployed in-scope contracts — bytecode, transaction history, tx simulation, raw storage slots. Used to verify that deployed bytecode matches the audited source.
**Environment variable:** `QUICKNODE_ENDPOINT_<CHAIN>` (separate per chain: ETHEREUM, ARBITRUM, BASE, POLYGON)
**Failure behavior:** Prints warning to stderr, returns `None` / empty result. Pipeline continues.

```bash
# Verify deployed code matches source:
python tools/quicknode_mcp.py bytecode 0xABCD... ethereum

# Transaction history:
python tools/quicknode_mcp.py history 0xABCD... ethereum --limit 50

# Simulate a transaction:
python tools/quicknode_mcp.py simulate --from 0x... --to 0x... --data 0x... --chain ethereum

# Raw storage slot:
python tools/quicknode_mcp.py storage 0xABCD... ethereum --slots 0,1,2
```

---

## dune_mcp.py — Protocol TVL and Volume

**File:** `tools/dune_mcp.py`
**Purpose:** Queries Dune Analytics for live protocol health data — TVL trends, trading volume, top positions, slippage. Used to ground economic threat modeling in real numbers rather than assumptions.
**Environment variable:** `DUNE_API_KEY` (https://dune.com/settings/api)
**Failure behavior:** Returns `{}` if `DUNE_API_KEY` absent. Non-fatal.

```bash
python tools/dune_mcp.py tvl <protocol_slug>
python tools/dune_mcp.py volume <protocol_slug> --days 7
python tools/dune_mcp.py top <protocol_slug> --limit 10
python tools/dune_mcp.py slippage <token_pair> <dex>
```

---

## graph_mcp.py — Historical On-Chain State

**File:** `tools/graph_mcp.py`
**Purpose:** Queries The Graph Protocol subgraphs for historical protocol state. Used to verify that invariants hold over real historical data and detect anomalies.
**Environment variable:** `GRAPH_API_KEY` (optional — public subgraphs work without it)
**Failure behavior:** Returns `{}` on request failure. Non-fatal.

```bash
python tools/graph_mcp.py query  <subgraph_url> "<graphql_query>"
python tools/graph_mcp.py history <subgraph_url> <entity> <field>
python tools/graph_mcp.py anomaly <subgraph_url> <entity> <field> --threshold 0.1
python tools/graph_mcp.py known  <protocol_slug>   # pre-configured slugs: enzyme, uniswap-v3, aave-v3, compound-v3, curve
```

---

## chainlist_mcp.py — Chain Metadata

**File:** `tools/chainlist_mcp.py`
**Purpose:** Chain ID, native currency, RPC endpoint metadata. Used by cross-chain agents to look up chain parameters when analyzing bridge contracts.
**Environment variable:** None
**Failure behavior:** Non-fatal.

---

## Security Notes

The `config/zero_trust_policy.json` defines a `network_allowlist` for all outbound MCP requests. Before registering any new MCP server:

1. Verify the server URL is in the allowlist
2. Do not register MCP servers that accept arbitrary user-supplied GraphQL/SQL without sanitization
3. Treat all MCP server responses as untrusted input — validate schema before passing to agents
4. MCP server responses must not be used as the sole basis for severity decisions

Allowlisted domains include: `api.immunefi.com`, `reports.immunefi.com`, `api.dune.com`, `api.thegraph.com`, `api.etherscan.io`, `api.arbiscan.io`, `api.basescan.org`, `api.polygonscan.com`, `api.llama.fi`, `api.github.com`, `raw.githubusercontent.com`, `api.glide.r.xyz`.
