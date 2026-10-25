# Supplemental daos.fun binary research

This contribution packages an independent, offline research lab for the five
Solana programs identified by the daos.fun client IDLs. It complements the
reconstructed `dao_v1` source in this repository. It does not change program
source, claim a deployed fix, or include the unrelated Clank project.

The lab first captured finalized ProgramData binaries and the site IDLs, then
mapped all **52 declared selectors** to current-binary dispatcher wrappers.
Across the five programs, **52/52** selectors have a bounded local success
with the exact current **target-program ELF** loaded. A downstream CPI
dependency may be from an older deployment: selected `dao_v1.init_curve`
and `dao_v1.migrate_bonding_to_meteora` paths succeed with the current DAO
ELF and source-era CP DAMM, while their tested current-CP controls fail
6067. A separate per-handler audit finds **50/52 selected bounded paths**
load current target and custom CPI executables: DAO **16/18**,
FeeShare **9/9**, Founder **6/6**, Pump **9/9**, and VirtualXYK **10/10**.
System, SPL Token and ATA execution uses the local runtime; restored or
synthetic account states are not a live mainnet prestate. These counts are an
entrypoint inventory, **not** full behavior coverage: untested
authority, token, account-state, arithmetic, upgrade, and historical branches
remain. `dao_v1` is the one program whose current binary also matches the
byte-identical reconstruction in this repository.

| Program | Current target ELF bounded success | Selected current custom stack | Strict full behavior | Current captured SHA-256 |
| --- | ---: | ---: | ---: | --- |
| `dao_v1` | 18/18 | 16/18 | 0/18 | `5020271255ea678fc110fed4671a86b1b7268acad04f990c590decd92091143d` |
| FeeShareTraderDAO | 9/9 | 9/9 | 0/9 | `88df1b4ddb152d4159b41b9eba68ab74e6f0e14c1930bad5828c44a14a3ca4f8` |
| FounderDAO | 6/6 | 6/6 | 0/6 | `816bc6d42ffea7d63bd7b1287589413aef04d8f7dceb34dd274a0f7872d40aa2` |
| PumpXYK | 9/9 | 9/9 | 0/9 | `2238aa5b96fc29e7693174b20d75063df2e1dfba28c26c5346338c23732e2fb9` |
| VirtualXYK | 10/10 | 10/10 | 0/10 | `c151c6b15b84d8bfc47a5f2e0e5b9e04babff0263a1125a9e8dcb07df6144377` |

The [DAO binary provenance](receipts/dao-v1-binary-provenance.json) and
[other-program version audit](receipts/non-dao-current-elf-version-audit.json)
pin the root handler ELF hash behind each bounded-success count. CPI
dependency versions are pinned in the
[DAO current-stack audit](receipts/dao-v1-custom-stack-version-audit.json)
and other-program audit; the
[virtual custom-stack audit](receipts/custom-stack-version-audit.json)
checks its ten selected direct paths.

Four [FeeShare](receipts/daos-fee-share-baseline.json),
[Founder](receipts/daos-founder-baseline.json),
[Pump](receipts/daos-pump-baseline.json), and
[VirtualXYK](receipts/daos-virtual-baseline.json) ELF baselines pin each
current file's section hashes, ELF extent, and zero-filled allocation
padding. They explicitly record **no source-built candidate** for those
programs at their capture checkpoint. Later
[incomplete full-interface candidates](receipts/daos-full-candidate-status.json)
expose the current selector surfaces but retain missing or failing handler
bodies. The FeeShare candidate now matches signed offline Raydium Lock 31/31,
CP 28/28, nested DAO v1/DBC 22/22, and payout 27/27 target-versus-candidate
cases, with synthetic local positive DBC accrual. The Raydium claim uses a
later captured pool; `sell_token` now matches 32/32 signed local claim-to-sell
cases with a synthetic creator substitution. All nine FeeShare handlers have
candidate bodies and fresh local comparisons. The [49 setup cases](receipts/daos-fee-share-setup-candidate-differential.json)
include 37 validly signed calls and 12 explicitly unsigned fixed-operator
simulations; no signed positive operator case is claimed. None is fully reversed.
Neither those SBF
candidates nor the native Rust behavior slices match a deployed whole-program
binary. The
[exact-build feasibility checkpoint](DAOS_EXACT_BUILD_FEASIBILITY.md) compares
all four current ELF layouts with Shaw's `dao_v1` recipe and identifies
FeeShare as the smallest next whole-program candidate, while recording that
none of the four has a source-built byte match. The
[FeeShare v1.41 compiler-format probe](receipts/daos-fee-share-v141-toolchain-probe.json)
is a toolchain hypothesis, not an exact FeeShare rebuild.

