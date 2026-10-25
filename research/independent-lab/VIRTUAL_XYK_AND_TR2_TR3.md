# Independent lab: virtual XYK and DAO wallet authority

This note records separate, bounded tests against pinned daos.fun Solana binaries and finalized public accounts. It complements the repository's [source reconstruction and audit](../../audit/AUDIT.md); it does not claim a new live exploit. No mainnet transaction, real user-wallet signature, or live fund movement was made. Receipt paths below are lab-relative and included in the [daos.fun evidence bundle](daosfun-lab-evidence.tar.zst).

The tested `virtual_xyk` ProgramData binary is SHA-256 `c151c6b15b84d8bfc47a5f2e0e5b9e04babff0263a1125a9e8dcb07df6144377`. The current DAO-v1 binary is SHA-256 `5020271255ea678fc110fed4671a86b1b7268acad04f990c590decd92091143d`, matching this repository's byte-identical reconstruction. The lab's combined offline verifier passed after these receipts were integrated. All **10/10** listed virtual-XYK handlers have at least one bounded local path; **0/10** are marked fully reversed (`analysis/root_virtual_xyk/behavior-coverage.json`).

The incomplete VirtualXYK Anchor/SBF candidate now implements bounded
`buy_token` and `sell_token` bodies. The [14-case buy](receipts/daos-virtual-buy-candidate-differential.json)
and [16-case sell](receipts/daos-virtual-sell-candidate-differential.json)
signed offline differentials match the pinned executable's error outcomes
and complete watched account post-states: nine and ten successes, respectively.
The sell controls cover exact slippage, an unfunded user ATA, an empty funding
vault, deactivation, and a sale whose gross output exceeds the Curve's recorded
funding reserve. That last call traps and rolls back in both programs on the
sampled state; it does not establish a current live funds issue. The signer
ATAs are synthetic, and LP-enabled cases toggle a copied Curve's LP Option
locally rather than demonstrate real LP initialization. Other pools,
token-program combinations, transfer-fee modes, full error ordering,
compute units, and source-location logs remain unmatched or untested.
The candidate ELF is not byte-identical to deployment, and eight other
handlers still fail closed.

A [custom-stack version audit](receipts/custom-stack-version-audit.json)
finds current virtual-XYK ELF for ten selected signed local paths, including
the composed lifecycle and separate migration/LP withdrawal controls. That
does not establish exact historical prestates or every reachable CPI branch.

## Bounded virtual-XYK behavior

| Path | Independent observation | Main receipts |
| --- | --- | --- |
| Buy and sell | LP-disabled integer quotes, Curve changes and user/vault balances matched 227 local cases. LP-enabled quotes include a pre-division `995/1000` factor; 862 sampled two-way quotes and deltas matched the model. | `analysis/root_virtual_xyk/quote-cases.json`, `lp-swap-quote.json`, `lp-swap-sequence.json` |
| LP liquidity | Locally reconstructed add/remove paths matched 447 asserted reserve, LP-supply and account-delta cases. The LP-enabled prestate and some extreme states are synthetic. | `analysis/root_virtual_xyk/liquidity-probes.json`, `liquidity-guards.json`, `liquidity-zero-boundaries.json` |
| Composition | A fresh disposable Curve ran signed local initialization, LP creation, buys, sells, add/remove liquidity, migration and fee redemption. Initial traded-token account funding remained a local fixture. | `analysis/root_virtual_xyk/signed-local-lifecycle.json` |
| Migration and LP withdrawal | Reconstructed migration transfers stored `T` and `F`, burns the Curve LP vault, and deactivates the Curve. One validly signed Raydium-LP withdrawal matched its integer ratio after a one-unit LP holding was seeded locally; that holding has no historical provenance. | `analysis/root_virtual_xyk/migrate-liquidity-invariants.json`, `lp-supply-reconstruction.json`, `signed-lp-withdraw.json` |

These are differential observations of specific states, account layouts and branches. The original historical prestate is unavailable for several calls, and neither successful source transactions nor local fixtures cover every reachable behavior.

