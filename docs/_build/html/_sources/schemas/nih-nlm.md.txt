# NIH NLM CDE Schema

## Overview

The NIH NLM CDE schema represents Common Data Elements from the NIH and National Library of Medicine repositories. This schema covers COVID-19 related data elements.

## Schema Details

- **ID**: `https://example.org/schemas/nih_nlm_cde`
- **Name**: NIH_NLM_CDESchema
- **Version**: 1.0.0
- **Source**: NIH/NLM CDE Repository

## Structure

### Classes

The schema organizes CDEs into project-specific classes:

**Project 5 (COVID-19)**
- Contains COVID-19 related data elements
- Includes demographic, clinical, and outcome measures
- Covers complications, treatments, and mental health symptoms

### Example Data Elements

- Address and demographic information (City, State, Postal Code)
- Age and temporal data
- COVID-19 case classification and severity
- Complications and onset dates
- Mental health and psychosocial symptoms
- Medications and treatments
- Discharge disposition

### Ontology Bindings

The schema uses standard prefixes:

- **NCIT**: NCI Thesaurus for cancer-related terms
- **UMLS**: Unified Medical Language System
- **LinkML**: Core LinkML types

## Usage

```python
from linkml_runtime.utils.schemaview import SchemaView

schema = SchemaView("linkml/nih_nlm_schema.yaml")
classes = schema.all_classes()
for class_name in classes:
    print(f"Class: {class_name}")
```

## Files

- Schema definition: `linkml/nih_nlm_schema.yaml`
- Source data: `data/nlm/nlm-cdes.csv`
