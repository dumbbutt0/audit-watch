ZETACHAIN AUDIT CONTEST

High Issues

1. Functions sending ether to arbitrary destination
(ZetaTokenConsumerUniV3.strategy.sol :: 74-96) - getEthFromZeta(address,uint256,uint256)  sends eth to arbitrary user
Dangerous calls:
- (sent) = destinationAddress.call{value: amountOut}() 
-----------------------------------------------------------------------------------------------------------
Medium Issues

1.Dangerous Strict Equality
  UniswapV2Pair.sol::46 => require(success && (data.length == 0 || abi.decode(data, (bool))), 'UniswapV2: TRANSFER_FAILED');

2.Unchecked Transfer
  UniswapV2Router02.sol::113 => removeLiquidity(address,address,uint256,uint256,uint256,address,uint256) ignores return value by IUniswapV2Pair(pair).transferFrom(msg.sender,pair,liquidity)
-----------------------------------------------------------------------------------------------------------
Low Issues 

1. Do not use Deprecated Library Functions
ZetaTokenConsumerUniV3.strategy.sol::108 => IERC20(inputToken).safeApprove(address(uniswapV3Router),
inputTokenAmount);
ZetaTokenConsumerUniV3.strategy.sol::133 => IERC20(zetaToken).safeApprove(address(uniswapV3Router),
zetaTokenAmount);
ZetaTokenConsumerUniV3.strategy.sol::168 => IERC20(zetaToken).safeApprove(address(uniswapV3Router),
zetaTokenAmount);

