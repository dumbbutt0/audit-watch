#!/usr/bin/env python3
"""Append a 'Vulnerability classification & CVSS' section to each submission report.md.

Category labels are taken from the standard Bugcrowd/Immunefi VRT-style taxonomy supplied by the
operator. CVSS v3.1 base scores are computed with the official formula (roundup = ceil to 0.1) and the
vector string is recorded so a reviewer can re-derive. Idempotent: re-running replaces the section
between the BEGIN/END markers rather than duplicating it. Reports only — no production code touched.
"""
import math, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BEGIN = "<!-- BEGIN classification-cvss -->"
END = "<!-- END classification-cvss -->"

# CVSS v3.1 metric weights
AV = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2}
AC = {"L": 0.77, "H": 0.44}
PR_U = {"N": 0.85, "L": 0.62, "H": 0.27}          # scope unchanged
PR_C = {"N": 0.85, "L": 0.68, "H": 0.50}          # scope changed
UI = {"N": 0.85, "R": 0.62}
CIA = {"N": 0.0, "L": 0.22, "H": 0.56}


def roundup(x):
    return math.ceil(round(x * 100000) / 10000.0) / 10.0


def cvss(vec):
    m = dict(p.split(":") for p in vec.split("/") if ":" in p and not p.startswith("CVSS"))
    scope_c = m["S"] == "C"
    iss = 1 - (1 - CIA[m["C"]]) * (1 - CIA[m["I"]]) * (1 - CIA[m["A"]])
    if scope_c:
        impact = 7.52 * (iss - 0.029) - 3.25 * (iss - 0.02) ** 15
    else:
        impact = 6.42 * iss
    pr = (PR_C if scope_c else PR_U)[m["PR"]]
    expl = 8.22 * AV[m["AV"]] * AC[m["AC"]] * pr * UI[m["UI"]]
    if impact <= 0:
        return 0.0
    base = min((impact + expl) * (1.08 if scope_c else 1.0), 10)
    return roundup(base)


def band(score):
    if score == 0:
        return "None"
    if score < 4.0:
        return "Low"
    if score < 7.0:
        return "Medium"
    if score < 9.0:
        return "High"
    return "Critical"


