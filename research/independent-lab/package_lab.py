#!/usr/bin/env python3
"""Package only daos.fun lab files as a deterministic, verified tar.zst.

Example:
  python research/independent-lab/package_lab.py \
    --lab-root /path/to/solana-research-lab-20261023 \
    --output /tmp/daosfun-independent-lab.tar.zst

Requires the `zstd` command-line tool. The bundled manifest records each
lab-relative file's exact size and SHA-256. Timestamps, owners and modes in
the tar are fixed; no unrelated Meteora or HumidiFi lane is selected.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import os
import stat
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

from verify_bundle import (COMMON_HARNESS, DAOS_SOURCE_MODEL_FILES, FORMAT, MANIFEST_NAME,
                           validate_member_path, verify_archive)


EXTRA_DAOS_SCRIPTS = frozenset(COMMON_HARNESS)
SELECTION = {
    "trees": ["analysis/daos_fun", "analysis/root_virtual_xyk", "inputs/daos_fun"],
    "analysis_globs": ["daos_*.asm"],
    "evidence_prefixes": ["daos", "ghidra-daos"],
    "script_globs": ["daos_*.py", "root_virtual_xyk_*.py"],
    "additional_scripts": sorted(EXTRA_DAOS_SCRIPTS),
    "source_model_files": sorted(DAOS_SOURCE_MODEL_FILES),
}


def _regular_file(path: Path) -> None:
    mode = path.lstat().st_mode
    if not stat.S_ISREG(mode):
        raise ValueError(f"non-regular input is not bundleable: {path}")


def select_files(lab_root: Path) -> list[tuple[str, Path]]:
    """Return sorted, validated lab-relative paths from the scoped selection."""
    lab_root = lab_root.resolve(strict=True)
    if not lab_root.is_dir():
        raise ValueError(f"lab root is not a directory: {lab_root}")
    paths: set[Path] = set()

    def add(path: Path) -> None:
        _regular_file(path)
        relative = path.relative_to(lab_root).as_posix()
        validate_member_path(relative)
        paths.add(path)

    def add_tree(relative: str) -> None:
        tree = lab_root / relative
        if not tree.is_dir() or tree.is_symlink():
            raise ValueError(f"required input tree unavailable: {tree}")
        for path in tree.rglob("*"):
            if "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            if path.is_symlink():
                raise ValueError(f"symlink in input tree: {path}")
            if path.is_file():
                add(path)
            elif not path.is_dir():
                raise ValueError(f"special file in input tree: {path}")

    for tree in SELECTION["trees"]:
        add_tree(tree)
    for pattern in SELECTION["analysis_globs"]:
        for path in (lab_root / "analysis").glob(pattern):
            add(path)
    evidence = lab_root / "evidence"
    if not evidence.is_dir() or evidence.is_symlink():
        raise ValueError("evidence directory unavailable")
    for path in evidence.iterdir():
        if not any(path.name.startswith(prefix) for prefix in SELECTION["evidence_prefixes"]):
            continue
        if path.is_symlink():
            raise ValueError(f"symlink in selected evidence: {path}")
        if path.is_dir():
            add_tree(path.relative_to(lab_root).as_posix())
        else:
            add(path)
    scripts = lab_root / "scripts"
    if not scripts.is_dir() or scripts.is_symlink():
        raise ValueError("scripts directory unavailable")
    for pattern in SELECTION["script_globs"]:
        for path in scripts.glob(pattern):
            add(path)
    for name in EXTRA_DAOS_SCRIPTS:
        path = scripts / name
        if not path.exists():
            raise ValueError(f"necessary daos.fun harness missing: {name}")
        add(path)
    for relative in SELECTION["source_model_files"]:
        path = lab_root / relative
        if not path.is_file():
            raise ValueError(f"required daos.fun source model file missing: {relative}")
        add(path)

    selected = {path.stem for path in paths if path.parent == scripts and path.suffix == ".py"}
    for path in sorted(paths):
        if path.parent != scripts or path.suffix != ".py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            imports = []
            if isinstance(node, ast.Import):
                imports = [alias.name.split(".", 1)[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports = [node.module.split(".", 1)[0]]
            for module in imports:
                if (scripts / f"{module}.py").is_file() and module not in selected:
                    raise ValueError(f"unbundled local script dependency: {path.name} -> {module}.py")
    result = sorted((path.relative_to(lab_root).as_posix(), path) for path in paths)
    if not result:
        raise ValueError("no daos.fun files selected")
    return result


def sha256_size(path: Path) -> tuple[str, int]:
    _regular_file(path)
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
            size += len(block)
    return digest.hexdigest(), size


def source_commit(lab_root: Path, override: str | None) -> str:
    """Pin HEAD, without implying that all selected files are committed."""
    if override is not None:
        commit = override.lower()
    else:
        top = subprocess.run(
            ["git", "-C", str(lab_root), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=False,
        )
        if top.returncode or Path(top.stdout.strip()).resolve() != lab_root:
            raise ValueError("lab root needs its own Git HEAD or --source-commit")
        result = subprocess.run(
            ["git", "-C", str(lab_root), "rev-parse", "--verify", "HEAD"],
            capture_output=True, text=True, check=False,
        )
        if result.returncode:
            raise ValueError("cannot resolve source lab HEAD commit")
        commit = result.stdout.strip().lower()
    if len(commit) != 40 or any(char not in "0123456789abcdef" for char in commit):
        raise ValueError("source lab commit must be a 40-character hex SHA-1")
    return commit


def _tar_info(name: str, size: int) -> tarfile.TarInfo:
    info = tarfile.TarInfo(name)
    info.size = size
    info.mode = 0o644
    info.uid = info.gid = info.mtime = 0
    info.uname = info.gname = ""
    info.type = tarfile.REGTYPE
    return info


def build_manifest(files: list[tuple[str, Path]], commit: str) -> tuple[dict, bytes]:
    rows = []
    for relative, source in files:
        digest, size = sha256_size(source)
        rows.append({"path": relative, "sha256": digest, "size": size})
    manifest = {
        "format": FORMAT,
        "source_lab_commit": commit,
        "selection": SELECTION,
        "file_count": len(rows),
        "total_bytes": sum(row["size"] for row in rows),
        "files": rows,
    }
    raw = (json.dumps(manifest, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True) + "\n").encode("utf-8")
    return manifest, raw


def package(lab_root: Path, output: Path, *, force: bool = False,
            source_commit_override: str | None = None) -> dict:
    lab_root = lab_root.resolve(strict=True)
    output = output.expanduser().absolute()
    if output.suffixes[-2:] != [".tar", ".zst"]:
        raise ValueError("output filename must end in .tar.zst")
    if not output.parent.is_dir():
        raise ValueError(f"output parent directory does not exist: {output.parent}")
    output = output.parent.resolve(strict=True) / output.name
    if output == lab_root or lab_root in output.parents:
        raise ValueError("output must be outside the selected lab root")
    external = output.parent / MANIFEST_NAME
    if output.exists() and not force:
        raise FileExistsError(f"output exists; pass --force to replace: {output}")
    if external.exists() and not force:
        raise FileExistsError(f"adjacent manifest exists; pass --force to replace: {external}")
    files = select_files(lab_root)
    commit = source_commit(lab_root, source_commit_override)
    manifest, manifest_bytes = build_manifest(files, commit)
    sizes = {row["path"]: row["size"] for row in manifest["files"]}
    temporary_path = None
    temporary_manifest = None
    try:
        with tempfile.TemporaryFile(mode="w+b") as plain:
            with tarfile.open(fileobj=plain, mode="w", format=tarfile.PAX_FORMAT) as archive:
                archive.addfile(_tar_info(MANIFEST_NAME, len(manifest_bytes)),
                                io.BytesIO(manifest_bytes))
                for relative, source in files:
                    _regular_file(source)
                    with source.open("rb") as body:
                        archive.addfile(_tar_info(relative, sizes[relative]), body)
            plain.seek(0)
            with tempfile.NamedTemporaryFile(
                mode="w+b", prefix=".daosfun-bundle-", suffix=".tar.zst",
                dir=output.parent, delete=False
            ) as compressed:
                temporary_path = Path(compressed.name)
                completed = subprocess.run(
                    ["zstd", "--quiet", "--single-thread", "--check", "-6", "--stdout"],
                    stdin=plain, stdout=compressed, stderr=subprocess.PIPE,
                    check=False,
                )
                if completed.returncode:
                    raise ValueError("zstd compression failed: " +
                                     completed.stderr.decode(errors="replace")[:300])
                compressed.flush()
                os.fsync(compressed.fileno())
        # No archive is published unless the standalone verifier can stream
        # all members and match each size and digest without extraction.
        result = verify_archive(temporary_path, check_external=False)
        if result["file_count"] != manifest["file_count"]:
            raise ValueError("self-verification file count mismatch")
        external_record = {
            "format": FORMAT,
            "source_lab_commit": commit,
            "source_lab_commit_note": (
                "The selected lab commit identifies a revision; per-file SHA-256 "
                "values define the packaged working-tree bytes."
            ),
            "archive_filename": output.name,
            "archive_sha256": result["archive_sha256"],
            "archive_size": temporary_path.stat().st_size,
            "embedded_manifest_sha256": result["manifest_sha256"],
            "file_count": manifest["file_count"],
            "total_bytes": manifest["total_bytes"],
            "selection": manifest["selection"],
            "files": manifest["files"],
        }
        external_bytes = (json.dumps(external_record, sort_keys=True,
                                     separators=(",", ":"), ensure_ascii=True) + "\n").encode()
        with tempfile.NamedTemporaryFile(
            mode="w+b", prefix=".daosfun-manifest-", suffix=".json",
            dir=output.parent, delete=False
        ) as manifest_file:
            temporary_manifest = Path(manifest_file.name)
            manifest_file.write(external_bytes)
            manifest_file.flush()
            os.fsync(manifest_file.fileno())
        os.replace(temporary_path, output)
        temporary_path = None
        os.replace(temporary_manifest, external)
        temporary_manifest = None
        return verify_archive(output, require_external=True)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        if temporary_manifest is not None:
            temporary_manifest.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lab-root", type=Path, required=True,
                        help="source solana-research-lab directory")
    parser.add_argument("--output", type=Path, required=True,
                        help="bundle .tar.zst path outside the lab")
    parser.add_argument("--force", action="store_true", help="replace an existing output")
    parser.add_argument("--source-commit", help="explicit 40-hex lab HEAD for a frozen copy without .git")
    args = parser.parse_args()
    try:
        print(json.dumps(package(args.lab_root, args.output, force=args.force,
                                 source_commit_override=args.source_commit), sort_keys=True))
    except (OSError, ValueError, tarfile.TarError, SyntaxError) as error:
        print(f"bundle packaging failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
