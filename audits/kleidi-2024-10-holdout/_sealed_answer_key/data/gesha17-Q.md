## [L-01] Timelock can be in unpaused state while no guardian is present which opens the possibility of an attack without option to pause
It's not possible to update the guardian before the pause duration expires, meaning that after a pause, the protocol will be in a state without any guardian until the transactions to update it pass through the timelock and its delay. Updating the pause duration while the contract is paused will remove the pause without any guardian present. This creates risk for the protocol as it is not possible to pause the contracts in case of an immediate subsequent signer key compromise.

## Proof of Concept
The Timelock will be paused in the case of an emergency and guard will thus have his role automatically revoked:

https://github.com/code-423n4/2024-10-kleidi/blob/main/src/ConfigurablePause.sol#L93
```js
    /// calling removes the pause guardian
    function pause() public virtual whenNotPaused {
        ...
        /// kick the pause guardian
        pauseGuardian = address(0);

        ...
    }
```

Once the signers are rotated, the pause can be lifted and a new pause guardian can be set. The pause can be lifted by calling updatePauseDuration(), since that is the only function that will lift the pause.

https://github.com/code-423n4/2024-10-kleidi/blob/main/src/ConfigurablePause.sol#L104
```js
    function _updatePauseDuration(uint128 newPauseDuration) internal {
        require(
            newPauseDuration >= MIN_PAUSE_DURATION
                && newPauseDuration <= MAX_PAUSE_DURATION,
            "ConfigurablePause: pause duration out of bounds"
        );

        /// if the contract was already paused, reset the pauseStartTime to 0
        /// so that this function cannot pause the contract again
        _setPauseTime(0);

        uint256 oldPauseDuration = pauseDuration;
        pauseDuration = newPauseDuration;

        emit PauseDurationUpdated(oldPauseDuration, pauseDuration);
    }
```

However, the function will still lift the pause if there is no guardian set, leaving the contract vulnerable to an immediate attack if the new signer keys are compromised as well.

## Recommended Mitigation Steps
Mitigation is non-trivial