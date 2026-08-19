#!/usr/bin/env bash
# Cronos latent-Critical watcher: pings when either dormant bug becomes LIVE.
#
#  1) Fulcrom broker-fee drain  -> arms when Vault.isLeverageEnabled() flips to TRUE
#     (and/or feeReserves becomes fundable). Vault 0x8C7Ef34aa54210c76D6d5E475f43e0c11f876098
#  2) VVS ConditionalLiquidity breakLp sweep -> arms when the contract starts holding VVS
#     or has LP staked. CL 0xb79dcd181bc79d1774df65658fcbe9916beda3a5
#
# Read-only (eth_call). Prints OK / ALERT, writes state JSON, exits 0 (no flip) or 9 (flip).
set -u
CAST="${CAST:-$HOME/.foundry/bin/cast}"
STATE="${STATE_FILE:-$HOME/clones/audit-watch/smart-contract-auditor/audits/_monitors/cronos_latent_state.json}"
mkdir -p "$(dirname "$STATE")"

RPCS=("https://evm.cronos.org" "https://cronos-evm-rpc.publicnode.com" "https://cronos.drpc.org")
VAULT=0x8C7Ef34aa54210c76D6d5E475f43e0c11f876098
VVS=0x2D03bECE6747ADC00E1a131BBA1469C15fD11e03
CL=0xb79dcd181bc79d1774df65658fcbe9916beda3a5
CRAFT=0xDccd6455AE04b03d785F12196B492b18129564bc

call() { # usage: call <sig> <to> [args...] ; tries each RPC. cast order: cast call <to> <sig> [args...]
  local sig="$1" to="$2"; shift 2
  for rpc in "${RPCS[@]}"; do
    out=$("$CAST" call "$to" "$sig" "$@" --rpc-url "$rpc" 2>/dev/null) && { echo "$out"; return 0; }
  done
  echo "RPC_ERROR"; return 1
}

# Fulcrom: leverage flag (the gate that makes the broker-fee bug reachable)
LEV=$(call "isLeverageEnabled()(bool)" "$VAULT")
# VVS: does ConditionalLiquidity now hold VVS, or have LP staked in Craftsman pid 4?
VVSBAL=$(call "balanceOf(address)(uint256)" "$VVS" "$CL"); VVSBAL=${VVSBAL%% *}
STAKED=$(call "userInfo(uint256,address)(uint256,uint256)" "$CRAFT" 4 "$CL" | head -1); STAKED=${STAKED%% *}

ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
fulcrom_armed=false; vvs_armed=false
[ "$LEV" = "true" ] && fulcrom_armed=true
case "$VVSBAL" in ''|0|RPC_ERROR) :;; *) vvs_armed=true;; esac
case "$STAKED" in ''|0|RPC_ERROR) :;; *) vvs_armed=true;; esac

cat > "$STATE" <<EOF
{"checked_at":"$ts","fulcrom":{"isLeverageEnabled":"$LEV","armed":$fulcrom_armed},
 "vvs":{"conditionalLiquidity_vvsBalance":"$VVSBAL","craftsman_pid4_staked":"$STAKED","armed":$vvs_armed}}
EOF

flip=0
echo "[$ts] Fulcrom.isLeverageEnabled=$LEV | VVS CL vvsBalance=$VVSBAL stakedPid4=$STAKED"
if $fulcrom_armed; then
  echo "ALERT: FULCROM broker-fee bug is now LIVE-REACHABLE (isLeverageEnabled=true). Submit reports/cronos-fulcrom-2026-06-20/DISCLOSURE_broker_fee_liquidation_double_charge.md as a Critical with a fork PoC at the current block. BE FIRST."
  flip=9
fi
if $vvs_armed; then
  echo "ALERT: VVS ConditionalLiquidity now holds funds (vvsBalance/staked>0) -> breakLp sweep is becoming LIVE. Submit reports/cronos-vvs-2026-06-20/DISCLOSURE_breakLp_full_balance_sweep.md as a Critical with a fork PoC. BE FIRST."
  flip=9
fi
[ "$flip" = "0" ] && echo "OK: both latent bugs still dormant (perps disabled / CL empty). No action."
exit $flip
