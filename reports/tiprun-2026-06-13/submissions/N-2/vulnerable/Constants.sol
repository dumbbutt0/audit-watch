// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

int256 constant FXP_32_ONE = 1 << 32;
uint64 constant NO_SYNTHETIC_DELTA_ASSET_ID = type(uint64).max;
int256 constant NO_SYNTHETIC_POSITION_ID = -1;

int256 constant FUNDING_INDEX_UPPER_BOUND = 2 ** 63;
int256 constant FUNDING_INDEX_LOWER_BOUND = -(2 ** 63);

int256 constant TOTAL_VALUE_UPPER_BOUND = 2 ** 63;
int256 constant TOTAL_VALUE_LOWER_BOUND = -(2 ** 63);

int256 constant TOTAL_VALUE_UPPER_BOUND_FXP = 2 ** 63 * FXP_32_ONE;
int256 constant TOTAL_VALUE_LOWER_BOUND_FXP = -(2 ** 63) * FXP_32_ONE;

int256 constant TOTAL_RISK_UPPER_BOUND = 2 ** 64;

int256 constant ASSET_RESOLUTION_LOWER_BOUND = 1;
int256 constant ASSET_RESOLUTION_UPPER_BOUND = 2 ** 64;

// Default collateral position index (replaces MARGIN_MODE_CROSS = 0)
uint64 constant DEFAULT_COLLATERAL_POSITION_INDEX = 0;

uint8 constant TYPE_DEPOSIT = 1;
uint8 constant TYPE_WITHDRAWAL = 2;
uint8 constant TYPE_FORCED_WITHDRAWAL = 3;
uint8 constant TYPE_TRADE = 4;
// 5: TYPE_FORCED_TRADE — removed (deprecated)
uint8 constant TYPE_TRANSFER = 6;
// 7: TYPE_CONDITIONAL_TRANSFER — removed (deprecated)
uint8 constant TYPE_LIQUIDATE = 8;
uint8 constant TYPE_DELEVERAGE = 9;
uint8 constant TYPE_FUNDING_TICK = 10;
uint8 constant TYPE_ORACLE_PRICES_TICK = 11;
uint8 constant TYPE_REGISTER_ACCOUNT = 12;
uint8 constant TYPE_SET_COLLATERAL_POSITION = 13;
uint8 constant TYPE_TRANSFER_COLLATERAL = 14;
uint8 constant TYPE_SET_SIGNER_PERMISSIONS = 16;
uint8 constant TYPE_ADD_SIGNERS = 17;
uint8 constant TYPE_SETTLEMENT = 18;
uint8 constant TYPE_SET_SYNTHETIC_ASSET_INFO = 19;
uint8 constant TYPE_ADMIN_SET_SIGNER_PERMISSIONS = 20;

// ─── Plugin capabilities (used by TransactionProcessor.registerPlugin) ───
// CAP_BALANCE_CHECK: universally needed — required wherever collateral leaves an
//   account (currently BalancePlugin's withdraw). Implementations check
//   "balance >= amount" or stronger.
// CAP_MARGIN_CHECK: perp-only — required by PositionManager.checkValidTransition
//   for maintenance-margin checks on trades / liquidations. Spot doesn't need it.
bytes32 constant CAP_BALANCE_CHECK = keccak256("BALANCE_CHECK");
bytes32 constant CAP_MARGIN_CHECK = keccak256("MARGIN_CHECK");
