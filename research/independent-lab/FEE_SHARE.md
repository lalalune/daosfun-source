# FeeShareTraderDAO: layout, payout, and legacy authority

The pinned current FeeShareTraderDAO executable is
`Fee33nMZNbbC7Zm6Yx7tiHa9KH2Ao8fWTH3HNMkLMzWk`, SHA-256
`88df1b4ddb152d4159b41b9eba68ab74e6f0e14c1930bad5828c44a14a3ca4f8`
(last deployment slot 364247116). The nine site-IDL handlers each have a
bounded local success; full behavior remains open.

The 169-byte FeeShare state contains a Borsh `Option<Pubkey>` referrer. When
the tag is `None`, fee counters begin at **byte 113**; when it is `Some`, they
begin at **byte 145**. Treating the `None` layout as a fixed 145-byte prefix
creates false zero-counter readings. A captured no-referrer account instead
shows creator and platform payouts of **809,340,185,180** funding units each,
with one unit in its vault. A historical transaction paid 475,188,415 units
to each of two recipients. Twenty local payout/guard cases, with signer
metadata modeled under disabled signature verification, conserve vault,
recipient, and counter changes in the tested layouts. This corrects a parser
artifact; it is not an unpaid-fee
finding. See the [Option-layout matrix](receipts/fee-share-redeem-option-layout-matrix.json)
(`analysis/daos_fun/fee-share-redeem-option-layout-matrix.json`).

The [signed payout lifecycle](receipts/fee-share-signed-payout-lifecycle.json)
adds **27 validly signed, committed local sends** against the exact current
FeeShare ELF. It uses the two captured State/vault layouts plus a locally
distinct-referrer variant. Creator and referrer keys are replaced with
disposable signing keys and canonical recipient ATAs; the exhausted
no-referrer account receives 1,000 synthetic fee/vault units. The signed
creator receives its exact 500-unit cap there and 8,922,753,598 units on
each referrer layout; vault and `creator_distributed` deltas reconcile.
A signed third-party fee payer then collects the no-referrer platform's
remaining 500 units, leaving the original one-unit vault balance. Signed
outsider/referrer and tested entity 1/2 redemption attempts fail 6001;
over-cap and repeat claims fail 6002 without changing tracked protocol
accounts. Pinned BPF instructions independently show the nonzero-entity
authorization branch and 50/100 cap path. The distinct referrer and fee
accrual are local constructions; no real referrer entitlement, live payout,
or fund-loss finding follows.

The [writable offline Surfpool lifecycle](receipts/fee-share-signed-surfpool-stateful.json)
commits **24 validly signed local transactions** against the pinned current
ELF across `None` and `Some` referrer layouts. Creator and platform payouts
reconcile with vault and distributed-counter deltas; wrong-signer,
over-cap, and repeat controls leave tracked protocol accounts unchanged.
Creator/referrer keys, recipient ATAs, and fee accrual are explicitly local
substitutions, so this is a stateful payout check rather than a live claim.

The [external-fee claim and payout receipt](receipts/fee-share-external-claim-signed-surfpool.json)
adds **nine validly signed, submitted offline Surfpool transactions** on
pinned current FeeShare and Meteora CP AMM ELFs. A third party triggers
`claim_meteora_fees`, moving **79,828,645 raw WSOL units** from the CP pool
vault into FeeShare's vault and `total_fees`; creator and platform then
receive **39,914,323 units each**. The two payouts total one unit more than
the new claim because the captured FeeShare vault and undistributed counter
already held **one raw unit**. Redirect, outsider payout, overclaim, and
repeat controls reject without tracked-account mutation. The pool and
FeeShare accounts are later captured states, while creator and recipient
identities are local substitutions. This is a positive bounded CPI path,
not an exact historical prestate or proof that every fee-claim route works.

The [15-case FeeShare/CP Rust differential](receipts/fee-share-meteora-claim-rust-differential.json)
adds a native model of FeeShare's **post-CPI claim accounting**. Seven fresh
signed local claims succeed, including a zero-repeat path; eight guard or
overflow cases fail with rollback. The model takes the amount actually
claimed by CP as an **input** and compares FeeShare State and funding-vault
deltas. It does not derive CP position fees, reconstruct the Anchor account
parser or CPI instruction builder, or reproduce the whole SBF handler. Its
synthetic near-`u64` addition overflow rolls back in the current ELF; it is
not evidence of a reachable live-account overflow. The native source and
test instructions are bundled in `reconstruction/fee-share-meteora-claim/`.