The incomplete Founder candidate now has bounded `start_presale`,
`start_curve`, and `start_vest` bodies with
[162/162 signed presale matches](receipts/start-presale-differential.json),
[66/66 signed curve matches](receipts/start-curve-differential.json), and
[64/64 signed Vest matches](receipts/start-vest-differential.json).
Five positive curve cases use synthetic presale finalization and funding;
successful Vest cases locally reset an already-started tag in later captures.
Three other Founder handler bodies remain incomplete. The VirtualXYK candidate
has bounded [`buy_token`](receipts/daos-virtual-buy-candidate-differential.json)
and [`sell_token`](receipts/daos-virtual-sell-candidate-differential.json) bodies
matching 14/14 and 16/16 signed local target/candidate cases, respectively.
The trade fixtures use a later captured Curve, synthetic signer ATAs, and
locally rewritten LP Option states. Eight VirtualXYK bodies still fail closed;
neither candidate matches its deployed ELF.

The original research files are in a compressed [evidence bundle](daosfun-lab-evidence.tar.zst).
[`MANIFEST.json`](MANIFEST.json) lists each bundled path, byte length, and
SHA-256, as well as the upstream lab commit. The bundle retains the complete
daos.fun analysis, virtual-XYK analysis, five current-program disassemblies,
current and reconstructed program binary captures, read-only RPC receipts,
local test scripts, and four narrow native Rust behavior models for PumpXYK
`migrate_v2`, FeeShare payouts and post-CP-claim accounting, and Founder
presale pricing. The models are
not original on-chain source or SBF rebuilds. Four separate incomplete
Anchor/SBF interface candidates and their non-secret status receipts are
also included; **they are not matching or deployable replacements**. The
bundle excludes
Meteora DLMM/HumidiFi research except where those external programs are
explicit CPI dependencies of a daos.fun test.

The refreshed bundle pins private lab commit
`4ca86bef866cacd725c1ab7f5ed483b4db332766`, contains **1,171** scoped
files (123,018,587 uncompressed bytes), and has archive SHA-256
`f4b96e52d8ce867d9c93ff4c5a09614d34059ae0bb722885b197401e127e3877`.
All **87** direct JSON receipts match bundled member size and
SHA-256. The prior daos.fun offline gate's saved receipt records **113**
commands; the refreshed FeeShare four-candidate integrity gate passes
separately. Strict full behavior remains **0/52**.

The most reviewable distinct results are summarized in the adjacent notes.
A small selection of key JSON receipts is also available directly in
[`receipts/`](receipts/), without unpacking the full bundle:

- [`DAO_V1.md`](DAO_V1.md): source-era replays, DAO/DBC migration, issuance,
  delegation and redemption paths, signed offline checks of BM-1,
  TR-1 expiry, TR-5 redemption timing, six current-CP variants, and a
  conditional Token-2022 transfer-hook redemption failure against the
  captured original ELF. The ten-wallet finalized sample found no
  TransferHook mint in its bounded set; current live user loss is unproved.
- [`FOUNDER.md`](FOUNDER.md): tested presale-goal model, allocation and vesting
  controls, a native Rust goal/amount slice with 120/120 local differential
  matches, and a fresh signed Founder-to-Pump lifecycle.
- [`FEE_SHARE.md`](FEE_SHARE.md): `Option<Pubkey>` decoding, fee conservation,
  signed offline Surfpool external-fee claim, payout and counter reachability
  checks, a 78-case platform-fee branch probe, legacy fee-authority CPI,
  and a bounded native Rust payout model with 96/96 creator cases, 49/49
  referrer/error-order matches and nine platform-arithmetic cases, plus a
  separate 15-case post-CP-claim accounting slice.
- [`PUMP_XYK.md`](PUMP_XYK.md): source-era migration transfer formula and
  failure rollback, current `migrate_v2` native Rust data model with 72
  full-data matches and eight parser-rejection matches, and signed trade
  lifecycles on restored and fresh Curves.
- [`VIRTUAL_XYK_AND_TR2_TR3.md`](VIRTUAL_XYK_AND_TR2_TR3.md): swap/liquidity
  and fee-authority controls, current Curve census, conditional synthetic
  Token-2022 transfer-fee and LP-exit checks, and bounded exposure checks
  for the DAO cosigner and redemption findings.

Constructed test transactions execute in LiteSVM or offline Surfpool; one
saved historical transaction was also resimulated with public RPC's
read-only `simulateTransaction`. Other public RPC calls read accounts,
binaries, and historical transactions. No real user-wallet signature,
fund transfer, or submitted mainnet transaction is part of this
contribution. An error from one account mutation rules out only that tested
state. The captured programs remain upgradeable; binary hashes and account
slots are part of every result's scope.

To check every bundled member without extracting it (with `zstd` installed), run:

```sh
python3 research/independent-lab/verify_bundle.py --require-external research/independent-lab/daosfun-lab-evidence.tar.zst
```

Replaying the full lab
requires Python dependencies, external CPI binaries, and snapshots documented
in the bundle. This contribution does not extend the byte-identical source
claim from `dao_v1` to the other four programs.
