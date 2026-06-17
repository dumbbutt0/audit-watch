// SPDX-License-Identifier: MIT
pragma solidity 0.8.25;

// P122 runtime harness — phi PhiFactory.claim (research-only, un-wired).
// One question: can a permissionless caller of claim (a) claim without a valid signer entitlement / spoof minter,
// (b) over-claim past the per-art guards, or (c) exploit the fee-binding gap (excess msg.value stuck / underpay
// subsidized by standing balance)? Runtime decides. phi src is UNMUTATED (PhiFactory imported via remapping).

import "forge-std/Test.sol";
import {PhiFactory} from "phi/PhiFactory.sol";
import {IPhiFactory} from "phi/interfaces/IPhiFactory.sol";
import {ERC1967Proxy} from "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";
import {LibZip} from "solady/utils/LibZip.sol";
import {ECDSA} from "solady/utils/ECDSA.sol";

// ---- mock NFT1155 implementation: cloned by createArt (minimal proxy, storage in clone) ----
contract MockPhiNFT1155 {
    uint256 public claimCount;
    uint256 public lastQuantity;
    uint256 public received;
    function initialize(uint256, uint256, string memory, address) external {}
    function createArtFromFactory(uint256) external payable returns (uint256) { return 1; }
    function getTokenIdFromFactoryArtId(uint256) external pure returns (uint256) { return 1; }
    function claimFromFactory(uint256, address, address, address, uint256 quantity_, bytes32, string memory)
        external payable
    {
        claimCount += 1;
        lastQuantity = quantity_;
        received += msg.value;
    }
}

// ---- mock rewards: drives getArtMintFee = computeMintReward(quantity, mintFee) + quantity*mintProtocolFee ----
contract MockPhiRewards {
    function computeMintReward(uint256 quantity_, uint256 mintFee_) external pure returns (uint256) {
        return quantity_ * mintFee_;
    }
}

