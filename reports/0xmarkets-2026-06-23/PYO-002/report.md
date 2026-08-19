# PYO-002 — Config.setPythLazerFeed writes Lazer feed config to the WRONG DataStore keys (DATA_STREAM_* instead of PYTH_LAZER_FEED_*) and as the wrong type (setBytes32 vs the getUint the provider reads)

- **Severity (recommended):** Low
- **Category (HackenProof VRT):** Business Logic Errors
- **Confidence:** High
- **ICE:** Impact=PythLazerFeedProvider.getOraclePrice reverts EmptyPythLazerFeedId -> price unavailable for the token · Confidence=- · Exploitability=-
- **Location(s):** `/home/dummy/clones/0xMarkets_contract-main/contracts/config/Config.sol:135-169`
- **Vulnerable files (bundled in `sources/`):** `Config.sol`, `PythLazerFeedProvider.sol`

## Description

Config.setPythLazerFeed (config/Config.sol:135-169) is the on-chain config-keeper function intended to configure a Pyth Lazer feed for a token. It writes: dataStore.setBytes32(Keys.dataStreamIdKey(token), pythLazerFeedId); setBool(Keys.dataStreamInvertedKey(token), ...); setUint(Keys.dataStreamMultiplierKey(token), ...); and only the spread factor to the correct setUint(Keys.pythLazerFeedSpreadFactorKey(token), ...). But PythLazerFeedProvider.getOraclePrice (PythLazerFeedProvider.sol:34-40) reads: uint32(dataStore.getUint(Keys.pythLazerFeedIdKey(token))), dataStore.getUint(Keys.pythLazerFeedMultiplierKey(token)), dataStore.getBool(Keys.pythLazerFeedInvertedKey(token)). The keys differ (DATA_STREAM_ID/INVERTED/MULTIPLIER vs PYTH_LAZER_FEED_ID/INVERTED/MULTIPLIER) AND the feedId type differs (setBytes32 written vs getUint read). Consequently, configuring a feed through setPythLazerFeed leaves pythLazerFeedIdKey == 0, so getOraclePrice reverts with Errors.EmptyPythLazerFeedId(token) (DoS / unconfigurable). The function also gates on dataStreamIdKey() and reverts DataStreamIdAlreadyExistsForToken, conflating Lazer and Data Stream config namespaces. The team is aware: deploy/configurePythLazerFeeds.ts and scripts/configure-tao-oracle.ts (comment: 'must use setUint -- PythLazerFeedProvider reads getUint') set the CORRECT keys/types off-chain, which is why live feeds work. This is a latent footgun: any operator using the on-chain Config path would silently bring the price feed down or, if combined with a later getBytes32-based migration, risk reading mismatched values. Not attacker-reachable (onlyConfigKeeper).

## Impact

An admin configuring a Lazer feed via the on-chain Config.setPythLazerFeed function produces a non-functional feed (provider reverts EmptyPythLazerFeedId) -> token price unavailable -> orders/liquidations for that token DoS until reconfigured via the correct keys. No fund loss; correctness / operational-safety defect.

## Attack path (Intent / Technique / Evasion)

- **Intent:** n/a (config keeper footgun, not an attacker objective).
- **Technique:** onlyConfigKeeper calls setPythLazerFeed; writes land in DATA_STREAM_* keys; provider reads PYTH_LAZER_FEED_* keys -> feedId==0 -> revert.
- **Evasion:** The intended config path and the provider read path were never reconciled to the same key set/type; off-chain scripts paper over it.
