# daosfun-source

Recovered source, original binaries, reproducible builds and security audits for
two independent projects: the Solana DAO program and Clank / AGI on Robinhood Chain.

The recovered source preserves the deployed behavior, including known vulnerabilities.
It is not a remediated release.

| Project | Source and build instructions | Audit |
| --- | --- | --- |
| Solana DAO | [`programs/`](programs/) · [reproduce the build](docs/BUILD.md) | [Solana audit](audit/AUDIT.md) |
| Clank / AGI | [recovery overview](clank/README.md) · [reproduce the build](clank/docs/BUILD.md) | [Clank audit](clank/docs/AUDIT.md) |

## Solana DAO

Program: `4FqThZWv3QKWkSyXCDmATpWkpEiCHq5yhkdGWpSEDAZM`

The Anchor/Rust reconstruction produces the complete captured binary byte for byte,
including 79,056 zero-padding bytes from the deployed account allocation.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| [Original capture](evidence/mainnet.so) | 1,120,784 | `5020271255ea678fc110fed4671a86b1b7268acad04f990c590decd92091143d` |
| [Rebuilt binary](binaries/dao_v1.deployed.so) | 1,120,784 | `5020271255ea678fc110fed4671a86b1b7268acad04f990c590decd92091143d` |

The build uses a pinned lockfile, official platform-tools v1.41 and recovered linker
section ordering. Executable bytes are compiled from source. Original comments and
identifiers cannot be uniquely recovered from a binary. See the
[comparison proof](repro/final-proof.json) and [verification record](docs/DELIVERY.md).

The [audit](audit/AUDIT.md) records **1 CRITICAL, 4 MEDIUM and 1 LOW** finding.
The packaged differential suite passed **410 cases across 15 suites**; all six
security scripts passed. See [scope and limitations](docs/SECURITY_SCOPE.md).

An [independent supplemental lab](research/independent-lab/README.md) pins all
five daos.fun Solana programs, maps their 52 site-IDL entrypoints on current
binaries, and adds bounded local paths across current and historical versions
plus fund-safety controls. Its hash-checked evidence
bundle is separate from the byte-identical `dao_v1` source claim above.

After installing `requirements.txt` in a Python virtual environment:

```sh
python scripts/verify_release.py
python scripts/security_tests.py
python scripts/test_variant.py binaries/dao_v1.deployed.so .build/differential
```

Use a new directory for differential output. Tests run locally in LiteSVM.
Do not format span-sensitive Rust source when reproducing the exact binary:
panic source locations affect the emitted bytes.

## Clank / AGI

Token: `0xfa31d04462746aaa24bc7e5626403e09e4b106ec`

Network: Robinhood Chain, chain ID **4663**

The recovered Solidity source reproduces AGI's supplied creation payload and runtime
byte for byte. The package also verifies **17 runtime pairs** across the surrounding
contracts. AGI belongs to a historical Clank factory that differs from the website
factory captured during this review.

The [audit](clank/docs/AUDIT.md) records **1 MEDIUM and 1 LOW** finding, with no
confirmed CRITICAL or HIGH findings. Both findings have explicit applicability
limits for AGI's already-graduated curve. The validated suites passed **28 tests**.

See the [Clank README](clank/README.md) for binary hashes, contract addresses and
reproduction commands. Separate [research harnesses](clank/research/local-harnesses/README.md)
are retained with unresolved observations and are not counted as validated tests.

## Repository contents

| Path | Contents |
| --- | --- |
| [`programs/`](programs/) | Reconstructed Solana source and supporting crates |
| [`binaries/`](binaries/), [`evidence/`](evidence/) | Solana rebuilt artifact, original capture and test fixtures |
| [`scripts/`](scripts/), [`repro/`](repro/) | Solana reproduction tooling and verification records |
| [`audit/`](audit/) | Solana findings and local test evidence |
| [`research/independent-lab/`](research/independent-lab/) | Independent five-program daos.fun evidence and bounded behavior notes |
| [`clank/`](clank/) | EVM source, original and rebuilt bytecode, tooling and audit |

See [SECURITY.md](SECURITY.md) for reporting vulnerabilities.