contract PhiFactoryClaimRuntime is Test {
    PhiFactory factory;
    MockPhiNFT1155 nftImpl;
    MockPhiRewards rewards;
    address artAddr;
    uint256 constant SIGNER_PK = 0xA11CE;
    address signer;
    address owner = makeAddr("owner");
    address protocolFeeDest = makeAddr("protocolFeeDest");
    address minter = makeAddr("minter");
    address attacker = makeAddr("attacker");
    uint256 constant ART_MINT_FEE = 0.001 ether;
    uint256 constant PROTOCOL_FEE = 0.0001 ether;
    uint256 artId;

    function setUp() public {
        signer = vm.addr(SIGNER_PK);
        nftImpl = new MockPhiNFT1155();
        rewards = new MockPhiRewards();
        PhiFactory impl = new PhiFactory();
        bytes memory initData = abi.encodeCall(
            PhiFactory.initialize,
            (signer, protocolFeeDest, address(nftImpl), address(rewards), owner, PROTOCOL_FEE, 0)
        );
        factory = PhiFactory(payable(address(new ERC1967Proxy(address(impl), initData))));
        artId = 1;
        artAddr = _createArt();
    }

    function _createArt() internal returns (address) {
        bytes memory credData = abi.encode(uint256(1), address(0xC0FFEE), "SIGNATURE", block.chainid, bytes32(0));
        uint256 expiresIn = block.timestamp + 1000;
        bytes memory signedData = abi.encode(expiresIn, "ipfs://uri", credData);
        bytes memory sig = _sign(SIGNER_PK, keccak256(signedData));
        IPhiFactory.CreateConfig memory cfg = IPhiFactory.CreateConfig({
            artist: address(this),
            receiver: makeAddr("receiver"),
            endTime: block.timestamp + 10_000,
            startTime: block.timestamp,
            maxSupply: 5,
            mintFee: ART_MINT_FEE,
            soulBounded: false
        });
        return factory.createArt(signedData, sig, cfg);
    }

    function _sign(uint256 pk, bytes32 hash) internal pure returns (bytes memory) {
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(pk, ECDSA.toEthSignedMessageHash(hash));
        return abi.encodePacked(r, s, v);
    }

    // build the LibZip-compressed SIGNATURE claim payload for `claim`
    function _claimPayload(uint256 signPk, address minter_, uint256 quantity_) internal view returns (bytes memory) {
        uint256 expiresIn = block.timestamp + 1000;
        address ref = address(0);
        address verifier = signer;
        bytes32 data = bytes32(0);
        // inner claimData (must match claim()'s reconstruction) signed by the signer
        bytes memory claimData = abi.encode(expiresIn, minter_, ref, verifier, artId, block.chainid, data);
        bytes memory innerSig = _sign(signPk, keccak256(claimData));
        // outer decompressed payload (SIGNATURE decode order in claim())
        bytes memory raw = abi.encode(artId, minter_, ref, verifier, expiresIn, quantity_, data, "img://x", innerSig);
        return LibZip.cdCompress(raw);
    }

    // ---------- CASE A: bad signer -> AddressNotSigned (no minter spoof without a valid signature) ----------
    function test_A_invalid_signature_rejected() public {
        bytes memory payload = _claimPayload(0xBADBAD, minter, 1); // wrong key
        uint256 fee = factory.getArtMintFee(artId, 1);
        vm.deal(address(this), 1 ether);
        vm.expectRevert(); // AddressNotSigned (bubbled through the self-call)
        factory.claim{value: fee}(payload);
    }

    // ---------- CASE B: happy path, msg.value == mintFee -> success, fees split, refund 0 ----------
    function test_B_happy_path_exact_fee() public {
        bytes memory payload = _claimPayload(SIGNER_PK, minter, 1);
        uint256 fee = factory.getArtMintFee(artId, 1);
        assertEq(fee, ART_MINT_FEE + PROTOCOL_FEE, "fee = computeMintReward + protocolFee");
        vm.deal(address(this), 1 ether);
        uint256 pfdBefore = protocolFeeDest.balance;
        uint256 artBefore = artAddr.balance;

        factory.claim{value: fee}(payload);

        assertEq(MockPhiNFT1155(artAddr).claimCount(), 1, "claimFromFactory called once");
        assertEq(protocolFeeDest.balance - pfdBefore, PROTOCOL_FEE, "protocol fee routed");
        assertEq(artAddr.balance - artBefore, fee - PROTOCOL_FEE, "remainder routed to art");
        assertEq(address(factory).balance, 0, "no excess stuck on exact payment");
    }

    // ---------- CASE C: overpayment via claim -> excess STUCK in the factory (no refund on wrapper path) ----------
    function test_C_overpayment_excess_stuck() public {
        bytes memory payload = _claimPayload(SIGNER_PK, minter, 1);
        uint256 fee = factory.getArtMintFee(artId, 1);
        uint256 overpay = 0.5 ether;
        vm.deal(address(this), 1 ether);
        uint256 callerBefore = address(this).balance;

        factory.claim{value: fee + overpay}(payload);

        // the excess is neither refunded to the caller nor forwarded — it sits in the factory
        assertEq(address(factory).balance, overpay, "excess msg.value stuck in factory");
        assertEq(callerBefore - address(this).balance, fee + overpay, "caller paid fee + the lost excess");
    }

    // ---------- CASE D: underpay -> draws on standing balance (fee-binding gap); empty balance -> revert ----------
    function test_D_underpay_draws_standing_balance() public {
        // D1: with NO standing balance, msg.value=0 cannot fund the inner {value: mintFee} call -> revert
        bytes memory p1 = _claimPayload(SIGNER_PK, minter, 1);
        vm.deal(address(this), 1 ether);
        vm.expectRevert();
        factory.claim{value: 0}(p1);

        // D2: pre-fund the factory (simulate stuck excess from prior overpayers), then a valid claimer pays 0
        vm.deal(address(factory), 1 ether);
        uint256 fee = factory.getArtMintFee(artId, 1);
        uint256 facBefore = address(factory).balance;
        uint256 pfdBefore = protocolFeeDest.balance;
        bytes memory p2 = _claimPayload(SIGNER_PK, attacker, 1); // attacker is the minter in a signer-signed claim
        factory.claim{value: 0}(p2);
        // the claim succeeded paying nothing: factory standing balance funded the whole mintFee
        assertEq(MockPhiNFT1155(artAddr).claimCount(), 1, "claim succeeded with msg.value==0");
        assertEq(facBefore - address(factory).balance, fee, "factory standing balance paid the mintFee");
        assertEq(protocolFeeDest.balance - pfdBefore, PROTOCOL_FEE, "fee routed from standing balance");
    }

    // ---------- CASE E: caps — over maxSupply reverts (guards enforced) ----------
    function test_E_over_maxsupply_reverts() public {
        vm.deal(address(this), 5 ether);
        // maxSupply = 5; mint 5 then the 6th must revert
        for (uint256 i = 0; i < 5; i++) {
            bytes memory p = _claimPayload(SIGNER_PK, address(uint160(0x1000 + i)), 1);
            uint256 fee = factory.getArtMintFee(artId, 1);
            factory.claim{value: fee}(p);
        }
        bytes memory pOver = _claimPayload(SIGNER_PK, address(uint160(0x2000)), 1);
        uint256 feeOver = factory.getArtMintFee(artId, 1);
        vm.expectRevert(); // OverMaxAllowedToMint
        factory.claim{value: feeOver}(pOver);
    }

    receive() external payable {}
}
