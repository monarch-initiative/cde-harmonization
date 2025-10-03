# CDE Harmonization

This project makes Common Data Elements (CDEs) more interoperable across clinical research studies using LinkML schemas and AI-assisted semantic mapping.

## What We're Doing

Clinical research uses CDEs—standardized data fields with defined permissible values—but they're fragmented across repositories and lack semantic bindings to ontologies. This limits data integration and AI-readiness.

We're building tools to:
- **Collect CDEs** from major repositories (NIH, PhenX, caDSR, RADx, HEAL)
- **Convert to LinkML schemas** for computability
- **Generate semantic mappings** using AI and human curation
- **Enable data harmonization** across studies

## Quick Start

```bash
# Install
pip install -e .

# Convert CDEs to LinkML
cde2linkml --nih-nlm --input-folder data/nlm --output-folder linkml
```

## Documentation

**📖 Full documentation:** https://monarch-initiative.github.io/cde-harmonization/

- [Installation Guide](https://monarch-initiative.github.io/cde-harmonization/intro/installation.html)
- [Schema Documentation](https://monarch-initiative.github.io/cde-harmonization/schemas/index.html)
- [Project Roadmap](https://monarch-initiative.github.io/cde-harmonization/roadmap.html)

## Repository Contents

- `data/` - Raw CDEs from multiple repositories
- `linkml/` - Generated LinkML schemas
- `cde2linkml/` - Conversion tools
- `docs/` - Documentation source

Large files are in the [Monarch Google Cloud bucket](https://console.cloud.google.com/storage/browser/cde-harmonization).

## Technologies

- **[LinkML](https://linkml.io)** - Schema modeling framework
- **[SSSOM](https://github.com/mapping-commons/sssom)** - Mapping standard
- **Ontologies** - LOINC, HPO, Mondo, NCIT, OBA

## License

[Specify license]

## Citation

[Add citation information]
