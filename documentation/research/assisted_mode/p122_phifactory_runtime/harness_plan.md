# P122 — Harness plan & feasibility

**Classification: HARNESS_COMPLEX, no fork — and BUILT (not HARNESS_UNAVAILABLE).** The heaviest harness so far:
UUPS proxy init → signature-gated `createArt` (LibClone of a PhiNFT1155 impl) → `LibZip`-compressed, signer-signed
claim payload. phi `src/PhiFactory.sol` imported via remapping (UNMUTATED).

## Project — `/tmp/p122-phifactory-harness/`
phi deps are all on disk (`@prb/test` is only needed by phi's own tests, not `PhiFactory.sol`). `foundry.toml`:
solc **0.8.25**, `evm = paris`. Remappings (absolute to phi lib):
```
forge-std/=lib/forge-std/src/                                  (symlink -> /tmp/p89-phi/lib/forge-std)
solady/=/tmp/p89-phi/lib/solady/src/
@openzeppelin/contracts/=/tmp/p89-phi/lib/openzeppelin-contracts-upgradeable/lib/openzeppelin-contracts/contracts/
@openzeppelin/contracts-upgradeable/=/tmp/p89-phi/lib/openzeppelin-contracts-upgradeable/contracts/
phi/=/tmp/p89-phi/src/
```

## Deploy / setup (real contract under test)
1. `PhiFactory impl = new PhiFactory(); ERC1967Proxy(impl, initData)` → `factory`. `initialize(signer,
   protocolFeeDest, address(MockPhiNFT1155 impl), address(MockPhiRewards), owner, protocolFee=1e14, artCreateFee=0)`
   with `signer = vm.addr(0xA11CE)`.
2. `createArt(signedData, sig, CreateConfig{maxSupply:5, mintFee:1e15, start..end window})`:
   `signedData = abi.encode(expiresIn, uri, credData)`, `credData = abi.encode(credId, credCreator, "SIGNATURE",
   chainId, bytes32(0))`, `sig = sign(pk, keccak256(signedData))` (solady `ECDSA.toEthSignedMessageHash`). Returns the
   cloned `artAddr`.
3. Claim payload (SIGNATURE): inner `claimData = abi.encode(expiresIn, minter, ref, verifier, artId, chainid, data)`
   signed by `pk`; outer `raw = abi.encode(artId, minter, ref, verifier, expiresIn, quantity, data, imageURI, innerSig)`;
   `LibZip.cdCompress(raw)` → passed to `claim` with varying `msg.value`.

## Mocks (only what createArt's clone path + claim call — clone via cloneDeterministic, storage in clone)
| Mock | Implements | Behavior |
|---|---|---|
| `MockPhiNFT1155` (clone impl) | `initialize(uint256,uint256,string,address)`, `createArtFromFactory(uint256) payable returns(uint256)`, `getTokenIdFromFactoryArtId(uint256)`, `claimFromFactory(7 args) payable` | returns tokenId=1; `claimFromFactory` records `claimCount`/`received` |
| `MockPhiRewards` | `computeMintReward(uint256,uint256)` | returns `quantity*mintFee` (drives `getArtMintFee`) |

## Test matrix (Cases A–E) → `PhiFactoryClaimRuntime.t.sol`
- **A** invalid signer signature → revert (`AddressNotSigned` bubbled through the self-call) — no minter spoof.
- **B** exact fee (`msg.value == mintFee`) → success; `claimFromFactory` called once; protocolFee → destination,
  remainder → artAddr; no excess stuck.
- **C** overpayment (`msg.value = fee + 0.5e18`) → excess **stuck** in factory; caller loses it.
- **D** underpay: D1 empty balance + `msg.value=0` → revert (can't fund inner call); D2 pre-funded factory +
  valid claim + `msg.value=0` → **succeeds drawing the mintFee from standing balance** (fee-binding gap).
- **E** over `maxSupply` (mint 5 then 6th) → revert (`OverMaxAllowedToMint`).

## Deps present?
forge-std ✓, solady ✓, OZ-upgradeable + nested OZ (ERC1967Proxy) ✓, phi src ✓, solc 0.8.25 ✓. → COMPLEX but BUILT;
all 5 cases executed (see `runtime_matrix.md` / `execution_output.txt`).
