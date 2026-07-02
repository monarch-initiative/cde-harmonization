# `cde2onto`: All-by-All Mappers

> **Status:** early stage. This README covers just the two mapper scripts
> below. A CLI wrapper and a full ontology-build README (covering the rest
> of `cde2onto`) will be added later.

These scripts inject OWL restrictions into an already-annotated CDE
ontology, linking each CDE variable to the PhenX Bundle protocols or OMOP
CDM columns it's semantically closest to. Matching is done via
[`CurateGPT`](https://github.com/monarch-initiative/curategpt)'s
`all-by-all` command against the `bundle_phenx` / `cdm_omop` ChromaDB
collections built by `cde2vec`.

| Script                    | Adds property   | Matches against  | ChromaDB collection |
|---------------------------|-----------------|-------------------|----------------------|
| `allxall_mapper_phenx.py` | `inBundleExact` / `inBundleClose` | PhenX protocols | `bundle_phenx` |
| `allxall_mapper_omop.py`  | `inCDMExact` / `inCDMClose`       | OMOP CDM columns | `cdm_omop`     |

### Thresholds

| Property        | Similarity                  | phenx mapper | omop mapper |
|------------------|------------------------------|--------------|-------------|
| `*Exact`         | `>=` EXACT_THRESHOLD          | 0.98         | 0.97        |
| `*Close`         | `>=` CLOSE_THRESHOLD, `<` EXACT | 0.90         | 0.85        |

Thresholds are constants at the top of each script — edit `EXACT_THRESHOLD` /
`CLOSE_THRESHOLD` directly if you need to tune them.

---

## Prerequisites

- An **annotated OWL file** to inject into (`cdes_values_ontology_annotated.owl`) — produced by an earlier, not-yet-documented step in `cde2onto`.
- A **populated ChromaDB** at `--chroma` containing:
  - the source collection(s) you're matching against (e.g. `cde_phenx`, `cde_nih`)
  - `bundle_phenx` and/or `cdm_omop`, built via `make embed-phenx-bundle` / `make embed-omop-cdm` (see the `cde2vec` README)
- The corresponding LinkML schema file:
  - `linkml/phenx_bundle_schema.yaml` for the PhenX mapper
  - `linkml/omop_cdm_schema.yaml` (or `data/cdm-omop/omop_5.4.xlsx`) for the OMOP mapper

---

## Usage

### PhenX Bundle mapper

```bash
python cde2onto/allxall_mapper_phenx.py \
    --owl    cde2onto/cdes_values_ontology_annotated.owl \
    --phenx  linkml/phenx_bundle_schema.yaml \
    --chroma db \
    --source cde_phenx \
    --out    cde2onto/cdes_values_ontology_annotated_phenx.owl
```

### OMOP CDM mapper

```bash
python cde2onto/allxall_mapper_omop.py \
    --owl    cde2onto/cdes_values_ontology_annotated_phenx.owl \
    --omop   linkml/omop_cdm_schema.yaml \
    --chroma db \
    --source cde_phenx \
    --out    cde2onto/cdes_values_ontology_annotated_phenx_omop.owl
```

### Chaining multiple sources

Both scripts are incremental — pass the previous run's `--out` back in as
the next run's `--owl`, and switch `--source` to the next collection
(`cde_nih`, `cde_heal`, etc.). The PhenX/OMOP hierarchy and object
properties are only appended once; re-runs detect them and skip.

```bash
python cde2onto/allxall_mapper_phenx.py --owl a.owl --phenx ... --source cde_phenx --out b.owl
python cde2onto/allxall_mapper_phenx.py --owl b.owl --phenx ... --source cde_nih   --out c.owl
python cde2onto/allxall_mapper_omop.py  --owl c.owl --omop  ... --source cde_phenx --out d.owl
```

---

## Options

| Flag                  | Applies to | Description                                                        |
|------------------------|------------|----------------------------------------------------------------------|
| `--owl`                | both       | Input annotated OWL file                                             |
| `--phenx`              | phenx      | Path to `phenx_bundle_schema.yaml`                                   |
| `--omop`               | omop       | Path to `omop_cdm_schema.yaml` or `omop_5.4.xlsx`                    |
| `--chroma`             | both       | ChromaDB directory (e.g. `db`)                                       |
| `--source`             | both       | Source collection to match against (e.g. `cde_phenx`, `cde_nih`)     |
| `--out`                | both       | Output OWL file                                                      |
| `--phenx-collection`   | phenx      | ChromaDB collection name for PhenX Bundle (default: `bundle_phenx`)  |
| `--omop-collection`    | omop       | ChromaDB collection name for OMOP CDM (default: `cdm_omop`)          |
| `--limit`              | both       | Max candidates per left item passed to `all-by-all -l` (default: 50) |
| `--ns-prefix`          | both       | XML namespace prefix added to the OWL header (default: `ex`)         |

---

## Output

Each run prints a summary of match counts and writes the modified OWL to
`--out`, e.g.:

```
── Summary ──────────────────────────────────────────────────────────────
  Input OWL      : cde2onto/cdes_values_ontology_annotated.owl
  PhenX schema   : linkml/phenx_bundle_schema.yaml
  ChromaDB       : db
  Reference      : bundle_phenx
  Source         : cde_phenx
  OWL crosswalk  : 48,291 classes
  Matched classes: 19,796
  inBundleExact  : 5,011 protocol links  (>= 0.98)
  inBundleClose  : 16,622 protocol links  (>= 0.9, < 0.98)
  Output         : cde2onto/cdes_values_ontology_annotated_phenx_test.owl  (93.1 MB)
─────────────────────────────────────────────────────────────────────────
```

---

## Coming later

- A CLI wrapper (`cde2onto` entry point) to replace the manual `python
  cde2onto/allxall_mapper_*.py` invocations
- A full README documenting the rest of the ontology-build pipeline
  (annotation step, other mappers, final ontology assembly)