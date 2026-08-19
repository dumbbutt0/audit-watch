// Clean DeFi SDK — public API.
// Provides a safe cast helper and a thin ethers wrapper. No network calls at import time.

import { Contract, type Provider } from "ethers";

/** Safely narrow a bigint to a uint128 range, reverting callers on overflow. */
export function safeCastUint128(value: bigint): bigint {
  const MAX = (1n << 128n) - 1n;
  if (value < 0n || value > MAX) {
    throw new RangeError("value out of uint128 range");
  }
  return value;
}

export function attach(address: string, abi: unknown[], provider: Provider): Contract {
  return new Contract(address, abi as any, provider);
}
