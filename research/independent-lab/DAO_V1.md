# DAO v1: independent versioned replays and binding checks

The current `dao_v1` ProgramData ELF captured by this lab is SHA-256
`5020271255ea678fc110fed4671a86b1b7268acad04f990c590decd92091143d`,
byte-identical to this repository's original capture and rebuilt binary.
All 18 current site-IDL selectors have a bounded successful local path with
the exact current DAO binary. The [per-handler custom-stack audit](receipts/dao-v1-custom-stack-version-audit.json)
finds **16/18** selected bounded paths using current custom CPI binaries.
`init_curve` and `migrate_bonding_to_meteora` succeed locally with source-era
CP DAMM, while their restored current-CP controls reject downstream 6067.
These are compatibility controls on selected account prestates, not proof
that every current account state reaches or fails the same CPI. **0/18** are
certified full behavior. The
[per-handler binary provenance](receipts/dao-v1-binary-provenance.json)
pins the root ELF hash and receipt for each claim. The
[InitCurve ABI comparison](receipts/dao-v1-init-curve-abi-compatibility.json)
ties the 6067 failure to a fee-parameter layout mismatch in the tested
current CP DAMM path; its source interpretation is not a byte-identical CP
reconstruction. Exact source recovery materially improves
review, but this lab has not closed all
reachable account, authority, math, historical-version and error branches.
The [MigrateBonding current-CP replay](receipts/dao-v1-migrate-bonding-current-stack-restored-replay.json)
records the second 6067 control on a locally restored historical fixture.
An independent [offline Surfpool ABI matrix](receipts/dao-cp-abi-offline-surfpool.json)
uses a valid disposable signature: `init_curve` and
`migrate_bonding_to_meteora` each fail 6067 with current CP DAMM and
succeed with the source-era CP binary on their restored fixtures. Later
account bytes, flag resets and signer/ATA substitutions limit the result;
it neither proves every live route fails nor establishes permanent lock.
The [six-case current-CP variant matrix](receipts/dao-cp-current-variant-surfpool.json)
uses signed, committed offline Surfpool calls against the pinned current
DAO and CP binaries. Both handlers return CP 6067 and roll back tracked
application accounts across the two restored fixture families, including
locally transplanted alternate fee bytes and State variations. The DAO
source fixes the CP config address; the alternate bytes are a **synthetic
edit at that address**, not a selectable live config. These six failures
extend the bounded compatibility evidence, but do not prove a universal
live fund lock, all-route failure, or lack of other exits.
Original receipt filenames below are inside the
[daos.fun evidence bundle](daosfun-lab-evidence.tar.zst).

## Current DAO/DBC pool binding

The [published audit](../../audit/AUDIT.md) calls out an unbound DBC pool in
`finalize_meteora_bonding` (BM-1). An independent local fixture loaded **this
lab's** pinned current DAO and DBC ELFs, two distinct captured migrated DBC
pools and DAO States, and a genuinely signed disposable payer. Finalizing
DAO X with X's pool succeeded. On fresh local state, finalizing **DAO Y with
X's pool** also succeeded: X's pool migration-fee status moved 0→4 while Y's
`curve_initialized` moved 0→1 and `funding_goal` 0→66,000,000,000. X's later
honest finalize failed DBC 6040. This confirms an unprivileged cross-pool
lifecycle/state-binding flaw in the current binary under the tested account
layout. The saved DBC config's migration-fee field is **zero** and the
captured quote vault/treasury balances did not change, so this independent
fixture does **not** prove presently diverted treasury tokens. In an
**explicitly synthetic** config with migration-fee byte 10, the same local
route moves 6.6 billion raw funding units from X's quote vault into Y's
treasury before X's honest finalize fails. This isolates the conditional
fee-diversion mechanism. See the [signed cross-pool receipt](receipts/dao-bm1-cross-pool-current-config.json)
(`analysis/daos_fun/dao-bm1-cross-pool-current-config.json`) and
`scripts/daos_dao_bm1_cross_pool.py`.

The code mechanism is consistent with the published source: the handler
checks the supplied DAO State but takes a caller-chosen pool, then uses one
global `meteora_authority` PDA for the DBC fee-withdrawal CPI. A fee-bearing
configuration and a still-withdrawable pool are separate prerequisites for
current fund diversion. A later finalized [three-pool sample](receipts/dao-bm1-current-exposure-snapshot.json), not a
network-wide census, found three migrated DBC pools still at migration-fee
status zero paired with unfinalized DAO States; the same deployed DBC config
had fee byte zero. See `dao-bm1-current-exposure-snapshot.json`. No mainnet
transaction was sent.

