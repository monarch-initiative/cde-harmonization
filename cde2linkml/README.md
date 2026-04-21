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
### LinkML Naming Conventions

| Element               | Convention                           | Example                              |
|-----------------------|--------------------------------------|--------------------------------------|
| Classes               | `PascalCase`                         | `Phq4`, `PromisGlobalHealth`         |
| Slots                 | `snake_case`                         | `pain_intensity`, `phq4_item1`       |
| Enums                 | `PascalCase` + `Enum` suffix         | `FrequencyRatingEnum`                |
| Permissible values    | Human-readable text (spaces allowed) | `Never true`, `Always true`          |

### CDE Repositories — Source Column Mapping

| LinkML Fields    | HEAL                                       | CONNECTS                                                                           | NIH NLM                                                     | RADx-UP                                | PhenX                         |
|------------------|--------------------------------------------|------------------------------------------------------------------------------------|-------------------------------------------------------------|----------------------------------------|-------------------------------|
| `class.name`     | Filename minus `-cde`                      | Tab name                                                                           | `steward`                                                   | `Form Name`                            | Filename minus extension      |
| `slot.key`       | `Variable Name`                            | `Element`                                                                          | `designations[0].designation`                               | `Variable / Field Name`                | `VARNAME`                     |
| `slot.title`     | `CDE Name`                                 | `Variable Label`                                                                   | `designations[0].designation`                               | `Variable / Field Name` (human-readable) | —                             |
| `slot.description` | `Definition`                               | `Question`                                                                         | `definitions[0].definition`                                 | `Field Label`                          | `VARDESC`                     |
| `slot.range`     | `Data Type`                                | `Variable Type`                                                                    | `valueDomain.datatype`                                      | `Text Validation Type OR Show Slider Number` | `TYPE`                        |
| `slot.minimum_value` | —                                          | —                                                                                  | —                                                           | `Text Validation Min`                  | `MIN`                         |
| `slot.maximum_value` | —                                          | —                                                                                  | —                                                           | `Text Validation Max`                  | `MAX`                         |
| `slot_uri`       | —                                          | —                                                                                  | `tinyId`                                                    | —                                      | —                             |
| `slot.annotations` | `Additional Notes (Question Text)`         | `Variable`, `Variable Label`, `Implementation Notes`                               | `designations[*]` tag `Preferred Question Text`, `registrationState.registrationStatus`, `registrationState.administrativeStatus`, `copyrightStatus`, `nihEndorsed`, `properties[Tags/Keywords]`, `stewardOrg.name`, `sources[*].sourceName`, `classification[*].elements[*].name`, `partOfBundles`, `created` | — | `VARIABLE_SOURCE`, `SOURCE_VARIABLE_ID`, `COMMENT1` |
| `enum.permissible_values` | `PV Description` (`;`-separated, `1 = Label; 2 = Label`) | `Response Options / Derivation` (`\|`-separated, auto-detected regardless of `Variable Type`) | `valueDomain.permissibleValues` (with `meaning` from `conceptSource`) | `Choices, Calculations, OR Slider Labels` (`\|`-separated, `1, Label` format) | `VALUES` + columns to right (`\|`-separated) |
| **Not mapped**   | `CRF Question #`, `Short Description`, `Permissible Values`, `Disease Specific Instructions`, `Disease Specific References`, `Population`, `Classification`, `CRF Name`, `External Id CDISC`, `Notes` | `IP`, `OP`, `D`, `N`, `Length`, `BDC ID`, `CDISC Mapping` | `createdBy`, `dataElementConcept`, `objectClass`, `ids`, `attachments`, `history`, `views`, `referenceDocuments`, `dataSets`, `derivationRules`, `changeNote`, `archived`, `cdeTinyIds` | `Section Header`, `Field Type`, `Field Note`, `Identifier`, `Branching Logic`, `Required Field`, `Custom Alignment`, `Question Number`, `Matrix Group Name`, `Matrix Ranking`, `Field Annotation` | `DOCFILE`, `UNITS`, `RESOLUTION`, `COMMENT2`, `VARIABLE_MAPPING`, `UNIQUEKEY`, `COLLINTERVAL`, `ORDER` |

