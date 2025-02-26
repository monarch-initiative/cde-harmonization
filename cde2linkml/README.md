# CDE Harmonization (cde2linkml)

This package is designed to standardize Common Data Elements (CDEs) into the [LinkML](https://linkml.io/) format. It supports multiple domains, including **RADx-UP, PhenX, and NIMH**, facilitating data interoperability and harmonization.

## Features

- Converts RADx-UP, NLM, and PhenX CDE data into **LinkML-compatible schemas**.
- Provides a command-line interface (**CLI**) for easy data transformation.
- Includes automated **data download** scripts for CDE sources.

---

## Installation

To install it locally for development:

### 1. Clone the repository:

```bash
git clone https://github.com/yourusername/cde-harmonization.git
cd cde-harmonization
```

### 2. Create and activate a virtual environment (Recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows
```

### 3. Install the package:

```bash
pip install -e .
```

### 4. Install dependencies (if applicable):

```bash
pip install -r requirements.txt
```

To deactivate the virtual environment when done:

```bash
deactivate
```

---

## Data Download

The package provides **Makefile** commands to fetch data from different sources.

### Download CDE Data:

```bash
make download-all
```

### Download Specific CDE Data:

- **RADx-UP:**
  ```bash
  make download-radx-up-cde
  ```
- **NLM CDE:**
  ```bash
  make download-nlm-cde
  ```
- **PhenX CDE:**
  ```bash
  make download-phenx-cde
  ```

### Cleanup Downloaded Data:

```bash
make clean-all
```

To clean specific datasets:

```bash
make clean-radx-up-cde
make clean-nlm-cde
make clean-phenx-cde
```

---

## Usage

The package provides a **command-line interface (CLI)** for processing CDE data into LinkML. By default, it uses data from the downloaded folders.

### CLI Commands:

```bash
cde2linkml <command> [options]
```

#### Commands:

| Command     | Description                                 |
| ----------- | ------------------------------------------- |
| `--radx-up` | Converts RADx-UP CDE data to LinkML format. |
| `--phenx`   | Converts PhenX CDE data to LinkML format.   |
| `--nlm`     | Converts NLM CDE data to LinkML format.     |

#### Example:

Convert RADx-UP CDE data:

```bash
cde2linkml --radx-up
```

#### Available Options:

| Option     | Description                                                                                             |
| ---------- |---------------------------------------------------------------------------------------------------------|
| `--input`  | (Optional) Path to the input file (CSV). Defaults to downloaded folders.                                |
| `--output` | (Optional) Path to the output directory where the LinkML file will be saved. Defaults to linkml folder. |

To see the help menu:

```bash
cde2linkml -h
```






