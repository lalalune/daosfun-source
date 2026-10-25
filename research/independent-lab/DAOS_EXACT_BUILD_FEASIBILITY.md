# daos.fun exact Rust/SBF build checkpoint

This is a reviewer-facing copy of the exact report bundled at
`analysis/source_reconstruction/daos-exact-build-feasibility.md`; relative
links are adjusted for this repository layout. That original report predates
the incomplete candidate projects now also in the archive; their current
status is recorded below.

Shaw's [`dao_v1` reconstruction](../../README.md)
rebuilds its captured binary byte for byte. The four other current daos.fun
programs have pinned [ELF/section baselines](README.md), bounded native Rust
behavior models, and incomplete Anchor/SBF interface candidates. **None is a
complete deployed-program reconstruction or byte-identical build.** A
matching native behavioral model is not a matching SBF executable.

| Current program | ELF bytes | `.text` bytes | Relocations | Allocation padding | Whole-program source candidate |
| --- | ---: | ---: | ---: | ---: | --- |
| [`dao_v1`](../../repro/final-proof.json) | 1,041,728 | 951,456 | 3,550 | 79,056 | [Shaw's byte-identical rebuild](../../docs/BUILD.md) |
| [FeeShareTraderDAO](receipts/daos-fee-share-baseline.json) | 522,216 | 468,912 | 1,904 | 0 | Incomplete; no match |
| [FounderDAO](receipts/daos-founder-baseline.json) | 573,384 | 506,152 | 2,402 | 976 | Incomplete; no match |
| [PumpXYK](receipts/daos-pump-baseline.json) | 684,168 | 612,376 | 2,713 | 136 | Incomplete; no match |
| [VirtualXYK](receipts/daos-virtual-baseline.json) | 528,384 | 469,792 | 2,138 | 117,416 | Incomplete; no match |

The five captures have standard `EM_BPF` section ordering and identical
`.shstrtab` contents. That is evidence of a similar linker family; it does
not establish matching compiler versions or source. Their deployment slots,
full ProgramData hashes and upgrade authority are pinned in
[`daos-chain-manifest.json`](receipts/daos-chain-manifest.json).

FeeShare is the smallest next whole-program build target. Shaw's
[`fee_share_trader_dao` supporting crate](../../programs/fee_share_trader_dao/src/lib.rs)
implements `initialize`, `init_with_legacy`, and `change_creator` for DAO
integration. It defaults to `no-entrypoint`, lacks six of the nine deployed
handlers, including `redeem` and fee claims, and has different source file
paths from the nine `src/instructions/*.rs` locations embedded in the
deployed FeeShare ELF. It is not a deployable FeeShare source reconstruction.
The newer standalone [candidate status receipt](receipts/daos-full-candidate-status.json)
records all nine FeeShare selectors. Creator/platform payouts match 27/27
signed local cases, the CP fee claim 28/28, and the nested DAO v1/DBC fee
claim 22/22 target/candidate outcomes and tracked post-states. A sampled
Raydium Lock fee claim also matches 31/31 cases and 25 tracked account
post-states. The positive DBC fee accrual is a synthetic local fixture;
`sell_token` now matches 32/32 signed local claim-to-sell cases with a
synthetic local creator substitution. All nine selectors have non-stub
candidate bodies and fresh local comparisons. The 49 setup cases include 37
validly signed calls and 12 explicitly unsigned fixed-operator simulations.
No handler has a full behavior
proof.
The other three standalone candidates expose their listed selectors but
leave most or all on-chain bodies incomplete. Their source and non-secret
receipts are in the four explicitly selected `reconstruction/*-candidate/`
archive trees. **Do not deploy them as replacements.**
Founder now has bounded `start_presale`, `start_curve`, and `start_vest` paths
with 162/162, 66/66, and 64/64 signed local target/candidate matches.
Five positive curve cases need synthetic presale finalization; successful
Vest cases reset an already-started tag in later captured accounts. Three
Founder bodies remain incomplete. Its 400,112-byte candidate differs from the
574,360-byte deployed capture. VirtualXYK has bounded `buy_token` and
`sell_token` paths matching 14/14 and 16/16 signed local cases, respectively,
including synthetic LP Option variants; eight of its ten handlers remain
incomplete. Its 285,240-byte candidate differs from the 645,800-byte
deployed capture.
Our [FeeShare payout Rust slice](FEE_SHARE.md)
models only two accounting branches and omits Anchor account validation and
SPL Token CPI failures. The [Founder](FOUNDER.md)
and [Pump](PUMP_XYK.md) slices are also
bounded behavioral models. Shaw's `hedgefun_curve` has a different program
ID from VirtualXYK; it is not VirtualXYK source.

Shaw's [DAO build recipe](../../docs/BUILD.md)
pins Linux platform-tools v1.41 (`rustc 1.75.0-dev`, LLVM 17), Anchor 0.30.1,
Solana 1.18.26, dependencies and recovered linker/constant order for that
one DAO binary. These are hypotheses for the other programs, not
proven original settings. An isolated [FeeShare v1.41 toolchain probe](receipts/daos-fee-share-v141-toolchain-probe.json)
checked 47 official components and used a temporary v3 dependency lock
drawn from Shaw-versioned crates. It corrected the newer candidate's ELF
machine-format mismatch. The [current-source sell-stage probe](receipts/daos-fee-share-sell-v141-toolchain-probe.json)
produced **442,232** bytes versus the deployed **522,216**, with **0/9**
compared wrapper regions equal. This is a
compiler-format clue, not a proven original recipe or matching source.
Next, deeper FeeShare account/error order, state changes, CPI variants and
dependency versions need reconstruction and differential testing,
followed by linker-order recovery and whole-file SHA comparison.
Even a byte-identical result would establish an equivalent build artifact,
not uniquely recover historical comments or variable names.
