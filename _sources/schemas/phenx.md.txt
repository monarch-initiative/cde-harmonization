# PhenX CDE Schema

## Overview

The PhenX CDE schema represents Common Data Elements from the PhenX Toolkit, which provides standard measures for phenotype and exposure assessment in genomic research.

## Schema Details

- **ID**: `https://example.org/schemas/phenx_cde`
- **Name**: PhenX_CDESchema
- **Version**: 1.0.0
- **Source**: PhenX Toolkit

## Structure

### Classes

The schema organizes PhenX measures into classes based on assessment instruments. Classes are typically named after the data dictionary version (e.g., `DD_120902_finalized`).

### Example Measures

The schema includes measures such as:

- Social preference assessments
- Imagination and creativity indicators
- Sensory sensitivity measures
- Social interaction patterns
- Communication styles
- Behavioral preferences
- Interest patterns

### Data Elements

Example data elements include:
- Preference for doing things with others
- Ability to imagine story characters
- Notice of small sounds or details
- Social situation comfort
- Conversation abilities
- Fascination with patterns, dates, or numbers

## Usage

```python
from linkml_runtime.utils.schemaview import SchemaView

schema = SchemaView("linkml/phenx_schema.yaml")
slots = schema.all_slots()
for slot_name in list(slots.keys())[:10]:
    print(f"Slot: {slot_name}")
```

## Files

- Schema definition: `linkml/phenx_schema.yaml`
- Source data: `data/phenx-redcap/` (REDCap format)
