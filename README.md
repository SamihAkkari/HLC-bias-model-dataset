# 📊 Synthetic Dataset for Short-Duration Building Heat Loss Coefficient Estimation (SD-HLC)

This repository provides the documentation, metadata, representative sample data, and example code accompanying the research article:

**"Data-driven heat loss coefficient (HLC) estimation based upon a quick steady-state method"**

The complete dataset is archived on Zenodo and is **not stored in this GitHub repository** because of its size.

> 🔗 **Complete dataset:** [Zenodo: 10.5281/zenodo.23223811](https://doi.org/10.5281/zenodo.23223811)

---

## 📌 1. Overview

The dataset was generated to support the investigation of **short-duration, data-driven estimation of building heat loss coefficients (HLCs)**.

The underlying idea is to obtain an HLC estimate using a simple steady-state method based on averaging the measured data. The main advantage of this approach is its simplicity: it requires only a short measurement period and relies on a straightforward formulation based on the physical heat balance of the building. However, this simplicity also introduces an important limitation. Since the method makes strong assumptions about the thermal behaviour of the building and the surrounding conditions, the resulting HLC estimate can be significantly biased, particularly when the 12-hour period does not fully capture the building's dynamic thermal response.

However, this estimation error is not expected to be purely random. The steady-state estimator is derived from physical principles, meaning that its bias is related to identifiable interactions between factors such as building envelope characteristics, thermal dynamics, internal and solar gains, and outdoor weather conditions. These interactions can be complex and difficult to describe analytically, especially when only a short measurement period is available. As a result, directly quantifying and correcting the bias of the simple estimator becomes challenging using conventional physical modelling alone.

The approach presented in the associated article addresses this issue by combining the simplicity of the physical estimator with the pattern-learning capabilities of machine learning. The HLC estimation is therefore performed in two steps. First, the simple steady-state method is applied to obtain an initial estimate from the 12-hour measurement. Second, a machine-learning model is used to learn the systematic relationship between the initial estimate, the relevant building and weather characteristics, and the resulting estimation bias. This learned bias is then used to correct the initial estimate, bringing it closer to the reference HLC value.

This repository provides the metadata associated with the dataset used in this article.

The dataset comprises building simulation data and corresponding model results for eight building configurations, combining different building construction systems and insulation configurations.

The complete dataset contains (more details on the content and variables in `data_dictionary.csv` and `Manifest.csv`):

* 🏗️ detailed simulation variables;
* 🧱 building and envelope parameters;
* 🌦️ weather-related variables (🌡️temperature and solar radiation);
* 📐 calculated HLC and bias indicators;
* ⏱️ time-series variables;
* 🤖 model results and associated error metrics.

The dataset is intended to support:

* 🔬 reproducibility of the associated research;
* 📈 inspection and analysis of the simulated data;
* 🤖 development and evaluation of data-driven HLC estimation methods;
* 🏢 further research on building energy performance and heat-loss estimation.

**Note**: The dataset does not contain energy-related quantities such as heating demand, heating needs, or energy consumption. The simulation results are exclusively focused on the estimated Heat Loss Coefficient (HLC) of the building. Although hourly heating demand is used internally to derive the HLC, these intermediate heating-demand data are not retained in the publicly released dataset.

---

## 📄 2. Associated research

The dataset accompanies the research article:

> **Data-driven HLC estimation based upon a quick steady-state method**


* 📄 the **article** describes the methodology, analysis, and scientific findings;
* 💾 the **Zenodo dataset** provides the complete underlying public data;
* 💻 this **GitHub repository** provides documentation, metadata, representative samples, and example code.

The article DOI will be added here once the article has been formally published.

---

## 🏗️ 3. Building configurations

The dataset contains eight configurations.

| ID        | Building system | Insulation configuration | Description                               |
| --------- | --------------- | ------------------------ | ----------------------------------------- |
| `HC-EWI`  | Heavy concrete  | EWI                      | Heavy concrete, external wall insulation  |
| `HC-IWI`  | Heavy concrete  | IWI                      | Heavy concrete, internal wall insulation  |
| `HC-NINS` | Heavy concrete  | NINS                     | Heavy concrete, no insulation             |
| `CB-EWI`  | Concrete blocks | EWI                      | Concrete blocks, external wall insulation |
| `CB-IWI`  | Concrete blocks | IWI                      | Concrete blocks, internal wall insulation |
| `CB-NINS` | Concrete blocks | NINS                     | Concrete blocks, no insulation            |
| `LW-EWI`  | Lightweight     | EWI                      | Lightweight, external wall insulation     |
| `LW-IWI`  | Lightweight     | IWI                      | Lightweight, internal wall insulation     |

Where:

* **HC** = Heavy Concrete
* **CB** = Concrete Blocks
* **LW** = Lightweight
* **EWI** = External Wall Insulation
* **IWI** = Internal Wall Insulation
* **NINS** = No Insulation

These configuration identifiers are used consistently throughout the repository and the Zenodo dataset.

Each configuration contains two principal data files:

| 📄 File             | Description                                   |
| ------------------- | --------------------------------------------- |
| `Data.parquet`      | Full simulation dataset for the configuration |
| `model_results.csv` | HLC/bias results associated with the models MLP; RF; and STM (presented in the article) |

---

## 🗂️ 4. Repository contents


```text
hlc-bias-model-dataset/
│
├── 📁 data/
│   └── 📁 sample/
│       ├── 📁 CB-EWI/
│       │   ├── Data_sample.txt
│       │   └── model_results_sample.csv
│       ├── 📁 CB-IWI/
│       │   ├── Data_sample.txt
│       │   └── model_results_sample.csv
│       ├── 📁 CB-NINS/
│       │   ├── Data_sample.txt
│       │   └── model_results_sample.csv
│       ├── 📁 HC-EWI/
│       │   ├── Data_sample.txt
│       │   └── model_results_sample.csv
│       ├── 📁 HC-IWI/
│       │   ├── Data_sample.txt
│       │   └── model_results_sample.csv
│       ├── 📁 HC-NINS/
│       │   ├── Data_sample.txt
│       │   └── model_results_sample.csv
│       ├── 📁 LW-EWI/
│       │   ├── Data_sample.txt
│       │   └── model_results_sample.csv
│       └── 📁 LW-IWI/
│           ├── Data_sample.txt
│           └── model_results_sample.csv
│
├── 📁 examples/
│   └── 01_load_and_inspect.ipynb
│
├── 📁 metadata/
│   ├── data_dictionary.csv
│   └── manifest.csv
│
├── 📁 scripts/
│   └── validate_download.py
│
├── .gitignore
├── CHANGELOG.md
├── LICENSE
└── README.md
```

### 🧪 `data/sample/`

Contains small representative samples from each of the eight configurations.

The samples are provided so that users can inspect the data structure and experiment with the example workflow without downloading the complete dataset from Zenodo.

The sample files are **not intended to replace the complete dataset** and should not be used as a substitute for the full analysis.

### 📓 `examples/`

Contains example workflows demonstrating inspect the dataset.

The notebook:

```text
examples/01_load_and_inspect.ipynb
```

uses the sample data included in this repository and is designed to provide a straightforward introduction to the dataset structure.

### 📚 `metadata/`

Contains the documentation required to understand the dataset.

#### `data_dictionary.csv`

Provides descriptions of all the variables (fields) included in the dataset.

The data dictionary is intended for **documentation and interpretation**. It is not used as a conversion or data-processing schema.

#### `manifest.csv`

Provides the inventory of the complete public dataset, including file information and SHA-256 checksums.

### 🛠️ `scripts/`

#### `validate_download`

The validate_download script is provided to verify that the dataset has been downloaded and extracted correctly. It checks the downloaded files against the expected dataset structure and helps identify missing, corrupted, or incorrectly extracted files.

We recommend running this validation step before attempting to load or process the dataset. If the validation is successful, you can proceed with loading the data in Python.

---

## 📊 5. Data files

### 5.1 `Data.parquet`

The principal data file for each configuration is provided in **Apache Parquet** format.

Parquet was selected because it provides a compact, efficient, column-oriented representation suitable for large tabular datasets.

Each `Data.parquet` file contains **284 fields**

### 5.2 `model_results.csv`

Each configuration also contains a `model_results.csv` file containing model outputs and associated performance/error metrics.

The principal fields include:

* `HLC_true`
* `HLC_rf`
* `HLC_mlp`
* `Bias_rf`
* `Abs_Bias_rf`
* `Bias_mlp`
* `Abs_Bias_mlp`
* `Avg_Text_24`
* `Avg_Text_test`
* `STM_Bias`
* `STM_Abs_Bias`

This file remains in CSV format because it is relatively small and readily accessible with standard data-analysis tools.

---

## 🚀 6. Getting started

### Option 1: Explore the sample data

The easiest way to start is to clone or download this repository and open:

```text
examples/01_load_and_inspect.ipynb
```

The notebook works with the sample data contained in:

```text
data/sample/
```

No download of the complete dataset is required for this introductory workflow.

### Option 2: Use the complete dataset

For analyses requiring the complete simulation data, download the dataset from Zenodo:

1. Download the dataset
> 🔗 **https://doi.org/10.5281/zenodo.23223811**

2. Extract the contents of the downloaded archive into a directory of your choice.

3. After extraction, make sure that the resulting directory contains the expected dataset files and folder structure.

    ```text
    📁 YourDir/
    │       ├── 📁 CB-EWI/
    │       │   ├── Data_sample.txt
    │       │   └── model_results_sample.csv
    │       ├── 📁 CB-IWI/
    │       │   ├── Data_sample.txt
    │       │   └── model_results_sample.csv
    │       ├── 📁 CB-NINS/
    │       │   ├── Data_sample.txt
    │       │   └── model_results_sample.csv
                etc.
    ```

4. From the repository root, run:

    ```bash
    python -m scripts.validate_download /path/to/YourDir 
    ``` 
    Replace /path/to/YourDir with the path to the directory containing the extracted dataset. Note that if you only want to validate one configuration (e.g. CB-EWI), you can use the argument ```--config CB-EWI ```. For more arguments and flexibility, you can check the docstring in ```scripts/validate_download.py ```

    The script will check whether the downloaded dataset is complete and correctly structured. A successful validation indicates that the download and extraction were completed correctly.

5. Once validate_download completes successfully, you can proceed to load and work with the dataset in Python.

    **Important:** If the validation does not succeed, we recommend resolving the reported download or extraction issues before proceeding with data loading. This helps avoid errors caused by missing or incomplete files.

---

## 🐍 7. Loading the data with Python

Parquet files can be loaded using commonly available Python libraries such as `pandas` and `pyarrow`.

For example:

```python
import pandas as pd

data = pd.read_parquet("HC-EWI/Data.parquet")

print(data.shape)
print(data.head())
```

The model results can be loaded with:

```python
import pandas as pd

results = pd.read_csv("HC-EWI/model_results.csv")

print(results.shape)
print(results.head())
```

The example notebook provides a more complete introduction to inspecting the sample data.


---

## 🔄 8. Reproducibility

The repository and Zenodo archive have complementary roles.

### 💻 GitHub

Provides:

* 📚 documentation;
* 🧾 metadata;
* 📖 data dictionary;
* 🧪 representative samples;
* 📓 example notebook;
* 🛠️ dataset-management utilities;
* 📝 version history.

### 🗄️ Zenodo

Provides:

* 📦 the complete dataset;
* 🔒 persistent long-term archiving;
* 🔗 a citable DOI;
* ✅ the final public data files and their associated checksums.

---

## 🏷️ 9. Dataset version

The current public dataset release is:

**Version 1.0.0**

The Zenodo record provides the persistent archive for this release:

> 🔗 **DOI:** [10.5281/zenodo.23223811](https://doi.org/10.5281/zenodo.23223811)

Changes to the dataset will be documented in `CHANGELOG.md` and, where appropriate, released as subsequent dataset versions.

---

## 📖 10. Citation

If you use the complete dataset in a publication, presentation, or other research output, please cite the Zenodo dataset:

> **Akkari, S. (2026). *Synthetic Dataset for Short-Duration Building Heat Loss Coefficient Estimation*. Zenodo. https://doi.org/10.5281/zenodo.23223811**

The associated research article is:

> **Akkari, S., Pei, L., Schalbart, P., Challansonnex, A., & Peuportier, B. *Data-driven HLC estimation based upon a quick steady-state method*.**

The article DOI will be added to this repository and the Zenodo record once the article is published.

---

## 📜 11. License

The dataset is distributed under the:

**Creative Commons Attribution 4.0 International (CC BY 4.0)**

This license permits sharing and adaptation provided that appropriate credit is given to the creator.

Please refer to the `LICENSE` file in this repository and the Zenodo record for the applicable licensing information.

---

## 🙏 12. Acknowledgement

If you use this dataset, please acknowledge the dataset and cite both the Zenodo record and the associated research article when applicable.

For questions concerning the dataset, methodology, or reproducibility, please refer to the repository documentation and the associated publication.

For feedback or issues related to the dataset or this repository, please feel free to open an issue or reach out via email at samih.akkari.95@gmail.com

---
