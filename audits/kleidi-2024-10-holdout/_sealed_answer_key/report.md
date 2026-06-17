---
sponsor: "Kleidi"
slug: "2024-10-kleidi"
date: "2024-11-20"
title: "Kleidi"
findings: "https://github.com/code-423n4/2024-10-kleidi-findings/issues"
contest: 455
---

# Overview

## About C4

Code4rena (C4) is an open organization consisting of security researchers, auditors, developers, and individuals with domain expertise in smart contracts.

A C4 audit is an event in which community participants, referred to as Wardens, review, audit, or analyze smart contract logic in exchange for a bounty provided by sponsoring projects.

During the audit outlined in this document, C4 conducted an analysis of the Kleidi smart contract system written in Solidity. The audit took place between October 15—October 25 2024.

## Wardens

27 Wardens contributed reports to Kleidi:

  1. [dhank](https://code4rena.com/@dhank)
  2. [KlosMitSoss](https://code4rena.com/@KlosMitSoss)
  3. [Allarious](https://code4rena.com/@Allarious)
  4. [gesha17](https://code4rena.com/@gesha17)
  5. [DemoreX](https://code4rena.com/@DemoreX)
  6. [0xAkira](https://code4rena.com/@0xAkira)
  7. [Japy69](https://code4rena.com/@Japy69)
  8. [Drynooo](https://code4rena.com/@Drynooo)
  9. [0xAlix2](https://code4rena.com/@0xAlix2) ([a\_kalout](https://code4rena.com/@a_kalout) and [ali\_shehab](https://code4rena.com/@ali_shehab))
  10. [tenge\_club](https://code4rena.com/@tenge_club) ([ABAIKUNANBAEV](https://code4rena.com/@ABAIKUNANBAEV) and [typicalHuman](https://code4rena.com/@typicalHuman))
  11. [Brene](https://code4rena.com/@Brene)
  12. [DanielArmstrong](https://code4rena.com/@DanielArmstrong)
  13. [0x37](https://code4rena.com/@0x37)
  14. [jsonDoge](https://code4rena.com/@jsonDoge)
  15. [stuart\_the\_minion](https://code4rena.com/@stuart_the_minion)
  16. [klau5](https://code4rena.com/@klau5)
  17. [Sathish9098](https://code4rena.com/@Sathish9098)
  18. [JustAWanderKid](https://code4rena.com/@JustAWanderKid)
  19. [Rhaydden](https://code4rena.com/@Rhaydden)
  20. [Guardians](https://code4rena.com/@Guardians) ([igdbase](https://code4rena.com/@igdbase) and [0xozovehe](https://code4rena.com/@0xozovehe))
  21. [0xSecuri](https://code4rena.com/@0xSecuri)
  22. [Sparrow](https://code4rena.com/@Sparrow)
  23. [aariiif](https://code4rena.com/@aariiif)
  24. [ZanyBonzy](https://code4rena.com/@ZanyBonzy)

This audit was judged by [Alex the Entreprenerd](https://code4rena.com/@GalloDaSballo).

Final report assembled by [liveactionllama](https://twitter.com/liveactionllama).

# Summary

The C4 analysis yielded an aggregated total of 3 unique vulnerabilities. Of these vulnerabilities, 0 received a risk rating in the category of HIGH severity and 3 received a risk rating in the category of MEDIUM severity.

Additionally, C4 analysis included 11 reports detailing issues with a risk rating of LOW severity or non-critical.

All of the issues presented here are linked back to their original finding.

# Scope

The code under review can be found within the [C4 Kleidi repository](https://github.com/code-423n4/2024-10-kleidi), and is composed of 10 smart contracts written in the Solidity programming language and includes 1,393 lines of Solidity code.

# Severity Criteria

C4 assesses the severity of disclosed vulnerabilities based on three primary risk categories: high, medium, and low/non-critical.

High-level considerations for vulnerabilities span the following key areas when conducting assessments:

- Malicious Input Handling
- Escalation of privileges
- Arithmetic
- Gas use

For more information regarding the severity criteria referenced throughout the submission review process, please refer to the documentation provided on [the C4 website](https://code4rena.com), specifically our section on [Severity Categorization](https://docs.code4rena.com/awarding/judging-criteria/severity-categorization).

# Medium Risk Findings (3)
## [[M-01] Gas griefing/attack via creating the proposals](https://github.com/code-423n4/2024-10-kleidi-findings/issues/24)
*Submitted by [Allarious](https://github.com/code-423n4/2024-10-kleidi-findings/issues/24), also found by [Allarious](https://github.com/code-423n4/2024-10-kleidi-findings/issues/25), [DemoreX](https://github.com/code-423n4/2024-10-kleidi-findings/issues/53), [Japy69](https://github.com/code-423n4/2024-10-kleidi-findings/issues/46), [Drynooo](https://github.com/code-423n4/2024-10-kleidi-findings/issues/43), [KlosMitSoss](https://github.com/code-423n4/2024-10-kleidi-findings/issues/32), gesha17 ([1](https://github.com/code-423n4/2024-10-kleidi-findings/issues/5), [2](https://github.com/code-423n4/2024-10-kleidi-findings/issues/4)), [tenge\_club](https://github.com/code-423n4/2024-10-kleidi-findings/issues/51), [Brene](https://github.com/code-423n4/2024-10-kleidi-findings/issues/41), and [JustAWanderKid](https://github.com/code-423n4/2024-10-kleidi-findings/issues/38)*

<https://github.com/code-423n4/2024-10-kleidi/blob/c474b9480850d08514c100b415efcbc962608c62/src/Timelock.sol#L512-L539><br>
<https://github.com/code-423n4/2024-10-kleidi/blob/c474b9480850d08514c100b415efcbc962608c62/src/Timelock.sol#L652-L665>

The timelock acts in a way that once the proposals are submitted, they need to be cancelled or executed. This behaviour opens up a griefing attack vector towards the owners of the vault in case at least `threshold` amount of owners' private keys are exposed.

When the keys are exposed, the attackers can send as many transactions as they need to the network from the safe with different salts. Even if one of the transactions go through, funds can be stolen. The protocol defence mechanisms in these situations is (1) Pause guardian can cancel all the proposals (2) Cold signers can cancel proposals.

Both these defence mechanisms require gas usage from the victim's accounts, and **it is important to note that they can not use the funds inside the Kleidi wallet**. This can lead to a gas war between attackers and the victims and can cause them to at least cause a griefing attack.

### Impact

Assumption in this section is that the victims do not get external help and they have invested most of their liquidity inside Kleidi, and only kept minimal amounts out for gas payments.

*   Imagine if victims have access to `F` amounts of funds, and 95% of those funds is locked into Kleidi.
*   The proof of concept below shows that the gas consumption of `cancel` is close to 5% of `schedule`.
*   In case the keys are compromised, attackers can send many transactions spending `G` amount of gas. The requires the victims to need to spend `0.05 * G` in gas to cancel those proposals.
*   The reward for attackers, only if one of their transactions go through, is `0.95 * F`.
*   Given that victims only have access to `0.05 * F` to pay for `0.05 * G`, if attackers pay more than the funds inside the protocol, meaning (`G > F`), they can claim the funds in the protocol and drain it as victims do not have enough funds to cancel all proposals.

At the end, attackers can re-claim most of what they spent. Overall spending `G - 0.95 * F = G - 0.95 * G = 0.05 * G`, and steal `0.95 * G` from the user.

Note: In case the victims have invested more than `~95%` into the Kleidi, attackers will be able to make profit.

### Proof of Concept

Gas consumptions is thoroughly investigated in the test below:

<details>

```solidity
    function testGasConsumption() public {

        bytes32 scheduleSalt = bytes32("saltxyz");
        uint256 numOfProposals = 100000;
        bytes32[] memory saltArray = new bytes32[](numOfProposals);

        for(uint i; i < numOfProposals; i++) {
            saltArray[i] = keccak256(abi.encodePacked("salt", bytes32(i + 1)));
        }

        bytes memory scheduleData = abi.encode(timelock.updateDelay, MINIMUM_DELAY);
        address timelockAddress = address(timelock);


        // initial call costs more gas
        vm.prank(address(safe));
        timelock.schedule(
            timelockAddress,
            0,
            scheduleData,
            scheduleSalt,
            MINIMUM_DELAY
        );

        vm.startPrank(address(safe));
        uint256 gasBeforeSchedule = gasleft();
        for(uint256 i; i < numOfProposals; i++){
            timelock.schedule(
                timelockAddress,
                0,
                scheduleData,
                saltArray[i],
                MINIMUM_DELAY
            );   
        }
        uint256 gasAfterSchedule = gasleft();
        vm.stopPrank();

        bytes32[] memory ids = new bytes32[](numOfProposals);

        for(uint256 i; i < numOfProposals; i++){
            ids[i] = timelock.hashOperation(
                address(timelock),
                0,
                scheduleData,
                saltArray[i]
            );
        }

        vm.startPrank(timelock.pauseGuardian());
        uint256 gasBeforeCancel = gasleft();
        timelock.pause(); // 10000 -> 32,260,154 4.6%
        uint256 gasAfterCancel = gasleft();
        vm.stopPrank();

        // vm.startPrank(address(safe));
        // uint256 gasBeforeCancel = gasleft();
        // for(uint256 i; i < numOfProposals; i++){
        //     timelock.cancel(ids[i]); // 10000 -> 44,890,040  448,900,040 6%
        // }
        // uint256 gasAfterCancel = gasleft();
        // vm.stopPrank();

        // For 100,000 proposals
        // shecdule 7,398,200,040
        // pause guardian pause 340,048,201 ~ 4.6%
        // safe cancel 448,900,040 ~ 6%



        console.log("Gas consumption of schedule: ", gasBeforeSchedule - gasAfterSchedule); // 10000 -> 739,820,040 7,398,200,040
        console.log("Gas consumption of cancel: ", gasBeforeCancel - gasAfterCancel);
    }
```

</details>

### Recommended Mitigation Steps

Add epochs to the timelock, each time the contract is paused, move the epoch to the next variable. Also, include epochs in the transaction hashes, and only execute transactions from this epoch. This way, the pause guardian does not need to clear all the transactions one by one, and once the epoch is moved to the next stage, all the previous transactions will be automatically invalidated.

**[Alex the Entreprenerd (judge) decreased severity to Medium and commented](https://github.com/code-423n4/2024-10-kleidi-findings/issues/24#issuecomment-2447602100):**
 > I adapted the test, that can be dropped in `Timelock.t.sol` to verify my statements:
> 
> <details>
> 
> ```solidity
> function testGasConsumption() public {
> 
>         bytes32 scheduleSalt = bytes32("saltxyz");
>         uint256 numOfProposals = 1000;
>         bytes32[] memory saltArray = new bytes32[](numOfProposals);
> 
>         for(uint i; i < numOfProposals; i++) {
>             saltArray[i] = keccak256(abi.encodePacked("salt", bytes32(i + 1)));
>         }
> 
>         bytes memory scheduleData = abi.encode(timelock.updateDelay, MINIMUM_DELAY);
>         address timelockAddress = address(timelock);
> 
> 
>         // initial call costs more gas
>         vm.prank(address(safe));
>         timelock.schedule(
>             timelockAddress,
>             0,
>             scheduleData,
>             scheduleSalt,
>             MINIMUM_DELAY
>         );
> 
>         // Schedule until we consume 30 MLN Gas
>         vm.startPrank(address(safe));
>         uint256 gasBeforeSchedule = gasleft();
>         uint256 count;
>         while(true) {
>             timelock.schedule(
>                 timelockAddress,
>                 0,
>                 scheduleData,
>                 saltArray[count],
>                 MINIMUM_DELAY
>             );  
>             count++; 
> 
>             // Stop at 30 MLN gas used
>             if(gasBeforeSchedule - gasleft() > 30e6) {
>                 break;
>             } 
>         }
> 
>         console.log("count", count);
> 
>         uint256 gasAfterSchedule = gasleft();
>         vm.stopPrank();
> 
>         vm.startPrank(timelock.pauseGuardian());
>         uint256 gasBeforeCancel = gasleft();
>         timelock.pause(); // 10000 -> 32,260,154 4.6%
>         uint256 gasAfterCancel = gasleft();
>         vm.stopPrank();
> 
>         // vm.startPrank(address(safe));
>         // uint256 gasBeforeCancel = gasleft();
>         // for(uint256 i; i < numOfProposals; i++){
>         //     timelock.cancel(ids[i]); // 10000 -> 44,890,040  448,900,040 6%
>         // }
>         // uint256 gasAfterCancel = gasleft();
>         // vm.stopPrank();
> 
>         // For 100,000 proposals
>         // shecdule 7,398,200,040
>         // pause guardian pause 340,048,201 ~ 4.6%
>         // safe cancel 448,900,040 ~ 6%
> 
> 
> 
>         console.log("Gas consumption of schedule: ", gasBeforeSchedule - gasAfterSchedule); // 10000 -> 739,820,040 7,398,200,040
>         console.log("Gas consumption of cancel: ", gasBeforeCancel - gasAfterCancel);
>     }
> ```
> 
> </details>
> 
> It's worth noting that the POC doesn't work in isolation, leading me to believe that the math given is incorrect.
> 
> I have ran my POC in both modes, and both versions seems to indicate that the cost to attack is a lot higher than the cost to defend, specifically the attack is 7 times more expensive than defending.
> 
> I'm not fully confident that Foundry treats the calls as isolated in this way, so I'm happy to be corrected.
> 
> 
> Result from `forge test --match-test testGasConsumption -vv --isolate`
> 
> ```solidity
> Ran 1 test for test/unit/Timelock.t.sol:TimelockUnitTest
> [PASS] testGasConsumption() (gas: 33562952)
> Logs:
>   count 282
>   Gas consumption of schedule:  30021964
>   Gas consumption of cancel:  4053325
> ```
> 
> 7 times more expensive
> 
> Result from `forge test --match-test testGasConsumption -vv`
> ```solidity
> Ran 1 test for test/unit/Timelock.t.sol:TimelockUnitTest
> [PASS] testGasConsumption() (gas: 25463501)
> Logs:
>   count 403
>   Gas consumption of schedule:  30049168
>   Gas consumption of cancel:  1307414
> ```
> 22 times more expensive
> 
> -----
> 
> Barring a mistake from me, I think the finding is valid and Medium is the most appropriate as the guardian can with some likelihood prevent it as the cost of the attack and the setup is higher than the cost to defend.
> 
> Also the attack must be done over multiple blocks.

**[Alex the Entreprenerd (judge) commented](https://github.com/code-423n4/2024-10-kleidi-findings/issues/24#issuecomment-2447604246):**
 > Mitigation would require changing the way initiatives are tracked.
> 
> By simply shifting a "valid ts" all initiatives created and queued before it can be made invalid, this makes the change a O(1) meaning it should not longer be dossable.

**[ElliotFriedman (Kleidi) commented](https://github.com/code-423n4/2024-10-kleidi-findings/issues/24#issuecomment-2447841367):**
 > I think that cost on the attack side is likely more expensive than your PoC shows because it just pranks as the safe, and doesn't generate the signatures, have them validated in the gnosis safe + increment the nonce in the gnosis safe + 21k base transaction cost. When you add all of that together, it would have to be at least 30x more expensive to attack than to defend.
> 
> Mitigation is in here: https://github.com/solidity-labs-io/kleidi/pull/53.

**[Alex the Entreprenerd (judge) commented](https://github.com/code-423n4/2024-10-kleidi-findings/issues/24#issuecomment-2449256984):**
 > I generally agree, when also considering memory expansion costs that should happen when dealing with so many signatures.
> 
> I think Medium severity is the most appropriate because the attack is IMO not possible in one block, but to say this could have been prevented would be incorrect.
> 
> Fundamentally, if the guardian doesn't urgently pause, they may not be able to within a few blocks (strictly more than 1).
> 
> Medium seems appropriate given this.


***

## [[M-02] Wrong handling of call data check indices, forcing it sometimes to revert](https://github.com/code-423n4/2024-10-kleidi-findings/issues/17)
*Submitted by [0xAlix2](https://github.com/code-423n4/2024-10-kleidi-findings/issues/17), also found by [DemoreX](https://github.com/code-423n4/2024-10-kleidi-findings/issues/54), [DanielArmstrong](https://github.com/code-423n4/2024-10-kleidi-findings/issues/50), [0x37](https://github.com/code-423n4/2024-10-kleidi-findings/issues/48), [jsonDoge](https://github.com/code-423n4/2024-10-kleidi-findings/issues/47), [dhank](https://github.com/code-423n4/2024-10-kleidi-findings/issues/35), [KlosMitSoss](https://github.com/code-423n4/2024-10-kleidi-findings/issues/31), [stuart\_the\_minion](https://github.com/code-423n4/2024-10-kleidi-findings/issues/29), [Allarious](https://github.com/code-423n4/2024-10-kleidi-findings/issues/26), and [klau5](https://github.com/code-423n4/2024-10-kleidi-findings/issues/2)*

Cold signers can add call data checks as whitelisted checks that hot signers could execute without timelocks, the call data checks depend on the indices of the encoded call. However, the protocol invalidly handles these indices in 2 separate places:

1.  <https://github.com/code-423n4/2024-10-kleidi/blob/main/src/Timelock.sol#L1136>
2.  <https://github.com/code-423n4/2024-10-kleidi/blob/main/src/BytesHelper.sol#L50>

Where length is computed as `end index—start index`, which is usually wrong as index subtraction needs `+1` to be translated to a length. For most of the scenario, this is okay; however, if a parameter that is being checked filled all of its bytes then this would be an issue (PoC is an example). For example, a uint256 filling all of its 32 bytes.
**NB:** This is not caught in the unit tests because there isn't any test that checks this edge case, where a parameter that fills all its bytes is being checked.

This forces the whitelisted call to revert.

### Proof of Concept

The following PoC shows a scenario where an infinite approval call is being whitelisted, we don't want to allow fewer approvals (only uint256 max), so the encoding of the call:

```solidity
abi.encodeWithSelector(IERC20.approve.selector, owner, amount)
```

results in the following bytes string:

```solidity
0x095ea7b30000000000000000000000001eff47bc3a10a45d4b230b5d10e37751fe6aa718ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
```

To have an infinite approval call whitelisted we need to add conditions on both the spender and the amount:

1.  Spender: `0x1efF47bc3a10a45D4B230B5d10E37751FE6AA718`
2.  Amount: `115792089237316195423570985008687907853269984665640564039457584007913129639935`

For the spender part, it's straightforward where we need to check from index 16 to 35 (`1eff47bc3a10a45d4b230b5d10e37751fe6aa718` from the encoded bytes); however, passing 16 and 35 will cause the TX to revert with `CalldataList: Data length mismatch`, this is where the issue starts, we pass 16 to 36, but now 36 is the start of the unit max. And we pass 37 to 69, to have the whole 32 bytes included (unit max fills all 32 bytes), passing the end index less than 69 reverts.

Now, when the whitelisted call is triggered with the above params, the TX will revert with `End index is greater than the length of the byte string`, and this is because the amount's byte length is 68 while the end index is 69.

As a result: wrong index/length handling => forcing to pass incorrect params.

**Coded POC:**

Add the following test in `test/integration/System.t.sol`, and run it using `forge test -vv --fork-url "https://mainnet.infura.io/v3/PROJECT_ID" --fork-block-number 20515328 --mt test_DaiTransfer_withoutPlus1`:

<details>

```solidity
function test_DaiTransfer_withoutPlus1() public {
    address owner = vm.addr(pk1);

    address[] memory owners = new address[](1);
    owners[0] = owner;

    address[] memory hotSigners = new address[](1);
    hotSigners[0] = HOT_SIGNER_ONE;

    vm.prank(HOT_SIGNER_ONE);
    SystemInstance memory wallet = deployer.createSystemInstance(
        NewInstance({
            owners: owners,
            threshold: 1,
            recoverySpells: new address[](0),
            timelockParams: DeploymentParams(
                MIN_DELAY,
                EXPIRATION_PERIOD,
                guardian,
                PAUSE_DURATION,
                hotSigners,
                new address[](0),
                new bytes4[](0),
                new uint16[](0),
                new uint16[](0),
                new bytes[][](0),
                bytes32(0)
            )
        })
    );

    Timelock timelock = wallet.timelock;

    uint256 amount = type(uint256).max;
    bytes4 selector = IERC20.approve.selector;

    console.logBytes(abi.encodeWithSelector(selector, owner, amount));

    uint16 startIdx = 16;
    uint16 endIdx = 36;
    bytes[] memory data = new bytes[](1);
    data[0] = abi.encodePacked(owner);

    vm.prank(address(timelock));
    timelock.addCalldataCheck(dai, selector, startIdx, endIdx, data);

    startIdx = 37;
    endIdx = 69;
    data = new bytes[](1);
    data[0] = abi.encodePacked(amount);

    vm.prank(address(timelock));
    timelock.addCalldataCheck(dai, selector, startIdx, endIdx, data);

    assertEq(IERC20(dai).allowance(address(timelock), owner), 0);

    vm.prank(HOT_SIGNER_ONE);
    vm.expectRevert(
        bytes("End index is greater than the length of the byte string")
    );
    timelock.executeWhitelisted(
        address(dai),
        0,
        abi.encodeWithSelector(selector, owner, amount)
    );
}
```

</details>

<details>
<summary>Correct test with the mitigation implemented:</summary>

```solidity
function test_DaiTransfer_withPlus1() public {
    address owner = vm.addr(pk1);

    address[] memory owners = new address[](1);
    owners[0] = owner;

    address[] memory hotSigners = new address[](1);
    hotSigners[0] = HOT_SIGNER_ONE;

    vm.prank(HOT_SIGNER_ONE);
    SystemInstance memory wallet = deployer.createSystemInstance(
        NewInstance({
            owners: owners,
            threshold: 1,
            recoverySpells: new address[](0),
            timelockParams: DeploymentParams(
                MIN_DELAY,
                EXPIRATION_PERIOD,
                guardian,
                PAUSE_DURATION,
                hotSigners,
                new address[](0),
                new bytes4[](0),
                new uint16[](0),
                new uint16[](0),
                new bytes[][](0),
                bytes32(0)
            )
        })
    );

    Timelock timelock = wallet.timelock;

    uint256 amount = type(uint256).max;
    bytes4 selector = IERC20.approve.selector;

    console.logBytes(abi.encodeWithSelector(selector, owner, amount));

    uint16 startIdx = 16;
    uint16 endIdx = 35;
    bytes[] memory data = new bytes[](1);
    data[0] = abi.encodePacked(owner);

    vm.prank(address(timelock));
    timelock.addCalldataCheck(dai, selector, startIdx, endIdx, data);

    startIdx = 36;
    endIdx = 67;
    data = new bytes[](1);
    data[0] = abi.encodePacked(amount);

    vm.prank(address(timelock));
    timelock.addCalldataCheck(dai, selector, startIdx, endIdx, data);

    assertEq(IERC20(dai).allowance(address(timelock), owner), 0);

    vm.prank(HOT_SIGNER_ONE);
    timelock.executeWhitelisted(
        address(dai),
        0,
        abi.encodeWithSelector(selector, owner, amount)
    );

    assertEq(IERC20(dai).allowance(address(timelock), owner), amount);
}
```

</details>

### Recommended Mitigation Steps

In `BytesHelper.sol`:

```diff
function sliceBytes(bytes memory toSlice, uint256 start, uint256 end)
    public
    pure
    returns (bytes memory)
{
    ...

-   uint256 length = end - start;
+   uint256 length = end - start + 1;
    bytes memory sliced = new bytes(length);

    ...
}
```

In `Timelock.sol`:

```diff
function _addCalldataCheck(
    address contractAddress,
    bytes4 selector,
    uint16 startIndex,
    uint16 endIndex,
    bytes[] memory data
) private {
    ...

    for (uint256 i = 0; i < data.length; i++) {
        /// data length must equal delta index
        require(
-           data[i].length == endIndex - startIndex,
+           data[i].length == endIndex - startIndex + 1,
            "CalldataList: Data length mismatch"
        );
        bytes32 dataHash = keccak256(data[i]);

        /// make require instead of assert to have clear error messages
        require(
            indexes[targetIndex].dataHashes.add(dataHash),
            "CalldataList: Duplicate data"
        );
    }

    ...
}
```

**[ElliotFriedman (Kleidi) confirmed and commented](https://github.com/code-423n4/2024-10-kleidi-findings/issues/17#issuecomment-2444991245):**
 > Good finding, valid medium!

**[Alex the Entreprenerd (judge) commented](https://github.com/code-423n4/2024-10-kleidi-findings/issues/17#issuecomment-2446543452):**
 > Seems to be very closely related to [issue #2](https://github.com/code-423n4/2024-10-kleidi-findings/issues/2). 
> 
> I'd be careful about mitigating these. Probably best to use both cases for tests and then mitigate in one go.

**[Alex the Entreprenerd (judge) commented](https://github.com/code-423n4/2024-10-kleidi-findings/issues/17#issuecomment-2449269406):**
 > I'm not fully confident this bug is not different from the `addCalldataChecks`,  checking in with the Sponsor to see how the bugs are mitigated.
>
 > @ElliotFriedman can you please confirm if you fixed this issue separately, or if you fixed it by fixing the finding from [issue #2](https://github.com/code-423n4/2024-10-kleidi-findings/issues/2)?

**[Alex the Entreprenerd (judge) commented](https://github.com/code-423n4/2024-10-kleidi-findings/issues/17#issuecomment-2466042383):**
 > As discussed am making a duplicate of the rest of the reports tied to indices.
> 
> @ElliotFriedman would appreciate if you can re-link all fixes tied to indices as to ensure the issues and gotchas were fixed.

**[ElliotFriedman (Kleidi) commented](https://github.com/code-423n4/2024-10-kleidi-findings/issues/17#issuecomment-2466089555):**
 > Mitigated with this PR https://github.com/solidity-labs-io/kleidi/pull/54/files
>
 > All other changes were backed out as we realized the previous ways of fixing things were incomplete.


***

## [[M-03] `UpdateExpirattionPeriod()` cannot be executed when the `newExpirationPeriod` is less than `currentExpirationPeriod`](https://github.com/code-423n4/2024-10-kleidi-findings/issues/9)
*Submitted by [dhank](https://github.com/code-423n4/2024-10-kleidi-findings/issues/9), also found by [KlosMitSoss](https://github.com/code-423n4/2024-10-kleidi-findings/issues/42)*

Safe cannot reduce  `expirationPeriod` to a `newExpirationPeriod` when

```
    currentTimeStamp < timestamp[id] +  expirationPeriod and
    currentTimeStamp >= timestamp[id] +  newExpirationPeriod
```

where `id` is the `hash` of `updateExpirationPeriod()` and `timestamp[id]` is the timestamp when the `id` can be executed.

Safe should be able to update the `expirationPeriod` to any values >= `MIN_DELAY` by scheduling the `updateExpirationPeriod()` and later execute from `timelock` when the operation is ready (before the expiry).

```solidity
    require(newPeriod >= MIN_DELAY, "Timelock: delay out of bounds");
```

But the protocol has overlooked the situation and added an reduntant  check inside [\_afterCall()](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L1009-L1015) which is executed at the end of [\_execute()](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L608).

```solidity
    function _afterCall(bytes32 id) private {
        /// unreachable state because removing the proposal id from the
        /// _liveProposals set prevents this function from being called on the
        /// same id twice
        require(isOperationReady(id), "Timelock: operation is not ready"); //@audit
        timestamps[id] = _DONE_TIMESTAMP;
    }
```

Here the `isOperationReady(id)` will be executed with the `newExpirationPeriod`.<br>
[code](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/Timelock.sol#L399-L404)

```solidity
    function isOperationReady(bytes32 id) public view returns (bool) {
        /// cache timestamp, save up to 2 extra SLOADs
        uint256 timestamp = timestamps[id];
        return timestamp > _DONE_TIMESTAMP && timestamp <= block.timestamp
   =>         && timestamp + expirationPeriod > block.timestamp;
    }
```

There it is checking whether the `currentTimestamp` is less than the `timestamp` + `updated EpirationPeriod` instead of the `actual expirationPeriod`.

### Proof Of Concept

forge test --match-test testDUpdateExpirationPeriodRevert -vvv

```solidity
function testDUpdateExpirationPeriodRevert() public {
        // Prepare the scheduling parameters
        // Call schedule() first time
        
        uint256 newExpirationPeriod =  EXPIRATION_PERIOD - 2 days; //newExpirationPeriod =  3 days since EXPIRATION_PERIOD = 5 days intially

        _schedule({       //safe has scheduled updateExpirationPeriod() call
            caller: address(safe),
            timelock: address(timelock),
            target: address(timelock),
            value: 0,
            data: abi.encodeWithSelector(
                timelock.updateExpirationPeriod.selector,newExpirationPeriod
            ),
            salt: bytes32(0),
            delay: MINIMUM_DELAY
        });
      
        //delay time has passed
        vm.warp(block.timestamp + MIN_DELAY + EXPIRATION_PERIOD - 1 days); //current timestamp is 1 day before the expiry period.

        vm.expectRevert("Timelock: operation is not ready"); //it will  revert with this msg

        timelock.execute(address(timelock),0, abi.encodeWithSelector(
                timelock.updateExpirationPeriod.selector,newExpirationPeriod
            ),bytes32(0));

    }
```

Updating to the new expirationPeriod  will revert in this case.<br>
This can affect the protocols core design features.

### Recommended Mitigation Steps

```solidity
 function _afterCall(bytes32 id) private {
       //no need to check
        timestamps[id] = _DONE_TIMESTAMP;
    }
```

**[ElliotFriedman (Kleidi) confirmed, but disagreed with severity and commented](https://github.com/code-423n4/2024-10-kleidi-findings/issues/9#issuecomment-2445088158):**
 > Seems like this is a valid issue, but it's valid only if you execute the proposal more than min delay after the transaction becomes executable and you are lowering the expiration period.
> 
> The title is misleading because you can execute this operation, but you just have to execute it within the new expiration period.
> 
 > Feels more like a low severity than a medium.

**[Alex the Entreprenerd (judge) commented](https://github.com/code-423n4/2024-10-kleidi-findings/issues/9#issuecomment-2446575955):**
 > I need to think about it a bit more, but fundamentally it seems to be something that the owner would cause to themselves.

**[Alex the Entreprenerd (judge) decreased severity to Low/Non-Critical and commented](https://github.com/code-423n4/2024-10-kleidi-findings/issues/9#issuecomment-2447623895):**
 > With a similar point to [issue #21](https://github.com/code-423n4/2024-10-kleidi-findings/issues/21) this is an operative mistake that the user can make.
> 
> Because this is a gotcha, where under valid use no harm would be done, I think the finding is best categorized as QA.

**[Alex the Entreprenerd (judge) commented](https://github.com/code-423n4/2024-10-kleidi-findings/issues/9#issuecomment-2459431105):**
 > After running the test, and reviewing the code, I see the issue.<br>
> The new expiration is being used to validate the executed function.<br>
> I see that this is a valid bug and am leaning towards raising the severity to Medium.

**[ElliotFriedman (Kleidi) commented](https://github.com/code-423n4/2024-10-kleidi-findings/issues/9#issuecomment-2461170405):**
 > I agree that this is a valid finding, so now we're just talking about impact and severity. The solution for the end user is just execute the transaction before the new expiration period takes place. We can warn on the UI about this.
> 
> @Alex the Entreprenerd - Will leave severity of finding to your judgement.

**[Alex the Entreprenerd (judge) increased severity to Medium and commented](https://github.com/code-423n4/2024-10-kleidi-findings/issues/9#issuecomment-2466041051):**
 > The finding is a bit of an edge case, when changing a proposal expiration to a smaller value, the OZ reentrancy guard will use the expiration that was newly set, causing the execution to revert.
> 
> Fundamentally given this specific scenario, a proposal will not be executable, this leads me to agree with Medium severity.


***

# Low Risk and Non-Critical Issues

For this audit, 11 reports were submitted by wardens detailing low risk and non-critical issues. The [report highlighted below](https://github.com/code-423n4/2024-10-kleidi-findings/issues/61) by **0xAkira** received the top score from the judge.

*The following wardens also submitted reports: [KlosMitSoss](https://github.com/code-423n4/2024-10-kleidi-findings/issues/60), [Sathish9098](https://github.com/code-423n4/2024-10-kleidi-findings/issues/59), [0x37](https://github.com/code-423n4/2024-10-kleidi-findings/issues/63), [Rhaydden](https://github.com/code-423n4/2024-10-kleidi-findings/issues/62), [Guardians](https://github.com/code-423n4/2024-10-kleidi-findings/issues/58), [0xSecuri](https://github.com/code-423n4/2024-10-kleidi-findings/issues/57), [Sparrow](https://github.com/code-423n4/2024-10-kleidi-findings/issues/56), [DemoreX](https://github.com/code-423n4/2024-10-kleidi-findings/issues/52), [aariiif](https://github.com/code-423n4/2024-10-kleidi-findings/issues/44), and [ZanyBonzy](https://github.com/code-423n4/2024-10-kleidi-findings/issues/22).*

## [01] Typo

### Description

In the `Timelock` contract, there is a typo on [L947](https://github.com/code-423n4/2024-10-kleidi/blob/main/src/Timelock.sol#L947).

```solidity 
function removeAllCalldataChecks(
        address[] memory contractAddresses,
        bytes4[] memory selectors
    ) external onlyTimelock {
        require(
            contractAddresses.length == selectors.length,
            "Timelock: arity mismatch" //@audit typo 
        );
        for (uint256 i = 0; i < contractAddresses.length; i++) {
            _removeAllCalldataChecks(contractAddresses[i], selectors[i]);
        }
    }
```

### Recommendation

Consider solving the typo by changing the `arity` to `length`

## [02] Inconsistency between reality and NatSpec documentation  

https://github.com/code-423n4/2024-10-kleidi/blob/main/src/Timelock.sol#L799-L804

### Description

NatSpec's comments imply that the function below can be called by either the address `safe` or the `Timelock` contract. But if we talk about **this** function only, then it can be called **only by safe**, because the `onlySafe` modifier is present. This comment by NatSpec may be misleading.

```solidity 
/// @notice function to revoke the hot signer role from an address
/// can only be called by the timelock or the safe
/// @param deprecatedHotSigner the address of the hot signer to revoke

function revokeHotSigner(address deprecatedHotSigner) external onlySafe {

_revokeRole(HOT_SIGNER_ROLE, deprecatedHotSigner);

}
```

### Recommendation
You should remove the comments in natspec that this function can be called by `timelock` or create a new modifier `onlySafeAndTimelock` to simplify entry
```solidity 
modifier `onlySafeAndTimelock`() {
require(msg.sender == address(this) || msg.sender == safe,
"Timelock: caller is not the timelock and is not the safe"
);
_;
}
```

## [03] Code duplication  

### Description 

There is duplicated code in the [_addCalldataCheck](https://github.com/code-423n4/2024-10-kleidi/blob/main/src/Timelock.sol#L1034-L1155) function.
Specifically on the [1058](https://github.com/code-423n4/2024-10-kleidi/blob/main/src/Timelock.sol#L1058-L1060)
and on the [1089](https://github.com/code-423n4/2024-10-kleidi/blob/main/src/Timelock.sol#L1089-L1090)
Duplicate code, make the code base more difficult to read. They also make it more error-prone, harder to fix, and complicate maintainability and updateability.

### Recommendation

Consider refactoring the code for the above cases. This will lower gas consumption and increase the codebase's overall readability and quality.

## [04] With the expiration period update, the proposals will become expired

https://github.com/code-423n4/2024-10-kleidi/blob/main/src/Timelock.sol#L972-L977

### Description 

Proposals become expired if no one has executed them during the expiration period. After that we will have to delete the proposal, add it again and wait for the delay.  Suppose that the expiration period is set to 5 days, a proposal is added, and we have to wait for the set delay to execute it. If at this moment the `updateExpirationPeriod` function is called and changes the `expirationPeriod` variable to a smaller one than the current period, many proposals will become expired.

```solidity 
function updateExpirationPeriod(uint256 newPeriod) external onlyTimelock {

require(newPeriod >= MIN_DELAY, "Timelock: delay out of bounds");

emit ExpirationPeriodChange(expirationPeriod, newPeriod);

expirationPeriod = newPeriod;

}
```

### Proof of Concept
Copy this code and paste it into the test file `Timelock.t.sol`:

```solidity 
function testEspirationPeriod() public {
bytes memory data = abi.encodeWithSelector(
timelock.updateDelay.selector,
MINIMUM_DELAY
);

bytes32 id = timelock.hashOperation(
address(timelock),
0,
data,
bytes32(0)
);

_schedule({
caller: address(safe),
timelock: address(timelock),
target: address(timelock),
value: 0,
data: abi.encodeWithSelector(
timelock.updateDelay.selector,
MINIMUM_DELAY
),
salt: bytes32(0),
delay: MINIMUM_DELAY
});

assertEq(timelock.expirationPeriod(), 5 days);
assertFalse(timelock.isOperationExpired(id));
vm.warp(block.timestamp + 2 days);
assertFalse(timelock.isOperationExpired(id));
vm.prank(address(timelock));
timelock.updateExpirationPeriod(1 days);
assertTrue(timelock.isOperationExpired(id));
}
```

```bash 
forge test --mt testEspirationPeriod

Ran 1 test for test/unit/Timelock.t.sol:TimelockUnitTest
[PASS] testEspirationPeriod() (gas: 134723)
Suite result: ok. 1 passed; 0 failed; 0 skipped; finished in 9.33ms (1.47ms CPU time)

Ran 1 test suite in 242.82ms (9.33ms CPU time): 1 tests passed, 0 failed, 0 skipped (1 total tests)
```

### Recommendation

Consider making a static `expirationPeriod` for the proposals.

**[Alex the Entreprenerd (judge) commented](https://github.com/code-423n4/2024-10-kleidi-findings/issues/61#issuecomment-2454219930):**
 > [01] - Refactor<br>
> [02] - Low<br>
> [03] - Ignored<br>
> [04] - Low
> 
> Final count: 2 Low + 1 Refactor


***

# Disclosures

C4 is an open organization governed by participants in the community.

C4 audits incentivize the discovery of exploits, vulnerabilities, and bugs in smart contracts. Security researchers are rewarded at an increasing rate for finding higher-risk issues. Audit submissions are judged by a knowledgeable security researcher and solidity developer and disclosed to sponsoring developers. C4 does not conduct formal verification regarding the provided code but instead provides final verification.

C4 does not provide any guarantee or warranty regarding the security of this project. All smart contract software should be used at the sole risk and responsibility of users.
