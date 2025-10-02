# CDE Harmonization Documentation

This directory contains the Sphinx documentation for the CDE Harmonization project.

## Building the Documentation

### Prerequisites

Install documentation dependencies:

```bash
pip install sphinx myst-parser sphinx-design furo
```

### Build HTML Documentation

```bash
cd docs
make html
```

The built documentation will be in `_build/html/`. Open `_build/html/index.html` in a browser.

### Clean Build

```bash
make clean
make html
```

## Documentation Structure

- `intro/` - Overview and installation guides
- `schemas/` - LinkML schema documentation
- `howtos/` - Practical how-to guides
- `_static/` - Static assets (CSS, images)
- `_templates/` - Sphinx templates

## Contributing

When adding new documentation:

1. Use Markdown (`.md`) or reStructuredText (`.rst`)
2. Update the appropriate `index.rst` toctree
3. Build locally to check for errors
4. Follow existing style and formatting

## Publishing

Documentation is published via GitHub Pages or Read the Docs (to be configured).
