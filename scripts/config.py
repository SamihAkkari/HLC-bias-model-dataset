from pathlib import Path


# ============================================================
# DATASET CONFIGURATION
# ============================================================

# Parent directory containing the eight building configuration
# folders.
DATA_DIR = Path(r"C:\Users\sakkari\Code\hlc-bias-model\data")


# Files included in the public dataset
DATA_FILE = "Data.txt"
MODEL_FILE = "model_results.csv"


# Number of rows used when creating public samples
SAMPLE_ROWS = 100


# ============================================================
# BUILDING CONFIGURATIONS
# ============================================================

# The folder names are the configuration IDs.
#
# The information here is shared by the inventory and sample
# creation scripts so that configuration metadata has one
# source of truth.

CONFIGURATIONS = {
    "HC-EWI": {
        "configuration_name": "Heavy concrete EWI",
        "building_system": "Heavy concrete",
        "insulation_configuration": "EWI",
    },

    "HC-IWI": {
        "configuration_name": "Heavy concrete IWI",
        "building_system": "Heavy concrete",
        "insulation_configuration": "IWI",
    },

    "HC-NINS": {
        "configuration_name": "Heavy concrete NINS",
        "building_system": "Heavy concrete",
        "insulation_configuration": "NINS",
    },

    "CB-EWI": {
        "configuration_name": "Concrete blocks EWI",
        "building_system": "Concrete blocks",
        "insulation_configuration": "EWI",
    },

    "CB-IWI": {
        "configuration_name": "Concrete blocks IWI",
        "building_system": "Concrete blocks",
        "insulation_configuration": "IWI",
    },

    "CB-NINS": {
        "configuration_name": "Concrete blocks NINS",
        "building_system": "Concrete blocks",
        "insulation_configuration": "NINS",
    },

    "LW-EWI": {
        "configuration_name": "Lightweight EWI",
        "building_system": "Lightweight",
        "insulation_configuration": "EWI",
    },

    "LW-IWI": {
        "configuration_name": "Lightweight IWI",
        "building_system": "Lightweight",
        "insulation_configuration": "IWI",
    },
}