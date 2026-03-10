"""
Convert NHLBI CONNECTS CDE Excel file (CONNECTS_DD_V1.3.xlsx) to a LinkML YAML schema.

Each non-metadata tab becomes a LinkML class.
Tabs whose name starts and ends with '-' (e.g. -README-, -Units-, -Change Log-)
are skipped.

Column mapping:
    Element                      -> slot key  (snake_case)
    Question                     -> slot.description
    Variable                     -> annotation: variable
    Variable Label               -> annotation: variable_label  / slot title
    Implementation Notes         -> annotation: implementation_notes
    Variable Type                -> slot.range  (enum when type indicates coded values)
    Response Options / Derivation -> enum permissible_values  (when Variable Type is coded)

Naming conventions (LinkML spec):
    Classes  : PascalCase           e.g.  Demographics, VitalSigns
    Slots    : snake_case           e.g.  age_at_enrollment
    Enums    : PascalCase + 'Enum'  e.g.  SexAtBirthEnum
    PVs      : human-readable text  e.g.  'Male', 'Female', 'Unknown'
"""

import os
import re
import yaml
import pandas as pd


# --------------------------------------------------------------------------- #
# Naming helpers  (identical conventions to heal2linkml)
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
# Variable Type -> LinkML range
# Types that imply a coded / enumerated response set
# --------------------------------------------------------------------------- #

_ENUM_TYPES = {
    'coded', 'code', 'categorical', 'ordinal',
    'nominal', 'choice', 'select', 'enum',
}

_TYPE_MAP = {
    'integer':   'integer',
    'int':       'integer',
    'float':     'float',
    'double':    'float',
    'numeric':   'float',
    'number':    'float',
    'decimal':   'float',
    'date':      'date',
    'datetime':  'datetime',
    'boolean':   'boolean',
    'string':    'string',
    'text':      'string',
    'char':      'string',
    'varchar':   'string',
}


def _is_enum_type(var_type: str) -> bool:
    return str(var_type).strip().lower() in _ENUM_TYPES


def _map_datatype(var_type: str) -> str:
    return _TYPE_MAP.get(str(var_type).strip().lower(), 'string')


# --------------------------------------------------------------------------- #
# Response Options parser
#
# Handles common CONNECTS formats, e.g.:
#   "1=Male; 2=Female; 3=Unknown"
#   "Yes; No; Unknown"
#   "0 = No\n1 = Yes"
# --------------------------------------------------------------------------- #

def _parse_response_options(raw: str) -> dict | None:
    if not isinstance(raw, str) or not raw.strip():
        return None

    # normalise separators: newline or semicolon -> pipe for splitting
    raw = raw.replace('\n', ';')
    items = [s.strip() for s in re.split(r'[;|]+', raw) if s.strip()]
    if not items:
        return None

    result = {}
    for item in items:
        # try  "<code> = <label>"  or  "<code>: <label>"
        m = re.match(r'^(\S+)\s*[=:]\s*(.+)$', item)
        if m:
            code  = m.group(1).strip()
            label = m.group(2).strip()
            result[label] = code
        else:
            result[item] = None   # no code; use text as PV key directly
    return result if result else None


# --------------------------------------------------------------------------- #
# Tab filter
# --------------------------------------------------------------------------- #

def _is_metadata_tab(sheet_name: str) -> bool:
    """Skip tabs whose name is wrapped in '-' like -README- or -Change Log-."""
    name = sheet_name.strip()
    return name.startswith('-') and name.endswith('-')


# --------------------------------------------------------------------------- #
# Main processor
# --------------------------------------------------------------------------- #

