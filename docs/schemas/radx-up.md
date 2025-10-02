# RADx-UP CDE Schema

## Overview

The RADx-UP (Rapid Acceleration of Diagnostics - Underserved Populations) CDE schema represents data elements used in COVID-19 testing and outcomes research focused on underserved populations.

## Schema Details

- **ID**: `https://example.org/schemas/radx_up_cde`
- **Name**: RADx_UP_CDESchema
- **Version**: 1.0.0
- **Source**: RADx-UP Initiative

## Structure

The RADx-UP schema includes data elements for:

- COVID-19 testing protocols
- Demographics and social determinants of health
- Clinical outcomes
- Community engagement measures
- Health equity indicators

## Data Dictionary

The schema is based on the RADx-UP Phase 3 Tier 1 and Tier 2 data dictionary.

## Usage

```python
from linkml_runtime.utils.schemaview import SchemaView

schema = SchemaView("linkml/radx_up_schema.yaml")
classes = schema.all_classes()
print(f"Schema contains {len(classes)} classes")
```

## Files

- Schema definition: `linkml/radx_up_schema.yaml`
- Source data: `data/radx-up/RADxUP_1.7_Phase3_Tier1_Tier2_DataDictionary-1.csv`
