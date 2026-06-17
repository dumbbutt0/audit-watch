// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "../IOracle.sol";
import "../../config/GeneralConfig.sol";
import "../../../utils/SignaturesLib.sol";
import "../../../utils/EIP712DomainLib.sol";

struct OraclePricesTick {
    uint64 assetId;
    OraclePrice[] prices;
    bytes[] signatures;
}

/**
 * @title OraclePriceTickTransLib
 * @dev Oracle price update
 */
library OraclePriceTickTransLib {
    bytes32 public constant ORACLE_PRICE_TYPEHASH = keccak256("OraclePrice(int256 price,uint256 timestamp)");

    bytes32 public constant ORACLE_PRICE_TICK_TYPEHASH = keccak256(
        "OraclePriceTick(uint64 assetId,OraclePrice priceEntry,uint64 oraclePriceSignedAssetId)"
        "OraclePrice(int256 price,uint256 timestamp)"
    );

    function process(OraclePricesTick[] memory ticks, IOracle oracle, GeneralConfig generalConfig, address verifyingContract)
        internal
    {
        uint256 length = ticks.length;
        for (uint256 i = 0; i < length;) {
            _processSingle(ticks[i], oracle, generalConfig, verifyingContract);
            unchecked {
                ++i;
            }
        }
    }

    function _processSingle(OraclePricesTick memory tick, IOracle oracle, GeneralConfig generalConfig, address verifyingContract) private {
        uint256 len = tick.prices.length;
        require(tick.signatures.length == len && len > 0, "OraclePriceTickTransLib: signatures length mismatch");
        SyntheticAssetInfo memory assetInfo = generalConfig.getSyntheticAssetInfo(tick.assetId);
        require(assetInfo.oraclePriceSignedAssetIds.length == len, "OraclePriceTickTransLib: prices length mismatch");

        uint256 currentTimestamp = oracle.getCurrentTimestamp(tick.assetId);
        uint256 validCount = 0;
        int256[] memory pricesArray = new int256[](len);
        uint256[] memory timestamps = new uint256[](len);
        for (uint256 i = 0; i < len;) {
            OraclePrice memory priceEntry = tick.prices[i];
            bytes memory signature = tick.signatures[i];
            if (priceEntry.price <= 0 || signature.length != 65) {
                unchecked {
                    ++i;
                }
                continue;
            }
            _validatePrice(tick.assetId, currentTimestamp, priceEntry, signature, assetInfo, i, verifyingContract);
            pricesArray[validCount] = priceEntry.price;
            timestamps[validCount] = priceEntry.timestamp;
            unchecked {
                ++i;
                ++validCount;
            }
        }
        require(validCount >= uint256(assetInfo.oraclePriceQuorum), "OraclePriceTickTransLib: quorum not met");
        OraclePrice memory median = medianPrice(pricesArray, timestamps, validCount);
        oracle.updatePrice(tick.assetId, median);
    }

    function _validatePrice(
        uint64 assetId,
        uint256 timestamps,
        OraclePrice memory priceEntry,
        bytes memory signature,
        SyntheticAssetInfo memory assetInfo,
        uint256 index,
        address verifyingContract
    ) private view {
        require(priceEntry.price >= 0, "OraclePriceTickTransLib: price negative");
        // TODO: check with backend behaviour
        // require(priceEntry.timestamp > timestamps, "OraclePriceTickTransLib: timestamp in future");
        require(priceEntry.timestamp <= block.timestamp, "OraclePriceTickTransLib: timestamp in future");
        require(priceEntry.timestamp + 1 days >= block.timestamp, "OraclePriceTickTransLib: timestamp too old");
        require(
            SignaturesLib.verify(
                getOraclePriceHash(assetId, priceEntry, assetInfo.oraclePriceSignedAssetIds[index], block.chainid, verifyingContract),
                signature,
                assetInfo.oraclePriceSigners[index]
            ),
            "OraclePriceTickTransLib: signature invalid"
        );
    }

    function hashOraclePrice(OraclePrice memory p) internal pure returns (bytes32) {
        return keccak256(abi.encode(ORACLE_PRICE_TYPEHASH, p.price, p.timestamp));
    }

    function getOraclePriceHash(
        uint64 assetId,
        OraclePrice memory priceEntry,
        uint64 oraclePriceSignedAssetId,
        uint256 chainId,
        address verifyingContract
    ) public pure returns (bytes32) {
        bytes32 structHash = keccak256(
            abi.encode(ORACLE_PRICE_TICK_TYPEHASH, assetId, hashOraclePrice(priceEntry), oraclePriceSignedAssetId)
        );
        return EIP712DomainLib.toTypedDataHash(structHash, chainId, verifyingContract);
    }

    function medianPrice(int256[] memory pricesArray, uint256[] memory timestamps, uint256 count)
        internal
        pure
        returns (OraclePrice memory)
    {
        require(count > 0, "OraclePriceTickTransLib: no valid prices");

        _sortAscending(pricesArray, timestamps, count);

        uint256 mid = count / 2;
        return OraclePrice({price: pricesArray[mid], timestamp: timestamps[mid]});
    }

    function _sortAscending(int256[] memory prices, uint256[] memory timestamps, uint256 len) private pure {
        for (uint256 i = 1; i < len;) {
            int256 key = prices[i];
            uint256 ts = timestamps[i];
            uint256 j = i;
            while (j > 0 && prices[j - 1] > key) {
                prices[j] = prices[j - 1];
                timestamps[j] = timestamps[j - 1];
                unchecked {
                    --j;
                }
            }
            prices[j] = key;
            timestamps[j] = ts;
            unchecked {
                ++i;
            }
        }
    }
}
