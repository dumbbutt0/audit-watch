// SPDX-License-Identifier: MIT
// Fixture for the semantic_tvl_completeness research prototype. One scenario per contract.
pragma solidity ^0.8.0;

// A. Aerodrome-style positive — stake into gauge, TVL reads only local LP (omitted_external_stake_balance)
contract GaugeStakerBad {
    function stake(address pool, uint256 liq) public {
        address gauge = voter.gauges(pool);
        IGauge(gauge).deposit(liq, address(this));
    }
    function _getPositionTVL(HoldingPI memory p, address base) public view returns (uint256) {
        uint256 balance = IERC20(pool).balanceOf(address(this));
        return _getValue(token0, base, balance);
    }
}

// B. Safe gauge read — TVL reads gauge.balanceOf(this) (no candidate)
contract GaugeStakerSafe {
    function stake(address pool, uint256 liq) public {
        address gauge = voter.gauges(pool);
        IGauge(gauge).deposit(liq, address(this));
    }
    function _getPositionTVL(HoldingPI memory p, address base) public view returns (uint256) {
        uint256 staked = IGauge(gauge).balanceOf(address(this));
        return _getValue(token0, base, staked);
    }
}

// C. Local-balance-only — supplies into a market, TVL reads only token.balanceOf (local_balance_only_tvl)
contract MarketLocalOnly {
    function supplyToMarket(uint256 amt) public {
        IComet(market).supply(token, amt);
    }
    function _getPositionTVL(HoldingPI memory p, address base) public view returns (uint256) {
        return _getValue(token, base, IERC20(token).balanceOf(address(this)));
    }
}

// D. UNIv3-style ownership assumption — mint via positionManager, TVL reads pool.positions(tick key)
contract UniBad {
    function openPosition() external {
        positionManager.mint(params);
    }
    function _getPositionTVL(HoldingPI memory p, address base) public view returns (uint256 tvl) {
        bytes32 key = keccak256(abi.encodePacked(positionManager, tL, tU));
        (uint128 liquidity,,,,) = pool.positions(key);
        (uint160 sp,,,,,,) = pool.slot0();
        tvl += _getValue(token0, base, liquidity);
    }
}

// E. Safe UNIv3 — TVL reads positionManager.positions(tokenId) (no candidate)
contract UniSafe {
    function openPosition() external {
        positionManager.mint(params);
    }
    function _getPositionTVL(HoldingPI memory p, address base) public view returns (uint256 tvl) {
        (,,,,,,, uint128 liquidity,,,,) = positionManager.positions(tokenId);
        tvl += _getValue(token0, base, liquidity);
    }
}

// F. Helper-resolution safe — TVL delegates to a local helper that reads the gauge (no candidate)
contract HelperSafe {
    function stake(address pool, uint256 liq) public {
        IGauge(gauge).deposit(liq, address(this));
    }
    function _stakedBalance() internal view returns (uint256) {
        return IGauge(gauge).balanceOf(address(this));
    }
    function _getPositionTVL(HoldingPI memory p, address base) public view returns (uint256) {
        return _getValue(token0, base, _stakedBalance());
    }
}

// G. Claim-only — harvests rewards only, no principal movement; TVL reads gauge anyway (no candidate)
contract ClaimOnly {
    function claim(address pool) public {
        IGauge(gauge).getReward(address(this));
    }
    function _getPositionTVL(HoldingPI memory p, address base) public view returns (uint256) {
        return _getValue(token0, base, IGauge(gauge).balanceOf(address(this)));
    }
}

// H. Transient router — approve/swap through a router, no persistent external position (no candidate)
contract RouterOnly {
    function doSwap(uint256 amt) public {
        IERC20(token).forceApprove(address(swapRouter), amt);
        ISwapRouter(swapRouter).swap(amt);
    }
    function _getPositionTVL(HoldingPI memory p, address base) public view returns (uint256) {
        return _getValue(token, base, IERC20(token).balanceOf(address(this)));
    }
}

// I. Staker with NO TVL function — cannot pair, no candidate
contract StakerNoTVL {
    function stake(address pool, uint256 liq) public {
        IGauge(gauge).deposit(liq, address(this));
    }
}