The separate incomplete [FeeShare Anchor/SBF candidate](receipts/daos-full-candidate-status.json)
now implements `claim_meteora_fees` through current CP AMM,
`claim_meteora_dbc_fees` through current DAO v1 and DBC executables, and
`claim_raydium_fees` through pinned Raydium Lock/CPMM dependencies. In fresh
signed offline target-versus-candidate runs, the sampled Raydium path
matches **31/31** outcomes and all 25 tracked account post-states. Its
positive claim from one later captured Lock/pool state moves 5,701,049 raw
wrapped-SOL units and 1,761,233,394,246 raw DAO-token units into FeeShare;
repeat and rollback controls match. The inner CPI bytes and 18 account keys
are checked against a saved transaction. On this current candidate, CP
**28/28**, DBC **22/22**, and creator/platform payout **27/27** regressions
also match. The DBC pool's captured claimable fees were zero; its 1,000-unit
positive-fee cases were constructed only in disposable local fixtures. See
the [Raydium differential](receipts/daos-fee-share-raydium-candidate-differential.json),
[CP regression](receipts/daos-fee-share-raydium-candidate-cp-regression.json),
[DBC regression](receipts/daos-fee-share-raydium-candidate-dbc-regression.json),
and [payout regression](receipts/daos-fee-share-raydium-candidate-payout-regression.json).
The candidate now also maps `sell_token` to a sampled Raydium CPMM
`SwapBaseInput` CPI. Its [32-case signed offline claim-to-sell differential](receipts/daos-fee-share-sell-candidate-differential.json)
matches outcomes and all 27 tracked post-states. In one positive local
fixture, 1,761,233,394,246 raw DAO-token units sell for 5,686,649 raw
wrapped-SOL units; exact minimum output succeeds and minimum+1 rejects.
Half/double input, clock, owner, overflow, signer and paired-fault controls
also match. A synthetic local creator substitution enables signed positive
tests; separate unsigned local authority simulations are **not** counted
among the 32 signed cases. Raydium **31/31**, DBC **22/22**, CP **28/28**, and
payout **27/27** regressions pass on this final candidate. All nine declared
handlers now have source bodies and fresh local comparisons. The [49-case
setup differential](receipts/daos-fee-share-setup-candidate-differential.json)
matches `initialize` 12/12, `init_with_legacy` 13/13, and `change_creator`
24/24 on tested outcomes and watched post-states. **37 cases have verified
signatures.** The 12 fixed-operator ChangeCreator cases, including its six
positive calls, are explicitly unsigned local simulations because the
operator private key is unavailable. Full behavior remains unrecovered.
An isolated v1.41 build is **442,232 bytes** against the **522,216-byte**
deployed ELF, with **0/9** selected wrapper regions equal. These bounded
matches do not establish a live sale, fee diversion, vulnerability, or
whole-program source equivalence.

The bundle also includes `reconstruction/fee-share-redeem/`, a newly written
**native Rust model** of the 169-byte State `Option<Pubkey>` layout and the
tested creator `redeem(entity=0)` and `collect_platform_fees` accounting
branches. Its [differential receipt](receipts/fee-share-redeem-rust-differential.json)
matches **96/96** validly signed local calls against the unmodified current
FeeShare ELF: 59 successes and 37 expected failures across captured account
layouts with explicit synthetic creator/referrer keys, ATAs, and positive
accrual. The model omits Anchor account constraints, vault/ATA checks, SPL
Token CPI, unobserved alternative claim routes, and fee accrual. It is not
original source, an SBF build, byte-identical reconstruction, or a full
handler proof.

