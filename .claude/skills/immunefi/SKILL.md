---
name: immunefi
description: "Direct Immunefi bug bounty report search. Use to find real-world exploit precedents for a specific query without running a full agent. Activate on: /immunefi, immunefi search, has this been exploited before, show immunefi reports for, real-world exploit examples, search immunefi."
---

# Direct Immunefi Search

Direct search of the Immunefi bug bounty report database. Returns real-world exploit precedents for any vulnerability pattern.

## Phase 1: Parse Query + Vuln Type

Parse the user's command for: `/immunefi [optional-vuln-type] "<query>"`

- `vuln-type` is optional. Valid values: `reentrancy`, `flash-loan`, `oracle-manipulation`, `access-control`, `arithmetic`, `dos`, `logic-error`
- `query` is the natural language search term

If no query is provided, ask: "What vulnerability or pattern should I search Immunefi for? (e.g., 'flash loan governance attack' or 'reentrancy drain withdraw')"

If no vuln-type provided, use `--all` to search across all categories.

## Phase 2: Execute Search

```bash
python tools/immunefi_retriever.py <vuln-type-or---all> "<user query>" --top-k 10
```

## Phase 3: (Skip — no agent in this skill)

Not applicable. Display: "Searching Immunefi directly — no specialist agent spawned."

## Phase 4: (Skip — no KB cross-reference needed)

Not applicable for direct search.

## Phase 5: Display Results

```
Immunefi Search: "<query>" [vuln-type: <type or all>]
Found N matching reports

[1] <title>
    Severity: <severity>  |  Protocol: <protocol>
    <description excerpt (first 150 chars)>
    URL: <url>

[2] <title>
    ...

(up to 10 results)
```

If the immunefi_retriever returns an empty array (network error or no matches):
```
Immunefi retriever returned no results.
Possible reasons: network unavailable, MCP endpoint unreachable, or no matching reports.

Try the Solodit KB instead:
  python tools/retriever.py --all reentrancy "<your query>" --top-k 10

Or try a different query — Immunefi uses natural language search, so rephrase the concept.
```

Display after results:
```
Cross-reference with Solodit KB:
  python tools/retriever.py --all reentrancy "<query>" --top-k 5
  Or: /kb-patterns <vuln-type>
```
