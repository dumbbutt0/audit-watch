# P151 — Gate 6: Trace-Test Disposition (deferred, with rationale)

Gate 6 asks for an optional real-upstream-caller trace "if feasible without changing production source."

## Assessment: deferred (structural proof is decisive; trace exceeds the ~2-mock threshold)
A faithful `UTB.swapAndExecute` end-to-end trace requires mocking, beyond the real `UTBFeeCollector`:
- `wrapped` (WETH) with `deposit`/`withdraw` (`performSwap` UTB.sol:78-79, native path),
- a registered `ISwapper` (`getId`, `swap`, `updateSwapParams`) + `SwapParams`-encoded `swapPayload`
  (`performSwap` UTB.sol:63-100),
- token plumbing for both the fee token and the swap `tokenIn` (`transferFrom`/`approve`),
- an `IUTBExecutor` (`executor.execute`).
That is >2 small mocks. More importantly, a runtime trace **cannot prove the negative** (unreachability) better
than the structural fact already established by source:

> `swapAndExecute`/`bridgeAndExecute` take **no user `packedInfo` parameter**; `packedInfo` is built inline as
> `abi.encode(instructions, fees)` (`UTB.sol:115`, `:266`). There is therefore no caller path by which an
> unprivileged user can supply a `packedInfo` that excludes the executed `fees`.

A positive-control trace would only re-show the happy path (charges the signed fee), which P150 already implies.
The reachability verdict (`trusted_router_only_not_externally_reachable`) is **invariant** to running it.

## Conclusion
Trace deferred; the reachability/severity verdict rests on the source-structural proof + the P150 mechanism. No
production source touched; no heavy harness added. (If a human later wants the positive control, build it under
`audits/decent-2024-01-holdout/pocs/p151/` with the four mocks above.)
