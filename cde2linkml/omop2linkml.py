"""
cde2linkml/omop2linkml.py
=========================
Convert omop_{version}.xlsx into a LinkML YAML schema for the cdm_omop
ChromaDB collection.

Parallel to bundle_phenx2linkml.py — reads the "Columns (CDEs)" sheet
produced by omop_scraper.py and emits one LinkML slot per column, with
the full CDM hierarchy encoded as separate annotations.

Each xlsx column becomes one LinkML slot:

    slot name   : {table_name}__{column_name}   e.g. person__birth_datetime
    description : Column Description             ← CURATE embeds this
    annotations :
        source               : OMOP_CDM
        source_variable_id   : OMOPColumn_PERSON__birth_datetime
        cdm_version          : 5.4
        column_name          : birth_datetime
        datatype             : datetime
        is_required          : No
        is_primary_key       : No
        is_foreign_key       : No
        fk_table             : (empty)
        fk_domain            : (empty)
        table_name           : PERSON
        table_group          : Clinical_Data_Tables
        schema               : CDM
        table_url            : https://ohdsi.github.io/CommonDataModel/cdm54.html#person
        table_description    : This table serves as the central identity …

Full hierarchy (parallel to PhenX):
    TableGroup  ↔  Collection
    Table       ↔  SubCollection / Protocol
    Column      ↔  Variable (CDE)
"""

import os
import re
import yaml
import pandas as pd


def _to_snake(text: str) -> str:
    text = str(text).strip()
    text = re.sub(r'[\s\-\.]+', '_', text)
    text = re.sub(r'[^a-zA-Z0-9_]', '', text)
    text = re.sub(r'_+', '_', text).strip('_')
    return text.lower()


class _Dumper(yaml.SafeDumper):
    def represent_str(self, data: str):
        return self.represent_scalar('tag:yaml.org,2002:str', data)

_Dumper.add_representer(str, _Dumper.represent_str)


def _s(v) -> str:
    """Safe string — handles NaN, None, trailing .0 on numeric IDs."""
    if v is None or (isinstance(v, float) and v != v):
        return ""
    sv = str(v).strip()
    if sv.endswith(".0") and sv[:-2].lstrip("-").isdigit():
        sv = sv[:-2]
    return sv


