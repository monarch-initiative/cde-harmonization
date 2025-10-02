# Collecting and Converting CDEs

This guide shows how to collect CDEs from major repositories and convert them into computable LinkML schemas.

## Overview

The CDE harmonization project integrates CDEs from multiple repositories:

- **NIH CDE Repository**: NIH/NLM Common Data Elements
- **PhenX Toolkit**: Phenotype and exposure assessment measures
- **caDSR**: NCI Cancer Data Standards Registry
- **RADx-UP**: COVID-19 underserved populations data elements
- **HEAL**: Pain and opioid research data elements

The `cde2linkml` tool converts these heterogeneous formats into unified LinkML schemas that capture:
- Identifiers and provenance
- Permissible values and datatypes
- Metadata and context
- Relationships to other CDEs

## Converting NIH/NLM CDEs

### Input Format

NIH/NLM CDEs are provided in CSV format with columns for:
- CDE name
- Description
- Data type
- Permissible values
- Ontology mappings

### Conversion Command

```bash
cde2linkml --nih-nlm \
  --input-folder data/nlm \
  --output-folder linkml
```

### Output

The command generates a LinkML schema with:
- Classes for each project or survey
- Slots for each data element
- Enumerations for categorical values
- Type definitions and constraints

## Converting PhenX CDEs

### Input Format

PhenX CDEs come from REDCap data dictionaries, which include:
- Variable names
- Field labels
- Field types
- Validation rules
- Branching logic

### Conversion Command

```bash
cde2linkml --phenx \
  --input-folder data/phenx-redcap \
  --output-folder linkml
```

### Special Considerations

PhenX conversions handle:
- REDCap-specific field types (radio, dropdown, checkbox)
- Branching logic translation
- Calculated fields
- Multiple choice questions

## Converting RADx-UP CDEs

### Input Format

RADx-UP uses CSV data dictionaries with:
- Variable names
- Descriptions
- Data types
- Value ranges

### Conversion Command

```bash
cde2linkml --radx-up \
  --input-folder data/radx-up \
  --output-folder linkml
```

## Customizing Conversions

### Adding Ontology Mappings

Edit the generated schema to add ontology mappings:

```yaml
slots:
  blood_pressure:
    description: Systolic blood pressure
    range: integer
    unit:
      ucum_code: mm[Hg]
    exact_mappings:
      - LOINC:8480-6
```

### Creating Enumerations

Define reusable value sets:

```yaml
enums:
  YesNoUnknown:
    permissible_values:
      Yes:
        meaning: NCIT:C49488
      No:
        meaning: NCIT:C49487
      Unknown:
        meaning: NCIT:C17998
```

## Validation

Validate the generated schema:

```bash
linkml-validate linkml/nih_nlm_schema.yaml
```

## Next Steps

See the [Project Roadmap](../roadmap.md) for planned features including AI-assisted mapping, human curation workflows, and data harmonization.
