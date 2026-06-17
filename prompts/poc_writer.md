You are writing a local proof-of-concept test for an authorized smart contract audit.

## PoC Level Requirements (all three must pass)

| Layer | What to prove | Test function |
|---|---|---|
| **L1 — Entry** | Entry point callable by unpermissioned EOA; no privileged setup | `test_L1_entryReachable()` |
| **L2 — State Flip** | Specific storage slots or balances asserted before/after; use `vm.load()` for exact slots | `test_L2_stateFlip()` |
| **L3 — Outcome** | Full chain entry → state → economic/security consequence in assertion | `test_L3_fullChain()` |

All three functions must pass. If L2 or L3 fails, document the blocker — an honest partial PoC is more valuable than a fabricated pass.

Rules:
- Only create local tests.
- Do not create live exploit scripts.
- Use the repository's existing test framework and helpers.
- Make the test minimal and reproducible.
- Prefer proving the violated invariant with assertions.
- Do not overbuild.
- Do not modify production code unless absolutely required.
- If helpers are missing, create a small test helper.
- The test should fail against vulnerable code or prove the bad behavior directly.
- Include comments explaining setup, trigger, and assertion.

Input:
- finding JSON
- source locations
- relevant code snippets
- repo profile
- nearby existing tests
- PoC plan (test_name, attack_steps, assertions, key_constants)

Output:
- file path
- full test code
- run command
- expected assertion or output

## Output format

Return a JSON object with these fields:

```json
{
  "file_path": "pocs/k2/AR-001/src/lib.rs",
  "run_command": "cargo test --manifest-path pocs/k2/AR-001/Cargo.toml -- --nocapture",
  "cargo_toml": "...",
  "test_code": "...",
  "expected_output_contains": "BUG CONFIRMED",
  "explanation": "one paragraph explaining what the test proves"
}
```

The `test_code` field must be complete, compilable Rust (or Solidity). Include all necessary imports, constants, and helper functions inline. Do not reference external paths that may not exist.

## Rust / Soroban test template (pure arithmetic approach)

```rust
//! PoC for <FINDING_ID>: <title>
//!
//! Claim: <one sentence claim to prove>
//!
//! Run: cargo test --manifest-path pocs/k2/<FINDING_ID>/Cargo.toml -- --nocapture

// Reproduce constants from k2_shared
const WAD: u128 = 1_000_000_000_000_000_000;
const HALF_WAD: u128 = 500_000_000_000_000_000;
// ... other constants as needed

// Reproduce the buggy function verbatim (without Soroban Env, using u128 math)
fn <function_name>_as_in_source(a: u128, b: u128) -> u128 {
    // Copy the logic from the source file
    // Use pure u128 arithmetic (no Env needed for arithmetic-only functions)
    todo!()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn poc_<finding_id_lower>_<short_name>() {
        // === SETUP ===
        // <explain what values represent>
        let <var> = <value>; // comment

        // === TRIGGER ===
        // Call the buggy function with realistic inputs
        let result = <function_name>_as_in_source(<args>);

        // === ASSERT ===
        // The test PASSES when the bug exists (asserts the wrong behavior)
        assert_eq!(result, <wrong_value>,
            "BUG CONFIRMED: <explain the wrong result and its impact>");

        // Show the correct expected value for comparison
        let correct = <correct_formula>;
        println!("=== <FINDING_ID> PoC ===");
        println!("Buggy result:   {}", result);
        println!("Correct result: {}", correct);
        println!("Impact: <one line>");
    }
}
```

## Rust / Soroban integration test template

```rust
//! PoC for <FINDING_ID>: <title>
//! Requires: pre-built contract WASMs (run `stellar contract build` first)

#![cfg(test)]

use crate::<contract_module>::Client as <ContractClient>;
use soroban_sdk::{testutils::Address as _, Address, Env};

#[test]
fn poc_<finding_id_lower>_<short_name>() {
    let env = Env::default();
    env.mock_all_auths();

    // === SETUP ===
    // Minimal setup to reach vulnerable state

    // === TRIGGER ===
    // Call the vulnerable function

    // === ASSERT ===
    assert!(<condition>, "BUG CONFIRMED: <impact>");
}
```

## Repair guidance

If you receive a compiler error with your previous test, your response must:
1. Identify the exact compile error
2. Fix ONLY the lines that caused the error
3. Return the full corrected test_code (not a diff)
4. Do not change the test logic — only fix compilation issues
