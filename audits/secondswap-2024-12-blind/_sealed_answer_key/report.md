# SecondSwap (Code4rena 2024-12) — Awarded Findings (revealed at adjudication)

Source: https://code4rena.com/reports/2024-12-secondswap (web-fetched 2026-06-17 at REVEAL, AFTER the blind
cold pass — the prior stub peeked counts only, titles UNSEEN). 3 High / 20 Medium. Titles used for
token-overlap adjudication vs the blind cold pass; NEVER matched against source.

## High Risk Findings
- H-01 | Vesting listing order affects claimable amounts at given steps
- H-02 | transferVesting creates incorrect vesting for new users due to uniform stepsClaimed
- H-03 | Incorrect releaseRate calculation allows unlocking more tokens than locked

## Medium Risk Findings
- M-01 | Incorrect listing type validation bypasses minimum purchase enforcement
- M-02 | Discounted listings become unpurchasable due to rounding
- M-03 | Missing token removal option from whitelist risks financial losses
- M-04 | One vesting plan creator can affect others' vesting plans
- M-05 | Price granularity limited by payment token decimals
- M-06 | Underflow in claimable function prevents claiming
- M-07 | Buy and sell fees unknown before purchase execution
- M-08 | Outdated penalty fees charged if modified since listing
- M-09 | Users can prevent reallocation by listing to marketplace
- M-10 | Already-vested tokens can be transferred from users
- M-11 | maxSellPercent bypassed by selling previously bought vestings
- M-12 | Unauthorized increase of maxSellPercent possible
- M-13 | Marketplace change in vesting manager loses previous listings
- M-14 | Incorrect referral fee calculations
- M-15 | Missing sellable check allows buying unsellable tokens
- M-16 | DoS possible when transferring vests to another address
- M-17 | Rounding error in stepDuration calculations
- M-18 | Unlisting after claiming locks tokens that should be claimable
- M-19 | Large step counts may cause fund loss or uneven distribution
- M-20 | maxSellPercent broken when delisting after additional claims