## Active fees and authorization

A read-only finalized capture found **48 active LP-disabled Curves**, of which **45** recorded `319,466,808,380` wrapped-SOL base units in available fees (`total_fee_amount − total_fee_distributed`). These fees are **already included** in their funding-vault balances. Thirty-five Curves name legacy FeeShare PDAs as fee authority; thirteen name the **same** system-owned administrative address. Every captured funding vault covered stored `F + available fees`. No vault exceeded `F + V + available fees`: 26 equaled that expression, while 22 held less because some or all `V` was virtual. The excess over `F + fees` in fifteen vaults is therefore not evidence of freely withdrawable surplus. See `analysis/root_virtual_xyk/active-fee-authority-census.json` and `active-fee-census-validation.json`.

Signed local outer calls through the pinned legacy FeeShare binary let its PDA sign inner `virtual_xyk::redeem_fees` calls on three finalized Curve states. On two **active** legacy-authority Curves, zero, partial and exact-full available-fee claims changed fee counters, wrapped-SOL token amounts and lamports by the same amount; one above the counter failed. The destination was the legacy PDA's ATA, not a caller-owned account. One active Curve's authority ATA was absent: redemption failed `AccountNotInitialized` until that canonical ATA was created **only inside LiteSVM**, after which the recorded fee could move while its `V`-related vault balance stayed. See `analysis/root_virtual_xyk/signed-legacy-redeem-cpi.json`, `signed-legacy-redeem-peers.json`, and `signed-active-legacy-redeem.json`.

On an active Curve whose fee authority is the system-owned administrative key, an unrelated signed key failed `InvalidFeeAuthority`; a call naming the real key but lacking its signature failed signature verification. Successful direct claims required explicitly replacing the Curve's fee-authority field **in a local copy** with a disposable signer. They do not show control of the real administrative key or an on-chain claim (`analysis/root_virtual_xyk/active-system-fee-snapshot.json`, `signed-active-system-redeem.json`).

## Migration signer boundary

An unrelated signer cannot directly migrate an LP-enabled Curve: `migrate_liquidity` requires **both** the recipient `signer` and Curve `depositor` signatures. A fresh signed local Curve paid its depositor on a D-only call; D and an unrelated O co-signing deliberately routed reserves to O's canonical ATAs. Missing either signature rejected. On extant DAO Curves the depositor is a program PDA, so this local D keypair does not represent live DAO authorization (`analysis/root_virtual_xyk/signed-outsider-migrate.json`).

The historical DAO `LegacyToRaydium` selector is absent from the pinned current DAO binary: a local dispatch call returns Anchor fallback 101. Current DAO `ExecuteInvoke` can reach an inner virtual `MigrateLiquidity` call but does **not** sign the DAO State/depositor PDA; the inner handler rejects `AccountNotSigner` 3010. That same guard preceded deactivation and balance checks when the Curve was restored to a synthetic active prestate. These tests rule out the sampled current generic wrapper as a depositor-signature bypass; they do not cover every other DAO handler or the source-era wrapper (`analysis/root_virtual_xyk/dao-legacy-migration-selector.json`, `dao-execute-virtual-migrate.json`). The finalized Curve census had **zero active LP-enabled Curves** at capture.

## Token-2022 compatibility is prospective

On **synthetic** transfer-fee traded mints, a signed buy accepted a gross token minimum while the recipient received less spendable balance; initialization and sells created or widened a stored-reserve-versus-vault gap. A later buy could fail at its exact spendable-vault boundary. On a **synthetic** fee-bearing funding mint, a sell's gross minimum passed although its spendable payout was lower, and LP migration failed until a controlled local top-up restored backing. Zero-fee controls conserved balances. Receipts: `analysis/root_virtual_xyk/signed-fee-buy.json`, `signed-fee-sell-sequence.json`, `signed-fee-migration.json`, and `signed-funding-fee.json`.

