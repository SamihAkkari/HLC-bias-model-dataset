"""
Validate a downloaded release of the HLC dataset.

The validator is intentionally data-driven:
- File-level expectations come from metadata/manifest.csv.
- Configuration IDs come from metadata/manifest.csv.

Usage
-----
Validate all configurations:
    python scripts/validate_download.py "C:\\path\\to\\hlc-dataset"

Validate one configuration:
    python scripts/validate_download.py "C:\\path\\to\\hlc-dataset" --config CB-IWI

Validate multiple configurations:
    python scripts/validate_download.py "C:\\path\\to\\hlc-dataset" --config CB-IWI HC-EWI LW-IWI

Validate all explicitly:
    python scripts/validate_download.py "C:\\path\\to\\hlc-dataset" --config all

Optional arguments:
    --manifest PATH
        Path to manifest.csv.

    --skip-checksum
        Skip SHA-256 checksum validation.

    --quiet
        Print only the final validation result.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq


# ---------------------------------------------------------------------------
# Generic constants
# ---------------------------------------------------------------------------

DEFAULT_MANIFEST = Path("metadata") / "manifest.csv"

SHA256_CHUNK_SIZE = 8 * 1024 * 1024


# ---------------------------------------------------------------------------
# Command-line interface
# ---------------------------------------------------------------------------

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate downloaded HLC dataset files against the "
            "published manifest."
        )
    )

    parser.add_argument(
        "data_dir",
        type=Path,
        help=(
            "Parent directory containing the configuration directories."
        ),
    )

    parser.add_argument(
        "--config",
        nargs="+",
        default=None,
        help=(
            "Configuration(s) to validate. "
            "Provide one or more configuration IDs. "
            "Use 'all' to validate all configurations. "
            "If omitted, all configurations are validated."
        ),
    )

    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help=(
            "Path to metadata/manifest.csv. "
            "Default: metadata/manifest.csv"
        ),
    )

    parser.add_argument(
        "--skip-checksum",
        action="store_true",
        help="Skip SHA-256 checksum validation.",
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Print only the final validation result.",
    )

    return parser.parse_args()


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def print_message(
    message: str,
    quiet: bool = False,
) -> None:
    if not quiet:
        print(message)


def print_check(
    label: str,
    success: bool,
    details: str = "",
    quiet: bool = False,
) -> None:
    if quiet:
        return

    status = "OK" if success else "FAIL"

    if details:
        print(f"  [{status}] {label}: {details}")
    else:
        print(f"  [{status}] {label}")


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------

def load_manifest(
    manifest_path: Path,
) -> list[dict[str, str]]:
    """
    Load manifest.csv.

    The manifest is the source of truth for:
    - configuration IDs
    - file paths
    - file sizes
    - row counts
    - column counts
    - SHA-256 checksums
    """
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"Manifest not found: {manifest_path}"
        )

    with manifest_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    if not rows:
        raise ValueError(
            f"Manifest is empty: {manifest_path}"
        )

    required_columns = {
        "configuration_id",
        "file_name",
        "relative_path",
        "size_bytes",
        "row_count",
        "column_count",
        "sha256",
    }

    missing_columns = required_columns - set(fieldnames)

    if missing_columns:
        raise ValueError(
            "Manifest is missing required column(s): "
            + ", ".join(sorted(missing_columns))
        )

    return rows


def get_configuration_ids(
    manifest: list[dict[str, str]],
) -> list[str]:
    """
    Return configuration IDs from the manifest.

    Order is preserved.
    """
    configuration_ids = []
    seen = set()

    for row in manifest:
        configuration_id = row["configuration_id"]

        if configuration_id not in seen:
            configuration_ids.append(configuration_id)
            seen.add(configuration_id)

    return configuration_ids


def select_configurations(
    manifest: list[dict[str, str]],
    requested_configs: list[str] | None,
) -> list[str]:
    """
    Determine which configurations should be validated.

    Behavior:

        --config omitted
            -> all configurations

        --config all
            -> all configurations

        --config CONFIG1 CONFIG2
            -> only requested configurations
    """
    available = get_configuration_ids(manifest)

    if requested_configs is None:
        return available

    normalized = [
        config.strip()
        for config in requested_configs
        if config.strip()
    ]

    if not normalized:
        return available

    if any(config.lower() == "all" for config in normalized):
        if len(normalized) > 1:
            raise ValueError(
                "Use either '--config all' or specific configuration IDs, "
                "not both."
            )

        return available

    unknown = [
        config
        for config in normalized
        if config not in available
    ]

    if unknown:
        raise ValueError(
            "Unknown configuration(s): "
            + ", ".join(unknown)
            + "\nAvailable configurations: "
            + ", ".join(available)
        )

    # Remove duplicates while preserving order.
    selected = []
    seen = set()

    for config in normalized:
        if config not in seen:
            selected.append(config)
            seen.add(config)

    return selected


def get_manifest_entries(
    manifest: list[dict[str, str]],
    configuration_id: str,
) -> list[dict[str, str]]:
    """
    Return manifest entries for one configuration.
    """
    entries = [
        row
        for row in manifest
        if row["configuration_id"] == configuration_id
    ]

    if not entries:
        raise ValueError(
            f"No manifest entries found for configuration "
            f"'{configuration_id}'."
        )

    return entries


# ---------------------------------------------------------------------------
# SHA-256
# ---------------------------------------------------------------------------

def calculate_sha256(
    file_path: Path,
) -> str:
    """
    Calculate SHA-256 without loading the complete file into memory.
    """
    digest = hashlib.sha256()

    with file_path.open("rb") as file:
        while True:
            chunk = file.read(SHA256_CHUNK_SIZE)

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


# ---------------------------------------------------------------------------
# Parquet validation
# ---------------------------------------------------------------------------

def validate_parquet(
    file_path: Path,
    expected_rows: int,
    expected_columns: int,
    quiet: bool,
) -> bool:
    """
    Validate a Parquet file.

    Expected row and column counts come from the manifest.
    No column names or data types are checked.
    """
    valid = True

    try:
        parquet_file = pq.ParquetFile(file_path)
        metadata = parquet_file.metadata
        schema = parquet_file.schema_arrow

    except Exception as exc:
        print_check(
            "Parquet readability",
            False,
            str(exc),
            quiet,
        )
        return False

    print_check(
        "Parquet readability",
        True,
        quiet=quiet,
    )

    # Row count
    actual_rows = metadata.num_rows

    rows_ok = actual_rows == expected_rows

    print_check(
        "row count",
        rows_ok,
        f"{actual_rows:,} "
        f"(expected {expected_rows:,})",
        quiet,
    )

    if not rows_ok:
        valid = False

    # Column count
    actual_columns = len(schema.names)

    columns_ok = actual_columns == expected_columns

    print_check(
        "column count",
        columns_ok,
        f"{actual_columns} "
        f"(expected {expected_columns})",
        quiet,
    )

    if not columns_ok:
        valid = False

    return valid


# ---------------------------------------------------------------------------
# CSV validation
# ---------------------------------------------------------------------------

def validate_csv(
    file_path: Path,
    expected_rows: int,
    expected_columns: int,
    quiet: bool,
) -> bool:
    """
    Validate a CSV file.

    Expected row and column counts come from the manifest.
    No column names or data types are checked.
    """
    valid = True

    # ---------------------------------------------------------------
    # Readability and column count
    # ---------------------------------------------------------------

    try:
        header = pd.read_csv(
            file_path,
            nrows=0,
        )

    except Exception as exc:
        print_check(
            "CSV readability",
            False,
            str(exc),
            quiet,
        )
        return False

    print_check(
        "CSV readability",
        True,
        quiet=quiet,
    )

    actual_columns = len(header.columns)

    columns_ok = actual_columns == expected_columns

    print_check(
        "column count",
        columns_ok,
        f"{actual_columns} "
        f"(expected {expected_columns})",
        quiet,
    )

    if not columns_ok:
        valid = False

    # ---------------------------------------------------------------
    # Row count
    # ---------------------------------------------------------------

    try:
        with file_path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.reader(file)

            # Skip header.
            next(reader, None)

            actual_rows = sum(
                1
                for _ in reader
            )

    except Exception as exc:
        print_check(
            "row count",
            False,
            str(exc),
            quiet,
        )
        return False

    rows_ok = actual_rows == expected_rows

    print_check(
        "row count",
        rows_ok,
        f"{actual_rows:,} "
        f"(expected {expected_rows:,})",
        quiet,
    )

    if not rows_ok:
        valid = False

    return valid


# ---------------------------------------------------------------------------
# Individual file validation
# ---------------------------------------------------------------------------

def validate_file(
    file_path: Path,
    manifest_entry: dict[str, str],
    skip_checksum: bool,
    quiet: bool,
) -> bool:
    """
    Validate one file against its manifest entry.
    """
    valid = True

    file_name = manifest_entry["file_name"]

    print_message(
        f"\nFile: {file_name}",
        quiet,
    )

    # ---------------------------------------------------------------
    # Existence
    # ---------------------------------------------------------------

    if not file_path.exists():
        print_check(
            "file exists",
            False,
            str(file_path),
            quiet,
        )
        return False

    print_check(
        "file exists",
        True,
        quiet=quiet,
    )

    # ---------------------------------------------------------------
    # File size
    # ---------------------------------------------------------------

    expected_size = int(
        manifest_entry["size_bytes"]
    )

    actual_size = file_path.stat().st_size

    size_ok = actual_size == expected_size

    print_check(
        "size",
        size_ok,
        f"{actual_size:,} bytes "
        f"(expected {expected_size:,})",
        quiet,
    )

    if not size_ok:
        valid = False

    # ---------------------------------------------------------------
    # SHA-256
    # ---------------------------------------------------------------

    if skip_checksum:
        print_check(
            "SHA-256",
            True,
            "skipped",
            quiet,
        )

    else:
        expected_hash = (
            manifest_entry["sha256"]
            .strip()
            .lower()
        )

        if not expected_hash:
            print_check(
                "SHA-256",
                False,
                "no checksum found in manifest",
                quiet,
            )
            valid = False

        else:
            print_message(
                "  Calculating SHA-256...",
                quiet,
            )

            actual_hash = calculate_sha256(
                file_path
            )

            hash_ok = (
                actual_hash == expected_hash
            )

            print_check(
                "SHA-256",
                hash_ok,
                (
                    "matches published file"
                    if hash_ok
                    else (
                        f"mismatch "
                        f"(expected {expected_hash}, "
                        f"found {actual_hash})"
                    )
                ),
                quiet,
            )

            if not hash_ok:
                valid = False

    # ---------------------------------------------------------------
    # Expected dimensions from manifest
    # ---------------------------------------------------------------

    expected_rows = int(
        manifest_entry["row_count"]
    )

    expected_columns = int(
        manifest_entry["column_count"]
    )

    # ---------------------------------------------------------------
    # Structure validation
    # ---------------------------------------------------------------

    suffix = file_path.suffix.lower()

    if suffix == ".parquet":

        structure_ok = validate_parquet(
            file_path=file_path,
            expected_rows=expected_rows,
            expected_columns=expected_columns,
            quiet=quiet,
        )

    elif suffix == ".csv":

        structure_ok = validate_csv(
            file_path=file_path,
            expected_rows=expected_rows,
            expected_columns=expected_columns,
            quiet=quiet,
        )

    else:

        print_check(
            "structure",
            True,
            f"no specialized validator for "
            f"{suffix or 'unknown'}",
            quiet,
        )

        structure_ok = True

    if not structure_ok:
        valid = False

    print_message(
        f"  RESULT: {'PASSED' if valid else 'FAILED'}",
        quiet,
    )

    return valid


# ---------------------------------------------------------------------------
# Configuration validation
# ---------------------------------------------------------------------------

def validate_configuration(
    data_dir: Path,
    configuration_id: str,
    manifest: list[dict[str, str]],
    skip_checksum: bool,
    quiet: bool,
) -> bool:
    """
    Validate one configuration.
    """
    entries = get_manifest_entries(
        manifest,
        configuration_id,
    )

    configuration_dir = (
        data_dir / configuration_id
    )

    print_message(
        "\n"
        + "=" * 72
        + f"\nConfiguration: {configuration_id}\n"
        + "=" * 72,
        quiet,
    )

    if not configuration_dir.exists():
        print_message(
            f"ERROR: configuration directory not found:\n"
            f"  {configuration_dir}",
            quiet,
        )
        return False

    if not configuration_dir.is_dir():
        print_message(
            f"ERROR: configuration path is not a directory:\n"
            f"  {configuration_dir}",
            quiet,
        )
        return False

    configuration_valid = True

    for entry in entries:

        relative_path = Path(
            entry["relative_path"]
        )

        # The manifest path is relative to the dataset root.
        # The configuration directory is already the configuration
        # root, so remove the configuration ID from the path.
        relative_parts = relative_path.parts

        if (
            relative_parts
            and relative_parts[0] == configuration_id
        ):
            relative_path = Path(
                *relative_parts[1:]
            )

        file_path = (
            configuration_dir / relative_path
        )

        file_valid = validate_file(
            file_path=file_path,
            manifest_entry=entry,
            skip_checksum=skip_checksum,
            quiet=quiet,
        )

        if not file_valid:
            configuration_valid = False

    print_message(
        "\n"
        + f"Configuration result: "
        f"{'PASSED' if configuration_valid else 'FAILED'}",
        quiet,
    )

    return configuration_valid


# ---------------------------------------------------------------------------
# Dataset validation
# ---------------------------------------------------------------------------

def validate_dataset(
    data_dir: Path,
    manifest_path: Path,
    requested_configs: list[str] | None,
    skip_checksum: bool,
    quiet: bool,
) -> bool:
    """
    Validate the requested configurations.
    """
    if not data_dir.exists():
        print(
            f"ERROR: dataset directory does not exist: "
            f"{data_dir}"
        )
        return False

    if not data_dir.is_dir():
        print(
            f"ERROR: dataset path is not a directory: "
            f"{data_dir}"
        )
        return False

    # ---------------------------------------------------------------
    # Load manifest
    # ---------------------------------------------------------------

    try:
        manifest = load_manifest(
            manifest_path
        )

    except Exception as exc:
        print(f"ERROR: {exc}")
        return False

    # ---------------------------------------------------------------
    # Determine configurations
    # ---------------------------------------------------------------

    try:
        configurations = select_configurations(
            manifest,
            requested_configs,
        )

    except Exception as exc:
        print(f"ERROR: {exc}")
        return False

    # ---------------------------------------------------------------
    # Header
    # ---------------------------------------------------------------

    if not quiet:
        print()
        print("=" * 72)
        print("HLC DATASET VALIDATION")
        print("=" * 72)
        print(f"Dataset directory : {data_dir}")
        print(f"Manifest          : {manifest_path}")
        print(
            "Configurations    : "
            + ", ".join(configurations)
        )
        print("=" * 72)

    # ---------------------------------------------------------------
    # Validate configurations
    # ---------------------------------------------------------------

    overall_valid = True

    for configuration_id in configurations:

        configuration_valid = (
            validate_configuration(
                data_dir=data_dir,
                configuration_id=configuration_id,
                manifest=manifest,
                skip_checksum=skip_checksum,
                quiet=quiet,
            )
        )

        if not configuration_valid:
            overall_valid = False

    # ---------------------------------------------------------------
    # Final result
    # ---------------------------------------------------------------

    print()

    if overall_valid:
        print("VALIDATION RESULT: PASSED")
        print(
            f"Successfully validated "
            f"{len(configurations)} configuration(s)."
        )
    else:
        print("VALIDATION RESULT: FAILED")
        print(
            "One or more configurations did not pass validation."
        )

    return overall_valid


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    args = parse_arguments()

    success = validate_dataset(
        data_dir=args.data_dir,
        manifest_path=args.manifest,
        requested_configs=args.config,
        skip_checksum=args.skip_checksum,
        quiet=args.quiet,
    )

    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())