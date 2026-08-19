// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IERC20} from "openzeppelin-contracts/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "openzeppelin-contracts/contracts/token/ERC20/utils/SafeERC20.sol";
import {IExchangeRouter} from "../interfaces/IExchangeRouter.sol";
import {I0xMReader} from "../interfaces/I0xMReader.sol";
import {I0xMOracle} from "../interfaces/I0xMOracle.sol";

interface IExchangeRouterRouter {
    function router() external view returns (address);
}

/// @title PoolDeployLib
/// @notice 0xM pool deploy/recall logic extracted to reduce CarthaVault bytecode size.
///         Functions are `external` so Solidity generates DELEGATECALL (not inlined).
library PoolDeployLib {
    using SafeERC20 for IERC20;

    uint256 internal constant GM_PRICE_PRECISION = 1e30;
    bytes32 internal constant MAX_PNL_FACTOR_FOR_DEPOSITS = keccak256(abi.encode("MAX_PNL_FACTOR_FOR_DEPOSITS"));

    function deploy(
        address asset,
        address router,
        address market,
        address depositVault,
        uint256 amount,
        uint256 minMarketTokens,
        uint256 executionFee
    ) external returns (bytes32 depositKey) {
        address internalRouter = IExchangeRouterRouter(router).router();
        IERC20(asset).safeIncreaseAllowance(internalRouter, amount);
        IExchangeRouter(router).sendTokens(asset, depositVault, amount);

        if (executionFee > 0) {
            IExchangeRouter(router).sendWnt{value: executionFee}(address(this), executionFee);
        }

        address[] memory empty = new address[](0);

        depositKey = IExchangeRouter(router)
            .createDeposit(
                IExchangeRouter.CreateDepositParams({
                receiver: address(this),
                callbackContract: address(0),
                uiFeeReceiver: address(0),
                market: market,
                initialLongToken: asset,
                initialShortToken: asset,
                longTokenSwapPath: empty,
                shortTokenSwapPath: empty,
                minMarketTokens: minMarketTokens,
                shouldUnwrapNativeToken: false,
                executionFee: executionFee,
                callbackGasLimit: 0
            })
            );
    }

    function recall(
        address router,
        address market,
        address withdrawalVault,
        uint256 gmAmount,
        uint256 minShortTokenAmount,
        uint256 executionFee
    ) external returns (bytes32 withdrawalKey) {
        address internalRouter = IExchangeRouterRouter(router).router();
        IERC20(market).safeIncreaseAllowance(internalRouter, gmAmount);
        IExchangeRouter(router).sendTokens(market, withdrawalVault, gmAmount);

        if (executionFee > 0) {
            IExchangeRouter(router).sendWnt{value: executionFee}(address(this), executionFee);
        }

        address[] memory empty = new address[](0);

        withdrawalKey = IExchangeRouter(router)
            .createWithdrawal(
                IExchangeRouter.CreateWithdrawalParams({
                receiver: address(this),
                callbackContract: address(0),
                uiFeeReceiver: address(0),
                market: market,
                longTokenSwapPath: empty,
                shortTokenSwapPath: empty,
                minLongTokenAmount: 0,
                minShortTokenAmount: minShortTokenAmount,
                shouldUnwrapNativeToken: false,
                executionFee: executionFee,
                callbackGasLimit: 0
            })
            );
    }

    function gmValueInUsdc(address poolToken, address reader, address dataStore, address market, address oracle)
        external
        view
        returns (uint256)
    {
        uint256 gmBalance = poolToken != address(0) ? IERC20(poolToken).balanceOf(address(this)) : 0;
        if (gmBalance == 0 || reader == address(0)) return 0;

        int256 gmPrice = _getGmPrice(reader, dataStore, market, oracle);
        if (gmPrice <= 0) return 0;

        return (gmBalance * uint256(gmPrice)) / GM_PRICE_PRECISION;
    }

    function _getGmPrice(address reader, address dataStore, address market, address oracle)
        private
        view
        returns (int256 gmPrice)
    {
        I0xMReader r = I0xMReader(reader);
        I0xMOracle o = I0xMOracle(oracle);

        I0xMReader.MarketProps memory mkt = r.getMarket(dataStore, market);
        I0xMReader.PriceProps memory indexPrice = o.getPrimaryPrice(mkt.indexToken);
        I0xMReader.PriceProps memory longPrice = o.getPrimaryPrice(mkt.longToken);
        I0xMReader.PriceProps memory shortPrice = o.getPrimaryPrice(mkt.shortToken);

        (gmPrice,) = r.getMarketTokenPrice(
            dataStore, mkt, indexPrice, longPrice, shortPrice, MAX_PNL_FACTOR_FOR_DEPOSITS, false
        );
    }
}