A later [finalized read-only account capture](receipts/bm1-mainnet-readonly-20261024.json)
pins the current DAO/DBC binaries and both pool/State accounts in one RPC
context at slot 460,995,695. A separate
[public RPC simulation](receipts/bm1-mainnet-unsigned-atomic-success1-20261024.json)
used `simulateTransaction` with **`sigVerify:false`** and a public payer
whose key was not held. It simulated the missing wallet and ATA setup plus
the cross-pool finalization in one transaction and returned no instruction
error. Pre/post finalized reads stayed unchanged: the simulation did not
broadcast, verify a real signature, create a live wallet, or move funds.
The [validly signed offline Surfpool control](receipts/dao-bm1-cross-pool-surfpool.json)
separately reproduces honest and cross-pool state/status transitions with
the captured deployed fee byte **0**, so its token payout is zero. A
positive 6.6-billion-raw-unit redirect again requires a locally edited fee
byte **10**; one absent base-vault PDA is supplied only as a synthetic local
placeholder. These receipts strengthen current-version mechanism evidence
without proving a broadcastable outsider transaction or current token theft.

## Conditional transfer-hook redemption failure

A [22-transaction signed offline control](receipts/dao-hook-redemption-receipt.json)
loads the captured original DAO ELF into LiteSVM. In a closed, redeeming DAO
fixture, a hook-free Token-2022 treasury asset pays **90,939,343 raw units**
to the holder. An otherwise equivalent asset with an active, immutable
TransferHook reaches Token-2022 `TransferChecked` but fails `MissingAccount`;
token balances and the attempted redemption records roll back, apart from
the local transaction fee. Supplying the hook validation PDA and hook program
as extra *outer* DAO account metas does not change that result. A direct
transfer with those accounts succeeds and invokes the allow-all hook, so the
control distinguishes the nested DAO transfer from a broken hook fixture.
An open-fund `execute_invoke` control can transfer the hooked asset after
synthetic admin/cosigner substitution; the equivalent wallet-signed exit
after closure stops at DAO error 6013 before Token-2022 CPI.

The DAO State, DAO mint, and State token vault were restored from a later
finalized capture. The hook and hook-free treasury mints, allow-all hook,
mint authority, and burn credit are **local synthetic fixtures**. Token-2022,
System, and ATA execute through LiteSVM's native defaults. The reviewed hook
has no update authority, but another mint could have one; a delegate, other
exit, or upgrade might also change reachability. This is a bounded
compatibility failure against the captured original, **not** proof of an
affected live treasury, user loss, or an irreversible lock. The complete
[source, fixture binary, verifier, and receipt](daosfun-lab-evidence.tar.zst)
are under `analysis/daos_fun/dao-hook-redemption/` in the bundle. The saved
verifier checks the 22 signatures and recorded account/error controls; the
local runner with fixed disposable signing vectors is intentionally omitted.

A [finalized read-only ten-wallet sample](receipts/dao-transfer-hook-mainnet-sample.json)
covered eight previously observed closed/redeeming DAO wallets and two
nonredemption controls. Their 32 Token-2022 accounts held 23 nonzero
balances over 19 mints; **none** of those sampled mints had a TransferHook
extension at the recorded slots. The sample neither covers every DAO nor
proves absence later. A separate [ProgramData header check](receipts/programdata-head-check.json)
at RPC slot **461,128,520** found the pinned last-deploy slot **370,107,442**.
It supports version continuity but did **not** rehash the current full
ProgramData payload. No public transaction was submitted.

## Signed offline expiry and redemption timing

The [TR-1 Surfpool receipt](receipts/dao-tr1-expiry-signed-surfpool.json)
commits a validly signed local admin-and-cosigner `execute_invoke` wallet
transfer after the copied State's expiration. An ordinary signed holder
cannot `close_fund` or `init_redemption` while that State remains open;
locally setting the closed flag allows redemption. The admin and cosigner
identities were replaced with disposable local keys, so this demonstrates
the missing holder-enforceable expiry gate in the tested current-binary path,
not the real platform's cosigning policy, a live locked fund, or an outsider
drain.