def process_omop_bundle(input_file: str, output_file: str) -> None:
    """
    Read omop_{version}.xlsx (produced by omop_scraper.py) and write a
    LinkML YAML schema to output_file.

    All column headers are read dynamically from the sheet — no positions
    or names hardcoded. Slot names follow the pattern {table}__{column}
    (lower-snake-case) matching how phenx uses {protocol_id}_{var_name}.
    """
    # ── Columns sheet (one row = one CDE) ────────────────────────────────────
    df = pd.read_excel(input_file, sheet_name="Columns (CDEs)", header=1)
    df.columns = df.columns.str.strip()

    # ── Tables sheet — for hierarchy fields not duplicated in Columns sheet ──
    df_t = pd.read_excel(input_file, sheet_name="Tables", header=1)
    df_t.columns = df_t.columns.str.strip()

    # table_name → full row dict (all headers dynamic)
    table_lookup: dict = {}
    for _, row in df_t.iterrows():
        tname = _s(row.get("Table Name", "")).upper()
        if tname:
            table_lookup[tname] = {k: _s(row.get(k, "")) for k in df_t.columns}

    df = df[df["Column Name"].notna()].reset_index(drop=True)

    # Resolve CDM version from README sheet
    cdm_version = "unknown"
    try:
        df_readme = pd.read_excel(input_file, sheet_name="README", header=None)
        for _, row in df_readme.iterrows():
            if str(row.iloc[0]).strip().lower() == "cdm version":
                m = re.search(r'(\d+\.\d+)', str(row.iloc[1]))
                if m:
                    cdm_version = m.group(1)
                break
    except Exception:
        pass
    if cdm_version == "unknown" and "CDM Version" in df.columns:
        vals = df["CDM Version"].dropna().unique()
        if len(vals):
            cdm_version = _s(vals[0])

    ver_slug = cdm_version.replace(".", "")
    schema = {
        "id":            f"https://example.org/schemas/omop_cdm_{ver_slug}_bundle",
        "name":          "OMOPCDMBundleSchema",
        "description": (
            f"LinkML schema for OMOP CDM v{cdm_version} columns. "
            "Generated from omop_{version}.xlsx by omop2linkml.py. "
            "Hierarchy: TableGroup → Table → Column "
            "(parallel to PhenX: Collection → SubCollection → Protocol → Variable)."
        ),
        "version":       f"{cdm_version}.0",
        "default_range": "string",
        "license":       "https://www.apache.org/licenses/LICENSE-2.0",
        "imports":       ["linkml:types"],
        "prefixes": {
            "linkml": "https://w3id.org/linkml/",
            "omop":   "https://ohdsi.github.io/CommonDataModel/",
        },
        "default_prefix": "omop",
        "slots": {},
    }

    seen:    set = set()
    skipped: int = 0

    for _, row in df.iterrows():
        col_id   = _s(row.get("Column ID (CDE ID)", ""))
        col_name = _s(row.get("Column Name",         ""))
        col_desc = _s(row.get("Column Description",  ""))
        tname    = _s(row.get("Table Name",          "")).upper()

        if not col_name or not tname:
            skipped += 1
            continue

        # Slot name: {table_lower}__{column_lower}  e.g. person__birth_datetime
        # Mirrors PhenX pattern where slot key is snake_case of the variable name
        slot_key = f"{_to_snake(tname)}__{_to_snake(col_name)}"
        if not slot_key or slot_key in seen:
            skipped += 0 if slot_key in seen else 1
            continue
        seen.add(slot_key)

        description = col_desc or col_name

        # ── Annotations: one key per hierarchy level ──────────────────────────
        # Mirrors phenx which has separate keys for protocol_id, protocol_name,
        # domain_id, domain_name, sub_collection_id, collection_id, etc.
        annotations: dict = {"source": "OMOP_CDM"}

        # Column-level fields (from Columns sheet)
        col_fields = {
            "Column ID (CDE ID)": "source_variable_id",
            "CDM Version":        "cdm_version",
            "Column Name":        "column_name",
            "Datatype":           "datatype",
            "Is Required":        "is_required",
            "Is Primary Key":     "is_primary_key",
            "Is Foreign Key":     "is_foreign_key",
            "FK Table":           "fk_table",
            "FK Field":           "fk_field",
            "FK Domain":          "fk_domain",
            "FK Class":           "fk_class",
        }
        for sheet_col, annot_key in col_fields.items():
            v = _s(row.get(sheet_col, ""))
            if v:
                annotations[annot_key] = v

        # Table-level fields — prefer Columns sheet, fall back to Tables sheet
        tbl_fields = {
            "Table Name":        "table_name",
            "Table Group":       "table_group",
            "Schema":            "schema",
            "Table URL":         "table_url",
        }
        for sheet_col, annot_key in tbl_fields.items():
            v = _s(row.get(sheet_col, ""))
            if not v and tname in table_lookup:
                v = _s(table_lookup[tname].get(sheet_col, ""))
            if v:
                annotations[annot_key] = v

        # Table description (truncated — long text, not needed for embedding)
        td = _s(row.get("Table Description", ""))
        if not td and tname in table_lookup:
            td = _s(table_lookup[tname].get("Table Description", ""))
        if td:
            annotations["table_description"] = td[:300]

        schema["slots"][slot_key] = {
            "description": description,
            "annotations": annotations,
        }

    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)

    raw = yaml.dump(schema, Dumper=_Dumper, sort_keys=False,
                    default_flow_style=False, allow_unicode=True)
    raw = raw.replace(": null\n", ":\n")

    with open(output_file, "w", encoding="utf-8") as fh:
        fh.write(raw)

    print(f"OMOP CDM LinkML schema saved → {output_file} "
          f"({len(schema['slots']):,} slots, {skipped} skipped, CDM v{cdm_version})")