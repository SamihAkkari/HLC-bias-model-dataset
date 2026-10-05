import csv

from config import (
    CONFIGURATIONS,
    DATA_DIR,
    DATA_FILE,
    MODEL_FILE,
)


# ============================================================
# OUTPUT
# ============================================================

OUTPUT_FILE = "metadata/manifest.csv"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def read_header(file_path):
    """
    Read only the first line/header of a CSV/TXT file.

    The complete file is NOT loaded into memory.
    """

    with file_path.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.reader(
            f,
            delimiter=","
        )

        return next(reader)


# ============================================================
# CHECK DATASET DIRECTORY
# ============================================================

if not DATA_DIR.exists():

    raise FileNotFoundError(
        "\nDataset directory does not exist:\n"
        f"{DATA_DIR}\n\n"
        "Please update DATA_DIR in config.py."
    )


if not DATA_DIR.is_dir():

    raise NotADirectoryError(
        f"DATA_DIR is not a directory:\n{DATA_DIR}"
    )


# ============================================================
# FIND CONFIGURATION FOLDERS
# ============================================================

building_dirs = [
    directory
    for directory in sorted(DATA_DIR.iterdir())
    if directory.is_dir()
    and directory.name.lower() != "other"
]


print()
print("=" * 70)
print("BUILDING-ENERGY DATASET INVENTORY")
print("=" * 70)

print()
print("Dataset directory:")
print(f"  {DATA_DIR}")

print()
print(f"Configuration folders found: {len(building_dirs)}")


# ============================================================
# INVENTORY
# ============================================================

records = []


for building_dir in building_dirs:

    # Folder name is the configuration ID
    folder_name = building_dir.name

    # --------------------------------------------------------
    # Check that the folder is a known configuration
    # --------------------------------------------------------

    if folder_name not in CONFIGURATIONS:

        print()
        print("WARNING")
        print("-" * 70)
        print(f"Unknown configuration folder: {folder_name}")
        print("This folder will be ignored.")
        print()

        continue

    config = CONFIGURATIONS[folder_name]

    print()
    print("=" * 70)
    print(
        f"{folder_name} - "
        f"{config['configuration_name']}"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # Files that belong to the public dataset
    #
    # We deliberately do NOT inspect anything inside 'other'.
    # --------------------------------------------------------

    files_to_inventory = [
        (
            DATA_FILE,
            "raw_simulation"
        ),
        (
            MODEL_FILE,
            "model_results"
        ),
    ]

    for file_name, component in files_to_inventory:

        file_path = building_dir / file_name

        # ----------------------------------------------------
        # Check that the expected file exists
        # ----------------------------------------------------

        if not file_path.exists():

            print(
                f"WARNING: Missing file: "
                f"{folder_name}/{file_name}"
            )

            continue

        if not file_path.is_file():

            print(
                f"WARNING: Expected file is not a file: "
                f"{folder_name}/{file_name}"
            )

            continue

        print(
            f"Inspecting: "
            f"{folder_name}/{file_name}"
        )

        # ----------------------------------------------------
        # Read header and obtain file size
        # ----------------------------------------------------

        try:

            header = read_header(file_path)

            size_bytes = file_path.stat().st_size

            size_gb = (
                size_bytes /
                (1024 ** 3)
            )

            records.append({

                "configuration_id":
                    folder_name,

                "configuration_name":
                    config["configuration_name"],

                "building_system":
                    config["building_system"],

                "insulation_configuration":
                    config["insulation_configuration"],

                "component":
                    component,

                "file_name":
                    file_name,

                "relative_path":
                    str(
                        file_path.relative_to(DATA_DIR)
                    ),

                "size_bytes":
                    size_bytes,

                "size_gb":
                    round(size_gb, 3),

                "column_count":
                    len(header),

            })

        except Exception as error:

            print(
                f"ERROR reading: "
                f"{folder_name}/{file_name}"
            )

            print(
                f"       {error}"
            )

            records.append({

                "configuration_id":
                    folder_name,

                "configuration_name":
                    config["configuration_name"],

                "building_system":
                    config["building_system"],

                "insulation_configuration":
                    config["insulation_configuration"],

                "component":
                    component,

                "file_name":
                    file_name,

                "relative_path":
                    str(
                        file_path.relative_to(DATA_DIR)
                    ),

                "size_bytes":
                    "",

                "size_gb":
                    "",

                "column_count":
                    "",

            })


# ============================================================
# WRITE MANIFEST
# ============================================================

from pathlib import Path

output_file = Path(OUTPUT_FILE)

output_file.parent.mkdir(
    parents=True,
    exist_ok=True
)


fieldnames = [
    "configuration_id",
    "configuration_name",
    "building_system",
    "insulation_configuration",
    "component",
    "file_name",
    "relative_path",
    "size_bytes",
    "size_gb",
    "column_count",
]


with output_file.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(records)


# ============================================================
# SUMMARY
# ============================================================

configuration_count = len(
    set(
        record["configuration_id"]
        for record in records
    )
)


print()
print("=" * 70)
print("INVENTORY COMPLETE")
print("=" * 70)

print()
print(
    f"Configurations inventoried: "
    f"{configuration_count}"
)

print(
    f"Files inventoried:          "
    f"{len(records)}"
)

print()
print("Configurations:")

for configuration_id, config in CONFIGURATIONS.items():

    count = sum(
        1
        for record in records
        if record["configuration_id"]
        == configuration_id
    )

    if count > 0:

        print(
            f"  {configuration_id:8} "
            f"{config['configuration_name']:25} "
            f"{count} files"
        )

print()
print("Manifest:")
print(
    f"  {output_file.resolve()}"
)

print()
print("The 'other' directories were not inspected.")
print()