An added [49/49 fresh signed Rust differential](receipts/fee-share-referrer-order-rust-differential.json)
compares `None`, self-referrer `Some`, and distinct-referrer `Some` layouts.
The tested nonzero `redeem` entities, including entity 1 signed by the
configured referrer, reject 6001 before payout-cap evaluation; this does
**not** exclude other authorized referrer routes. A deliberately corrupted
`creator_distributed` counter above the half-fee cap causes the pinned ELF
to panic on subtraction, which the bounded model also predicts. Reachability
of that **synthetic** over-cap state on a deployed account is unproven; no
live denial-of-service finding or whole-program source match follows.

The [counter and referrer reachability receipt](receipts/fee-share-counter-reachability-signed-surfpool.json)
adds **16 validly signed, committed transactions** across four independent
writable offline Surfpool ledgers. `Initialize` and `InitWithLegacy` create
zero counters, a positive CP claim increases `total_fees`, and partial then
remainder creator/platform payouts conserve tokens while keeping the
creator's distributed counter at or below `floor(total_fees/2)`. A
**synthetic near-`u64`** total-fee prestate overflows on addition and rolls
back, rather than reaching the subtraction panic above. In the tested
distinct-referrer fixture, configured-referrer redemption and payout
redirection reject, while authorized creator/platform accounting exhausts
the remaining vault without a separate referrer allocation. The nine
documented IDL selectors contain no standalone referrer payout instruction.
These paths do **not** prove the over-cap state unreachable through the
whole program or rule out another authorized referrer route. Captured
accounts are later snapshots with disposable signer and ATA substitutions;
no live fund exposure is established.

An expanded [78-case signed `collect_platform_fees` probe](receipts/fee-share-platform-full-branch-probe.json)
tests amount decoding, both State layouts, canonical recipient constraints,
Token CPI failures, error order, and atomic rollback, with 24 fresh payout
holdouts and selected BPF instruction checks. For ordinary totals, the
observed cap is `floor(total_fees * 50 / 100) - platform_distributed`.
Multiplication occurs before division: a **synthetic** `u64::MAX` total-fee
prestate panics even for a zero payout, while a **synthetically corrupted**
platform counter above cap panics on subtraction. Neither state was shown
reachable through legitimate instructions. A changed State `token_mint`
field was accepted in one locally mutated fixture; no legitimate route to
that mutation or cross-pool diversion was found. The scoped report
`analysis/daos_fun/fee-share-platform-full-branch-probe.md` records the
remaining parser, token-extension, account-alias and CPI gaps.

The same bounded native payout crate now models that platform arithmetic.
Its [nine-case signed Rust differential](receipts/fee-share-platform-arithmetic-rust-differential.json)
matches the pinned ELF at safe and first-overflow multiplication inputs,
counter underflow, and a synthetic State `token_mint` mismatch. The crate
still omits full Anchor account parsing, Token CPI, and other handler
branches; this is neither full behavior reversal nor exact SBF source.

The tested `redeem` creator cap is `floor(total_fees/2) −
creator_distributed`. Cap+1 and altered owner/program/account cases reject.
`collect_platform_fees`, `claim_meteora_fees`, `claim_raydium_fees`, and
`claim_meteora_dbc_fees` execute on pinned local snapshots. The tested claim
handlers allow a different caller to trigger the claim while their recipient
and protocol-account guards remain in force; permissionless triggering is
not evidence of permissionless redirection. A sampled Raydium claim then
token sale conserves its token/funding deltas when the local Clock matches
the historical transaction. See the corresponding `fee-share-*.json`
receipts and `analysis/daos_fun/REPORT.md` in the bundle.

An older, distinct FeeShare program controls 168-byte fee states through
legacy PDAs. A successful historical `CurveWithdraw` made that program's PDA
an inner CPI signer to VirtualXYK `RedeemFees`; a later-state signed local
replay moves exactly the requested funding units up to the stored fee cap.
Current FeeShare cannot sign the legacy program's PDA. This identifies an
authorized legacy fee route, not an outsider fee drain. See
`analysis/daos_fun/legacy-curve-withdraw-authority-path.json` and
`analysis/root_virtual_xyk/signed-active-legacy-redeem.json`.

Historical initialization of eight newer 169-byte states from old 168-byte
accounts matches eight rent balances and surviving headers, but the source
transaction predates the current FeeShare deployment and exact source-slot
program bytes are not available. The distinction between source-era and
current binaries is recorded in `fee-share-legacy-eight-replay.json`.
