// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// VULNERABLE: dominance is DISPROVEN by an alternative path. Manager.validateRound guards one route to
// Vault._apply, but Router.execute reaches _apply directly (guard-free). A clear leaning on the manager
// guard ignores the router path — exactly what `alternative_paths_considered` must enumerate (proxy/
// router/facet/callback/batch/delegatecall). The call-graph check finds Router.execute → _apply.
contract Vault {
    function _apply(uint256 v) external {            // reachable from two callers
        // sensitive op
    }
}

contract Manager {
    Vault vault;
    function validateRound(uint256 round, uint256 v) public {
        require(round == 1, "stale round");          // guard on THIS path only
        vault._apply(v);
    }
}

contract Router {
    Vault vault;
    function execute(uint256 v) external {           // bypass: no round guard
        vault._apply(v);
    }
}
