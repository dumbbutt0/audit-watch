# PYO-004 — Pyth confidence band has no minimum-spread floor: spreadFactor=0 collapses min==max (no execution buffer), and identity-default applies the raw Pyth confidence directly to GMX min/max execution prices

- **Severity (recommended):** Low
- **Category (HackenProof VRT):** Business Logic Errors
- **Confidence:** Medium
- **ICE:** Impact=Loss of oracle bid/ask buffer on opens/closes/liquidations -> reduced slippage protection, value extraction around the point price · Confidence=- · Exploitability=-
- **Location(s):** `/home/dummy/clones/0xMarkets_contract-main/contracts/oracle/PythLazerFeedProvider.sol:67-90`
- **Vulnerable files (bundled in `sources/`):** `PythLazerFeedProvider.sol`

## Description

PythLazerFeedProvider._buildPrice (PythLazerFeedProvider.sol:67-90) turns the Pyth confidence into the GMX bid/ask spread: scaledConfidence = applyFactor(rawConfidence, spreadFactor); minPrice = (price - scaledConfidence)*mult; maxPrice = (price + scaledConfidence)*mult. There is an upper guard (revert if scaledConfidence >= price, line 71) but NO lower guard: per deploy/configurePythLazerFeeds.ts and the test 'zero spread factor collapses the band to the price', a spreadFactor of 0 yields min==max==price, removing the protective bid/ask buffer entirely for that token. The default spreadFactor is FLOAT_PRECISION (1e30), i.e. the raw Pyth confidence is used as-is for the spread. Pyth Lazer confidence can be very tight in calm markets, so min and max can be near-identical -- meaning GMX executes opens/closes/liquidations with essentially no oracle spread, removing the cushion GMX normally relies on (its native oracle and Chainlink Data Streams provide explicit bid/ask). For a synthetic-only fork pricing FX/metals/oil/TAO with no Chainlink ref cross-check (see PYO-001), a too-tight or zeroed band increases the value an informed keeper/searcher can extract around the price point and removes slippage protection on the disadvantaged side of each trade. Inverted handling (lines 86-90) recomputes min/max as FLOAT_PRECISION^2/max and /temp; with a collapsed band both inverted bounds equal 1e30^2/price, consistent but still spread-less.

## Impact

Tokens configured with spreadFactor=0 (or a very small factor) get min==max execution prices: no oracle bid/ask buffer, so opens/closes/liquidations execute at a single point price. Combined with the absence of a Chainlink ref cross-check (PYO-001), this reduces slippage protection and can let an informed party (keeper/searcher) transact at a tighter-than-market price. Severity bounded because spreadFactor is config-keeper controlled and the more likely default (raw confidence) is reasonable; flagged as a missing safety floor.

## Attack path (Intent / Technique / Evasion)

- **Intent:** Execute against the protocol at a point price with no oracle spread cushion (advantageous fills / reduced slippage protection).
- **Technique:** Token configured with pythLazerFeedSpreadFactor=0 (or tiny); _buildPrice produces min==max; GMX uses that single price for both sides of execution.
- **Evasion:** _buildPrice guards only the upper bound (scaledConfidence < price) and has no minimum-spread floor; GMX's native/data-stream feeds provide an explicit bid/ask the Lazer path can collapse.