The finalized 133-Curve mint census found **no** traded mint with Token-2022 `TransferFeeConfig`, and every observed Curve used classic wrapped SOL as funding mint (`analysis/root_virtual_xyk/risk-current-inventory.json`). These local incompatibilities identify neither an affected present pool nor present user loss. Token-2022 [transfer-fee configuration must precede mint initialization](https://solana.com/docs/tokens/extensions/transfer-fees); a new eligible mint/pool or an exceptional reinitialization route would need separate proof.

The [stateful signed Surfpool fee matrix](receipts/fee-surfpool-stateful.json)
repeats the gross-minimum versus spendable-balance result with a fresh
synthetic transfer-fee mint. A zero-fee control conserves balances; at
100 bps, the buy accepts a gross minimum above the buyer's spendable
receipt, and the reserve shortfall can stop migration until a precisely
measured local top-up. The [LP-exit fee matrix](receipts/lp-exit-fee-surfpool.json)
shows a full LP withdrawal failing on a 10-million-raw-unit spendable-vault
shortfall at 100 bps, then succeeding after a signed local top-up while a
larger stored reserve remains unbacked. Its minimum-token check also uses
gross output. Both are conditional compatibility and exit-liquidity risks
on synthetic mints, not current live exposure.

## Active traded-mint authority

All 48 captured active Curve traded mints retained a mint authority derived
as a DAO-v1 State PDA (35) or FounderDAO State PDA (13). On one mint of each
kind, direct signed Token-2022 `MintTo` failed without the program PDA's
signature; a deliberately substituted local mint authority supplied the
positive control. Current DAO `ExecuteInvoke` did not sign its State PDA for
the tested MintTo route. In 39 saved successful post-deployment Founder
transactions, the seven `ClaimTeamAllo` calls minted a distinct party mint
and transferred previously issued DAO tokens; they did not mint more of the
traded token in those traces. See the [active-mint reachability audit](receipts/active-mint-reachability.json)
and [signed controls](receipts/active-mint-signer-controls.json). This does not rule out other
State-PDA-signing handlers, key custody paths or future issuance.

## DAO-v1 TR-2 and TR-3 live-state controls

The [published DAO-v1 audit](../../audit/AUDIT.md) establishes the underlying code mechanisms. The independent work below narrows **current exposure**, without testing the off-chain cosigning policy or submitting a live call.

* **TR-2, shared cosigner.** A [finalized owner census](receipts/tr2-current-cosigner-census.json) found the configured cosigner `AeqZQ…` held `3,910,061,294` lamports (about 3.91 SOL) and **zero** classic SPL or Token-2022 token accounts. In a [valid-signature local-key substitution](receipts/tr2-cosigner-sol-local.json), DAO `ExecuteInvoke` forwarded a writable disposable cosigner's genuine outer signature into a System transfer of 1,000,000 local lamports. An unrelated unsigned source and a missing cosigner signature rejected. Real SOL exposure requires an admin/delegate-authored payload that makes the real cosigner writable **and** approval by its off-chain signing service; neither was observed.
* **TR-3, closed treasuries.** Among 35 DAO-v1 State PDAs associated with active virtual-XYK Curves, eight were admin-closed with redemption started. Their wallet PDAs' wrapped-SOL token accounts held `275,112,958,624` atoms. [Read-only owner enumeration](receipts/tr3-closed-wallet-token-accounts.json) of **all eight closed wallets** found **202** token accounts (180 classic SPL; 22 Token-2022), including 192 outside the initial derived-ATA screen. **None** had a token delegate or close authority at the captured finalized slots. This does not negate the source-level close/snapshot flaw or rule out other DAO wallets, authority types or future approvals. Full receipts in the bundle: `analysis/root_virtual_xyk/tr3-active-dao-wallet-authorities.json`, `tr3-closed-wallet-query-cache.json`.

`analysis/root_virtual_xyk/tr2-tr3-offline-validation.json` pins and rechecks the saved TR-2/3 account records and local controls. RPC captures span several finalized slots; State bytes were rechecked, but balances and delegated authority can change afterward. The research adds no claim beyond the [repository audit](../../audit/AUDIT.md) about severity or exploitation.
