"""
Convert NEPTUNE Data Dictionary Excel file (multi-tab) to a LinkML YAML schema.

Naming conventions (per https://linkml.io/linkml/schemas/models.html):
  - Classes:  PascalCase            e.g.  Patient, LabResults
  - Slots:    snake_case            e.g.  pat_sex, pat_age_v2
  - Enums:    PascalCase + 'Enum'   e.g.  NoyesEnum, EthnicEnum
  - PVs:      stub only — actual values defined in SAS format catalog (.sas7bcat)

Excel column mapping (per tab):
  Tab name      -> class name (PascalCase)
  Variable      -> slot key (snake_case)
  Label         -> slot.description
  Type          -> slot.range (1=numeric -> integer, 2=char -> string)
  Format        -> enum stub name (PascalCase + Enum)
  Length        -> slot.annotations
  Format Length -> slot.annotations
"""

import os
import re
import warnings
import yaml
import pandas as pd

warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')


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


def _enum_name_from_format(fmt: str) -> str:
    return _to_pascal_case(fmt.strip()) + 'Enum'


# --------------------------------------------------------------------------- #
# SAS Type codes: 1=numeric, 2=character
# Formats that are display/reference only — not coded enums
# --------------------------------------------------------------------------- #

_TYPE_MAP = {'1': 'integer', '2': 'string'}
_SKIP_FORMATS = {'BEST', 'BEST32', 'D', '$', ''}

def _map_datatype(type_code: str) -> str:
    return _TYPE_MAP.get(str(type_code).strip(), 'string')


# --------------------------------------------------------------------------- #
# Main processor
# --------------------------------------------------------------------------- #

def process_neptune_file(input_folder: str, output_file: str) -> None:
    """
    Read NEPTUNE Data Dictionary xlsx from *input_folder*, convert every
    tab to a LinkML class with stub enums from SAS Format names,
    and write schema to *output_file*.
    """
    xlsx_files = [
        f for f in os.listdir(input_folder)
        if ('Neptune' in f or 'NEPTUNE' in f) and f.endswith('.xlsx')
    ]
    if not xlsx_files:
        print(f"ERROR: No NEPTUNE xlsx file found in {input_folder}.")
        return

    xlsx_path = os.path.join(input_folder, sorted(xlsx_files)[-1])

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        try:
            xl = pd.ExcelFile(xlsx_path, engine='openpyxl')
        except Exception as e:
            print(f"ERROR: could not open {xlsx_path}: {e}")
            return

    linkml_schema = {
        'id':            'https://example.org/schemas/neptune_cde',
        'name':          'NEPTUNE_CDESchema',
        'description':   (
            'A schema representing NEPTUNE (Nephrotic Syndrome Study Network) '
            'Study and Administrative Forms Data Dictionary CDEs. '
            'Enum permissible values are stubs — populate from SAS format catalog (.sas7bcat).'
        ),
        'version':       '1.0.0',
        'default_range': 'string',
        'license':       'https://creativecommons.org/publicdomain/zero/1.0/',
        'imports':       ['linkml:types'],
        'prefixes': {
            'linkml':   'https://w3id.org/linkml/',
            'schema':   'http://schema.org/',
            'xsd':      'http://www.w3.org/2001/XMLSchema#',
            'neptune':  'https://neptune.med.umich.edu/cde/',
        },
        'default_prefix': 'neptune',
        'classes':  {},
        'slots':    {},
        'enums':    {},
    }

    # format_name -> enum_name (shared across tabs)
    _format_enum_map: dict[str, str] = {}

    for sheet_name in xl.sheet_names:
        try:
            df = xl.parse(sheet_name, header=None)
        except Exception as e:
            print(f"WARNING: could not parse sheet '{sheet_name}': {e}")
            continue

        # Auto-detect header row
        header_row = None
        for i, row in df.iterrows():
            if 'Variable' in [str(v).strip() for v in row.values]:
                header_row = i
                break

        if header_row is None:
            print(f"WARNING: 'Variable' column not found in sheet '{sheet_name}', skipping.")
            continue

        df = xl.parse(sheet_name, header=header_row)
        df.columns = [re.sub(r'\s+', ' ', str(c)).strip() for c in df.columns]

        if 'Variable' not in df.columns:
            continue

        class_name      = _to_pascal_case(sheet_name)
        slots_for_class: list[str] = []

        for _, row in df.iterrows():
            variable = row.get('Variable')
            if pd.isna(variable) or not str(variable).strip():
                continue
            var_str = str(variable).strip()
            if var_str.isdigit():
                continue

            slot_key  = _to_snake_case(var_str)
            label     = str(row.get('Label', '')).strip()
            type_code = str(row.get('Type', '2')).strip()
            fmt       = str(row.get('Format', '')).strip()
            length    = row.get('Length')
            fmt_len   = row.get('Format Length')

            range_val = _map_datatype(type_code)

            slot: dict = {
                'description': label,
                'range':       range_val,
            }

            # --- annotations ---
            annotations: dict = {'source': 'https://www.neptune-study.org'}
            if pd.notna(length) and str(length).strip() not in ('', 'nan'):
                annotations['length'] = str(length).strip()
            if pd.notna(fmt_len) and str(fmt_len).strip() not in ('', 'nan', '0'):
                annotations['format_length'] = str(fmt_len).strip()
            if fmt and fmt.upper() not in _SKIP_FORMATS:
                annotations['sas_format'] = fmt
            slot['annotations'] = annotations

            # --- stub enum from Format name ---
            fmt_upper = fmt.strip().upper()
            if fmt_upper and fmt_upper not in _SKIP_FORMATS:
                if fmt_upper not in _format_enum_map:
                    enum_name = _enum_name_from_format(fmt_upper)
                    _format_enum_map[fmt_upper] = enum_name
                else:
                    enum_name = _format_enum_map[fmt_upper]

                # create stub enum with no PVs — to be populated from SAS catalog
                if enum_name not in linkml_schema['enums']:
                    linkml_schema['enums'][enum_name] = {
                        'description': (
                            f'Stub enum from SAS format {fmt_upper}. '
                            f'Populate permissible_values from SAS format catalog.'
                        ),
                        'permissible_values': {}
                    }
                slot['range'] = enum_name

            if slot_key not in linkml_schema['slots']:
                linkml_schema['slots'][slot_key] = slot

            if slot_key not in slots_for_class:
                slots_for_class.append(slot_key)

        if slots_for_class:
            linkml_schema['classes'][class_name] = {
                'description': f"CDEs from NEPTUNE tab '{sheet_name}'.",
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
        f"NEPTUNE LinkML schema saved to {output_file} "
        f"({n_classes} classes, {n_slots} slots, {n_enums} enums — stubs, populate PVs from SAS catalog)."
    )