def process_connects_file(input_folder: str, output_file: str) -> None:
    """
    Read CONNECTS_DD_V1.3.xlsx from *input_folder*, convert every
    non-metadata tab to a LinkML class, and write schema to *output_file*.
    """

    xlsx_path = os.path.join(input_folder, 'CONNECTS_DD_V1.3.xlsx')
    if not os.path.exists(xlsx_path):
        print(f"ERROR: {xlsx_path} not found. Run 'make download-connects-cde' first.")
        return

    linkml_schema = {
        'id':             'https://example.org/schemas/connects_cde',
        'name':           'CONNECTS_CDESchema',
        'description':    (
            'A schema representing NHLBI CONNECTS COVID-19 Therapeutic Trial '
            'Common Data Elements (CDEs).'
        ),
        'version':        '1.0.0',
        'default_range':  'string',
        'license':        'https://creativecommons.org/publicdomain/zero/1.0/',
        'imports':        ['linkml:types'],
        'prefixes': {
            'linkml':    'https://w3id.org/linkml/',
            'schema':    'http://schema.org/',
            'xsd':       'http://www.w3.org/2001/XMLSchema#',
            'connects':  'https://nhlbi-connects.org/cde/',
        },
        'default_prefix': 'connects',
        'classes':  {},
        'slots':    {},
        'enums':    {},
    }

    # dedup enums across tabs: choices_tuple -> enum_name
    _enum_registry: dict[tuple, str] = {}

    try:
        xl = pd.ExcelFile(xlsx_path, engine='openpyxl')
    except Exception as e:
        print(f"ERROR: could not open {xlsx_path}: {e}")
        return

    for sheet_name in xl.sheet_names:
        if _is_metadata_tab(sheet_name):
            continue

        class_name = _to_pascal_case(sheet_name)

        try:
            raw = xl.parse(sheet_name, header=None)
        except Exception as e:
            print(f"WARNING: could not parse sheet '{sheet_name}': {e}")
            continue

        # Find the header row by scanning for the row that contains 'Element'
        header_row = None
        for i, row in raw.iterrows():
            vals = [str(v).strip() for v in row.values]
            if 'Element' in vals:
                header_row = i
                break

        if header_row is None:
            print(f"WARNING: 'Element' column missing in sheet '{sheet_name}', skipping.")
            continue

        # Re-parse using the detected header row
        try:
            df = xl.parse(sheet_name, header=header_row)
        except Exception as e:
            print(f"WARNING: could not re-parse sheet '{sheet_name}' with header={header_row}: {e}")
            continue

        # Normalise column names (collapse internal whitespace too)
        df.columns = [re.sub(r'\s+', ' ', str(c)).strip() for c in df.columns]

        # Resolve Variable Type column name (may have single or double space)
        var_type_col = next(
            (c for c in df.columns if re.sub(r'\s+', ' ', c).strip() == 'Variable Type'),
            None
        )
        response_col = next(
            (c for c in df.columns if 'Response Options' in c),
            None
        )

        # Debug: print unique Variable Type values on first run
        slots_for_class: list[str] = []

        for _, row in df.iterrows():
            element = row.get('Element')
            if pd.isna(element) or not str(element).strip():
                continue

            slot_key = _to_snake_case(str(element))

            # --- description from Question column ---
            question = row.get('Question', '')
            description = str(question).strip() if pd.notna(question) else ''

            # --- slot title from Variable Label ---
            var_label = row.get('Variable Label', element)
            title = str(var_label).strip() if pd.notna(var_label) else slot_key

            # --- data type ---
            raw_type  = str(row.get(var_type_col, 'string')) if var_type_col else 'string'
            range_val = _map_datatype(raw_type)

            # --- parse Response Options ---
            raw_response = row.get(response_col) if response_col else None
            pv_parsed = _parse_response_options(
                str(raw_response) if pd.notna(raw_response) else ''
            )

            # Treat as enum if response options contain 2+ discrete choices
            # (regardless of Variable Type — CONNECTS uses 'Char' for coded fields)
            use_enum = pv_parsed is not None and len(pv_parsed) >= 2
            annotations: dict = {}
            variable = row.get('Variable')
            if pd.notna(variable) and str(variable).strip():
                annotations['variable'] = str(variable).strip()
            annotations['variable_label'] = title
            impl = row.get('Implementation Notes')
            if pd.notna(impl) and str(impl).strip():
                annotations['implementation_notes'] = str(impl).strip()

            # --- build slot ---
            slot: dict = {
                'title':       title,
                'description': description,
                'range':       range_val,
            }
            if annotations:
                slot['annotations'] = annotations

            # --- build enum if discrete choices detected ---
            if use_enum and pv_parsed:
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
                    for label, code in pv_parsed.items():
                        pv_entry: dict = {}
                        if code is not None:
                            pv_entry['annotations'] = {'code': code}
                        pv_entries[label] = pv_entry or None
                    linkml_schema['enums'][enum_name] = {
                        'permissible_values': pv_entries
                    }
                slot['range'] = enum_name

            elif not use_enum:
                slot['range'] = _map_datatype(raw_type)

            # first definition wins across tabs
            if slot_key not in linkml_schema['slots']:
                linkml_schema['slots'][slot_key] = slot

            if slot_key not in slots_for_class:
                slots_for_class.append(slot_key)

        if slots_for_class:
            linkml_schema['classes'][class_name] = {
                'description': f"CDEs from CONNECTS tab '{sheet_name}'.",
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
        f"CONNECTS LinkML schema saved to {output_file} "
        f"({n_classes} classes, {n_slots} slots, {n_enums} enums)."
    )