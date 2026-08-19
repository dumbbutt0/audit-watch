/**
 * TON (FunC) Level-3 PoC skeleton — @ton/sandbox (local, in-process TVM; no network/keys).
 *
 * Drop this into a Blueprint repo's tests/ (for STON.fi: ston-fi/dex-core-v2, which already ships typed
 * wrappers under wrappers/). Replace the <FINDING> placeholders. The three layers (L1 entry / L2 state-flip /
 * L3 outcome) are separate `it()` blocks; on the L3 exploit assertion the test prints "BUG CONFIRMED" so the
 * harness (scripts/run_poc_tests.py determine_status) marks the PoC "proved".
 *
 * Run:  npx blueprint test poc      (or)   npx jest tests/poc.spec.ts
 */
import { Blockchain, SandboxContract, TreasuryContract } from '@ton/sandbox';
import { Address, beginCell, toNano } from '@ton/core';
import '@ton/test-utils';
// import { Router } from '../wrappers/Router';   // reuse the AUDITED typed wrappers — do not re-implement
// import { Pool } from '../wrappers/Pool';
// import { LPAccount } from '../wrappers/LPAccount';

describe('<FINDING-ID> — <one-line claim>', () => {
    let blockchain: Blockchain;
    let deployer: SandboxContract<TreasuryContract>;
    let victim: SandboxContract<TreasuryContract>;
    let attacker: SandboxContract<TreasuryContract>;
    // let router: SandboxContract<Router>;
    // let pool: SandboxContract<Pool>;

    beforeEach(async () => {
        blockchain = await Blockchain.create();
        deployer = await blockchain.treasury('deployer');
        victim = await blockchain.treasury('victim');
        attacker = await blockchain.treasury('attacker'); // L1: a fresh, unprivileged EOA-equivalent

        // --- legitimate setup via the contracts' OWN flows (no hand-written storage) ---
        // router = blockchain.openContract(Router.createFromConfig({ ... }, await compile('Router')));
        // await router.sendDeploy(deployer.getSender(), toNano('1'));
        // ...provide real liquidity, mint real jettons to `victim`, etc.
    });

    it('L1 entry: attacker can reach the in-scope message unprivileged', async () => {
        // Send the in-scope message from `attacker` with NO privileged setup.
        // const res = await router.sendSomething(attacker.getSender(), { value: toNano('0.2'), ... });
        // expect(res.transactions).toHaveTransaction({ from: attacker.address, to: router.address, success: true });
        expect(true).toBe(true); // <-- replace
    });

    it('L2 state flip: name the exact storage/balance and assert before vs after', async () => {
        // const before = (await blockchain.getContract(pool.address)).balance; // raw TON balance
        // const reservesBefore = await pool.getReserves();                     // get-method on the wrapper
        //
        // ...perform the attacker action (forged transfer_notification / crafted cell / interleaved msg)...
        //
        // const reservesAfter = await pool.getReserves();
        // expect(reservesAfter.reserve0).not.toEqual(reservesBefore.reserve0); // the concrete invariant break
        expect(true).toBe(true); // <-- replace
    });

    it('L3 outcome: prove the economic/security consequence', async () => {
        // Example shapes (uncomment the one that fits the finding):
        //
        // (a) THEFT — attacker jetton/TON balance increased with no legitimate deposit:
        //   const attackerBalBefore = await attackerJettonWallet.getBalance();
        //   ...attack...
        //   const attackerBalAfter = await attackerJettonWallet.getBalance();
        //   expect(attackerBalAfter).toBeGreaterThan(attackerBalBefore);
        //
        // (b) SENDER-SPOOF — a forged transfer_notification from a NON-real-wallet treasury is accepted:
        //   const res = await pool.sendTransferNotification(attacker.getSender(), { jettonAmount, fromAddress: victim.address, forwardPayload });
        //   expect(res.transactions).toHaveTransaction({ to: pool.address, success: true }); // should have reverted
        //
        // (c) BOUNCE STRANDING — force downstream throw; bounce returns but state not restored:
        //   const res = await lpAccount.sendAddLiquidity(victim.getSender(), { ...makeDownstreamFail });
        //   expect(res.transactions).toHaveTransaction({ inMessageBounced: true });
        //   const data = await lpAccount.getData();
        //   expect(data.amount0).toBeGreaterThan(0n); // reserved amount stranded, never refunded
        //
        const exploitProven = false; // <-- set from the real assertion above
        expect(exploitProven).toBe(true);
        if (exploitProven) console.log('BUG CONFIRMED'); // harness keys "proved" off this string
    });
});
