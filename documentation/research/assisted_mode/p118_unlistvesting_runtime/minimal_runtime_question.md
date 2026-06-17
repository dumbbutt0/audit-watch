# P118 — Minimal runtime question

> **Can a party other than the seller/admin unlist a seller's ACTIVE listing via
> `SecondSwap_Marketplace.unlistVesting`, or can a listing be unlisted twice — i.e. can the suspected
> "permissionless" surface (per the ranking) actually delist someone else's vesting or return its balance more than
> once?**

- Independent variable: caller identity (seller vs admin vs unauthorized) and number of unlist calls.
- Measured: does `unlistVesting` revert for an unauthorized caller; does a second unlist revert; does the legitimate
  seller/admin path succeed exactly once.
- The harness answers ONLY this access/double-unlist integrity question. Runtime decides; source frames.
