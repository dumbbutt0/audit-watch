# Rejected & Merged Candidates — Beanstalk Finale (API-free eval2)

_Preserved for eval completeness (false-positive / duplicate analysis)._

## Rejected (9)  — with disproofs where safety-net

- **FL-002** (Informational): Explicit negative-result documentation, not a finding: confirms the sunrise/gm deltaB mint is NOT flash-loan manipulable. Rejected as a non-vulnerability (recorded only to close the hypothesis).  [disproof: To over-mint Beans in sunrise an attacker must inflate twaDeltaB within one block, but LibWellMinting.twaDeltaB reads IC]
- **AR-003** (Info): Not safety-net code (a defensive abs() helper, not a solvency/oracle/bridge/init guard). LibConvert.abs(int256.min) would revert on unary negation, but no reachable path produces int256.min: deltaB =   
- **AR-004** (Info): Not safety-net code (a reward computation, not a protocol-protection guard). LibSilo.stalkReward would only mis-behave if endStem < startStem, but every caller derives startStem from a stored deposit   
- **AR-005** (Info): Not safety-net code (downcast notes). The two uint128 downcasts were re-derived: overflowing uint128 (~3.4e38) would require BDV magnitudes ~3.4e28 micro-BDV, orders of magnitude above any plausible B  
- **TI-001** (Info): Not safety-net code (token-pull accounting in a privileged-token path). LibFertilizer.addFertilizer credits the tokenAmountIn argument with a raw transferFrom and no balanceOf delta, which would drift  
- **TI-002** (Info): Not safety-net code. Documents the systemic 'records argument, not received amount' assumption across non-Silo token sinks, but every token through these paths is constrained to the governance-managed  
- **TI-003** (Info): Not safety-net code. Fertilizer1155._beforeTokenTransfer calls payFertilizer (external Bean payout) using pre-transfer balances before the ERC1155 acceptance check -- an ordering/CEI concern. Fertiliz  
- **SG-002** (Low): Not safety-net code (guard-consistency blemish). SiloFacet.safeTransferFrom/safeBatchTransferFrom omit nonReentrant relative to transferDeposit(s).  [disproof: To exploit the missing nonReentrant an attacker must re-enter during the transfer, but both functions immediately route ]
- **SG-003** (Low): Not safety-net code (guard-consistency blemish). ClaimFacet.mow/mowMultiple and ApprovalFacet.setApprovalForAll omit nonReentrant relative to siblings.  [disproof: To exploit the missing nonReentrant an attacker needs an external callback observing inconsistent state, but mow/mowMult]

## Merged / duplicates (15)

- **AC-001** → duplicate_of CC-001: Same root cause, function, and path as CC-001 (no spent-marker + setStalk +=, replayable public proof/sig in redeemDepositsAndInternalBalanc
- **SN-003** → duplicate_of CC-001: Same root cause/function/path as CC-001 (setStalk += roots/stalk on replayable redeem). Snapshot/earned-Bean lens of the identical replay bu
- **AC-002** → duplicate_of CC-003: Same root cause/function/path as CC-003 (merkle leaf omits reciever, destination bound only by signature). Access-control lens. Merged into 
- **BSA-004** → duplicate_of LG-001: Same root cause/function/lines as LG-001 (uninitialized totalDeposited/totalDepositedBdv written to global silo balances, L159-160/194-195).
- **US-001** → duplicate_of PC-001: Same root cause/path as PC-001 (reseed never writes global silo.stalk/roots -> div-by-zero DoS / genesis-root desync). Proxy/upgrade lens. M
- **SN-002** → duplicate_of PC-001: Same root cause/path as PC-001 (global silo.stalk/roots never seeded -> earned-Bean snapshot denominator desync). Snapshot lens. Merged into
- **DT-009** → duplicate_of PC-001: Same root cause as PC-001 (reseed does not initialize protocol-wide total stalk/roots). DT raised it as Medium 'pending a trace'; the trace 
- **BSA-002** → duplicate_of CC-002: Same root cause/function/lines as CC-002 (EXTERNAL_L1_BEANS=0 cap makes recieveL1Beans always revert after the L1 burn). Behavioral-divergen
- **SN-001** → duplicate_of LG-002: Same root cause/function/line as LG-002 (ReseedSilo L164 = overwrites per-token stalk for multi-token holders). Snapshot lens. Merged into L
- **BSA-003** → duplicate_of LG-002: Same root cause/function/line as LG-002 (ReseedSilo = vs += overwrites multi-token holders' stalk, contradicting the 're-issues all stalk' N
- **DT-006** → duplicate_of BSA-001: Same root cause/function/lines as BSA-001 (inverted lookback ternary in LibChainlinkOracle.getTokenPrice). Deep-trace/oracle lens. Merged in
- **AR-002** → duplicate_of DS-003: Same root cause/function/lines as DS-003 (missing zero-guard before 1e24/price in getTokenPriceFromExternal 0x01 branch -> div-by-zero DoS o
- **OR-006** → duplicate_of DS-003: Same root cause/function/lines as DS-003 (1e24/getTokenPrice with no zero-guard in the 0x01 branch). Oracle lens. Merged into DS-003.
- **DS-005** → duplicate_of DT-011: Same root cause/function as DT-011 (no farmers/balances length check in setInternalBalances -> OOB revert on malformed privileged input). Do
- **DT-012** → duplicate_of BSA-005: Same root cause/function as BSA-005 (mintFertilizers does not enforce ascending fertilizerIds -> malformed/cyclic linked list). Deep-trace l