# finding_file -> dict(primary, secondary(optional), cwe(optional), rows[(label,vector)], note(optional))
DATA = {
    "reports/tiprun-2026-06-13/submissions/F-1/report.md": dict(
        primary="Business Logic Errors (broken maintenance-margin validation in `Risk.checkValidTransition` → protocol insolvency / fund loss)",
        secondary="Blockchain → DoS with (Unexpected) revert (Manifestation B / M-1: inverted ratio guard reverts legitimate de-risking)",
        cwe="CWE-840 (Business Logic Errors); CWE-682 (Incorrect Calculation) for the inverted ratio comparison",
        rows=[
            ("Manifestation A (F-1, collateral-withdraw bypass)", "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H"),
            ("Manifestation B (M-1, de-risk DoS / unexpected revert)", "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L"),
        ],
        note="A is permissionless and needs no special chain state (any account holding a position). B is the same defect seen from the other direction.",
    ),
    "reports/tiprun-2026-06-13/submissions/F-2/report.md": dict(
        primary="Blockchain → DoS with (Unexpected) revert (`getRiskFactor` returns `(0,false)` past the top risk segment → `require(riskOk,\"Risk: no risk\")` reverts → account frozen, including un-liquidatable → bad debt)",
        cwe="CWE-755 (Improper Handling of Exceptional Conditions); CWE-691 (Insufficient Control Flow Management)",
        rows=[("Account freeze / liquidation-lock", "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H")],
        note="AC:H reflects the precondition that notional must exceed the top configured risk segment (reachable via a large position or an oracle move).",
    ),
    "reports/tiprun-2026-06-13/submissions/M-2/report.md": dict(
        primary="Insufficient Cryptography / Insecure Design → Business Logic Errors (oracle price consumed with no read-side staleness check; monotonic-update guard disabled)",
        secondary="Sensitive Data / data-authenticity: Insufficient Verification of Data Authenticity",
        cwe="CWE-345 (Insufficient Verification of Data Authenticity); CWE-672 (Operation on a Resource after Expiration/Release)",
        rows=[("Stale-price acceptance", "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L")],
        note="Impact realises only while the feed is stale (AC:H).",
    ),
    "reports/tiprun-2026-06-13/submissions/M-3/report.md": dict(
        primary="Unsecure Design → Violation of Secure Design Principles (Liquidate/Deleverage have no on-chain maintenance-margin precondition; correctness relies entirely on the trusted off-chain batcher)",
        cwe="CWE-657 (Violation of Secure Design Principles); CWE-285 (Improper Authorization of the liquidation precondition)",
        rows=[("Trusted-batcher precondition gap", "CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N")],
        note="PR:H — exploitation requires the privileged batcher to submit a liquidation against a healthy account; this is a trust/centralisation finding.",
    ),
    "reports/tiprun-2026-06-13/submissions/M-4/report.md": dict(
        primary="Business Logic Errors (`setSyntheticAssetsInfo` does not bump `configVersion`; signature/cache validation keyed on the version can pass against stale config)",
        cwe="CWE-840 (Business Logic Errors); CWE-1265 (Unintended Reentrancy/stale-state — informative)",
        rows=[("Missing config-version increment", "CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:L/A:N")],
        note="PR:H (admin config mutation) + AC:H (requires a consumer relying on the version).",
    ),
    "reports/cartha-2026-06-13/submissions/C-1/report.md": dict(
        primary="Business Logic Errors (ERC-4626 share mispricing: `_convertToShares` falls back to the first-deposit 1e12 rate when `_totalValueLocked()` reads 0 while `totalSupply>0` and value exists → deposit at a stale rate steals existing holders' value)",
        secondary="Blockchain → Transaction-Ordering Dependence (TOD) / Front Running (JIT deposit timed to the zero-TVL window)",
        cwe="CWE-682 (Incorrect Calculation); CWE-840 (Business Logic Errors)",
        rows=[("Stale/zero-TVL share theft", "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:N")],
        note="S:C — the loss accrues to *other* vault holders (beyond the attacker's own position). AC:H — requires the gmPrice<=0 / TVL==0 window (reachability confirmed via 0xMarkets X-1). CVSS band (Medium) is conservative; the protocol/bounty severity is **High** because it is direct, permissionless theft of other users' funds once that window is reached.",
    ),
    "reports/cartha-2026-06-13/submissions/L-1/report.md": dict(
        primary="Business Logic Errors (rounding/dust underpayment in parent-vault withdraw/release)",
        cwe="CWE-682 (Incorrect Calculation)",
        rows=[("Withdraw/release dust underpay", "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N")],
        note="Analysis-only (no runnable PoC); dust-magnitude impact.",
    ),
    "reports/cartha-2026-06-13/submissions/L-2/report.md": dict(
        primary="Business Logic Errors (child shares are ERC-20-transferable after lock but redemption is position-bound → transferred shares are not redeemable by the recipient)",
        cwe="CWE-840 (Business Logic Errors)",
        rows=[("Transferable-but-bound shares", "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N")],
        note="Low — a holder can orphan value by transferring locked shares; no theft from the protocol.",
    ),
    "reports/0xmarkets-2026-06-13/submissions/X-1/report.md": dict(
        primary="Business Logic Errors (signed `getMarketTokenPrice` can return ≤ 0 by design — int256, 0 when poolValue==0, negative when poolValue<0)",
        cwe="CWE-682 (Incorrect Calculation) — informative",
        rows=[("GMX-inherited signed price ≤ 0", "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:N")],
        note="Informational for 0xMarkets (inherited GMX-Synthetics behaviour, not a 0xM-introduced bug). No standalone impact here — recorded because it grounds the reachability of **Cartha C-1**. CVSS base 0.0 (no direct impact in 0xM scope).",
    ),
    "reports/0xmarkets-2026-06-13/submissions/I-1/report.md": dict(
        primary="Blockchain → Transaction-Ordering Dependence (TOD) / Front Running (insurance injection compensates *current* LP holders, not the drawdown-era holders → JIT capture of the insurance reserve)",
        secondary="Business Logic Errors (value-attribution mismatch in `attemptInjectPool`)",
        cwe="CWE-362 (Race Condition / TOD); CWE-840 (Business Logic Errors)",
        rows=[("JIT insurance-reserve capture", "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N")],
        note="Design finding (analysis-only, no standalone PoC — needs full GMX build). CVSS band Low; design severity Medium (value redistribution among LPs, timing-dependent).",
    ),
    "reports/0xmarkets-2026-06-13/submissions/I-2/report.md": dict(
        primary="Unsecure Design → Violation of Secure Design Principles (`triggerFactor` unset-default 0 means inject-on-any-drawdown; the disable sentinel is `uint256` max, an unsafe default)",
        cwe="CWE-1188 (Insecure Default Initialization of Resource); CWE-657 (Violation of Secure Design Principles)",
        rows=[("Unsafe default trigger config", "CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:L/A:N")],
        note="Config/design finding (analysis-only). PR:H — depends on deployment config.",
    ),
}


def section_for(meta):
    lines = [BEGIN, "", "## Vulnerability classification & CVSS", ""]
    lines.append(f"- **Category (VRT):** {meta['primary']}")
    if meta.get("secondary"):
        lines.append(f"- **Secondary category:** {meta['secondary']}")
    if meta.get("cwe"):
        lines.append(f"- **CWE (informative):** {meta['cwe']}")
    lines.append("")
    lines.append("| Aspect | CVSS v3.1 vector | Base score | Severity |")
    lines.append("|---|---|---|---|")
    for label, vec in meta["rows"]:
        s = cvss(vec)
        lines.append(f"| {label} | `{vec}` | **{s:.1f}** | {band(s)} |")
    lines.append("")
    if meta.get("note"):
        lines.append(f"> {meta['note']}")
        lines.append("")
    lines.append("> CVSS v3.1 base scores computed with the official formula (no temporal/environmental "
                 "modifiers). For smart-contract findings the protocol/bounty severity may differ from the "
                 "CVSS band; both are stated where they diverge.")
    lines.append("")
    lines.append(END)
    return "\n".join(lines)


def main():
    for rel, meta in DATA.items():
        path = os.path.join(ROOT, rel)
        with open(path) as f:
            txt = f.read()
        sect = section_for(meta)
        if BEGIN in txt and END in txt:
            txt = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), sect, txt, flags=re.S)
        else:
            txt = txt.rstrip() + "\n\n" + sect + "\n"
        with open(path, "w") as f:
            f.write(txt)
        scores = ", ".join(f"{cvss(v):.1f} {band(cvss(v))}" for _, v in meta["rows"])
        print(f"updated {rel}  -> {scores}")


if __name__ == "__main__":
    main()
