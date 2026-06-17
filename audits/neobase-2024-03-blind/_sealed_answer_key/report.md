---
sponsor: "Canto"
slug: "2024-03-neobase"
date: "2024-04-26"
title: "Neobase Invitational"
findings: "https://github.com/code-423n4/2024-03-neobase-findings/issues"
contest: 355
---

# Overview

## About C4

Code4rena (C4) is an open organization consisting of security researchers, auditors, developers, and individuals with domain expertise in smart contracts.

A C4 audit is an event in which community participants, referred to as Wardens, review, audit, or analyze smart contract logic in exchange for a bounty provided by sponsoring projects.

During the audit outlined in this document, C4 conducted an analysis of the Neobase smart contract system written in Solidity. The audit took place between March 29 — April 3, 2024.

## Wardens

In Code4rena's Invitational audits, the competition is limited to a small group of wardens; for this audit, 5 wardens contributed reports:

  1. [Arabadzhiev](https://code4rena.com/@Arabadzhiev)
  2. [said](https://code4rena.com/@said)
  3. [0xsomeone](https://code4rena.com/@0xsomeone)
  4. [rvierdiiev](https://code4rena.com/@rvierdiiev)
  5. [carrotsmuggler](https://code4rena.com/@carrotsmuggler)

This audit was judged by [0xTheC0der](https://code4rena.com/@0xTheC0der).

Final report assembled by [thebrittfactor](https://twitter.com/brittfactorC4).

# Summary

The C4 analysis yielded an aggregated total of 8 unique vulnerabilities. Of these vulnerabilities, 1 received a risk rating in the category of HIGH severity and 7 received a risk rating in the category of MEDIUM severity.

Additionally, C4 analysis included 4 reports detailing issues with a risk rating of LOW severity or non-critical. There were also 2 reports recommending gas optimizations.

All of the issues presented here are linked back to their original finding.

# Scope

The code under review can be found within the [C4 Neobase repository](https://github.com/code-423n4/2024-03-neobase), and is composed of 4 smart contracts written in the Solidity programming language and includes 895 lines of Solidity code.

# Severity Criteria

C4 assesses the severity of disclosed vulnerabilities based on three primary risk categories: high, medium, and low/non-critical.

High-level considerations for vulnerabilities span the following key areas when conducting assessments:

- Malicious Input Handling
- Escalation of privileges
- Arithmetic
- Gas use

For more information regarding the severity criteria referenced throughout the submission review process, please refer to the documentation provided on [the C4 website](https://code4rena.com), specifically our section on [Severity Categorization](https://docs.code4rena.com/awarding/judging-criteria/severity-categorization).

# High Risk Findings (1)
## [[H-01] If a gauge that a user has voted for gets removed, their voting power allocated for that gauge will be lost](https://github.com/code-423n4/2024-03-neobase-findings/issues/18)
*Submitted by [Arabadzhiev](https://github.com/code-423n4/2024-03-neobase-findings/issues/18), also found by [said](https://github.com/code-423n4/2024-03-neobase-findings/issues/3)*

<https://github.com/code-423n4/2024-03-neobase/blob/d6e6127e6763b93c23ee95cdf7622fe950d9ed30/src/GaugeController.sol#L224-L229>

<https://github.com/code-423n4/2024-03-neobase/blob/d6e6127e6763b93c23ee95cdf7622fe950d9ed30/src/GaugeController.sol#L402>

### Impact

When a gauge that an user has voted for gets removed by the governance, their voting power allocated for that gauge will be lost forever.

### Proof of Concept

Due to the current way the `GaugeController::vote_for_gauge_weights` function is implemented, whenever a given gauge that users have voted for gets removed, all of the voting powers allocated by those users to that gauge will be permanently lost. The same issue has actually already been reported in [this report](https://github.com/code-423n4/2023-08-verwa-findings/issues/62) from the last Code4rena audit of the codebase. 

As it can be seen from the following snippet:

```solidity
    function testLostVotingPower() public {
        // prepare
        uint256 v = 10 ether;
        vm.deal(gov, v);
        vm.startPrank(gov);
        ve.createLock{value: v}(v);

        // add gauges
        gc.add_gauge(gauge1, 0);
        gc.add_type("", 0);
        gc.add_gauge(gauge2, 1);

        // all-in on gauge1
        gc.vote_for_gauge_weights(gauge1, 10000);

        // governance removes gauge1
        gc.remove_gauge_weight(gauge1);
        gc.remove_gauge(gauge1);

        // cannot vote for gauge2
        vm.expectRevert("Used too much power");
        gc.vote_for_gauge_weights(gauge2, 10000);

        // cannot remove vote for gauge1
        vm.expectRevert("Gauge not added"); // @audit remove after mitigation
        gc.vote_for_gauge_weights(gauge1, 0);

        // cannot vote for gauge2 (to demonstrate again that voting power is not removed)
        vm.expectRevert("Used too much power");  // @audit remove after mitigation
        gc.vote_for_gauge_weights(gauge2, 10000);
    }
```

the recommended fix from that report has actually been implemented.

However, there are two other changes there as well. The `isValidGauge` mapping has been replaced with a new one named `gauge_types_`, which practically serves the same purpose as the old one in the context of this snippet. More importantly though, a new require statement has been added, as it can be seen on the last code line of the snippet, which checks whether the gauge type is greater than `0` and reverts otherwise. Since the gauge type for a given gauge address can only be `0`, in the case where the gauge does not actually exist (i.e. it has been removed or it was never created in the first place), this means that the implemented fix will no longer work and because of that the issue is once again present in the current implementation of the `GaugeController`.

The following coded PoC, which is a modification of the one in the above linked report verifies the existence of the issue:

```solidity
    function testLostVotingPower() public {
        // prepare
        uint256 v = 10 ether;
        vm.deal(gov, v);
        vm.startPrank(gov);
        ve.createLock{value: v}(v);

        // add gauges
        gc.add_gauge(gauge1, 0);
        gc.change_gauge_weight(gauge1, 100);
        gc.add_type("", 100);
        gc.add_gauge(gauge2, 1);
        gc.change_gauge_weight(gauge2, 100);

        // all-in on gauge1
        gc.vote_for_gauge_weights(gauge1, 10000);

        // governance removes gauge1
        gc.remove_gauge_weight(gauge1);
        gc.remove_gauge(gauge1);

        // cannot vote for gauge2
        vm.expectRevert("Used too much power");
        gc.vote_for_gauge_weights(gauge2, 10000);

        // cannot remove vote for gauge1
        vm.expectRevert("Gauge not added"); // @audit remove after mitigation
        gc.vote_for_gauge_weights(gauge1, 0);

        // cannot vote for gauge2 (to demonstrate again that voting power is not removed)
        vm.expectRevert("Used too much power");  // @audit remove after mitigation
        gc.vote_for_gauge_weights(gauge2, 10000);
    }
```

### Recommended Mitigation Steps

Remove the additional require statement that checks whether the gauge type for the `_gauge_addr` is different from `0`, in order to allow users to remove their votes from removed gauges:

```diff
    function vote_for_gauge_weights(address _gauge_addr, uint256 _user_weight) external {
        require(_user_weight >= 0 && _user_weight <= 10_000, "Invalid user weight");
        require(_user_weight == 0 || gauge_types_[_gauge_addr] != 0, "Can only vote 0 on non-gauges"); // We allow withdrawing voting power from invalid (removed) gauges
        VotingEscrow ve = votingEscrow;
        (
            ,
            /*int128 bias*/
            int128 slope_, /*uint256 ts*/

        ) = ve.getLastUserPoint(msg.sender);
        require(slope_ >= 0, "Invalid slope");
        uint256 slope = uint256(uint128(slope_));
        uint256 lock_end = ve.lockEnd(msg.sender);
        uint256 next_time = ((block.timestamp + WEEK) / WEEK) * WEEK;
        require(lock_end > next_time, "Lock expires too soon");

        int128 gauge_type = gauge_types_[_gauge_addr] - 1;
-       require(gauge_type >= 0, "Gauge not added");
        ...
    }
```

### Assessed type

Invalid Validation

**[zjesko (Neobase) confirmed](https://github.com/code-423n4/2024-03-neobase-findings/issues/18#issuecomment-2040756170)**

**[0xTheC0der (judge) commented](https://github.com/code-423n4/2024-03-neobase-findings/issues/18#issuecomment-2041583751):**
 > Voting power is considered an asset and can be lost in this scenario without malicious governance intent or mistake.

***

# Medium Risk Findings (7)
## [[M-01] In case a gauge weight reduction is performed via `GaugeController::change_gauge_weight`, it is possible that all functions will stop functioning permanently for that gauge](https://github.com/code-423n4/2024-03-neobase-findings/issues/25)
*Submitted by [Arabadzhiev](https://github.com/code-423n4/2024-03-neobase-findings/issues/25)*

If the weight of a given gauge has been manually changed using the `GaugeController::change_gauge_weight` function, all functions related to that gauge might become permanently DoSed.

### Proof of Concept

This issue has been reported in [this](https://github.com/code-423n4/2023-08-verwa-findings/issues/206) and [this](https://github.com/code-423n4/2023-08-verwa-findings/issues/386) report from the previous Code4rena audit of the codebase. However, by the looks of it, no fix has been applied in order to mitigate it, so it is still present.

### Recommended Mitigation Steps

Whenever `pt.slope` is less than `d.slope`, set the value of `pt.slope` to `0`:

```diff
        if (pt.bias > d_bias) {
            pt.bias -= d_bias;
            uint256 d_slope = changes_weight[_gauge_addr][t];
-           pt.slope -= d_slope;
+           if(pt.slope >= d.slope) {
+               pt.slope -= d_slope;
+           } else {
+               pt.slope = 0;
+           }
        } else {
            pt.bias = 0;
            pt.slope = 0;
        }
```

### Assessed type

Under/Overflow

**[zjesko (Neobase) confirmed](https://github.com/code-423n4/2024-03-neobase-findings/issues/25#issuecomment-2040758698)**

**[0xTheC0der (judge) decreased severity to Medium and commented](https://github.com/code-423n4/2024-03-neobase-findings/issues/25#issuecomment-2041580331):**
 > Assets not at direct risk, but the function of the protocol or its availability could be impacted. `change_gauge_weight` is only callable by the governance, but no admin mistake is required for this to happen.

**[Arabadzhiev (warden) commented](https://github.com/code-423n4/2024-03-neobase-findings/issues/25#issuecomment-2047423805):**
 > This issue will actually lead to an absolutely certain loss of funds in the event where a gauge weight reduction is performed via `GaugeController::change_gauge_weight`. This is because inside of the `LendingLedger::update_market` function ,which is called inside of both `LendingLedger::claim` and `LendingLedger::sync_ledger` there is [a call to `GaugeController::gauge_relative_weight_write`](https://github.com/code-423n4/2024-03-neobase/blob/d6e6127e6763b93c23ee95cdf7622fe950d9ed30/src/LendingLedger.sol#L83):
> 
> ```solidity
>     market.accCantoPerShare += uint128(
>         (blockDelta *
>             cantoPerBlock[epoch] *
>             gaugeController.gauge_relative_weight_write(_market, epochTime)) / marketSupply
>     );
> ```
> 
> What this means is that since `GaugeController::gauge_relative_weight_write` calls `GaugeController::_get_weight` internally, whenever a gauge weight reduction is performed, all of those functions will become permanently DoSed; making it impossible for users to claim their rewards for a given market/gauge from the `LendingLedger`. Also, if the gauge that the weight reduction is performed on uses a `LiquidityGauge`, the users that have deposited into that liquidity gauge won't be able to withdraw their underlying assets from it, since in the `LiquidityGauge::_afterTokenTransfer` hook there are calls to `LendingLedger::sync_ledger`.
> 
> Because of that, I believe that this issue deserves to be judged as one of a High severity, rather than a Medium.

**[0xTheC0der (judge) commented](https://github.com/code-423n4/2024-03-neobase-findings/issues/25#issuecomment-2048167848):**
 > @Arabadzhiev - From a judging perspective my reasoning is as follows:  
> The original report, which is already quite minimalist, states:  
> > ... , all functions related to that gauge might become permanently DoSed.
> 
> Furthermore, we have a [verdict about additional warden output during PJQA](https://docs.code4rena.com/awarding/judging-criteria/supreme-court-decisions-fall-2023#verdict-standardization-of-additional-warden-output-during-qa):
> > No new information should be introduced and considered in PJQA. Elaborations of the already introduced information can be considered (e.g. tweaking a POC), from either the Judge or the Warden, but they will only count towards the validity of the issue, not its quality score.
> 
> Although the underlying issue might qualify for High severity in case more elaboration of impacts and/or a PoC was provided in the original report, it seems to be fair and most in line with our present ruling to maintain Medium severity.

**[Arabadzhiev (warden) commented](https://github.com/code-423n4/2024-03-neobase-findings/issues/25#issuecomment-2049373949):**
 > I have one final note to make. In [this report](https://github.com/code-423n4/2023-08-verwa-findings/issues/206) from the previous audit of the codebase that I have linked to in my report, the following is stated in its impact section:
> 
> > ... the impact is that the entire gauge is useless, voting powers are permanently locked there and its weight is impossible to change, so the impact is high.
> 
> Given that this is actually a part of the original report and that issue #18 was judged as a High under pretty much the same reasoning, doesn't this issue also fall within the High severity category because of that?

**[0xTheC0der (judge) commented](https://github.com/code-423n4/2024-03-neobase-findings/issues/25#issuecomment-2049522460):**
 > I treat it as a supporting reference but not as a "replacement" for your report.  
> 
> Although the PoC and reasoning there *might* fully apply to this audit's code in scope, it's reasonable & fair to expect the present report to include impact-based reasoning for High severity and/or a coded PoC which undoubtedly applies to the current audit/code in scope.  
> 
> In contrast, [#18](https://github.com/code-423n4/2024-03-neobase-findings/issues/18) clearly argues and proves in the original report that voting power will be lost/locked.
> 
> I understand if you have reservations about my judgement as this one is definitely a narrow path to walk. Nevertheless, your input is legit and appreciated.

***

## [[M-02] `GaugeController::remove_gauge` will always revert whenever the gauge it's being called or has any weight attached to it](https://github.com/code-423n4/2024-03-neobase-findings/issues/22)
*Submitted by [Arabadzhiev](https://github.com/code-423n4/2024-03-neobase-findings/issues/22), also found by [said](https://github.com/code-423n4/2024-03-neobase-findings/issues/2)*

`GaugeController::remove_gauge` will always revert when it is called for gauges with weight that is `!= 0`.

### Proof of Concept

The current implementation of the `GaugeController::remove_gauge` function has a major flaw within it. Because it erases the gauge type of the gauge being removed prior to calling `_remove_gauge_weight`, it will always revert whenever it is called for gauges that have a weight value different from `0`. This is due to the fact that in `_remove_gauge_weight` there are subtractions being made to gauge type mappings (where the gauge type key being used will be `-1`, since the gauge type for the gauge has already been erased) using values from gauge mappings.

```solidity
    function _remove_gauge_weight(address _gauge) internal {
        int128 gauge_type = gauge_types_[_gauge] - 1;
        uint256 next_time = ((block.timestamp + WEEK) / WEEK) * WEEK;

        uint256 old_weight_bias = _get_weight(_gauge);
        uint256 old_weight_slope = points_weight[_gauge][next_time].slope;
        uint256 old_sum_bias = _get_sum(gauge_type);

        points_weight[_gauge][next_time].bias = 0;
        points_weight[_gauge][next_time].slope = 0;

        uint256 new_sum = old_sum_bias - old_weight_bias;
        points_sum[gauge_type][next_time].bias = new_sum;
        points_sum[gauge_type][next_time].slope -= old_weight_slope;
        // We have to cancel all slope changes (gauge specific and global) that were caused by this gauge
        // This is not very efficient, but does the job for a governance function that is called very rarely
        for (uint256 i; i < 263; ++i) {
            uint256 time_to_check = next_time + i * WEEK;
            uint256 gauge_weight_change = changes_weight[_gauge][time_to_check];
            if (gauge_weight_change > 0) {
                changes_weight[_gauge][time_to_check] = 0;
                changes_sum[gauge_type][time_to_check] -= gauge_weight_change;
            }
        }
    }
```

Although an argument can be made that this issue can be avoided by calling `GaugeController::remove_gauge_weight` prior to calling `GaugeController::remove_gauge`, it can still prove to be quite problematic in an event where an urgent removal of a given gauge is required. The initial `remove_gauge` call for doing so gets reverted, since the governance didn't know about the issue and the proper way of bypass it up until that point. In that case, a separate new governance proposal will have to be executed in order to remove the gauge, which will take a significant amount of time.

The following short coded PoC demonstrates the issue:

```solidity
    function testRemoveGaugeArithmeticUnderflow() public {
        uint256 v = 10 ether;
        vm.deal(gov, v);
        vm.startPrank(gov);
        ve.createLock{value: v}(v);

        gc.add_gauge(gauge1, 0);

        gc.vote_for_gauge_weights(gauge1, 10000);

        vm.expectRevert(abi.encodeWithSignature("Panic(uint256)", 0x11)); // arithmetic error panic code
        gc.remove_gauge(gauge1);
    }
```

### Recommended Mitigation Steps

Call `_remove_gauge_weight` prior to erasing the gauge type of the gauge:

```diff
    function remove_gauge(address _gauge) external onlyGovernance {
        require(gauge_types_[_gauge] != 0, "Invalid gauge address");
-       gauge_types_[_gauge] = 0;
-       _remove_gauge_weight(_gauge);
+       _remove_gauge_weight(_gauge);
+       gauge_types_[_gauge] = 0;
        emit GaugeRemoved(_gauge);
    }   
```

### Assessed type

Under/Overflow

**[zjesko (Neobase) confirmed](https://github.com/code-423n4/2024-03-neobase-findings/issues/22#issuecomment-2040757439)**

***

## [[M-03] Issue from previous audit still present: Gauge can have bigger weight than was intended by protocol](https://github.com/code-423n4/2024-03-neobase-findings/issues/17)
*Submitted by [rvierdiiev](https://github.com/code-423n4/2024-03-neobase-findings/issues/17)*

[M-01 from previous audit is still present](https://github.com/code-423n4/2023-08-verwa-findings/issues/294). In this issue, the sponsor said [they fixed it](https://github.com/code-423n4/2023-08-verwa-findings/issues/294#issuecomment-1698755740). I tried to check how it was fixed, but the link doesn't work for me.

But `change_gauge_weight` function [still exists](https://github.com/code-423n4/2024-03-neobase/blob/main/src/GaugeController.sol#L346-L348) which makes it possible to reproduce this. Also `remove_gauge_weight` function is present, that allows [to completely remove gauge](https://github.com/code-423n4/2024-03-neobase/blob/main/src/GaugeController.sol#L378-L380) and i think that fix was to remove `change_gauge_weight` function.

### Impact

Gauge can have bigger weight than was intended by protocol.

### Tools Used

VsCode

### Recommendation

Remove `change_gauge_weight` function.

### Assessed type

Error

**[zjesko (Neobase) confirmed](https://github.com/code-423n4/2024-03-neobase-findings/issues/17#issuecomment-2040754015)**

***

## [[M-04] Improper adjustment of Lending Ledger configuration](https://github.com/code-423n4/2024-03-neobase-findings/issues/16)
*Submitted by [0xsomeone](https://github.com/code-423n4/2024-03-neobase-findings/issues/16), also found by [carrotsmuggler](https://github.com/code-423n4/2024-03-neobase-findings/issues/19)*

<https://github.com/code-423n4/2024-03-neobase/blob/main/src/LendingLedger.sol#L136-L149> 

<https://github.com/code-423n4/2024-03-neobase/blob/main/src/LendingLedger.sol#L173-L185>

### Description

The `LendingLedger` utilizes an approximation system (to evaluate the time that has elapsed between two block numbers) which contains adjustable values. Additionally, it permits the governance to adjust the `cantoPerBlock` value of multiple epochs at any time.

The way these values are adjusted is insecure and thus can cause them to retroactively apply to markets that have not yet been updated.

In the case of the `LendingLedger::setBlockTimeParameters`, a notice exists within the `LendingLedger::update_market` function that warns that:

> If this ever drifts significantly, the average block time and/or reference block time & number can be updated. However, `update_market` needs to be called for all markets beforehand.

I do not consider the warning sufficient, as the `LendingLedger::setRewards` function illustrates that the problem is not understood accurately.

Any market that was not updated on the exact same block that either rewards or the block time parameters are adjusted will have these adjustments retroactively applied, leading to over-estimations or under-estimations of the rewards that should be attributed to the market.

### Impact

Reward measurements for markets that were not updated **in the exact same block** that rewards and/or block-time parameters were re-configured will result in over- or under-estimations, depending on the direction of these configurations.

### Severity Rationalization

Administrator mistakes usually fall under QA/Analysis reports; however, in this circumstance, the mistake is not based on input but rather on the state of the contract. Additionally, there are cases whereby the change cannot be performed securely (i.e. if the number of markets introduced would reach the gas limit if all are attempted to be updated at the same block).

Based on the above, I believe this constitutes a valid operational vulnerability that stems from an improperly coded configuration procedure for both rewards and block time parameters.

While there is a warning for the `LendingLedger::setBlockTimeParameters` function, it is located in an entirely different function and is insufficient, in my opinion. Even if considered sufficient, there is absolutely no warning or indication that the same restriction applies for the `LendingLedger::setRewards` function.

This submission may be split into two distinct ones if the reward-related and block-time-related impacts are considered distinct; however, I grouped them under the same submission as they pertain to the same operation (update of all markets) being absent albeit from two different code segments.

### Proof of Concept

I have coded the following PoC in `foundry` for completeness. Please add the following segment after `LendingLedger.t.sol::setupStateBeforeClaim`:

```solidity
function testInsecureRewardUpdate() public {
    setupStateBeforeClaim();

    // Based on `LendingLedger.t.sol::testClaimValidLenderOneBlock`, the reward of the `lender` should be `amountPerBlock - 1` at this time point
    vm.roll(BLOCK_EPOCH * 5 + 1);

    // We update the rewards of the epochs without updating the markets
    vm.prank(governance);
    uint256 newRewardPerBlock = amountPerBlock * 2;
    ledger.setRewards(fromEpoch, toEpoch, newRewardPerBlock);

    // We claim the `lender` rewards, should be `amountPerBlock` based on `LendingLedger.t.sol::testClaimValidLenderOneBlock`
    uint256 balanceBefore = address(lender).balance;
    vm.prank(lender);
    vm.roll(BLOCK_EPOCH * 5 + 1);
    ledger.claim(lendingMarket);
    uint256 balanceAfter = address(lender).balance;

    // Assertion will fail
    assertEq(balanceAfter - balanceBefore, amountPerBlock - 1);
}
```

To execute the above test, I recommend the following CLI instruction:

```
forge test --match-test testInsecureRewardUpdate -vv 
```

### Recommended Mitigation Steps

I advise all markets added to a `LendingLedger` to be tracked and iterated whenever either of the submission's referenced functions is executed, ensuring that all markets are indeed updated in the same block.

As a gas-optimal alternative, the total markets of the `LendingLedger` could be tracked as a number. The aforementioned adjustment functions could then accept an input array that would contain all markets, permitting a `for` loop to iterate them, ensure they are distinct (i.e. in strictly ascending order), and ensure that the total number of input markets is equal to the total number of registered markets.

Alternatively, and as a solution solely for the `LendingLedger::setRewards` function, the epochs that are mutated could be restricted to be future ones and thus never result in a retroactive application.

### Assessed type

Governance

**[0xTheC0der (judge) commented](https://github.com/code-423n4/2024-03-neobase-findings/issues/16#issuecomment-2035626708):**
 > Referring to README:  
> > **Publicly Known Issues**
> > **Mistakes by Governance:**
> > We assume that all calls that are performed by the governance address are performed with the correct parameters.
> 
> However, it's not just about correct call parameters but also about correct call timing (`reward-related and block-time-related impacts`); therefore, leaving this for sponsor review.
>
> The current duplicate [#19](https://github.com/code-423n4/2024-03-neobase-findings/issues/19) is more affected by the README; will reconsider during judging.

**[OpenCoreCH (Neobase) confirmed](https://github.com/code-423n4/2024-03-neobase-findings/issues/16#issuecomment-2041163016)**

**[0xTheC0der (judge) commented](https://github.com/code-423n4/2024-03-neobase-findings/issues/16#issuecomment-2043832907):**
 > > Administrator mistakes usually fall under QA/Analysis reports; however, in this circumstance, the mistake is not based on input but rather on the state of the contract.
> 
> I agree with this assessment in the report.

***

## [[M-05] Truncation exploitation of partial transfer system](https://github.com/code-423n4/2024-03-neobase-findings/issues/15)
*Submitted by [0xsomeone](https://github.com/code-423n4/2024-03-neobase-findings/issues/15)*

The `LendingLedger::sync_ledger` function is meant to permit partial transfers of each user's positions by updating the `amount`, `rewardDebt`, and `secRewardDebt` variables.

In the current system, the partial transfers performed are insecure as a non-zero `_delta` can be transferred with zero-value `rewardDebt` and `secRewardDebt` increments.

Specifically, any non-zero `_delta` value that would result in `(_delta * market.accCanotPerShare)/ 1e18` to result in a truncation can be transferred multiple times to exploit the truncation.

As the `LendingLedger::claim` function will utilize the **cumulative `user.amount` value**, multiple `_delta` transfers can result in a non-truncated `(user.amount * market.accCanotPerShare) / 1e18` value that would result in immediate profit as the user would be able to instantly claim the truncated amounts.

### Impact

A user is able to claim rewards from the `LendingLedger` without any time elapsing and without being eligible for them by taking advantage of debt truncations in the `LendingLedger::sync_ledger` function.

This exploit can be repeated infinitely to compound the rewards extracted via this mechanism.

### Proof of Concept

I coded a simple PoC in `foundry`, simply add the following function after the `LendingLedger.t.sol::setupStateBeforeClaim` function:

```solidity
function testFreeRewards() public {
    setupStateBeforeClaim();

    // Ensure accCantoPerShare is not 1e18
    vm.prank(lender);
    vm.roll(BLOCK_EPOCH * 5 + 1);
    ledger.claim(lendingMarket);

    // Demonstrate that user can claim but will acquire `0` due to having no balance
    address noBalanceLender = users[2];
    uint256 balanceBefore = address(noBalanceLender).balance;
    vm.prank(noBalanceLender);
    ledger.claim(lendingMarket);
    uint256 balanceAfter = address(noBalanceLender).balance;

    // Ensure user is normally entitled to no reward
    assertEq(balanceBefore, balanceAfter);

    // We calculate the exact amount that we would need to transfer to capture an instant reward
    (uint256 currentAccCantoPerShare, , ) = ledger.marketInfo(
        lendingMarket
    );
    uint256 remainder = currentAccCantoPerShare % 1e18;
    uint256 numberOfTimesForWholeValue = 1e18 / remainder;

    for (uint256 i = 0; i <= numberOfTimesForWholeValue; i++) {
        // We simulate a LiquidityGauge::_afterTokenTransfer between lender and noBalanceLender
        vm.prank(lendingMarket);
        ledger.sync_ledger(lender, -1);

        vm.prank(lendingMarket);
        ledger.sync_ledger(noBalanceLender, 1);
    }

    balanceBefore = address(noBalanceLender).balance;
    vm.prank(noBalanceLender);
    ledger.claim(lendingMarket);
    balanceAfter = address(noBalanceLender).balance;

    uint256 profit = balanceAfter - balanceBefore;

    // Ensure user is normally entitled to no reward, the assertion will fail
    assertEq(profit, 0);
}
```

To execute the above test concisely, kindly perform the following:

```
forge test --match-test testFreeRewards -vv
```

### Severity Rationalization

The above PoC is meant to demonstrate the flaw and does not do so efficiently. In detail, the profitability of the attack versus its gas cost is inherently attached to the error between the divisor (`1e18`) and the `cantoPerShare` value.

For an error equal to `1e18 - 1`, the attack can be executed in as little as two transfers and can be compounded infinitely. Even if we consider the attack not profitable, an off-by-one error has wider implications in the accounting system of the `LendingLedger`.

Specifically, the off-by-one error will cause the cumulative rewards of the system to not satisfy all awarded users. As a result, the last user who attempts to claim rewards will cause their claim to fail.

We can argue that there are a lot of avenues to resolve the accounting error once it presents itself; however, the value extracted would be irreversible, and the failure itself could be perpetuated.

### Recommended Mitigation Steps

For the mechanism to behave correctly, it should penalize rewards rather than penalize debt when truncation occurs. To achieve this, the subtraction execution path of `LendingLedger::sync_ledger` should continue subtracting the rounded-down amount from debt while the addition execution path should round the debt added upwards.

### Assessed type

Math

**[OpenCoreCH (Neobase) confirmed and commented](https://github.com/code-423n4/2024-03-neobase-findings/issues/15#issuecomment-2041162877):**
 > That's true and rounding up there is probably a good idea (although it could generate underflows in `claim` if this is not changed as well). However, I am not fully convinced about the impact. If `(uint256(_delta) * market.accCantoPerShare)` is for instance `1e18 - 1`, the "correct" debt value is `0.999999...`, so rounded up it would be `1`. We then underestimate the debt by exactly `1` token, which has a value of `10^{-18}` USD in the case of cNOTE.

**[0xTheC0der (judge) commented](https://github.com/code-423n4/2024-03-neobase-findings/issues/15#issuecomment-2041594337):**
 > Limited impact but high likelihood since there is no boundary on the repeatability of the attack, which can lead to further impacts (see Severity Rationalization of report.)

***

## [[M-06] Improper parallel time system](https://github.com/code-423n4/2024-03-neobase-findings/issues/10)
*Submitted by [0xsomeone](https://github.com/code-423n4/2024-03-neobase-findings/issues/10), also found by [carrotsmuggler](https://github.com/code-423n4/2024-03-neobase-findings/issues/12), [rvierdiiev](https://github.com/code-423n4/2024-03-neobase-findings/issues/11), and [said](https://github.com/code-423n4/2024-03-neobase-findings/issues/4)*

The `LendingLedger` system will employ a distinct time system from the `VotingEscrow` and `GaugeController` implementations whereby rewards are denoted per block rather than based on time.

From an implementation perspective, there is no real reason to implement this distinction as the `LendingLedger` can be simply updated to utilize a reward-per-second system instead.

To work around this discrepancy, the `LendingLedger` implements an imprecise time measurement for evaluating the `epochTime` whenever a market update occurs through `LendingLedger::update_market`.

In detail, the following variables are configured and utilized:

- `referenceBlockTime`: Indicates the time from which a reference data point is drawn from.
- `referenceBlockNumber`: Indicates the block number from which we should count the blocks that have elapsed since the reference block time.
- `averageBlockTime`: The average block time per block expressed in milliseconds.

The vulnerability lies in the fact that an overestimation of the time (i.e. a future time) will result in a `IGaugeController::gauge_relative_weight_write` result of `0`, effectively nullifying the full reward of the epoch which may be up to `1 week` worth of rewards.

Specifically, `GaugeController::_gauge_relative_weight` will yield `0` in the case the total weight of the epoch is `0` (`points_total`), a case that will occur 100% if the input time of the function exceeds the current `block.timestamp` to an extent that it would cause it to flow into the next `WEEK`.

This error does not need to necessarily be a full `WEEK`, as a timestamp at `5 weeks - 1` will fall in week `4` which can be calculated, while a timestamp at `5 weeks` will fall in week `5` which would be in the future and thus not calculate-able.

It is impossible to programmatically approximate the number of blocks in a particular time period for any blockchain; meaning, that the vulnerability will manifest itself with a high possibility as either an overestimation or underestimation of time elapsed for the number of blocks will occur in the `LendingLedger`.

An overestimation of time elapsed by the `LendingLedger::update_market` function will lead to the rewards for a particular epoch being `0` even though the gauge may have had a non-zero relative weight due to the weight not having been tracked yet for the miscalculated future timestamp.

### Impact

The non-zero rewards that should have been distributed for the latest epoch will not be processed correctly and would be considered `0`.

### Proof of Concept

I tried implementing a PoC in the `forge` toolkit; however, the test harness of `LendingLedger.t.sol` utilizes a **mock `GaugeController` (`DummyGaugeController`)** that yields a fixed value for the lookup and thus would require extensive time to re-build the test suite for just this PoC.

The actual vulnerability's validity can be observed in the `GaugeController::gauge_relative_weight_write` function, which also denotes that the `_time` should be a timestamp in the past or present.

If a future timestamp is provided (which the code permits), the `GaugeController::_get_weight` and `GaugeController::_get_total` functions would update the weights in the system up to the current `block.timestamp`, and the future week queried by the `GaugeController::_gauge_relative_weight` would yield `0`.

### Severity Rationalization

Due to the blockchain's by-design nature, it is impossible to precisely measure the time that has elapsed between two block numbers. As such, the likelihood at which this vulnerability would manifest is high.

A severity of "Medium" was assessed because even though rewards would be lost, they can be "re-instated" via administrative action through adjustment of the rewards per block to carry the rewards over to the next period.

A severity of "High" could be valid if we eliminate administrative intervention, and we consider that the `secRewardDebt` data point would become corrupted. Although meant for secondary rewards, it presently remains unused and would be corrupted in the aforementioned scenario as the `accCantoPerShare` value would be incremented by `0` while the `secRewardsPerShare` would be incremented by a non-zero value.

### Recommended Mitigation Steps

I would advise the `LendingLedger` implementation to be updated to a time-based reward mechanism instead, ensuring that it remains in sync with the `GaugeController`.

### Assessed type

Math


**[OpenCoreCH (Neobase) confirmed](https://github.com/code-423n4/2024-03-neobase-findings/issues/10#issuecomment-2041160486)**

**[0xTheC0der (judge) commented](https://github.com/code-423n4/2024-03-neobase-findings/issues/10#issuecomment-2043791831):**
 > Core issue of this group if findings: Parallel time system and resulting rewards epoch drift/mismatch due to time estimation based on `block.number` and related parameters (see report).
>
 > Selected for report due to overall best elaboration of the "parallel time system" and its impacts.

***

## [[M-07] When the `unlockOverride` flag is true, users can "freely" vote for gauge weights.](https://github.com/code-423n4/2024-03-neobase-findings/issues/5)
*Submitted by [said](https://github.com/code-423n4/2024-03-neobase-findings/issues/5), also found by [Arabadzhiev](https://github.com/code-423n4/2024-03-neobase-findings/issues/14)*

<https://github.com/code-423n4/2024-03-neobase/blob/main/src/VotingEscrow.sol#L295-L311>

<https://github.com/code-423n4/2024-03-neobase/blob/main/src/VotingEscrow.sol#L315-L350>

### Impact

Due to the lack of restrictions on `createLock` and `increaseAmount` when the `unlockOverride` flag is set to true, users can `createLock`/`increaseAmount` on `VotingEscrow`, vote for a gauge inside the `GaugeController` to increase the desired gauge's weight, and then immediately withdraw the locked native token from `VotingEscrow` to boost their desired gauge's weight for "free".

### Proof of Concept

When users lock their native token on `VotingEscrow`, they gain the ability to increase gauge weight on `GaugeController` based on the amount of native token they've locked, at the expense of having to lock the native token for `LOCKTIME` (1825 days) period, or until the governance toggle `unlockOverride` and set it to true.

<https://github.com/code-423n4/2024-03-neobase/blob/main/src/VotingEscrow.sol#L357>

```solidity
    function withdraw() external nonReentrant {
        LockedBalance memory locked_ = locked[msg.sender];
        // Validate inputs
        require(locked_.amount > 0, "No lock");
>>>     require(locked_.end <= block.timestamp || unlockOverride, "Lock not expired");
        require(locked_.delegatee == msg.sender, "Lock delegated");
        // Update lock
        uint256 amountToSend = uint256(uint128(locked_.amount));
        LockedBalance memory newLocked = _copyLock(locked_);
        newLocked.amount = 0;
        newLocked.end = 0;
        newLocked.delegated -= int128(int256(amountToSend));
        newLocked.delegatee = address(0);
        locked[msg.sender] = newLocked;
        newLocked.delegated = 0;
        // oldLocked can have either expired <= timestamp or zero end
        // currentLock has only 0 end
        // Both can have >= 0 amount
        _checkpoint(msg.sender, locked_, newLocked);
        // Send back deposited tokens
        (bool success, ) = msg.sender.call{value: amountToSend}("");
        require(success, "Failed to send CANTO");
        emit Withdraw(msg.sender, amountToSend, LockAction.WITHDRAW, block.timestamp);
    }
```

However, due to the lack of restrictions on calling `createLock` and `increaseAmount` when `unlockOverride` is set to true, users can lock their native token, use it to vote on `GaugeController`, and immediately withdraw the token to manipulate and boost the desired gauge weights.

Add the following test inside `GaugeController.t.sol`:

```solidity
    function testVoteGaugeWeightUnlockOverride() public {
        vm.startPrank(gov);
        gc.add_gauge(gauge1, 0);
        gc.add_gauge(gauge2, 0);
        ve.toggleUnlockOverride();
        vm.stopPrank();

        vm.startPrank(user1);
        ve.createLock{value: 1 ether}(1 ether);
        uint256 nextEpoch = ((block.timestamp + WEEK) / WEEK) * WEEK;
        gc.vote_for_gauge_weights(gauge1, 10000); // vote 100% for gauge1
        ve.withdraw();
        vm.stopPrank();

        console.logUint(gc.gauge_relative_weight_write(gauge1, nextEpoch));
    }
```

Run the test:

```
forge test --match-contract GaugeControllerTest --match-test testVoteGaugeWeightUnlockOverride -vv
```

Output:

```
Logs:
  1000000000000000000
```

From the test, it can be observed that relative gauge weight's of desired gauge increased for next epoch.

### Recommended Mitigation Steps

Considering that `unlockOverride` is potentially used to finish the lock time early for all users inside `VotingEscrow`, consider adding a check inside `createLock` and `increaseAmount`. If `unlockOverride` is set to true, revert the operation.

### Assessed type

Invalid Validation

**[zjesko (Neobase) confirmed](https://github.com/code-423n4/2024-03-neobase-findings/issues/5#issuecomment-2040750735)**

***

# Low Risk and Non-Critical Issues

For this audit, 4 reports were submitted by wardens detailing low risk and non-critical issues. The [report highlighted below](https://github.com/code-423n4/2024-03-neobase-findings/issues/7) by **said** received the top score from the judge.

*The following wardens also submitted reports: [carrotsmuggler](https://github.com/code-423n4/2024-03-neobase-findings/issues/21), [rvierdiiev](https://github.com/code-423n4/2024-03-neobase-findings/issues/8), and [Arabadzhiev](https://github.com/code-423n4/2024-03-neobase-findings/issues/24).*

## [01] `_remove_gauge_weight()` in GaugeController.sol should update points total

`points_total` does not immediately reflect the current value after the removal of gauge weight.

### Proof of Concept

It can be observed that inside ` _remove_gauge_weight()` function, it will only update `points_weight` of the gauge and `points_sum` of the gauge type, but not updating `points_total`:

```solidity
    function _remove_gauge_weight(address _gauge) internal {
        int128 gauge_type = gauge_types_[_gauge] - 1;
        uint256 next_time = ((block.timestamp + WEEK) / WEEK) * WEEK;

        uint256 old_weight_bias = _get_weight(_gauge);
        uint256 old_weight_slope = points_weight[_gauge][next_time].slope;
        uint256 old_sum_bias = _get_sum(gauge_type);

        points_weight[_gauge][next_time].bias = 0;
        points_weight[_gauge][next_time].slope = 0;

        uint256 new_sum = old_sum_bias - old_weight_bias;
        points_sum[gauge_type][next_time].bias = new_sum;
        points_sum[gauge_type][next_time].slope -= old_weight_slope;
        // We have to cancel all slope changes (gauge specific and global) that were caused by this gauge
        // This is not very efficient, but does the job for a governance function that is called very rarely
        for (uint256 i; i < 263; ++i) {
            uint256 time_to_check = next_time + i * WEEK;
            uint256 gauge_weight_change = changes_weight[_gauge][time_to_check];
            if (gauge_weight_change > 0) {
                changes_weight[_gauge][time_to_check] = 0;
                changes_sum[gauge_type][time_to_check] -= gauge_weight_change;
            }
        }
    }
```

After the operation, if `gauge_relative_weight` is queried by users without updating the total, it will return wrong value.

### Recommended Mitigation Steps

Update `points_total` inside `_remove_gauge_weight`

## [02] Unnecessary write to history inside `_checkpoint()` of `VotingEscrow` when epoch is `0`

Unnecessary saving `userOldPoint` to `userPointHistory[_addr][uEpoch + 1]` when `uEpoch` is `0`.

### Proof of Concept

https://github.com/code-423n4/2024-03-neobase/blob/main/src/VotingEscrow.sol#L168-L171

Inside the `_checkpoint()` function:

```solidity
    function _checkpoint(
        address _addr,
        LockedBalance memory _oldLocked,
        LockedBalance memory _newLocked
    ) internal {
        Point memory userOldPoint;
        Point memory userNewPoint;
        int128 oldSlopeDelta = 0;
        int128 newSlopeDelta = 0;
        uint256 epoch = globalEpoch;

        if (_addr != address(0)) {
            // Calculate slopes and biases
            // Kept at zero when they have to
            if (_oldLocked.end > block.timestamp && _oldLocked.delegated > 0) {
                userOldPoint.slope = _oldLocked.delegated / int128(int256(LOCKTIME));
                userOldPoint.bias = userOldPoint.slope * int128(int256(_oldLocked.end - block.timestamp));
            }
            if (_newLocked.end > block.timestamp && _newLocked.delegated > 0) {
                userNewPoint.slope = _newLocked.delegated / int128(int256(LOCKTIME));
                userNewPoint.bias = userNewPoint.slope * int128(int256(_newLocked.end - block.timestamp));
            }

            // Moved from bottom final if statement to resolve stack too deep err
            // start {
            // Now handle user history
            uint256 uEpoch = userPointEpoch[_addr];
            if (uEpoch == 0) {
                userPointHistory[_addr][uEpoch + 1] = userOldPoint;
            }
            userPointEpoch[_addr] = uEpoch + 1;
            userNewPoint.ts = block.timestamp;
            userNewPoint.blk = block.number;
            userPointHistory[_addr][uEpoch + 1] = userNewPoint;
            // ...
}
```

It can be observed that `userOldPoint` is stored to `userPointHistory[_addr][uEpoch + 1]`, but it will overwritten with `userNewPoint` afterward.

### Recommended Mitigation Steps

Consider to remove the `uEpoch == 0` conditional action.

**[0xTheC0der (judge) commented](https://github.com/code-423n4/2024-03-neobase-findings/issues/7#issuecomment-2043851806):**
> [01]: Low <br>
> [02]: Refactor
> 
> Also include: [#6](https://github.com/code-423n4/2024-03-neobase-findings/issues/6) 

## [[03] `claim` inside `LendingLedger` will revert if market removed from whitelist](https://github.com/code-423n4/2024-03-neobase-findings/issues/6)

*Note: At the judge’s request [here](https://github.com/code-423n4/2024-03-neobase-findings/issues/7#issuecomment-2043851806), this downgraded issue from the same warden has been included in this report for completeness.*

If a market is removed from the whitelist before a user claims the reward, users cannot claim it, and the reward will remain stuck.

### Proof of Concept

When users want to claim the reward from `LendingLedger` by calling `claim`, it will trigger `update_market` first before contract sending the reward to users.

https://github.com/code-423n4/2024-03-neobase/blob/main/src/LendingLedger.sol#L122

```solidity
    function claim(address _market) external {
>>>     update_market(_market); // Checks if the market is whitelisted
        MarketInfo storage market = marketInfo[_market];
        UserInfo storage user = userInfo[_market][msg.sender];
        int256 accumulatedCanto = int256((uint256(user.amount) * market.accCantoPerShare) / 1e18);
        int256 cantoToSend = accumulatedCanto - user.rewardDebt;

        user.rewardDebt = accumulatedCanto;

        if (cantoToSend > 0) {
            (bool success, ) = msg.sender.call{value: uint256(cantoToSend)}("");
            require(success, "Failed to send CANTO");
        }
    }
```

Inside `update_market`, if the market is not whitelisted, the call will revert.

https://github.com/code-423n4/2024-03-neobase/blob/main/src/LendingLedger.sol#L65

```solidity
    function update_market(address _market) public {
>>>     require(lendingMarketWhitelist[_market], "Market not whitelisted");
        MarketInfo storage market = marketInfo[_market];
        if (block.number > market.lastRewardBlock) {
            uint256 marketSupply = lendingMarketTotalBalance[_market];
            if (marketSupply > 0) {
                uint256 i = market.lastRewardBlock;
                while (i < block.number) {
                    uint256 epoch = (i / BLOCK_EPOCH) * BLOCK_EPOCH; // Rewards and voting weights are aligned on a weekly basis
                    uint256 nextEpoch = epoch + BLOCK_EPOCH;
                    uint256 blockDelta = Math.min(nextEpoch, block.number) - i;
                    // May not be the exact time, but will ensure that it is equal for all users and epochs.
                    // If this ever drifts significantly, the average block time and / or reference block time & number can be updated. However, update_market needs to be called for all markets beforehand.
                    uint256 epochTime = referenceBlockTime +
                        ((block.number - referenceBlockNumber) * averageBlockTime) /
                        1000;
                    market.accCantoPerShare += uint128(
                        (blockDelta *
                            cantoPerBlock[epoch] *
                            gaugeController.gauge_relative_weight_write(_market, epochTime)) / marketSupply
                    );
                    market.secRewardsPerShare += uint128((blockDelta * 1e36) / marketSupply); // Scale by 1e18, consumers need to divide by it
                    i += blockDelta;
                }
            }
            market.lastRewardBlock = uint64(block.number);
        }
    }
```

This could lead to an issue, if the market is removed from the whitelist before users can claim the reward, they cannot claim it, and the reward will remain stuck inside `LendingLedger`.

### Recommended Mitigation Steps

Consider to allow users provide additional flag param when calling `claim` so they can claim reward without triggering `update_market`.

```diff
-   function claim(address _market) external {
+   function claim(address _market, bool updateMarket) external {
-       update_market(_market); // Checks if the market is whitelisted
+       if (updateMarket) {
+         update_market(_market); 
+       }
        MarketInfo storage market = marketInfo[_market];
        UserInfo storage user = userInfo[_market][msg.sender];
        int256 accumulatedCanto = int256((uint256(user.amount) * market.accCantoPerShare) / 1e18);
        int256 cantoToSend = accumulatedCanto - user.rewardDebt;

        user.rewardDebt = accumulatedCanto;

        if (cantoToSend > 0) {
            (bool success, ) = msg.sender.call{value: uint256(cantoToSend)}("");
            require(success, "Failed to send CANTO");
        }
    }
```

### Assessed type

Invalid Validation

**[OpenCoreCH (Neobase) acknowledged and commented](https://github.com/code-423n4/2024-03-neobase-findings/issues/6#issuecomment-2041160347):**
> Technically true, but not really a problem for us/by design. Removing from the whitelist (i.e. blacklisting) is a permissioned operation that should only be performed under exceptional circumstances (e.g. when the corresponding market is exploited). I am not sure if the suggestion would be better in such scenarios because an attacker (that may have already performed some sync calls) could then still claim.

**[0xTheC0der (judge) decreased severity to Low and commented](https://github.com/code-423n4/2024-03-neobase-findings/issues/6#issuecomment-2041582109):**
> Blacklisting is intended by design, governance controlled and [reversible](https://github.com/code-423n4/2024-03-neobase/blob/d6e6127e6763b93c23ee95cdf7622fe950d9ed30/src/LendingLedger.sol#L154-L171). Therefore, rewards are not irrecoverably locked.

***

# Gas Optimizations

For this audit, 2 reports were submitted by wardens detailing gas optimizations. The [report highlighted below](https://github.com/code-423n4/2024-03-neobase-findings/issues/9) by **rvierdiiev** received the top score from the judge.

*The following wardens also submitted reports: [Arabadzhiev](https://github.com/code-423n4/2024-03-neobase-findings/issues/23).*

## [G-01] Remove delegation logic from `VotingEscrow`

The `VotingEscrow` contract is inherited from another protocol. That protocol used delegation of votes. But Neobase doesn't use it at all, but still has code to handle delegation and also [has delegated fields](https://github.com/code-423n4/2024-03-neobase/blob/main/src/VotingEscrow.sol#L54-L55) in each user's lock.

If protocol removes that logic, then it will reduce contract size, which will decrease deployment cost and also it will reduce gas costs for users as delegated fields will not be used and will not take storage.

## [G-02] Remove useless block

The `VotingEscrow._checkpoint` function [has this block](https://github.com/code-423n4/2024-03-neobase/blob/main/src/VotingEscrow.sol#L169-L171). This block is useless as later `userPointHistory` [always changes to a new point](https://github.com/code-423n4/2024-03-neobase/blob/main/src/VotingEscrow.sol#L176). That block of code can be cleared.

**[OpenCoreCH (Neobase) confirmed](https://github.com/code-423n4/2024-03-neobase-findings/issues/9#issuecomment-2041160419)**

**[0xTheC0der (judge) commented](https://github.com/code-423n4/2024-03-neobase-findings/issues/9#issuecomment-2041615427):**
 > [G-01]: Ok, also provides contract size reduction. <br>
> [G-02]: Ok.

***

# Disclosures

C4 is an open organization governed by participants in the community.

C4 audits incentivize the discovery of exploits, vulnerabilities, and bugs in smart contracts. Security researchers are rewarded at an increasing rate for finding higher-risk issues. Audit submissions are judged by a knowledgeable security researcher and solidity developer and disclosed to sponsoring developers. C4 does not conduct formal verification regarding the provided code but instead provides final verification.

C4 does not provide any guarantee or warranty regarding the security of this project. All smart contract software should be used at the sole risk and responsibility of users.
