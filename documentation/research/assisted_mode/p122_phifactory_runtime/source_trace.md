# P122 — Source trace: PhiFactory.claim (phi-2024-08)

Subject: `src/PhiFactory.sol` (UUPS-upgradeable, solc 0.8.25, evm paris). Read-only; framing only — runtime decides.

## claim (the wrapper)
`function claim(bytes calldata encodeData_) external payable` — permissionless.
- `encodedata_ = LibZip.cdDecompress(encodeData_); artId = abi.decode(encodedata_, (uint256));`
- `art = arts[artId]; tokenId = IPhiNFT1155Ownable(art.artAddress).getTokenIdFromFactoryArtId(artId);`
- if `art.verificationType == "MERKLE"`: decode (artId, minter, proof, ref, quantity, leafPart, imageURI);
  `mintFee = getArtMintFee(artId, quantity); this.merkleClaim{value: mintFee}(proof, claimData, mintArgs, leafPart);`
- if `"SIGNATURE"`: decode (artId, minter, ref, verifier, expiresIn, quantity, data, imageURI, signature);
  `claimData = abi.encode(expiresIn, minter, ref, verifier, artId, block.chainid, data);`
  `mintFee = getArtMintFee(artId, quantity); this.signatureClaim{value: mintFee}(signature, claimData, mintArgs);`
- else `revert InvalidVerificationType()`.

**Key: `claim` never checks the caller's `msg.value`.** It computes `mintFee` and forwards exactly that via an
EXTERNAL self-call (`this.merkleClaim`/`this.signatureClaim`), drawing on the contract balance.

## Inner verification (the entitlement guards)
- `signatureClaim`: `if (_recoverSigner(keccak256(encodeData_), signature_) != phiSignerAddress) revert AddressNotSigned();`
  + `expiresIn_ <= block.timestamp` ⇒ `SignatureExpired`. `minter_` is from the signed data, not `msg.sender`.
- `merkleClaim`: `MerkleProofLib.verifyCalldata(proof_, credMerkleRoot[...], keccak256(...minter_, leafPart_...))`.
- Both call `_validateAndUpdateClaimState(artId, minter, quantity)`:
  `tx.origin != _msgSender() && msg.sender != art.artAddress && msg.sender != address(this)` ⇒ `TxOriginMismatch`
  (on the wrapper path `msg.sender == address(this)` ⇒ passes); `msg.value < getArtMintFee` ⇒ `InvalidMintFee`
  (on the wrapper path inner `msg.value == mintFee` ⇒ passes); `startTime`/`endTime` window; `quantity > 0`;
  `numberMinted + quantity > maxSupply` ⇒ `OverMaxAllowedToMint`.

## Fee flow (_processClaim)
`mintFee = getArtMintFee(artId, quantity)`; **refund `etherValue_ - mintFee` to `_msgSender()`** — on the wrapper
path `etherValue_ == mintFee` ⇒ **refund 0**; `protocolFeeDestination.safeTransferETH(mintProtocolFee * quantity)`;
`art.artAddress.call{value: mintFee - mintProtocolFee*quantity}(claimFromFactory(...))`.
`getArtMintFee = IPhiRewards.computeMintReward(quantity, art.mintFee) + quantity * mintProtocolFee`.

## The fee-binding gap (probe target)
Because `claim` forwards a computed `mintFee` (not `msg.value`) and the inner refund nets to 0 on the wrapper path:
- **overpayment** (`msg.value > mintFee` to `claim`) leaves the excess in the factory — not refunded (only
  `withdraw()` → `protocolFeeDestination`, onlyOwner). The DIRECT `signatureClaim`/`merkleClaim` path DOES refund,
  so the wrapper is inconsistent.
- **underpayment** (`msg.value < mintFee`) still succeeds if the factory holds standing balance — the inner
  `{value: mintFee}` draws on it.

## Setup cost (for the harness)
`arts` is private; an art must be created via `createArt(signedData_, signature_, config)` — signature-gated by
`phiSignerAddress` (`_validateArtCreationSignature`) and it `cloneDeterministic`s the `erc1155ArtAddress` impl, calling
`initialize(credChainId, credId, verificationType, protocolFeeDestination)` + `createArtFromFactory(artId)` on the clone.

## Framed runtime question (→ harness)
Can a permissionless caller of `claim` claim without a valid signer entitlement / spoof `minter_`, over-claim past
the per-art guards, or exploit the fee-binding gap (excess stuck / underpay subsidized by standing balance)? →
answered by the harness.
