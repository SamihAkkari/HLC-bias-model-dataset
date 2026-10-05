# Building Energy Simulation and Model Results Dataset

## Overview

This dataset contains building-energy simulation data and associated model results for multiple building construction configurations.

The dataset is organized by building configuration. Each configuration contains:

- `Data.txt`: raw simulation data.
- `model_results.csv`: model and prediction results.

## Building configurations

The dataset contains eight building configurations.

Each configuration corresponds to a distinct combination of building construction system and insulation configuration.

The exact configuration names and their scientific definitions are documented in the dataset metadata.

## Dataset components

### Raw simulation data

The raw simulation data are stored as comma-separated TXT files.

Each file contains simulation inputs, environmental information, temperature-related variables, performance indicators, and time-related information.

### Model results

The `model_results.csv` files contain results associated with HLC prediction and model evaluation, including results from:

- Random Forest (RF)
- Multilayer Perceptron (MLP)
- Steady state method (STM)

## File organization

Each building configuration follows the structure:

    <building_configuration>/
    ├── Data.txt
    └── model_results.csv


## Data format

| Component | Format | Delimiter |
|---|---|---|
| Raw simulation data | TXT | comma |
| Model results | CSV | comma |

## Metadata

The `metadata/` directory contains:

- dataset overview: current md file
- data dictionary: defining the fields associated with the dataset
- machine-readable schemas
- file manifest

## Reproducibility

The current public code repository contains documentation, metadata, examples, and utilities for obtaining and verifying the dataset.

Large data files are distributed through the research data repository.

## Version

Initial dataset version: `v1.0.0`

## Important note

Scientific definitions, units, and calculation details for individual variables should be interpreted together with the associated research article and the detailed data dictionary.