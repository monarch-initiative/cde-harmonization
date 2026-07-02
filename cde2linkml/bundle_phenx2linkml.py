"""
cde2linkml/bundle_phenx2linkml.py
==================================
Convert phenx_2026.xlsx into a LinkML YAML schema for the bundle_phenx
ChromaDB collection.

Each xlsx variable becomes one LinkML slot:
    slot name   : snake_case of Variable Name
    description : Variable Description  ← CURATE embeds this
    annotations :
        source               : PhenX
        source_variable_id   : PX570101080100
        protocol_id          : 570101
        protocol_name        : Body Mass Index
        domain_id            : 230000
        domain_name          : Obesity
        sub_collection_id    : 33
        sub_collection_name  : Behaviors and Risks
        collection_id        : 8
        collection_name      : COVID-19 Research Collection

Full hierarchy supported:
    Bundles → bundle_phenx → Collection → SubCollection → Domain → Protocol
"""

import os
import re
import yaml
import pandas as pd


def _to_snake_case(text: str) -> str:
    text = str(text).strip()
    text = re.sub(r'[\s\-\.]+', '_', text)
    text = re.sub(r'[^a-zA-Z0-9_]', '', text)
    text = re.sub(r'_+', '_', text).strip('_')
    return text.lower()


class _Dumper(yaml.SafeDumper):
    def represent_str(self, data: str):
        return self.represent_scalar('tag:yaml.org,2002:str', data)

_Dumper.add_representer(str, _Dumper.represent_str)


def s(v) -> str:
    return "" if (v is None or (isinstance(v, float) and v != v)) \
           else str(v).strip().rstrip('.0') if str(v).endswith('.0') else str(v).strip()


def process_phenx_bundle(input_file: str, output_file: str) -> None:
    """
    Read phenx_2026.xlsx and write a LinkML YAML schema to output_file.
    """
    df = pd.read_excel(input_file, sheet_name="Variables (CDEs)", header=1)
    df.columns = df.columns.str.strip()

    # Also load Protocols sheet for IDs not in Variables sheet
    df_p = pd.read_excel(input_file, sheet_name="Protocols", header=1)
    df_p.columns = df_p.columns.str.strip()

    # Build protocol_id → full hierarchy IDs lookup from Protocols sheet
    proto_lookup = {}
    for _, row in df_p.iterrows():
        pid = s(row.get("Protocol ID", ""))
        if pid:
            proto_lookup[pid] = {
                "domain_id":           s(row.get("Domain ID",           "")),
                "domain_name":         s(row.get("Domain Name",         "")),
                "sub_collection_id":   s(row.get("Sub-collection ID",   "")),
                "sub_collection_name": s(row.get("Sub-collection Name", "")),
                "collection_id":       s(row.get("Collection ID",       "")),
                "collection_name":     s(row.get("Collection Name",     "")),
                "protocol_name":       s(row.get("Protocol Name",       "")),
                "protocol_url":        s(row.get("Protocol URL",        "")),
            }

    df = df[df["Variable Name"].notna()].reset_index(drop=True)

    schema = {
        "id":             "https://example.org/schemas/phenx_bundle",
        "name":           "PhenXBundleSchema",
        "description": (
            "LinkML schema for PhenX bundle variables. "
            "Generated from phenx_2026.xlsx by bundle_phenx2linkml.py. "
            "Supports full hierarchy: "
            "Bundles → bundle_phenx → Collection → SubCollection → Domain → Protocol."
        ),
        "version":        "1.0.0",
        "default_range":  "string",
        "license":        "https://creativecommons.org/publicdomain/zero/1.0/",
        "imports":        ["linkml:types"],
        "prefixes": {
            "linkml": "https://w3id.org/linkml/",
            "phenx":  "https://www.phenxtoolkit.org/",
        },
        "default_prefix": "phenx",
        "slots": {},
    }

    seen: set = set()
    skipped = 0

    for _, row in df.iterrows():
        def g(col):
            v = row.get(col, "")
            return "" if (v is None or (isinstance(v, float) and v != v)) \
                   else str(v).strip()

        var_name = g("Variable Name")
        var_desc = g("Variable Description")
        var_id   = g("Variable ID (CDE ID)")
        proto_id = g("Protocol ID")

        if not var_name:
            skipped += 1
            continue

        slot_key = _to_snake_case(var_name)
        if not slot_key or slot_key in seen:
            skipped += (1 if not slot_key else 0)
            continue
        seen.add(slot_key)

        description = var_desc or var_name

        # Get full hierarchy from protocol lookup
        ph = proto_lookup.get(proto_id, {})

        annotations = {"source": "PhenX"}
        if var_id:                          annotations["source_variable_id"]   = var_id
        if proto_id:                        annotations["protocol_id"]           = proto_id
        if ph.get("protocol_name"):         annotations["protocol_name"]         = ph["protocol_name"]
        if ph.get("protocol_url"):          annotations["protocol_url"]          = ph["protocol_url"]
        if ph.get("domain_id"):             annotations["domain_id"]             = ph["domain_id"]
        if ph.get("domain_name"):           annotations["domain_name"]           = ph["domain_name"]
        if ph.get("sub_collection_id"):     annotations["sub_collection_id"]     = ph["sub_collection_id"]
        if ph.get("sub_collection_name"):   annotations["sub_collection_name"]   = ph["sub_collection_name"]
        if ph.get("collection_id"):         annotations["collection_id"]         = ph["collection_id"]
        if ph.get("collection_name"):       annotations["collection_name"]       = ph["collection_name"]

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

    print(f"PhenX bundle LinkML schema saved to {output_file} "
          f"({len(schema['slots']):,} slots, {skipped} skipped).")