### CDE Repositories — Schema Statistics

| Source   | Classes | Slots  | Enums | Data Downloaded | Schema Generated |
|----------|---------|--------|-------|-----------------|------------------|
| NIH NLM  | 19      | 22,215 | 3,432 | 03-27-2026      | 03-27-2026       |
| PhenX    | 848     | 30,659 | 2,362 | 03-27-2026      | 03-27-2026       |
| HEAL     | 264     | 5,224  | 386   | 03-27-2026      | 03-27-2026       |
| CONNECTS | 16      | 356    | 52    | 03-27-2026      | 03-27-2026       |
| RADx-UP  | 30      | 1,097  | 150   | 2025            | 2025                |
| **Total**| **1,177** | **59,551** | **6,382** |                 |                  |

### NIDDK Data Dictionaries — Source Column Mapping

|                           | CureGN                                              | KPMP                                                                              | NEPTUNE                                                        | CRIC                                                                                      |
|---------------------------|-----------------------------------------------------|-----------------------------------------------------------------------------------|----------------------------------------------------------------|-------------------------------------------------------------------------------------------|
| Class name                | `DatasetName` (PascalCase)                          | `Form Name` (PascalCase)                                                          | Tab name (PascalCase)                                          | `DATASET` (PascalCase)                                                                    |
| Slot key (`snake_case`)   | `VarName`                                           | `Variable / Field Name`                                                           | `Variable`                                                     | `Variable_Name`                                                                           |
| `slot.title`              | —                                                   | `Variable / Field Name` (human-readable)                                          | —                                                              | —                                                                                         |
| `slot.description`        | `LABEL`                                             | `Field Label`                                                                     | `Label`                                                        | `Variable_Short_Label`                                                                    |
| `slot.range`              | `VarType` (`NUM` → `integer`)                       | `Text Validation Type OR Show Slider Number`                                      | `Type` (`1` → `integer`, `2` → `string`)                      | `Type` (`CONTINUOUS` → `float`, `INTEGER`/`count` → `integer`, else `string`)            |
| `slot.minimum_value`      | —                                                   | `Text Validation Min`                                                             | —                                                              | —                                                                                         |
| `slot.maximum_value`      | —                                                   | `Text Validation Max`                                                             | —                                                              | —                                                                                         |
| `slot.annotations`        | `source`                                            | `source`                                                                          | `Length`, `Format Length`, `sas_format`, `source`              | `PDF_FILE`, `source`                                                                      |
| `enum.permissible_values` | `AnswerChoices` (`\|`-separated, `1: Label` format) | `Choices, Calculations, OR Slider Labels` (`\|`-separated, `1, Label` format)    | `Format` name → stub enum                                      | `PDF_FILE` name → stub enum (e.g. `AI_CRIC.PDF` → `AiCricEnum`); fallback: `Type` (`BINARY`, `CATEGORICAL`) → `BinaryEnum`, `CategoricalEnum` |
| **Not mapped**            | `VarLength`, `VARNUM`, `FmtName`                    | `Section Header`, `Field Type`, `Field Note`, `Identifier`, `Branching Logic`, `Required Field`, `Custom Alignment`, `Question Number`, `Matrix Group Name`, `Matrix Ranking`, `Field Annotation` | `Num`, `Informat` | `Source_Tables`                                                   |

---

### NIDDK Data Dictionaries — Schema Statistics

| Source   | Classes | Slots      | Enums         | Data Downloaded | Schema Generated |
|----------|---------|------------|---------------|-----------------|------------------|
| CureGN   | 49      | 2,242      | 183           | —               | 04-07-2026       |
| KPMP     | 62      | 5,094      | 358           | —               | 04-07-2026       |
| NEPTUNE  | 34      | 1,906      | 150 (stubs)   | —               | 04-07-2026       |
| CRIC     | 11      | 1,191      | 879 (stubs)   | —               | 04-07-2026       |
| **Total**| **156** | **10,433** | **1,570**     |                 |                  |