# Installation

## Prerequisites

- Python 3.9 or higher
- Poetry (recommended) or pip

## Installing from Source

Clone the repository:

```bash
git clone https://github.com/monarch-initiative/cde-harmonization.git
cd cde-harmonization
```

### Using Poetry (Recommended)

```bash
poetry install
poetry shell
```

This installs all dependencies and makes the `cde2linkml` command available in the poetry environment.

### Using pip

```bash
pip install -e .
```

This installs the package in editable mode and creates the `cde2linkml` command.

## Verifying Installation

Test the installation by running:

```bash
cde2linkml --help
```

You should see the command-line interface help message with options for `--radx-up`, `--nih-nlm`, and `--phenx`.

## Dependencies

The project requires:

- **LinkML**: Schema modeling framework
- **SSSOM**: For mapping representations
- **Python packages**: See `pyproject.toml` for full list

## Data Access

Large data files are stored in the Monarch Google Cloud bucket. To access:

```bash
# Instructions for accessing cloud storage will be added
```

## Development Installation

For development work, install with dev dependencies:

```bash
poetry install --with dev
```

This includes:

- Testing frameworks (pytest)
- Code formatting tools (black, ruff)
- Documentation tools (sphinx)

## Next Steps

- Read the [Overview](overview.md) to understand the project
- Explore [Schema Documentation](../schemas/index.rst)
- Check out [How-To Guides](../howtos/index.rst)
