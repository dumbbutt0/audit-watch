# Clean DeFi SDK

A small, well-behaved TypeScript SDK for interacting with our contracts.

## Setup

```sh
npm ci --ignore-scripts
npm run build
npm test
```

## Safe math

We use a `safeCast` helper and document each function with NatSpec. See
`src/index.ts` for the public API.
