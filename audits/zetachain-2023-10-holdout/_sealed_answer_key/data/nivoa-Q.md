The contract `ZetaTokenConsumerUniV3` in `repos\protocol-contracts\contracts\evm\tools\ZetaTokenConsumerUniV3.strategy.sol` could use the function `refundETH` from `"@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol"`

The git diff in the file is the following:

```solidity

@@ -9,6 +9,10 @@ import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";
 import "../interfaces/ZetaInterfaces.sol";
 
+interface IUniswapRouter is ISwapRouter {
+    function refundETH() external payable;
+}
+
 interface ZetaTokenConsumerUniV3Errors {
     error InputCantBeZero();
 
@@ -34,7 +38,7 @@ contract ZetaTokenConsumerUniV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Erro
     address public immutable WETH9Address;
     address public immutable zetaToken;
 
-    ISwapRouter public immutable uniswapV3Router;
+    IUniswapRouter public immutable uniswapV3Router;
     IUniswapV3Factory public immutable uniswapV3Factory;
 
     bool internal _locked;
@@ -55,7 +59,7 @@ contract ZetaTokenConsumerUniV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Erro
         ) revert ZetaCommonErrors.InvalidAddress();
 
         zetaToken = zetaToken_;
-        uniswapV3Router = ISwapRouter(uniswapV3Router_);
+        uniswapV3Router = IUniswapRouter(uniswapV3Router_);
         uniswapV3Factory = IUniswapV3Factory(uniswapV3Factory_);
         WETH9Address = WETH9Address_;
         zetaPoolFee = zetaPoolFee_;
@@ -92,6 +96,8 @@ contract ZetaTokenConsumerUniV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Erro
         uint256 amountOut = uniswapV3Router.exactInputSingle{value: msg.value}(params);
 
         emit EthExchangedForZeta(msg.value, amountOut);
+        uniswapV3Router.refundETH();
+
         return amountOut;
     }
 

```
