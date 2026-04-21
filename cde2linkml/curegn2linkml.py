"""
Convert CureGN SAF Data Dictionary Excel file to a LinkML YAML schema.

Naming conventions (per https://linkml.io/linkml/schemas/models.html):
  - Classes:  PascalCase            e.g.  Demographics, LabResults
  - Slots:    snake_case            e.g.  age_at_biopsy, bun_value
  - Enums:    PascalCase + 'Enum'   e.g.  RaceEnum, BiopsyResultEnum
  - PVs:      human-readable text   e.g.  'White', 'Black or African American'

Excel column mapping:
  DatasetName      -> class name (PascalCase)
  VarName          -> slot key (snake_case)
  LABEL            -> slot.description
  VarType          -> slot.range (NUM -> integer, else string)
  AnswerChoices    -> enum.permissible_values (parsed from '1: Label | 2: Label')
"""

import os
import re
import yaml
import pandas as pd


# --------------------------------------------------------------------------- #
# Naming helpers
# --------------------------------------------------------------------------- #

def _to_pascal_case(text: str) -> str:
    text = re.sub(r'[^a-zA-Z0-9]+', ' ', str(text)).strip()
    return ''.join(w.capitalize() for w in text.split())


def _to_snake_case(text: str) -> str:
    text = str(text).strip()
    text = re.sub(r'[\s\-\.]+', '_', text)
    text = re.sub(r'[^a-zA-Z0-9_]', '', text)
    text = re.sub(r'_+', '_', text).strip('_')
    return text.lower()


def _enum_name_from_slot(slot_key: str) -> str:
    return _to_pascal_case(slot_key) + 'Enum'


# --------------------------------------------------------------------------- #
# Type mapping
# --------------------------------------------------------------------------- #

def _map_datatype(var_type: str) -> str:
    vt = str(var_type).strip().upper()
    if vt in ('NUM', 'NUMERIC', 'INTEGER', 'INT'):
        return 'integer'
    if vt in ('FLOAT', 'DOUBLE', 'DECIMAL'):
        return 'float'
    if vt in ('DATE',):
        return 'date'
    return 'string'


# --------------------------------------------------------------------------- #
# Answer choices parser
#
# Handles CureGN format: '1: Never | 2: Sometimes | 3: Always'
# --------------------------------------------------------------------------- #

def _parse_answer_choices(raw: str) -> dict | None:
    if not isinstance(raw, str) or not raw.strip():
        return None
    parts = [p.strip() for p in raw.split('|') if p.strip()]
    result = {}
    for part in parts:
        # split on first colon only: "1: Label text"
        if ':' in part:
            code, _, label = part.partition(':')
            label = label.strip()
            code  = code.strip()
        else:
            label = part.strip()
            code  = None
        if label:
            result[label] = code
    return result if result else None


# --------------------------------------------------------------------------- #
# Main processor
# --------------------------------------------------------------------------- #

