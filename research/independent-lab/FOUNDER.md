# FounderDAO: bounded allocation and presale recovery

The pinned current FounderDAO ProgramData is `Daosz93P15uZ1aTFTrBUAJyU1KERmZm3XQ5u4hbfHVQS`, SHA-256
`816bc6d42ffea7d63bd7b1287589413aef04d8f7dceb34dd274a0f7872d40aa2`
(last deployment slot 328988984). All six site-IDL handlers have a bounded
local success, and historical successful transactions were located for all
six. None is certified as fully reversed. Paths below name files inside the
[evidence bundle](daosfun-lab-evidence.tar.zst).

The `init` boundary matrix accepts exactly 1, 2, 3, and 4 quadrillion raw
token units of team allocation among 21 tested values on each of two source
instruction templates. It reserves 1 quadrillion for DAO allocation and
sets curve allocation to `9e15 − team_allocation`. The program disassembly
contains equality checks for those four cases. In 1,154 isolated tests over
40 valuation/allocation rays, `funding_goal = valuation × (9 − team/1e15)`
fails with 6010 and **one unit above** is the first success. These tests do
not close high-valuation overflow or alternate account states.

For `start_presale`, the source-era Founder binary constructs a Fundraise
CPI with a seven-day duration, the caller's token deposit, and a calculated
funding goal. Two captured historical CPI arguments agree with the local
replays; Fundraise receives an already computed goal. Presale amounts from
zero through `4e15` succeed in tested cases; `4e15 + 1` fails 6007. The
source-era disassembly and temporary local slope instrumentation support the
following **bounded integer model**. Write `T = 10^15`, `C` for curve
allocation, `V` for initial valuation, `G` for initial funding goal, and `A`
for presale amount:

```text
m = floor(10*C/11)
S = nearest_integer(20*(G*T - V*m)*T/m^2)
goal = ceil((20*V*A*T + S*A^2)/(20*T^2))
```

This model matches **1,119/1,119** unmodified local goal outputs, including
200 held-out wide cases and variants designed to distinguish the floor point
from an idealized rational point. A temporary, explicitly modified ELF is
used only to identify and vary the intermediate slope; final goal comparisons
run on the original pinned binary. Decimal overflow, exact half-way
rounding outside the tested domain, and other error branches remain open.

The bundle now includes `reconstruction/founder-presale/`, an independently
written **native Rust behavioral slice** of that goal, amount cap and
seven-day Fundraise CPI argument. Its [fresh differential receipt](receipts/founder-presale-rust-differential.json)
matches **120/120** local cases on the unmodified pinned Founder and
Fundraise ELFs across two historical transaction account layouts: 118
successful presales and two cap-6007 rejections. These fresh inputs have no
overlap with the earlier 200-case holdout. Init creates State locally; other
account bytes are later snapshots, and historical signer privileges are
simulated with signature verification disabled. The Rust model is neither
original source nor an SBF build and omits negative-slope, decimal overflow,
account validation, downstream CPI errors, and other handler branches.

The separate incomplete [Founder Anchor/SBF candidate](receipts/daos-full-candidate-status.json)
now implements bounded `start_presale`, `start_curve`, and `start_vest` bodies. Its [162-case signed offline
target/candidate differential](receipts/start-presale-differential.json)
matches every tested outcome and watched post-state across two local layouts:
142 successes and 20 failures, including 120 independent quote holdouts.
Fresh local Init creates State and vaults before the test; the Fundraise CPI
uses the pinned external ELF. A separate [66-case signed `start_curve`
differential](receipts/start-curve-differential.json) matches target/candidate
outcomes, exact Pump Init CPI data and watched post-states: 50 successes and
16 failures. Five positive presale-curve cases require synthetic Fundraise
finalization and funding. A [64-case signed `start_vest` differential](receipts/start-vest-differential.json)
matches outcomes, Vest CPI bytes and account keys, and watched post-states
across four historical call anchors: 20 successes and 44 rollbacks. Its
successful prestates locally clear an already-set Vest start tag from later
captures; the original source-slot prestate is unavailable. Three other
Founder handler bodies remain incomplete. The candidate differs from the
deployed capture. These cases do not prove full handler behavior or original source.

`claim_team_allo` moves `3e15` raw DAO-token units to a vest schedule ATA
and flips a one-time flag in a restored local prestate. An underfunded vault
fails and all five watched protocol accounts roll back. Four `start_vest`
transactions succeed locally after clearing an already-set start tag in
their captured later accounts; this is a hypothetical prestate. A synthetic
143-byte legacy `migrate_v2` account grows to 155 bytes and maps the old
allocation fields as observed, but exact historical input bytes are absent.

A separate 56-case `start_vest` authority matrix uses real local signatures
on four restored schedules. A distinct correctly signed payer succeeds in
all four, while unsigned payer, already-started schedule, empty Curve,
wrong account owner and wrong Vest program controls reject. Resetting only
the Vest start tag is synthetic, so these cases show a bounded permissionless
trigger, not a reachable premature start or fund-loss claim. See the
[signed authority matrix](receipts/founder-start-vest-authority-matrix.json).
The [time-boundary receipt](receipts/founder-start-vest-time-boundary.json)
adds static BPF and four local bisections: the first allowed timestamp is
`Curve.timestamp + 86,401` seconds; equality at `+86,400` fails 6005.
This limits the permissionless trigger to after the tested one-day guard.

A [fresh writable Surfpool Founder lifecycle](receipts/founder-surfpool-stateful.json)
commits signed `Init` and `StartPresale` with new program-created
State/vaults under the pinned Founder and Fundraise ELFs. Immediate
`ClaimTeamAllo` rejects because `curve_started` is false; a later successful
claim uses an explicit **synthetic** `curve_started=true` edit, not an
observed `StartCurve`. Wrong-authority, over-cap, and repeat controls roll
back tracked protocol accounts. The historical presale whitelist signer was
not available in this local run.

A separate [Founder-to-Pump Surfpool lifecycle](receipts/founder-pump-fresh-signed-surfpool.json)
does commit fresh signed Founder `Init`, Founder `StartCurve` and its Pump
`Init` CPI, followed by a buy and sell against that newly created Pump
Curve. Wrong-Founder, high-minimum sell, and repeat-start controls reject
with protocol-account rollback. It reuses public historical instruction
arguments but creates all state and signing keys locally; no mainnet state
or funds moved.

Key receipts: `analysis/daos_fun/founder-init-allocation-boundaries.json`,
`founder-init-goal-thresholds.json`, `founder-presale-cpi-source-attribution.json`,
the [static trace](receipts/founder-presale-static-trace.json),
`founder-presale-slope-patch-probes.json`,
`founder-start-presale-branch-matrix.json`,
`founder-claim-team-branch-matrix.json`, and
`founder-start-vest-branch-probes.json`. The overall replay gate is
`analysis/daos_fun/offline-verification.json`.
