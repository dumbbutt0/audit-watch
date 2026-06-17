# hybra — Phase 4: Discovery coverage (PRE-REVEAL, FROZEN)
## H-L1 multiSplit
- total discovered: 6 (M1-M3 + T4/T8/T5). by family: A×2, B×1, G×1; templates T4,T8,T5.
- top-5: T8 (voting-power inflation round-trip), M1 (permanentLockBalance desync), M2 (rounding dust), T4 (conversion residue), M3 (checkpoint).
- Pass 2 added beyond Pass 1? **YES** — T8 split/merge round-trip voting-power inflation (Pass 1 missed the round-trip framing).
- deserve ranking: T8, M1, M2.
## H-L2 merge
- total 4; top-5: M1, T6, M2, T4. Pass2 added T6 round-trip drift. deserve ranking: M1, T6.
## H-L3 _distribute
- total 4; top-5: M1, T6, M2, T1. Pass2 added T1 DoS + T6 drift. deserve ranking: M1, T6.
**Family/template coverage:** A/B/G + T1/T4/T5/T6/T8 populated; D/E/F sparse (ve is not callback/identity-heavy).
Pass 2 materially added round-trip (T8) and DoS (T1) shapes a family-only pass missed. **FREEZE.**