def process_curegn_file(input_folder: str, output_file: str) -> None:
    """
    Read CureGN_SAFDataDictionary_*.xlsx from *input_folder* and emit a
    single LinkML YAML schema to *output_file*.
    """
    # Find the CureGN xlsx file
    xlsx_files = [
        f for f in os.listdir(input_folder)
        if f.startswith('CureGN') and f.endswith('.xlsx')
    ]
    if not xlsx_files:
        print(f"ERROR: No CureGN xlsx file found in {input_folder}. "
              f"Run 'make download-curegn-cde' first.")
        return

    xlsx_path = os.path.join(input_folder, sorted(xlsx_files)[-1])  # latest

    try:
        df = pd.read_excel(xlsx_path, dtype=str).fillna('')
    except Exception as e:
        print(f"ERROR: could not read {xlsx_path}: {e}")
        return

    # Normalise column names
    df.columns = [c.strip() for c in df.columns]

    if 'DatasetName' not in df.columns or 'VarName' not in df.columns:
        print("ERROR: Expected columns 'DatasetName' and 'VarName' not found.")
        return

    linkml_schema = {
        'id':            'https://w3id.org/curegn/cde',
        'name':          'CureGN_CDESchema',
        'description':   (
            'A schema representing CureGN (Cure Glomerulonephritis Network) '
            'Study and Administrative Forms (SAF) Data Dictionary CDEs.'
        ),
        'version':       '1.0.0',
        'default_range': 'string',
        'license':       'https://creativecommons.org/publicdomain/zero/1.0/',
        'imports':       ['linkml:types'],
        'prefixes': {
            'linkml':  'https://w3id.org/linkml/',
            'schema':  'http://schema.org/',
            'xsd':     'http://www.w3.org/2001/XMLSchema#',
            'curegn':  'https://w3id.org/curegn/cde/',
        },
        'default_prefix': 'curegn',
        'classes':  {},
        'slots':    {},
        'enums':    {},
    }

    # dedup enums: choices_tuple -> enum_name
    _enum_registry: dict[tuple, str] = {}

    for dataset_name, group in df.groupby('DatasetName'):
        dataset_name = str(dataset_name).strip()
        if not dataset_name:
            continue

        class_name     = _to_pascal_case(dataset_name)
        slots_for_class: list[str] = []

        for _, row in group.iterrows():
            varname = str(row.get('VarName', '')).strip()
            if not varname:
                continue

            slot_key   = _to_snake_case(varname)
            label      = str(row.get('LABEL', '')).strip()
            var_type   = str(row.get('VarType', '')).strip()
            choices_raw = str(row.get('AnswerChoices', '')).strip()

            range_val = _map_datatype(var_type)

            slot: dict = {
                'description': label,
                'range':       range_val,
            }

            # --- annotations ---
            slot['annotations'] = {'source': 'https://curegn.org'}

            # --- parse AnswerChoices -> enum ---
            pv_parsed = _parse_answer_choices(choices_raw)
            if pv_parsed:
                choices_key = tuple(pv_parsed.keys())
                if choices_key not in _enum_registry:
                    enum_name = _enum_name_from_slot(slot_key)
                    existing  = set(_enum_registry.values())
                    base, n   = enum_name, 1
                    while enum_name in existing:
                        enum_name = f"{base}{n}"; n += 1
                    _enum_registry[choices_key] = enum_name
                else:
                    enum_name = _enum_registry[choices_key]

                if enum_name not in linkml_schema['enums']:
                    pv_entries: dict = {}
                    for lbl, code in pv_parsed.items():
                        pv_entry: dict = {}
                        if code is not None:
                            pv_entry['annotations'] = {'code': code}
                        pv_entries[lbl] = pv_entry or None
                    linkml_schema['enums'][enum_name] = {
                        'permissible_values': pv_entries
                    }
                slot['range'] = enum_name

            # first definition wins
            if slot_key not in linkml_schema['slots']:
                linkml_schema['slots'][slot_key] = slot

            if slot_key not in slots_for_class:
                slots_for_class.append(slot_key)

        if slots_for_class:
            linkml_schema['classes'][class_name] = {
                'description': f'CDEs from CureGN dataset: {dataset_name}.',
                'slots':       slots_for_class,
            }

    # ----------------------------------------------------------------------- #
    # YAML serialisation
    # ----------------------------------------------------------------------- #

    class _Dumper(yaml.SafeDumper):
        def represent_str(self, data: str):
            return self.represent_scalar('tag:yaml.org,2002:str', data)

    _Dumper.add_representer(str, _Dumper.represent_str)

    raw = yaml.dump(
        linkml_schema,
        Dumper=_Dumper,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    )
    raw = raw.replace(': null\n', ':\n')

    with open(output_file, 'w', encoding='utf-8') as fh:
        fh.write(raw)

    n_classes = len(linkml_schema['classes'])
    n_slots   = len(linkml_schema['slots'])
    n_enums   = len(linkml_schema['enums'])
    print(
        f"CureGN LinkML schema saved to {output_file} "
        f"({n_classes} classes, {n_slots} slots, {n_enums} enums)."
    )