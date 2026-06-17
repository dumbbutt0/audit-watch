// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "../../contracts/SecondSwap_StepVesting.sol";
import "../../contracts/SecondSwap_VestingManager.sol";
import "../../contracts/SecondSwap_Marketplace.sol";
import "../../contracts/SecondSwap_MarketplaceSetting.sol";

contract MockERC20 is ERC20 {
    constructor(string memory n, string memory s) ERC20(n, s) {}
    function mint(address to, uint256 amt) external { _mint(to, amt); }
}

/// @notice P118 runtime harness — does the high-ranked, "permissionless"-flagged SecondSwap_Marketplace.unlistVesting
/// let an UNAUTHORIZED party unlist a seller's listing, or let a listing be unlisted (balance returned) TWICE?
/// Real Marketplace + VestingManager + MarketplaceSetting + StepVesting + mock ERC20s (mirrors the M-11 setup).
/// RUNTIME ONLY — no severity / report / submission. State change is proven via revert behavior (double-unlist).
contract UnlistVestingRuntime is Test {
    MockERC20 vestingToken;
    MockERC20 currency;
    SecondSwap_VestingManager vmgr;
    SecondSwap_MarketplaceSetting setting;
    SecondSwap_Marketplace mkt;
    SecondSwap_StepVesting sv;

    address admin = makeAddr("admin");          // == s2Admin
    address tokenIssuer = makeAddr("tokenIssuer");
    address holder = makeAddr("holder");        // the seller
    address attacker = makeAddr("attacker");    // not seller, not admin
    address feeCollector = makeAddr("feeCollector");
    address whitelistDeployer = makeAddr("whitelistDeployer");

    uint256 constant A = 1000 ether;
    uint256 constant PRICE = 1e18;

    function setUp() public {
        vestingToken = new MockERC20("Vest", "VEST");
        currency = new MockERC20("USD", "USD");
        vmgr = new SecondSwap_VestingManager();
        vmgr.initialize(admin);
        setting = new SecondSwap_MarketplaceSetting(
            feeCollector, admin, whitelistDeployer, address(vmgr), address(currency)
        );
        mkt = new SecondSwap_Marketplace();
        mkt.initialize(address(currency), address(setting));
        vm.prank(admin);
        vmgr.setMarketplace(address(mkt));
        uint256 start = block.timestamp;
        sv = new SecondSwap_StepVesting(tokenIssuer, address(vmgr), vestingToken, start, start + 10 days, 10, address(this));
        vm.prank(admin);
        vmgr.setSellable(address(sv), true);
        vestingToken.mint(tokenIssuer, A);
        vm.prank(tokenIssuer);
        vestingToken.approve(address(sv), A);
        vm.prank(tokenIssuer);
        sv.createVesting(holder, A);
        currency.mint(holder, 1e30);
        currency.mint(attacker, 1e30);
        vm.prank(holder);
        currency.approve(address(mkt), type(uint256).max);
        vm.prank(attacker);
        currency.approve(address(mkt), type(uint256).max);
    }

    function _list(address who, uint256 amount) internal returns (uint256 listingId) {
        listingId = mkt.nextListingId(address(sv));
        vm.prank(who);
        mkt.listVesting(
            address(sv), amount, PRICE, 0,
            SecondSwap_Marketplace.ListingType.PARTIAL,
            SecondSwap_Marketplace.DiscountType.NO,
            0, address(currency), 0, false
        );
    }

    // CASE A — unauthorized (non-seller, non-admin) caller cannot unlist
    function test_A_nonseller_cannot_unlist() public {
        uint256 id = _list(holder, 100 ether);
        vm.prank(attacker);
        vm.expectRevert("SS_Marketplace: Not the seller");
        mkt.unlistVesting(address(sv), id);
    }

    // CASE B — a listing cannot be unlisted twice (no double balance-return)
    function test_B_no_double_unlist() public {
        uint256 id = _list(holder, 100 ether);
        vm.warp(block.timestamp + 121); // past minListingDuration(120) -> skip penalty branch
        vm.prank(holder);
        mkt.unlistVesting(address(sv), id);            // first unlist succeeds
        vm.prank(holder);
        vm.expectRevert("SS_Marketplace: Listing not active");
        mkt.unlistVesting(address(sv), id);            // second unlist blocked (status flipped, balance zeroed)
    }

    // CASE C — the legitimate seller can unlist once (positive control)
    function test_C_seller_can_unlist_once() public {
        uint256 id = _list(holder, 100 ether);
        vm.warp(block.timestamp + 121);
        vm.prank(holder);
        mkt.unlistVesting(address(sv), id);            // succeeds (no revert)
    }

    // CASE D — the s2Admin can unlist (intended privileged branch, skips penalty)
    function test_D_admin_can_unlist() public {
        uint256 id = _list(holder, 100 ether);
        vm.prank(admin);
        mkt.unlistVesting(address(sv), id);            // succeeds (no revert)
    }
}
