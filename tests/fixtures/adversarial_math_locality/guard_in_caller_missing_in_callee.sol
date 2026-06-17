// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// VULNERABLE: the caller `Router.run` checks the round, but the callee `vault` is itself public and
// callable directly, skipping the check. A clear of `vault` that leans on Router.run's guard is not
// path-dominant: the call graph shows `vault` reachable as its own public entry without the guard.
contract Vault {
    uint256 public state;

    // public + no local guard → directly callable, bypassing Router.run's check
    function vault(uint256 round, uint256 v) public {
        state = v;
    }
}

contract Router {
    Vault target;
    function run(uint256 round, uint256 v) external {
        require(round == 1, "stale round");          // guard only on the router path
        target.vault(round, v);
    }
}