The separate [TR-5 redemption-timing receipt](receipts/dao-redemption-timing-signed-surfpool.json)
uses two isolated writable Surfpool ledgers with the same signed holder
burns and signed one-SOL wallet deposit. A zero-value holder `redeem_sol`
fixes the shared payout basis. When the deposit comes after that first call,
neither holder's later redemption includes it and the SOL remains in the
wallet; depositing before the snapshot includes it. The holders, balances,
and deposit timing are controlled local fixtures. This is a conditional
late-arrival holder-access risk, not evidence of a currently affected fund.

## Issuance and historical versions

One sampled DAO mint initially received exactly `1e18` raw units at
`Initialize`, followed by `100e15` at a **source-era** `InitCurve`. Its later
captured supply of `1,099,887,774,968,560,241` is below that combined
issuance, so the first `+100e15` above initialization is explained; the
remaining historical MintTo/Burn sequence has not been fully attributed.
The source transaction's `InitCurve` had a different account layout from the
current IDL. `analysis/daos_fun/dao-v1-mint-issuance-source.json` preserves
the transaction/signature and deployment boundaries.

For an older DAO ELF reconstructed from archived upgrade-buffer writes,
`InitCurve` at slot 366145612 matches all nine watched post-token balances
and eleven changed lamport balances of the historical transaction when the
known later account state is inverse-restored. Thirteen selected branch
cases include signer guards and snipe amounts. The tested token quote is
`floor(150e15 × snipe / (336e9 + snipe))`; large synthetic snipe balances
are not evidence of a real funded opportunity. A separate source-era
`MigrateBondingToMeteora` replay matches nine post-token and ten changed
lamport balances, with explicit state restoration. See
`dao-v1-init-curve-source-era-binaries-replay.json`,
`dao-v1-init-curve-snipe-matrix.json`, and
`dao-v1-migrate-bonding-historical-dao-restored-replay.json`.

An even older `LegacyToRaydium` wrapper is present in a historical DAO ELF
but dispatches to fallback 101 in the current one. Its source-era local
replay matched recorded balances; recipient redirection did not yield a
retained caller gain under the tested wrapper and locked-LP path. Current
generic `ExecuteInvoke` reaches VirtualXYK migration but cannot sign the
required State/depositor PDA in the tested route. Historical wrapper
behavior must not be projected onto the current binary. See
`dao-legacy-wrapper-source-era-replay.json`,
`dao-legacy-wrapper-redirect-locked-lp.json`, and
`analysis/root_virtual_xyk/dao-execute-virtual-migrate.json`.

## Other bounded paths

Synthetic `Initialize` plus `StartRaise` calls create the expected State,
DAO mint, fee share, and Fundraise accounts under pinned binaries. Carry
basis 4000 succeeds while 4001 rejects in tested cases. Zero funding goal
passes `Initialize` but a later `StartRaise` reaches a Fundraise
divide-by-zero panic and rolls back. This is an account/configuration hazard
observed locally, not a confirmed current user loss.

Delegate/cosigner lifecycle, redemption, DBC fee claims, position-NFT
transfer and arbitrary-CPI cases are recorded in
`analysis/daos_fun/REPORT.md`. The live cosigner and closed-wallet exposure
screen is summarized in [`VIRTUAL_XYK_AND_TR2_TR3.md`](VIRTUAL_XYK_AND_TR2_TR3.md).

A separate [signed local Burn/Redeem Wallet receipt](receipts/dao-v1-signed-burn-redeem-wallet.json)
uses a finalized closed/redeeming DAO State and mint with a disposable signer.
The user's `100e15` raw DAO-token holding and a one-billion-lamport wrapped-SOL
wallet donation are **local constructions**, not live holdings or treasury
funds. Burn records `100e15` credit, a zero redemption creates a tracker,
then two partial claims pay 27,281,802 and 63,657,540 raw funding units.
Claiming one unit beyond the earned credit fails 6006 and leaves tracked
balances unchanged; a wrong source authority fails 2015. This bounds one
signed accounting path and does not establish outsider access or a live
donation opportunity.

Our findings are bounded by the pinned snapshots and explicit synthetic
mutations; they neither replace this repository's source audit nor certify
the reconstructed program as safe.
