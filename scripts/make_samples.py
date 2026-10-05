from pathlib import Path
import csv

from config import (
    CONFIGURATIONS,
    DATA_DIR,
    DATA_FILE,
    MODEL_FILE,
    SAMPLE_ROWS,
)


# ============================================================
# OUTPUT
# ============================================================

OUTPUT_DIR = Path("data") / "sample"


# ============================================================
# SAMPLE FUNCTION
# ============================================================

def create_sample(
    input_file,
    output_file,
    number_of_rows
):
    """
    Copy the header and the first number_of_rows data rows.

    The file is processed row-by-row, so large source files
    are never loaded into memory.
    """

    with input_file.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as source:

        reader = csv.reader(
            source,
            delimiter=","
        )

        with output_file.open(
            "w",
            encoding="utf-8",
            newline=""
        ) as destination:

            writer = csv.writer(
                destination,
                delimiter=","
            )

            try:
                header = next(reader)
            except StopIteration:
                raise ValueError(
                    f"Input file is empty:\n{input_file}"
                )

            writer.writerow(header)

            rows_written = 0

            for row in reader:

                writer.writerow(row)

                rows_written += 1

                if rows_written >= number_of_rows:
                    break

    return rows_written


# ============================================================
# CHECK SOURCE DIRECTORY
# ============================================================

if not DATA_DIR.exists():

    raise FileNotFoundError(
        f"\nDataset directory does not exist:\n"
        f"{DATA_DIR}\n\n"
        "Please update DATA_DIR in config.py."
    )


if not DATA_DIR.is_dir():

    raise NotADirectoryError(
        f"DATA_DIR is not a directory:\n{DATA_DIR}"
    )


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CREATE SAMPLES
# ============================================================

print()
print("=" * 70)
print("BUILDING-ENERGY DATASET SAMPLE CREATION")
print("=" * 70)

print()
print(
    f"Rows per sample: {SAMPLE_ROWS}"
)

print(
    f"Output directory: {OUTPUT_DIR.resolve()}"
)


total_files = 0


for configuration in CONFIGURATIONS:

    source_dir = DATA_DIR / configuration
    output_dir = OUTPUT_DIR / configuration

    print()
    print("=" * 70)
    print(configuration)
    print("=" * 70)

    if not source_dir.exists():

        print(
            f"WARNING: Configuration directory does not exist:"
            f"\n  {source_dir}"
        )

        continue

    if not source_dir.is_dir():

        print(
            f"WARNING: Configuration path is not a directory:"
            f"\n  {source_dir}"
        )

        continue

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    files_to_sample = [
        (
            DATA_FILE,
            "Data_sample.txt"
        ),
        (
            MODEL_FILE,
            "model_results_sample.csv"
        ),
    ]

    for source_name, output_name in files_to_sample:

        input_file = source_dir / source_name
        output_file = output_dir / output_name

        print()
        print("Source:")
        print(f"  {input_file}")

        print("Output:")
        print(f"  {output_file}")

        if not input_file.exists():

            print(
                "WARNING: Source file does not exist."
            )

            continue

        if not input_file.is_file():

            print(
                "WARNING: Source path is not a file."
            )

            continue

        if output_file.exists():

            raise FileExistsError(
                f"\nSample file already exists:\n"
                f"{output_file}\n\n"
                "Delete the existing sample manually if "
                "you want to recreate it."
            )

        rows_written = create_sample(
            input_file,
            output_file,
            SAMPLE_ROWS
        )

        print(
            f"Created sample with "
            f"{rows_written} data rows."
        )

        total_files += 1


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("SAMPLE CREATION COMPLETE")
print("=" * 70)

print()
print(
    f"Files created: {total_files}"
)

print()
print(
    "Samples are structural examples only."
)

print(
    "They contain the first rows of each source file and "
    "are not statistically representative samples."
)

print()
print("Output:")
print(
    f"  {OUTPUT_DIR.resolve()}"
)

print()