2. Block Timestamp
UniswapV2ERC20.sol:: 82 => require(deadline >= block.timestamp, 'UniswapV2: EXPIRED');
UniswapV2Pair.sol:: 77 => if (timeElapsed > 0 && _reserve0 != 0 && _reserve1 != 0) {

3. Missing zero address validation
  UniswapV2Router02.sol:: => constructor(address,address)._factory lacks a zero-check on :- factory = _factory UniswapV2Router02.constructor(address,address)._WETH  lacks a zero-check on :- WETH = _WETH
  Ownable2Step.sol::41 => transferOwnership(address).newOwner lacks a zero-check on :- _pendingOwner = newOwner
  ERC20Custody.sol::69 => TSSAddress = TSSAddress_
----------------------------------------------------------------------------------------------------------
Informational Issues

1. Function Visibility Can Be External
ZRC20.sol::83 => function name() public view virtual override returns (string memory) {
ZRC20.sol::91 => function symbol() public view virtual override returns (string memory) {
ZRC20.sol::99 => function decimals() public view virtual override returns (uint8) {
ZRC20.sol::107 => function totalSupply() public view virtual override returns (uint256) {
ZRC20.sol::116 => function balanceOf(address account) public view virtual override returns (uint256) {

2. State variable could be declared constant
WETH9.symbol should be constant


3. Use multiple `require()` and `if` statements instead of `&&`:
  WZETA.sol::49 => if (src != msg.sender && allowance[src][msg.sender] != uint(-1)) {

4. `<x> += <y>` costs more gas than `<x> = <x> + <y>` for state variables:
  WZETA.sol::21 => balanceOf[msg.sender] += msg.value;
  WZETA.sol::27 => balanceOf[msg.sender] -= wad;
  WZETA.sol::51 => allowance[src][msg.sender] -= wad;
  WZETA.sol::54 => balanceOf[src] -= wad;
  WZETA.sol::55 => balanceOf[dst] += wad;

5. Multiple mappings can be replaced with a single struct mapping:
  SystemContract_flatten.sol::120 => gasPriceByChainId[chainID] = price;
  SystemContract_flatten.sol::131 => gasCoinZRC20ByChainId[chainID] = zrc20;
  SystemContract_flatten.sol::143 => gasZetaPoolByChainId[chainID] = pool;

6. Missing Zero Address Validation
SystemContract.sol => constructor(address,address,address).wzeta_  lacks a zero-check on : - wZetaContractAddress = wzeta_ SystemContract.sol => constructor(address,address,address).uniswapv2Factory_ lacks a zero-check on : - uniswapv2FactoryAddress = uniswapv2Factory_ 

7. Dangerous Strict Equality
SafeERC20.safeTransfer(IERC20,address,uint256) uses a dangerous strict equality:
- prevBalance - _value == _token.balanceOf(address(this))
SafeERC20.safeTransferFrom(IERC20,address,address,uint256) uses a dangerous strict equality:
- prevBalance - _value == _token.balanceOf(_from) 


8. Using storage instead of memory for structs/arrays saves gas:
  ZetaTokenConsumerTrident.strategy.sol::82 => address[] memory pairPools = poolFactory.getPools(token0, token1, 0, 1);
  ZetaTokenConsumerTrident.strategy.sol::112 => address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1);
  ZetaTokenConsumerTrident.strategy.sol::179 => address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);
  ZetaTokenConsumerTrident.strategy.sol::82 => address[] memory path = new address[](2);
  ZetaTokenConsumerTrident.strategy.sol::148 => address[] memory pairPools = poolFactory.getPools(token0, token1, 0, 1);

9. Unsafe ERC20 Operation(s):
  ZetaTokenConsumerTrident.strategy.sol::264 => function transfer(address to, uint256 value) external returns (bool);
  ZetaTokenConsumerTrident.strategy.sol::298 => function transferFrom(address from, address to, uint256 value) external returns (bool);

10.
Using `bool`s for storage incurs overhead:
  ZetaTokenConsumerUniV3.strategy.sol::67 => _locked = true;
  ZetaTokenConsumerUniV3.strategy.sol::69 => _locked = false;

11.Constants in comparisons should appear on the left side:
  ZetaTokenConsumerUniV3.strategy.sol::78 => if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
  ZetaTokenConsumerUniV3.strategy.sol::79 => if (msg.value == 0) revert InputCantBeZero();
  ZetaTokenConsumerUniV3.strategy.sol::104 => if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
  ZetaTokenConsumerUniV3.strategy.sol::105 => if (inputTokenAmount == 0) revert InputCantBeZero();
  ZetaTokenConsumerUniV3.strategy.sol::129 => if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
  ZetaTokenConsumerUniV3.strategy.sol::165 => if (zetaTokenAmount == 0) revert InputCantBeZero();
  ZetaTokenConsumerUniV3.strategy.sol::164 => if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
  ZetaTokenConsumerUniV3.strategy.sol::187 => if (poolAddress == address(0)) {
  ZetaConnector.base.sol::118 => if (pauserAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();
  ZetaConnector.base.sol::130 => if (tssAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();
  ZetaConnector.base.sol::141 => if (tssAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
  ZetaConnector.non-eth.sol::72 => if (message.length > 0) {
  ZetaConnector.non-eth.sol::100 => if (message.length > 0) {2.
  UniswapV2Router02.sol::42 => if (IUniswapV2Factory(factory).getPair(tokenA, tokenB) == address(0)) {
  UniswapV2Router02.sol::46 => if (reserveA == 0 && reserveB == 0) {
  ZetaInteractor.sol::32 => if (zetaRevert.zetaTxSenderAddress != address(this)) revert InvalidZetaRevertCall();
  ZetaInteractor.sol::38 => if (zetaConnectorAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
  ZetaInteractor.sol::44 => if (msg.sender != address(connector)) revert InvalidCaller(msg.sender);
  ERC20Custody.sol::81 => if (TSSAddress_ == address(0)) {
  ERC20Custody.sol::93 => if (zetaFee_ == 0) {
  ERC20Custody.sol::108 => if (TSSAddress == address(0)) {
  ERC20Custody.sol::122 => if (TSSAddress == address(0)) {
  ERC20Custody.sol::177 => if (zetaFee != 0 && address(zeta) != address(0)) {

12.Use Shift Right/Left instead of Division/Multiplication if possible
ZetaConnector.non-eth.sol::16 => uint256 public maxSupply = 2 ** 256 - 1;

13.Functions guaranteed to revert when called by normal users can be marked `payable`:
  UUniswapV2ERC20.sol::81 => function permit(address owner, address spender, uint value, uint deadline, uint8 v, bytes32 r, bytes32 s) external {
  UniswapV2Factory.sol::40 => function setFeeTo(address _feeTo) external {
  UniswapV2Factory.sol::45 => function setFeeToSetter(address _feeToSetter) external {
  UniswapV2Pair.sol::66 => function initialize(address _token0, address _token1) external {

14.Use custom error instead of `assert`:
  UniswapV2Router02.sol::29 => assert(msg.sender == WETH); // only accept ETH via fallback from the WETH contract
  UniswapV2Router02.sol::55 => assert(amountAOptimal <= amountADesired);

15. The owner is a single point of failure and a centralization risk:
  ZetaInteractor.sol::54 => function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {

### Time spent:
8 hours