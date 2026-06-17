# Phi (Code4rena 2024-08) — Awarded Findings (revealed at adjudication)

Source: code4rena.com/reports/2024-08-phi — 7 High / 8 Medium.

## High
- H-01 | Signature replay in `signatureClaim` -> unauthorized claiming | signature validation lacks chain-ID binding, reuse across chains.
- H-02 | Signature replay in `createArt` -> impersonate artist & steal royalties | signature not bound to config params (artist/receiver), frontrun.
- H-03 | `shareBalance` bloating eventually blocks curator rewards distribution | zero-value entries remain in the EnumerableMap -> unbounded growth -> gas exhaustion in distribute.
- H-04 | Forced `endTime` extension in `updateArtSettings()` -> attacker can mint more | endTime forced >= now reopens the mint window post-event.
- H-05 | Exposed `_removeCredIdPerAddress` & `_addCredIdPerAddress` (public) | anyone manipulates curator tracking arrays.
- H-06 | Reentrancy in creating Creds -> steal all Ether | refund callback during cred creation reenters to overwrite cred data / exploit bonding-curve diff.
- H-07 | Unrestricted changes to token settings | artists can change soulbound/royalties/URIs post-mint without holder consent.

## Medium
- M-01 | `PhiNFT1155` can't be paused | inherits PausableUpgradeable not ERC1155Pausable -> transfers active when paused.
- M-02 | Incorrect fee handling prevents updating fees | fee setter max-value check (10,000) incompatible with actual fee amounts.
- M-03 | `PhiFactory:claim` loss of funds if `mintFee` changed beforehand | fee calc vuln between submit and execution.
- M-04 | Cred creator could cause stuck funds | insufficient validation during cred init -> failed refunds.
- M-05 | Lack of data validation when claiming -> bypass signature/merkle | ref_/artId_/imageURI not validated against signed data.
- M-06 | PhiNFT1155 keeps sending fees/royalties to old protocol destination | hardcoded/cached legacy address not re-read from current settings.
- M-07 | Attacker can DOS user from selling shares of a credId | share-lock validation permits blocking legitimate sells.
- M-08 | Refunds sent to incorrect addresses in certain cases | refund logic directs payments to wrong recipients.
