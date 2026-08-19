# CFG-002 — Config.setPythLazerFeed writes the Pyth Lazer feed config to the WRONG DataStore keys (data-stream keys) — feed is read as zero by PythLazerFeedProvider

- **Severity (recommended):** Medium
- **Category (HackenProof VRT):** Business Logic Errors
- **Confidence:** High
- **ICE:** Impact=Pyth Lazer provider reads zero feedId/multiplier -> token unpriceable / mis-priced; existing Chainlink data-stream multiplier for the token clobbered · Confidence=- · Exploitability=-
- **Location(s):** `contracts/config/Config.sol:153-155 (wrong keys) vs contracts/config/Timelock.sol:572-575 (correct keys) and contracts/oracle/PythLazerFeedProvider.sol:34,37,40 (readers)`
- **Vulnerable files (bundled in `sources/`):** `Config.sol`, `Timelock.sol`, `ConfigAllowedKeys.sol`, `PythLazerFeedProvider.sol`

## Description

Config.setPythLazerFeed (contracts/config/Config.sol:135-169) is intended to register a Pyth Lazer feed for a token, but it writes three of the four parameters to the Chainlink DATA-STREAM keys instead of the Pyth Lazer keys:
  - line 153: setBytes32(Keys.dataStreamIdKey(token), pythLazerFeedId)   // should be pythLazerFeedIdKey
  - line 154: setBool(Keys.dataStreamInvertedKey(token), pythLazerFeedInverted)  // should be pythLazerFeedInvertedKey
  - line 155: setUint(Keys.dataStreamMultiplierKey(token), pythLazerFeedMultiplier)  // should be pythLazerFeedMultiplierKey
  - line 156: setUint(Keys.pythLazerFeedSpreadFactorKey(token), pythLazerFeedSpreadFactor)  // this one is correct

PythLazerFeedProvider reads the feed config from the PYTH-LAZER keys: feedId from pythLazerFeedIdKey (line 34, via getUint), multiplier from pythLazerFeedMultiplierKey (line 37), inverted from pythLazerFeedInvertedKey (line 40), spread from pythLazerFeedSpreadFactorKey (line 68). Because setPythLazerFeed never writes pythLazerFeedIdKey/pythLazerFeedMultiplierKey/pythLazerFeedInvertedKey, a token configured through this function is read back by the provider with feedId=0 and multiplier=0 (only spread factor lands correctly). The provider therefore cannot price the token (or prices it at 0/with a zero multiplier). Additionally, writing the multiplier to dataStreamMultiplierKey(token) clobbers the Chainlink data-stream multiplier for the same token.

The Timelock equivalent setPythLazerFeedAfterSignal (contracts/config/Timelock.sol:572-575) writes ALL FOUR parameters to the CORRECT pythLazer* keys, proving the intended layout and that Config.setPythLazerFeed is the buggy copy. This is CONFIG_KEEPER-only and an operator has a correct alternative (the Timelock path, or setting the pythLazerFeed* base keys directly via the generic Config setters, which are allowlisted at ConfigAllowedKeys.sol:212-215).

## Impact

A Pyth Lazer feed configured via Config.setPythLazerFeed is non-functional / mis-priced: the provider reads feedId=0 and multiplier=0 from the never-written pyth keys, while the values land in the unrelated data-stream keys (also corrupting any existing Chainlink data-stream multiplier for that token). If this oracle is relied on for the token, the result is a mis-priced or unpriceable market. Privileged (CONFIG_KEEPER) and recoverable via the correct paths, so not a permissionless exploit.

## Attack path (Intent / Technique / Evasion)

- **Intent:** Cause a token's Pyth Lazer oracle to be mis-configured (feedId/multiplier read as zero) and/or clobber its Chainlink data-stream multiplier.
- **Technique:** CONFIG_KEEPER calls Config.setPythLazerFeed(token, feedId, inverted, multiplier, spread). The function writes feedId/inverted/multiplier into dataStreamIdKey/dataStreamInvertedKey/dataStreamMultiplierKey instead of the pythLazer* keys. PythLazerFeedProvider.getOraclePrice later reads pythLazerFeedIdKey (=0) and pythLazerFeedMultiplierKey (=0) -> wrong/zero price; the data-stream multiplier for the token is overwritten.
- **Evasion:** The Timelock copy (setPythLazerFeedAfterSignal) writes the correct pythLazer* keys; Config.setPythLazerFeed is a divergent copy that pasted the setDataStream key names. The file header claims 'modified from GMX … pure validation, no behavior change', masking the key-name divergence.
