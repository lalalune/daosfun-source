# PumpXYK: source-era migration accounting

The pinned current PumpXYK executable is
`CurvyB2V1gJVsSb7Zb112ScicJbUmQ7jyHLn8UHNYf6B`, SHA-256
`2238aa5b96fc29e7693174b20d75063df2e1dfba28c26c5346338c23732e2fb9`
(last deployment slot 328987601). All nine site-IDL handlers have a bounded
local success, while full behavior remains open. The historical migration
work deliberately uses the **effective source-era Pump and VirtualXYK
ELFs**, reconstructed from archived Upgrade-buffer writes rather than
assuming the current binaries were active at older transaction slots.

Three independently captured `migrate_daos` transactions replay locally
against those source-era binaries. Their observed token and protocol lamport
post-balances match the source metadata **12/12** and **18/18**. A formula
first inferred from one case and then checked against the other two is:

```text
Fv = floor(F / 2)
Tv = floor(VT * Fv / (F + VF))
```

Here `F` is the Pump funding reserve, `VF` its virtual funding reserve,
`VT` its virtual token reserve, and `Fv`/`Tv` the funding/token amounts
passed to VirtualXYK in the tested migration branch. Thirty-six one-field
mutations and zero-reserve boundary cases support that integer relation in
the bounded source-era fixture. See
the [three-source formula receipt](receipts/pump-migrate-daos-three-formula.json),
`pump-migrate-daos-source-era-formula-matrix.json`, and
`pump-migrate-daos-historical-prebalances-source-era-replay.json`.

Three restored failure fixtures keep seven watched protocol accounts
unchanged after a downstream CPI fails; the payer loses only the ordinary
transaction fee. Six wrong-account/program variants reject. This supports
atomic rollback in these local routes, not a statement about all migration
configurations or future upgrades. The current Pump binary and its nine
entrypoints remain separately pinned from the historical source-era
reconstruction.

## Native source model of the current `migrate_v2` layout conversion

The bundle now includes `reconstruction/pump-migrate-v2/` as a newly written
native Rust behavioral model of the **current**
PumpXYK handler's 203-byte legacy `PumpCurve` to 269-byte `CurveV2` data
conversion. The [differential receipt](receipts/pump-migrate-v2-rust-differential.json)
compares the native model with the unmodified current ELF on **72** freshly
generated, validly signed local inputs: every resulting account-data byte
matches. Eight malformed-layout parser rejections also agree. The inputs are
synthetic, not recovered historical legacy accounts. The native crate does
not model Solana owner, signer, rent, or CPI validation and cannot reproduce
the full SBF handler or binary. This `migrate_v2` state-layout path is
distinct from the source-era `migrate_to_daos` reserve transfer above.

## Writable offline Surfpool lifecycles

The [restored-Curve lifecycle](receipts/pump-surfpool-stateful-lifecycle.json)
loads a captured current Pump Curve/mint/vault into a fresh offline ledger.
Valid local signatures commit a buy, a sell, and a fee collection; a
high-minimum sell rejects and rolls back tracked accounts. That fixture
does not itself prove a fresh Curve can be initialized.

The separate [fresh Founder-to-Pump lifecycle](receipts/founder-pump-fresh-signed-surfpool.json)
commits Founder `Init` and `StartCurve` with a Pump `Init` CPI, then buys
and sells on the newly created Curve under pinned current ELFs. Its local
signer substitutions and funded trader wallet are controlled test inputs.
These paths have not produced a new live fund-risk finding.
