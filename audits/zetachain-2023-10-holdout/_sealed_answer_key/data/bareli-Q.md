https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol


interface ConcentratedLiquidityPoolFactory {
    function getPools(
        address token0,
        address token1,
        uint256 startIndex,
        uint256 count
    ) external view returns (address[] memory pairPools);

here we have to use I in front of the interface as the interface starts with I in front of them.
interface IConcentratedLiquidityPoolFactory {
    function getPools(
        address token0,
        address token1,
        uint256 startIndex,
        uint256 count
    ) external view returns (address[] memory pairPools);



