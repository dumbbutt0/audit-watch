#!/usr/bin/env python3
"""P215 — consolidate the 5 blind deep_trace cluster outputs into the real funnel substrate.
Writes audits/<active>/output/findings_deep_trace.json (specialist shape) for tools/report_generator.py,
plus the deliverable CANDIDATE_REGISTER.json and a record of refuted/early-rejected surfaces.
Source-derived only; the sealed answer key was never read.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts"))
from audit_context import audit_path  # noqa

DEL = Path(__file__).resolve().parent

# threat_ceiling -> claimed severity label (ceiling; the funnel + L3 calibrate down)
SEV = {"CRITICAL_THREAD": "Critical", "HIGH_THREAD": "High", "MEDIUM_THREAD": "Medium", "LOW": "Low"}

# 12 consolidated root-cause candidates (root-cause dedup of ~18 raw genuine hits)
C = [
 dict(id="ZETA-01", contract="ERC20Custody", function="withdraw", file="contracts/evm/ERC20Custody.sol", lines="193-199",
   ceiling="HIGH_THREAD", impact_class="accounting", attacker="conditional", confidence="High",
   title="ERC20Custody.withdraw transfers exact amount, ignoring fee-on-transfer tokens (custody insolvency)",
   mechanism="withdraw() does IERC20(asset).safeTransfer(recipient, amount) with the deposit-credited amount; deposit() uses a balance-delta but withdraw() does not, so for a fee-on-transfer whitelisted asset the contract pays out more than it net-received.",
   exploit_path="FoT token whitelisted -> users deposit (credited net of fee) -> TSS withdraws original amount -> over time custody balance < obligations -> later withdrawals revert / draw from other users.",
   impact="Insolvency / cross-user fund loss for whitelisted fee-on-transfer assets.",
   manifest_refs=["function:ERC20Custody:withdraw#0xwithdraw"]),
 dict(id="ZETA-02", contract="ERC20Custody", function="deposit", file="contracts/evm/ERC20Custody.sol", lines="165-185",
   ceiling="MEDIUM_THREAD", impact_class="accounting", attacker="conditional", confidence="Medium",
   title="ERC20Custody.deposit zetaFee transfer not balance-checked (fee accounting drift for FoT zeta)",
   mechanism="zeta.safeTransferFrom(msg.sender, TSSAddress, zetaFee) without balance-delta; if zeta is fee-on-transfer, TSS receives < zetaFee while depositor is debited full fee.",
   exploit_path="zeta set to FoT token -> each deposit under-pays TSS vs accounting expectation.",
   impact="Protocol fee accounting drift; not direct external theft.",
   manifest_refs=["function:ERC20Custody:deposit#0xdeposit"]),
 dict(id="ZETA-03", contract="ERC20Custody/ZetaConnectorBase/ZetaNonEth", function="updateTSSAddress/updateTssAddress/updateTssAndConnectorAddresses", file="contracts/evm/ERC20Custody.sol", lines="80-113",
   ceiling="CRITICAL_THREAD", impact_class="access_control", attacker="privileged", confidence="High",
   title="TSS trust-root rotation has no timelock/two-step; single privileged key can redirect custody/mint authority",
   mechanism="updateTSSAddress (custody, onlyTSSUpdater), updateTssAddress (connector: current tss can rotate itself), updateTssAndConnectorAddresses (ZetaNonEth: tss or updater) all atomically reassign the trust root with no delay; ZetaNonEth has no supply cap so the new connector can mint unbounded.",
   exploit_path="Compromise privileged key -> rotate TSS/connector to attacker -> withdraw all custody / mint unbounded ZETA.",
   impact="Full custody drain / unbounded mint IF a privileged key is compromised (centralization/trust risk).",
   manifest_refs=["function:ERC20Custody:updateTSSAddress#x","function:ZetaConnectorBase:updateTssAddress#x","function:ZetaNonEth:updateTssAndConnectorAddresses#x"]),
 dict(id="ZETA-04", contract="ZetaConnectorEth/NonEth", function="onReceive", file="contracts/evm/ZetaConnector.eth.sol", lines="52-69",
   ceiling="HIGH_THREAD", impact_class="access_control", attacker="conditional", confidence="High",
   title="onReceive lacks whenNotPaused (pause does not halt inbound delivery); onRevert has it",
   mechanism="onReceive is onlyTssAddress but NOT whenNotPaused, while onRevert IS whenNotPaused. Emergency pause cannot stop inbound token delivery/callbacks.",
   exploit_path="Operator pauses after incident -> TSS (compromised/erroring) still calls onReceive -> tokens delivered/minted during pause.",
   impact="Pause control ineffective for inbound messages; weakens incident response.",
   manifest_refs=["function:ZetaConnectorEth:onReceive#x"]),
 dict(id="ZETA-05", contract="ZetaConnectorEth/NonEth", function="onReceive/onRevert", file="contracts/evm/ZetaConnector.eth.sol", lines="52-111",
   ceiling="HIGH_THREAD", impact_class="theft", attacker="privileged", confidence="High",
   title="No internalSendHash replay/dedup tracking in connectors (double-delivery if TSS replays)",
   mechanism="No mapping(bytes32=>bool) of processed internalSendHash; the same hash can be processed repeatedly. internalSendHash is only used in events / passed to mint() for tracing.",
   exploit_path="Compromised/rogue TSS calls onReceive with same hash repeatedly -> repeated transfer (eth) / mint (non-eth) up to maxSupply.",
   impact="Double-spend / supply inflation conditional on TSS misbehaviour; no on-chain defense in depth.",
   manifest_refs=["function:ZetaConnectorEth:onReceive#x"]),
 dict(id="ZETA-06", contract="ZetaInteractor", function="isValidMessageCall", file="contracts/evm/tools/ZetaInteractor.sol", lines="23-28",
   ceiling="HIGH_THREAD", impact_class="cross_chain_auth", attacker="conditional", confidence="Medium",
   title="Uninitialized interactorsByChainId[chain] (empty bytes) lets empty zetaTxSenderAddress pass sender check",
   mechanism="modifier compares keccak256(sender) vs keccak256(interactorsByChainId[srcChain]) without first asserting the interactor entry is set; both empty -> keccak256('')==keccak256('') passes. _isValidChainId(ZERO_BYTES) guard exists but is NOT used in the modifier.",
   exploit_path="A chain with no registered interactor + TSS-relayed message with empty sender -> onZetaMessage executes as if from a registered peer.",
   impact="Sender allow-list bypass for unregistered chains (depends on inheriting onZetaMessage logic).",
   manifest_refs=["function:ZetaInteractor:isValidMessageCall#x"]),
 dict(id="ZETA-07", contract="ZRC20", function="withdrawGasFee/withdraw", file="contracts/zevm/ZRC20.sol", lines="236-260",
   ceiling="MEDIUM_THREAD", impact_class="accounting", attacker="conditional", confidence="High",
   title="withdrawGasFee has no GAS_LIMIT==0 / gasFee==0 guard (zero gas fee withdrawal)",
   mechanism="gasFee = gasPrice*GAS_LIMIT + PROTOCOL_FLAT_FEE; guards check gasPrice!=0 and gasZRC20!=0 but not GAS_LIMIT==0; with GAS_LIMIT=0 and flat fee 0, transferFrom(...,0) succeeds and burn proceeds fee-free.",
   exploit_path="FUNGIBLE_MODULE sets GAS_LIMIT=0 -> any user withdraws paying zero gas fee -> protocol eats outbound cost.",
   impact="Fee leakage when GAS_LIMIT misconfigured; conditional on privileged misconfig.",
   manifest_refs=["function:ZRC20:withdrawGasFee#x"]),
 dict(id="ZETA-08", contract="ZRC20", function="deposit/updateSystemContractAddress", file="contracts/zevm/ZRC20.sol", lines="225-272",
   ceiling="HIGH_THREAD", impact_class="access_control", attacker="privileged", confidence="High",
   title="Mint authority tied to mutable SYSTEM_CONTRACT_ADDRESS updated with no zero-address guard",
   mechanism="deposit() mints, allowed for FUNGIBLE_MODULE or mutable SYSTEM_CONTRACT_ADDRESS; updateSystemContractAddress(onlyFungible) has NO zero/address validation, so the mint-authorised address can be set to any contract.",
   exploit_path="Compromised FUNGIBLE_MODULE -> point SYSTEM_CONTRACT_ADDRESS at attacker -> attacker calls deposit() to mint unbounded ZRC20.",
   impact="Unbounded ZRC20 inflation IF FUNGIBLE_MODULE compromised (trust/centralization).",
   manifest_refs=["function:ZRC20:deposit#x","function:ZRC20:updateSystemContractAddress#x"]),
 dict(id="ZETA-09", contract="ZetaConnectorZEVM", function="constructor", file="contracts/zevm/ZetaConnectorZEVM.sol", lines="79-86",
   ceiling="MEDIUM_THREAD", impact_class="cross_chain_auth", attacker="permissionless", confidence="Medium",
   title="ZetaConnectorZEVM constructor has no FUNGIBLE_MODULE guard (anyone can deploy a connector instance)",
   mechanism="Unlike ZRC20/SystemContract constructors which revert if msg.sender!=FUNGIBLE_MODULE, ZetaConnectorZEVM constructor is unguarded; a rogue instance can emit ZetaSent events of identical shape.",
   exploit_path="Attacker deploys own connector with chosen wzeta; only harms users who approve/interact with the rogue instance, or off-chain consumers that trust ZetaSent emitter without authenticating address.",
   impact="Phishing / event-spoofing surface; NOT a drain of the canonical protocol (likely informational/by-design).",
   manifest_refs=["function:ZetaConnectorZEVM:constructor#x"]),
 dict(id="ZETA-10", contract="ZetaTokenConsumerUniV3/PancakeV3", function="getEthFromZeta", file="contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol", lines="124-156",
   ceiling="HIGH_THREAD", impact_class="theft", attacker="permissionless", confidence="Medium",
   title="getEthFromZeta lacks nonReentrant while sending ETH to caller-controlled destinationAddress (cross-fn reentrancy)",
   mechanism="getEthFromZeta swaps ZETA->WETH->ETH then destinationAddress.call{value}('') with NO nonReentrant (getTokenFromZeta has it). Re-entry into unguarded getZetaFromEth/getZetaFromToken is possible during the ETH callback. Same pattern in PancakeV3.",
   exploit_path="Attacker sets destinationAddress=malicious receiver -> on ETH receipt re-enters an unguarded swap entrypoint within the same tx.",
   impact="Cross-function reentrancy; realized fund impact UNCLEAR statically (needs executed PoC + control).",
   manifest_refs=["function:ZetaTokenConsumerUniV3:getEthFromZeta#x","function:ZetaTokenConsumerPancakeV3:getEthFromZeta#x"]),
 dict(id="ZETA-11", contract="ZetaTokenConsumerTrident", function="getZetaFromEth/getZetaFromToken/getEthFromZeta", file="contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol", lines="82-115",
   ceiling="HIGH_THREAD", impact_class="theft", attacker="conditional", confidence="Medium",
   title="Trident strategy uses poolFactory.getPools(...)[0] with no length/zero/legitimacy validation",
   mechanism="pairPools[0] used directly as the swap pool with no check that the array is non-empty or the pool is canonical; a front-run/permissionless factory entry could route swaps through an attacker pool, and an empty array reverts (DoS).",
   exploit_path="Attacker pre-registers a pool for the pair in a permissionless Trident factory -> victim swaps route through it; OR no pool -> out-of-bounds revert (DoS).",
   impact="Swap fund loss / DoS conditional on Trident factory permissionlessness.",
   manifest_refs=["function:ZetaTokenConsumerTrident:getZetaFromEth#x"]),
 dict(id="ZETA-12", contract="ZetaTokenConsumer*", function="get*Zeta*/get*From*", file="contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol", lines="45-154",
   ceiling="MEDIUM_THREAD", impact_class="griefing", attacker="permissionless", confidence="High",
   title="Swap deadline computed as block.timestamp+MAX_DEADLINE(200s); Trident path has no deadline (weak MEV protection)",
   mechanism="deadline = block.timestamp + 200 is always satisfied at inclusion time, so it provides no staleness protection; Trident router params omit a deadline entirely. minAmountOut is the only slippage guard and depends on the caller.",
   exploit_path="MEV withholds tx then includes during adverse price; deadline passes trivially -> sandwich within caller minOut tolerance.",
   impact="Systematic MEV/sandwich exposure on protocol swaps; griefing/value-leak.",
   manifest_refs=["function:ZetaTokenConsumerUniV2:getZetaFromEth#x"]),
]

# refuted / early-rejected surfaces (recorded, not routed)
REFUTED = [
 dict(id="ZETA-R1", surface="ERC20Custody.deposit reentrancy", reason="nonReentrant modifier present + balance-delta pattern"),
 dict(id="ZETA-R2", surface="ERC20Custody.whitelist/unwhitelist bypass", reason="both guarded by onlyTSS"),
 dict(id="ZETA-R3", surface="ZRC20.transferFrom CEI ordering", reason="EVM atomic revert; no token hooks -> not exploitable"),
 dict(id="ZETA-R4", surface="WZETA uint(-1) infinite-allowance no-decrement", reason="canonical WETH-by-design; owner explicitly approved max"),
 dict(id="ZETA-R5", surface="ZRC20 Deposit event always emits FUNGIBLE_MODULE as from", reason="informational event-attribution only; no fund/state impact"),
 dict(id="ZETA-R6", surface="ZetaNonEth no supply cap (cross-chain)", reason="folded into ZETA-03; relies on out-of-scope connector trust"),
]

findings = []
for c in C:
    findings.append({
        "id": c["id"], "title": c["title"], "severity": SEV[c["ceiling"]],
        "confidence": c["confidence"],
        "description": c["mechanism"],
        "location": {"file": c["file"], "lines": c["lines"], "function": c["function"]},
        "impact": c["impact"],
        "ite": {"intent": c["impact_class"], "technique": c["function"], "evasion": "n/a"},
        "ice_chain": {"exploit_path": c["exploit_path"], "impact": c["impact"], "severity_ceiling": SEV[c["ceiling"]]},
        "manifest_refs": c["manifest_refs"],
        "proof_of_concept": "see L3 readiness record / harness (if built)",
        "recommendation": "see triage",
        "_threat_ceiling": c["ceiling"], "_impact_class": c["impact_class"], "_attacker_model": c["attacker"],
        "_contract": c["contract"],
    })

spec = {"agent": "deep_trace", "contract": "contracts", "findings": findings}
out = audit_path("output") / "findings_deep_trace.json"
out.write_text(json.dumps(spec, indent=2))
print("wrote", out, "with", len(findings), "candidates")

reg = {"phase": "P215", "target": "zetachain-2023-10-holdout", "generated_blind": True,
       "answer_key_read": False, "cap": {"candidates": 12, "deep_traces": 5, "harnesses": 3},
       "candidates": [{"id": c["id"], "contract": c["contract"], "function": c["function"], "file": c["file"],
                       "lines": c["lines"], "threat_ceiling": c["ceiling"], "claimed_severity": SEV[c["ceiling"]],
                       "impact_class": c["impact_class"], "attacker_model": c["attacker"],
                       "confidence": c["confidence"], "title": c["title"]} for c in C],
       "refuted_or_rejected": REFUTED}
(DEL / "CANDIDATE_REGISTER.json").write_text(json.dumps(reg, indent=2))
print("wrote CANDIDATE_REGISTER.json:", len(C), "routed,", len(REFUTED), "refuted")
