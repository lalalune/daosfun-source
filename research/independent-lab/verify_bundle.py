#!/usr/bin/env python3
"""Verify a daos.fun lab tar.zst without extracting any member.

Requires the `zstd` command-line tool. The archive must contain one manifest
followed by sorted, regular, lab-relative files. Every file is SHA-256 checked.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tarfile
from pathlib import Path


FORMAT = "daosfun-independent-lab-v1"
MANIFEST_NAME = "MANIFEST.json"
COMMON_HARNESS = frozenset({
    "sample_daos_transactions.py",
    "svm_lab.py",
    "analyze_daos_sample.py",
    "build_daos_graph.py",
    "map_daos_dispatch.py",
    "verify_daos_idls.py",
    "summarize_daos_wrappers.py",
})
DAOS_SOURCE_MODEL_FILES = frozenset({
    "analysis/source_reconstruction/daos-fee-share-candidate-payout-differential.json",
    "analysis/source_reconstruction/daos-fee-share-dbc-candidate-cp-regression.json",
    "analysis/source_reconstruction/daos-fee-share-dbc-candidate-differential.json",
    "analysis/source_reconstruction/daos-fee-share-dbc-candidate-elf-compare.json",
    "analysis/source_reconstruction/daos-fee-share-dbc-candidate-payout-regression.json",
    "analysis/source_reconstruction/daos-fee-share-dbc-v141-function-regions.json",
    "analysis/source_reconstruction/daos-fee-share-dbc-v141-toolchain-probe.json",
    "analysis/source_reconstruction/daos-fee-share-full-candidate.json",
    "analysis/source_reconstruction/daos-fee-share-function-regions.json",
    "analysis/source_reconstruction/daos-fee-share-meteora-cpi-candidate-differential.json",
    "analysis/source_reconstruction/daos-fee-share-meteora-cpi-candidate-elf-compare.json",
    "analysis/source_reconstruction/daos-fee-share-meteora-cpi-v141-function-regions.json",
    "analysis/source_reconstruction/daos-fee-share-meteora-cpi-v141-toolchain-probe.json",
    "analysis/source_reconstruction/daos-fee-share-raydium-candidate-cp-regression.json",
    "analysis/source_reconstruction/daos-fee-share-raydium-candidate-dbc-regression.json",
    "analysis/source_reconstruction/daos-fee-share-raydium-candidate-differential.json",
    "analysis/source_reconstruction/daos-fee-share-raydium-candidate-elf-compare.json",
    "analysis/source_reconstruction/daos-fee-share-raydium-candidate-payout-regression.json",
    "analysis/source_reconstruction/daos-fee-share-raydium-v141-function-regions.json",
    "analysis/source_reconstruction/daos-fee-share-raydium-v141-toolchain-probe.json",
    "analysis/source_reconstruction/daos-fee-share-sell-candidate-cp-regression.json",
    "analysis/source_reconstruction/daos-fee-share-sell-candidate-dbc-regression.json",
    "analysis/source_reconstruction/daos-fee-share-sell-candidate-differential.json",
    "analysis/source_reconstruction/daos-fee-share-sell-candidate-elf-compare.json",
    "analysis/source_reconstruction/daos-fee-share-sell-candidate-payout-regression.json",
    "analysis/source_reconstruction/daos-fee-share-sell-candidate-raydium-regression.json",
    "analysis/source_reconstruction/daos-fee-share-sell-v141-function-regions.json",
    "analysis/source_reconstruction/daos-fee-share-sell-v141-toolchain-probe.json",
    "analysis/source_reconstruction/daos-fee-share-setup-candidate-differential.json",
    "analysis/source_reconstruction/daos-fee-share-v141-function-regions.json",
    "analysis/source_reconstruction/daos-fee-share-v141-toolchain-probe.json",
    "analysis/source_reconstruction/daos-fee-share-v141-toolchain-probe.md",
    "analysis/source_reconstruction/daos-full-candidate-status.json",
    "analysis/source_reconstruction/daos-full-candidates.md",
    "analysis/source_reconstruction/daos-virtual-buy-candidate-differential.json",
    "analysis/source_reconstruction/daos-virtual-sell-candidate-differential.json",
    "analysis/source_reconstruction/fee_share_dbc_full_candidate_differential.py",
    "analysis/source_reconstruction/fee_share_meteora_full_candidate_differential.py",
    "analysis/source_reconstruction/fee_share_raydium_full_candidate_differential.py",
    "analysis/source_reconstruction/fee_share_sell_full_candidate_differential.py",
    "analysis/source_reconstruction/fee_share_setup_full_candidate_differential.py",
    "analysis/source_reconstruction/fee-share-v141/Cargo.lock",
    "reconstruction/fee-share-full-candidate/.gitignore",
    "reconstruction/fee-share-full-candidate/Cargo.lock",
    "reconstruction/fee-share-full-candidate/Cargo.toml",
    "reconstruction/fee-share-full-candidate/README.md",
    "reconstruction/fee-share-full-candidate/compare_functions.py",
    "reconstruction/fee-share-full-candidate/differential.py",
    "reconstruction/fee-share-full-candidate/src/instructions/change_creator.rs",
    "reconstruction/fee-share-full-candidate/src/instructions/external.rs",
    "reconstruction/fee-share-full-candidate/src/instructions/init_with_legacy.rs",
    "reconstruction/fee-share-full-candidate/src/instructions/initialize.rs",
    "reconstruction/fee-share-full-candidate/src/instructions/payout.rs",
    "reconstruction/fee-share-full-candidate/src/instructions/state.rs",
    "reconstruction/fee-share-full-candidate/src/lib.rs",
    "reconstruction/fee-share-full-candidate/verify_interface.py",
    "reconstruction/founder-dao-anchor-candidate/.gitignore",
    "reconstruction/founder-dao-anchor-candidate/Cargo.lock",
    "reconstruction/founder-dao-anchor-candidate/Cargo.toml",
    "reconstruction/founder-dao-anchor-candidate/README.md",
    "reconstruction/founder-dao-anchor-candidate/elf-comparison.json",
    "reconstruction/founder-dao-anchor-candidate/start-presale-differential.json",
    "reconstruction/founder-dao-anchor-candidate/start_presale_differential.py",
    "reconstruction/founder-dao-anchor-candidate/start-curve-differential.json",
    "reconstruction/founder-dao-anchor-candidate/start_curve_differential.py",
    "reconstruction/founder-dao-anchor-candidate/start-vest-differential.json",
    "reconstruction/founder-dao-anchor-candidate/start_vest_differential.py",
    "reconstruction/founder-dao-anchor-candidate/src/lib.rs",
    "reconstruction/founder-dao-anchor-candidate/verification.json",
    "reconstruction/founder-dao-anchor-candidate/verify_candidate.py",
    "reconstruction/pump-full-candidate/Cargo.lock",
    "reconstruction/pump-full-candidate/Cargo.toml",
    "reconstruction/pump-full-candidate/README.md",
    "reconstruction/pump-full-candidate/build-reproducibility.json",
    "reconstruction/pump-full-candidate/build_reproduce.py",
    "reconstruction/pump-full-candidate/collect-fee-differential.json",
    "reconstruction/pump-full-candidate/compare_collect_fee.py",
    "reconstruction/pump-full-candidate/compare_migrate.py",
    "reconstruction/pump-full-candidate/comparison.json",
    "reconstruction/pump-full-candidate/generate_accounts.py",
    "reconstruction/pump-full-candidate/migrate-differential.json",
    "reconstruction/pump-full-candidate/src/collect_fee.rs",
    "reconstruction/pump-full-candidate/src/contexts.rs",
    "reconstruction/pump-full-candidate/src/lib.rs",
    "reconstruction/pump-full-candidate/src/state.rs",
    "reconstruction/virtual-xyk-anchor-candidate/Cargo.lock",
    "reconstruction/virtual-xyk-anchor-candidate/Cargo.toml",
    "reconstruction/virtual-xyk-anchor-candidate/README.md",
    "reconstruction/virtual-xyk-anchor-candidate/elf-comparison.json",
    "reconstruction/virtual-xyk-anchor-candidate/generate_accounts.py",
    "reconstruction/virtual-xyk-anchor-candidate/model_probe.rs",
    "reconstruction/virtual-xyk-anchor-candidate/src/contexts.rs",
    "reconstruction/virtual-xyk-anchor-candidate/src/buy.rs",
    "reconstruction/virtual-xyk-anchor-candidate/src/sell.rs",
    "reconstruction/virtual-xyk-anchor-candidate/src/lib.rs",
    "reconstruction/virtual-xyk-anchor-candidate/src/model.rs",
    "reconstruction/virtual-xyk-anchor-candidate/verification.json",
    "reconstruction/virtual-xyk-anchor-candidate/verify_candidate.py",
    "scripts/verify_full_candidates.py",
    "scripts/virtual_xyk_buy_candidate_differential.py",
    "scripts/virtual_xyk_sell_candidate_differential.py",
    "analysis/source_reconstruction/daos-exact-build-feasibility.md",
    "analysis/source_reconstruction/daos-fee-share-baseline.json",
    "analysis/source_reconstruction/daos-founder-baseline.json",
    "analysis/source_reconstruction/daos-pump-baseline.json",
    "analysis/source_reconstruction/daos-virtual-baseline.json",
    "analysis/source_reconstruction/fee-share-redeem-rust-differential.json",
    "analysis/source_reconstruction/fee-share-referrer-order-rust-differential.json",
    "analysis/source_reconstruction/fee-share-meteora-claim-rust-differential.json",
    "analysis/source_reconstruction/fee-share-platform-arithmetic-rust-differential.json",
    "reconstruction/fee-share-meteora-claim/Cargo.lock",
    "reconstruction/fee-share-meteora-claim/Cargo.toml",
    "reconstruction/fee-share-meteora-claim/README.md",
    "reconstruction/fee-share-meteora-claim/src/lib.rs",
    "reconstruction/fee-share-meteora-claim/src/main.rs",
    "analysis/source_reconstruction/founder-presale-rust-differential.json",
    "reconstruction/fee-share-redeem/Cargo.lock",
    "reconstruction/fee-share-redeem/Cargo.toml",
    "reconstruction/fee-share-redeem/README.md",
    "reconstruction/fee-share-redeem/src/lib.rs",
    "reconstruction/fee-share-redeem/src/main.rs",
    "reconstruction/founder-presale/Cargo.lock",
    "reconstruction/founder-presale/Cargo.toml",
    "reconstruction/founder-presale/README.md",
    "reconstruction/founder-presale/src/lib.rs",
    "reconstruction/founder-presale/src/main.rs",
    "reconstruction/pump-migrate-v2/Cargo.lock",
    "reconstruction/pump-migrate-v2/Cargo.toml",
    "reconstruction/pump-migrate-v2/README.md",
    "reconstruction/pump-migrate-v2/src/lib.rs",
    "reconstruction/pump-migrate-v2/src/main.rs",
})
HEX_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
HEX_COMMIT = re.compile(r"[0-9a-f]{40}\Z")
MAX_MANIFEST_BYTES = 8 * 1024 * 1024
MAX_MEMBER_BYTES = 2 * 1024 * 1024 * 1024
MAX_TOTAL_BYTES = 8 * 1024 * 1024 * 1024
MAX_FILES = 20_000
DIRECT_RECEIPT_ALIASES = {
    "dao-hook-redemption-receipt.json": "analysis/daos_fun/dao-hook-redemption/receipt.json",
}


def validate_member_path(name: str) -> None:
    """Reject traversal, platform-ambiguous names, and unrelated lanes."""
    if not isinstance(name, str) or not name or "\\" in name or "\x00" in name:
        raise ValueError(f"unsafe archive path: {name!r}")
    if name.startswith("/") or ":" in name:
        raise ValueError(f"unsafe archive path: {name!r}")
    parts = name.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise ValueError(f"unsafe archive path: {name!r}")
    if "__pycache__" in parts or name.endswith(".pyc"):
        raise ValueError(f"generated Python bytecode is not research evidence: {name!r}")
    if name == MANIFEST_NAME:
        return
    if name in DAOS_SOURCE_MODEL_FILES:
        return
    if len(parts) == 2 and parts[0] == "analysis" and (
        parts[1].startswith("daos_") and parts[1].endswith(".asm")
    ):
        return
    if len(parts) >= 3 and parts[0] == "analysis" and parts[1] in (
        "daos_fun", "root_virtual_xyk"
    ):
        return
    if len(parts) >= 3 and parts[:2] == ["inputs", "daos_fun"]:
        return
    if len(parts) >= 2 and parts[0] == "evidence" and (
        parts[1].startswith("daos") or parts[1].startswith("ghidra-daos")
    ):
        return
    if len(parts) == 2 and parts[0] == "scripts" and parts[1].endswith(".py"):
        script = parts[1]
        if (script.startswith("daos_") or script.startswith("root_virtual_xyk_")
                or script in COMMON_HARNESS):
            return
    raise ValueError(f"unrelated or unsupported archive path: {name!r}")


def _validate_manifest(raw: bytes) -> tuple[dict, list[dict]]:
    if len(raw) > MAX_MANIFEST_BYTES:
        raise ValueError("manifest exceeds size limit")
    manifest = json.loads(raw)
    if not isinstance(manifest, dict) or manifest.get("format") != FORMAT:
        raise ValueError("unsupported bundle manifest format")
    commit = manifest.get("source_lab_commit")
    if not isinstance(commit, str) or not HEX_COMMIT.fullmatch(commit):
        raise ValueError("missing or invalid source_lab_commit")
    files = manifest.get("files")
    if not isinstance(files, list) or not files or len(files) > MAX_FILES:
        raise ValueError("invalid manifest file list")
    if manifest.get("file_count") != len(files):
        raise ValueError("manifest file_count mismatch")
    names = []
    total = 0
    for row in files:
        if not isinstance(row, dict) or set(row) != {"path", "size", "sha256"}:
            raise ValueError("malformed manifest file entry")
        name, size, sha = row["path"], row["size"], row["sha256"]
        validate_member_path(name)
        if name == MANIFEST_NAME:
            raise ValueError("manifest cannot list itself")
        if not isinstance(size, int) or isinstance(size, bool) or not 0 <= size <= MAX_MEMBER_BYTES:
            raise ValueError(f"invalid member size for {name!r}")
        if not isinstance(sha, str) or not HEX_SHA256.fullmatch(sha):
            raise ValueError(f"invalid member digest for {name!r}")
        names.append(name)
        total += size
    if names != sorted(set(names)):
        raise ValueError("manifest paths must be unique and sorted")
    if total > MAX_TOTAL_BYTES or manifest.get("total_bytes") != total:
        raise ValueError("manifest total_bytes mismatch or size limit exceeded")
    return manifest, files


def _verify_direct_receipts(directory: Path, rows: list[dict]) -> int:
    """Check optional review copies against the hash-pinned archive members."""
    receipts = directory / "receipts"
    if not receipts.is_dir():
        return 0
    by_name: dict[str, list[dict]] = {}
    by_path = {row["path"]: row for row in rows}
    for row in rows:
        by_name.setdefault(Path(row["path"]).name, []).append(row)
    count = 0
    for path in sorted(receipts.glob("*.json")):
        if path.is_symlink():
            raise ValueError(f"direct receipt must be a regular file: {path}")
        raw = path.read_bytes()
        alias = DIRECT_RECEIPT_ALIASES.get(path.name)
        candidates = [by_path[alias]] if alias in by_path else by_name.get(path.name, [])
        if not any(row["size"] == len(raw) and
                   row["sha256"] == hashlib.sha256(raw).hexdigest()
                   for row in candidates):
            raise ValueError(f"direct receipt differs from bundled member: {path}")
        count += 1
    return count


def verify_archive(path: Path, *, check_external: bool = True,
                   require_external: bool = False) -> dict:
    """Stream a zstd tar and verify its manifest and every member in place."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    archive_hash = hashlib.sha256()
    with path.open("rb") as compressed:
        while block := compressed.read(1024 * 1024):
            archive_hash.update(block)
    process = subprocess.Popen(
        ["zstd", "--decompress", "--stdout", "--quiet", "--", str(path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        assert process.stdout is not None
        with tarfile.open(fileobj=process.stdout, mode="r|") as archive:
            members = iter(archive)
            first = next(members, None)
            if first is None or first.name != MANIFEST_NAME or not first.isfile():
                raise ValueError("first archive member must be a regular MANIFEST.json")
            if first.size > MAX_MANIFEST_BYTES:
                raise ValueError("manifest exceeds size limit")
            _check_metadata(first)
            source = archive.extractfile(first)
            if source is None:
                raise ValueError("manifest data unavailable")
            manifest_bytes = source.read(MAX_MANIFEST_BYTES + 1)
            if len(manifest_bytes) != first.size:
                raise ValueError("manifest byte length mismatch")
            manifest, rows = _validate_manifest(manifest_bytes)
            count = 0
            for member in members:
                if count >= len(rows):
                    raise ValueError("archive contains an unlisted extra member")
                row = rows[count]
                validate_member_path(member.name)
                if member.name != row["path"] or not member.isfile():
                    raise ValueError(
                        f"member order/type mismatch at index {count}: "
                        f"actual={member.name!r}, expected={row['path']!r}"
                    )
                if member.size != row["size"]:
                    raise ValueError(f"size mismatch for {member.name}")
                _check_metadata(member)
                body = archive.extractfile(member)
                if body is None:
                    raise ValueError(f"missing member data: {member.name}")
                digest = hashlib.sha256()
                actual_size = 0
                while block := body.read(1024 * 1024):
                    actual_size += len(block)
                    digest.update(block)
                if actual_size != row["size"] or digest.hexdigest() != row["sha256"]:
                    raise ValueError(f"hash or size mismatch for {member.name}")
                count += 1
            if count != len(rows):
                raise ValueError(f"archive has {count} files; manifest lists {len(rows)}")
        # tarfile stops after the tar end marker. Only bounded zero block
        # padding may follow it; hidden members or concatenated payloads fail.
        remainder = process.stdout.read(64 * 1024 + 1)
        if len(remainder) > 64 * 1024 or any(remainder):
            raise ValueError("nonzero or excessive bytes after tar end marker")
        process.stdout.close()
        stderr = process.stderr.read() if process.stderr is not None else b""
        if process.wait() != 0:
            raise ValueError("zstd decompression failed: " + stderr.decode(errors="replace")[:300])
    except BaseException:
        if process.poll() is None:
            process.kill()
        process.wait()
        raise
    result = {
        "archive": str(path),
        "archive_sha256": archive_hash.hexdigest(),
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "source_lab_commit": manifest["source_lab_commit"],
        "file_count": manifest["file_count"],
        "total_bytes": manifest["total_bytes"],
    }
    external = path.parent / MANIFEST_NAME
    if check_external and external.is_symlink():
        raise ValueError("adjacent MANIFEST.json must not be a symlink")
    if check_external and external.exists():
        raw = external.read_bytes()
        if len(raw) > MAX_MANIFEST_BYTES:
            raise ValueError("external manifest exceeds size limit")
        record = json.loads(raw)
        if not isinstance(record, dict) or set(record) != {
            "format", "source_lab_commit", "source_lab_commit_note", "archive_filename",
            "archive_sha256", "archive_size", "embedded_manifest_sha256",
            "file_count", "total_bytes", "selection", "files"
        }:
            raise ValueError("external manifest fields mismatch")
        if (record["format"] != FORMAT or
                record["source_lab_commit"] != manifest["source_lab_commit"] or
                record["archive_filename"] != path.name or
                record["archive_sha256"] != result["archive_sha256"] or
                record["archive_size"] != path.stat().st_size or
                record["embedded_manifest_sha256"] != result["manifest_sha256"] or
                record["file_count"] != manifest["file_count"] or
                record["total_bytes"] != manifest["total_bytes"] or
                record["selection"] != manifest.get("selection") or
                record["files"] != manifest["files"]):
            raise ValueError("external manifest does not match bundle")
        result["external_manifest"] = str(external)
        result["external_manifest_sha256"] = hashlib.sha256(raw).hexdigest()
        result["external_manifest_verified"] = True
    elif require_external:
        raise ValueError("adjacent MANIFEST.json is required")
    else:
        result["external_manifest_verified"] = False
    if check_external:
        result["direct_receipts_verified"] = _verify_direct_receipts(path.parent, rows)
    return result


def _check_metadata(member: tarfile.TarInfo) -> None:
    if member.uid != 0 or member.gid != 0 or member.mtime != 0:
        raise ValueError(f"noncanonical member metadata: {member.name}")
    if member.mode != 0o644 or member.uname or member.gname or member.linkname:
        raise ValueError(f"noncanonical member permissions/link: {member.name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="bundle.tar.zst to verify in place")
    parser.add_argument("--require-external", action="store_true",
                        help="fail if adjacent MANIFEST.json is absent")
    args = parser.parse_args()
    try:
        print(json.dumps(verify_archive(args.archive,
                                        require_external=args.require_external), sort_keys=True))
    except (OSError, ValueError, tarfile.TarError, json.JSONDecodeError) as error:
        print(f"bundle verification failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
