# CDE Harmonization (cde2linkml)

This package standardizes Common Data Elements (CDEs) into the [LinkML](https://linkml.io/) format. It supports multiple sources — **RADx-UP, NLM, PhenX, and NIH HEAL** — facilitating data interoperability and harmonization across pain and opioid research studies.

## Features

- Converts RADx-UP, NLM, PhenX, HEAL, and NHLBI CONNECTS CDE data into **LinkML-compatible schemas**.
- Provides a command-line interface (**CLI**) for easy data transformation.
- Includes automated **data download** scripts via `make` commands for all CDE sources.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/cde-harmonization.git
cd cde-harmonization
```

### 2. Create and activate a virtual environment (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows
```

### 3. Install the package

```bash
pip install -e .
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

> `openpyxl` is required for reading HEAL `.xlsx` files and is included in `requirements.txt`.

To deactivate the virtual environment when done:

```bash
deactivate
```

---

## Data Download

Makefile commands fetch data from all supported sources into their respective directories under `data/`.

| Directory            | Source          |
|----------------------|-----------------|
| `data/cde-radx-up`  | RADx-UP         |
| `data/cde-nlm`      | NIH NLM         |
| `data/cde-phenx`    | PhenX           |
| `data/cde-heal`     | NIH HEAL        |
| `data/cde-connects` | NHLBI CONNECTS  |

### Download all sources

```bash
make download-all
```

### Download a specific source

```bash
make download-radx-up-cde   # RADx-UP
make download-nlm-cde        # NIH NLM
make download-phenx-cde      # PhenX
make download-heal-cde       # NIH HEAL (scrapes all 14 pages of the HEAL CDE Repository)
make download-connects-cde   # NHLBI CONNECTS (single Excel file, multiple tabs)
```

### Clean downloaded data

```bash
make clean-all               # remove all
make clean-radx-up-cde
make clean-nlm-cde
make clean-phenx-cde
make clean-heal-cde
make clean-connects-cde
```

---

## Usage

After downloading the data, use the CLI to convert any source into a LinkML YAML schema. Schemas are written to the `linkml/` output folder by default.

```bash
cde2linkml [--radx-up] [--nih-nlm] [--phenx] [--heal] [options]
```

### Commands

| Flag          | Description                                           | Output file                    |
|---------------|-------------------------------------------------------|--------------------------------|
| `--radx-up`   | Convert RADx-UP CDE data to LinkML                    | `linkml/radx_up_schema.yaml`   |
| `--nih-nlm`   | Convert NIH NLM CDE data to LinkML                    | `linkml/nih_nlm_schema.yaml`   |
| `--phenx`     | Convert PhenX CDE data to LinkML                      | `linkml/phenx_schema.yaml`     |
| `--heal`      | Convert NIH HEAL CDE `.xlsx` files to LinkML          | `linkml/heal_schema.yaml`      |
| `--connects`  | Convert NHLBI CONNECTS CDE Excel tabs to LinkML       | `linkml/connects_schema.yaml`  |

Multiple flags can be combined in a single run:

```bash
cde2linkml --radx-up --phenx --heal
```

### Options

| Option            | Description                                                              |
|-------------------|--------------------------------------------------------------------------|
| `--input-folder`  | Path to input data folder. Overrides the default `data/cde-<source>` path. |
| `--output-folder` | Path to output directory for LinkML YAML files. Defaults to `linkml/`.  |

### Examples

Convert HEAL CDEs using default paths:

```bash
cde2linkml --heal
```

Convert all sources at once:

```bash
cde2linkml --radx-up --nih-nlm --phenx --heal --connects
```

Use a custom input and output directory:

```bash
cde2linkml --heal --input-folder /path/to/xlsx --output-folder /path/to/output
```

Show help:

```bash
cde2linkml -h
```


