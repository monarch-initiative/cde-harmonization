"""
Convert CRIC (Chronic Renal Insufficiency Cohort) Derived Variables Excel
to a LinkML YAML schema.

Naming conventions (per https://linkml.io/linkml/schemas/models.html):
  - Classes:  PascalCase            e.g.  Personlevel, Visitlevel
  - Slots:    snake_case            e.g.  pid, systolic, egfr_roche
  - Enums:    PascalCase + 'Enum'   e.g.  AiCricEnum, EduCat1Enum (stubs)

Excel column mapping:
  DATASET          -> class name (PascalCase)
  Variable_Name    -> slot key (snake_case)
  Variable_Short_Label -> slot.description
  Type             -> slot.range (CONTINUOUS->float, INTEGER/count->integer, else string)
  PDF_FILE         -> enum name stub (e.g. AI_CRIC.PDF -> AiCricEnum)
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


# --------------------------------------------------------------------------- #
# Type mapping
# --------------------------------------------------------------------------- #

def _map_datatype(raw_type: str) -> str:
    t = raw_type.strip().lower()
    if t in ('continuous', 'float', 'double', 'decimal'):
        return 'float'
    if t in ('integer', 'count', 'int'):
        return 'integer'
    return 'string'


def _is_enum_type(raw_type: str) -> bool:
    return raw_type.strip().lower() in ('binary', 'categorical', 'nominal', 'ordinal')


# --------------------------------------------------------------------------- #
# Main processor
# --------------------------------------------------------------------------- #

def process_cric_folder(input_folder: str, output_file: str) -> None:
    """
    Read CRIC derived variables Excel file(s) from *input_folder*
    and emit a single LinkML YAML schema to *output_file*.
    """
    xlsx_files = sorted(
        f for f in os.listdir(input_folder)
        if 'CRIC' in f and f.endswith('.xlsx')
    )

    if not xlsx_files:
        print(f"ERROR: No CRIC xlsx files found in {input_folder}. "
              f"Place CRIC Excel file(s) in 'data/dd-niddk-cric'.")
        return

    linkml_schema = {
        'id':            'https://example.org/schemas/cric_cde',
        'name':          'CRIC_CDESchema',
        'description':   (
            'A schema representing CRIC (Chronic Renal Insufficiency Cohort) '
            'Study Data Dictionary CDEs.'
        ),
        'version':       '1.0.0',
        'default_range': 'string',
        'license':       'https://creativecommons.org/publicdomain/zero/1.0/',
        'imports':       ['linkml:types'],
        'prefixes': {
            'linkml': 'https://w3id.org/linkml/',
            'schema': 'http://schema.org/',
            'xsd':    'http://www.w3.org/2001/XMLSchema#',
            'cric':   'https://www.cric-study.org/cde/',
        },
        'default_prefix': 'cric',
        'classes':  {},
        'slots':    {},
        'enums':    {},
    }

    # dedup enums: key -> enum_name
    _enum_registry: dict[str, str] = {}

    for xlsx_file in xlsx_files:
        xlsx_path = os.path.join(input_folder, xlsx_file)
        print(f"Parsing: {xlsx_file}")

        try:
            xl = pd.ExcelFile(xlsx_path, engine='openpyxl')
        except Exception as e:
            print(f"WARNING: could not open {xlsx_file}: {e}")
            continue

        for sheet_name in xl.sheet_names:
            try:
                df = xl.parse(sheet_name, header=None)
            except Exception:
                continue

            # auto-detect header row
            header_row = None
            for i, row in df.iterrows():
                vals = [str(v).strip().lower() for v in row.values]
                if any(v in ('variable', 'var', 'varname', 'variable_name', 'dataset') for v in vals):
                    header_row = i
                    break
            if header_row is None:
                continue

            df = xl.parse(sheet_name, header=header_row)
            df.columns = [re.sub(r'\s+', ' ', str(c)).strip() for c in df.columns]

            # locate columns
            var_col     = next((c for c in df.columns
                                if c.lower() in ('variable', 'var', 'varname', 'variable_name')), None)
            label_col   = next((c for c in df.columns if 'label' in c.lower()), None)
            type_col    = next((c for c in df.columns if c.lower() == 'type'), None)
            dataset_col = next((c for c in df.columns if c.lower() == 'dataset'), None)
            pdf_col     = next((c for c in df.columns if c.lower() == 'pdf_file'), None)

            if not var_col:
                continue

            for _, row in df.iterrows():
                variable = str(row.get(var_col, '')).strip()
                if not variable or variable.lower() in ('nan', 'variable', 'var', 'variable_name'):
                    continue

                # --- class from DATASET column ---
                dataset_val = str(row.get(dataset_col, '')).strip() if dataset_col else ''
                dataset_val = '' if dataset_val == 'nan' else dataset_val
                class_name  = _to_pascal_case(dataset_val) if dataset_val \
                              else _to_pascal_case(sheet_name)

                # --- slot fields ---
                slot_key  = _to_snake_case(variable)
                label     = str(row.get(label_col, '')).strip() if label_col else ''
                raw_type  = str(row.get(type_col,  '')).strip() if type_col  else ''
                pdf_file  = str(row.get(pdf_col,   '')).strip() if pdf_col   else ''

                label    = '' if label    == 'nan' else label
                raw_type = '' if raw_type == 'nan' else raw_type
                pdf_file = '' if pdf_file == 'nan' else pdf_file

                range_val = _map_datatype(raw_type)

                slot: dict = {
                    'description': label,
                    'range':       range_val,
                    'annotations': {'source': 'https://www.cric-study.org'},
                }

                if pdf_file:
                    slot['annotations']['pdf_file'] = pdf_file

                # --- enum: prefer PDF_FILE, fallback to Type ---
                if pdf_file:
                    enum_key  = pdf_file.upper()
                    stem      = re.sub(r'\.PDF$', '', pdf_file, flags=re.IGNORECASE)
                    enum_name = _to_pascal_case(stem) + 'Enum'
                    enum_desc = f'Stub enum. See {pdf_file} for permissible values.'
                elif _is_enum_type(raw_type):
                    enum_key  = raw_type.lower()
                    enum_name = _to_pascal_case(raw_type) + 'Enum'
                    enum_desc = f'Stub enum for CRIC Type={raw_type}.'
                else:
                    enum_key  = None
                    enum_name = None

                if enum_name:
                    if enum_key not in _enum_registry:
                        _enum_registry[enum_key] = enum_name
                    else:
                        enum_name = _enum_registry[enum_key]

                    if enum_name not in linkml_schema['enums']:
                        linkml_schema['enums'][enum_name] = {
                            'description':        enum_desc,
                            'permissible_values': {}
                        }
                    slot['range'] = enum_name

                # first definition wins
                if slot_key not in linkml_schema['slots']:
                    linkml_schema['slots'][slot_key] = slot

                # add to class
                if class_name not in linkml_schema['classes']:
                    linkml_schema['classes'][class_name] = {
                        'description': f"CDEs from CRIC dataset '{dataset_val or sheet_name}'.",
                        'slots':       [],
                    }
                if slot_key not in linkml_schema['classes'][class_name]['slots']:
                    linkml_schema['classes'][class_name]['slots'].append(slot_key)

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
        f"CRIC LinkML schema saved to {output_file} "
        f"({n_classes} classes, {n_slots} slots, {n_enums} enums — stubs)."
    )