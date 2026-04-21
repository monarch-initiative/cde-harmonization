"""
Convert KPMP Data Dictionary CSV to a LinkML YAML schema.

The KPMP data dictionary uses REDCap format — identical column structure to RADx-UP.

Naming conventions (per https://linkml.io/linkml/schemas/models.html):
  - Classes:  PascalCase            e.g.  ParticipantManagement, LabResults
  - Slots:    snake_case            e.g.  enrollment_date, biopsy_site
  - Enums:    PascalCase + 'Enum'   e.g.  BiopsySiteEnum
  - PVs:      human-readable text   e.g.  'Yes', 'No', 'Unknown'

CSV column mapping:
  Form Name                                    -> class name (PascalCase)
  Variable / Field Name                        -> slot key (snake_case)
  Field Label                                  -> slot.description
  Text Validation Type OR Show Slider Number   -> slot.range
  Text Validation Min                          -> slot.minimum_value
  Text Validation Max                          -> slot.maximum_value
  Choices, Calculations, OR Slider Labels      -> enum.permissible_values
"""

import os
import re
import glob
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


def _slot_title(variable_name: str) -> str:
    return ' '.join(w.capitalize() for w in variable_name.split('_'))


# --------------------------------------------------------------------------- #
# Type mapping
# --------------------------------------------------------------------------- #

_TYPE_MAP = {
    'integer':  'integer',
    'int':      'integer',
    'float':    'float',
    'number':   'float',
    'date':     'date',
    'datetime': 'datetime',
    'boolean':  'boolean',
    'string':   'string',
    'text':     'string',
}


def _map_datatype(raw) -> str:
    if not isinstance(raw, str) or not raw.strip():
        return 'string'
    return _TYPE_MAP.get(raw.strip().lower(), 'string')


# --------------------------------------------------------------------------- #
# Choices parser  (REDCap format: "1, Label | 2, Label")
# --------------------------------------------------------------------------- #

def _parse_choices(raw: str) -> list[str]:
    items = [s.strip() for s in raw.split('|') if s.strip()]
    labels = []
    for item in items:
        label = item.split(',', 1)[1].strip() if ',' in item else item.strip()
        if label:
            labels.append(label)
    return labels


# --------------------------------------------------------------------------- #
# Main processor
# --------------------------------------------------------------------------- #

def process_kpmp_folder(input_folder: str, output_file: str) -> None:
    """
    Read all KPMP data dictionary CSV files from *input_folder* and emit a
    single LinkML YAML schema to *output_file*.
    """
    csv_files = sorted(glob.glob(os.path.join(input_folder, '*.csv')))
    if not csv_files:
        print(f"ERROR: No CSV files found in {input_folder}.")
        return

    linkml_schema = {
        'id':            'https://example.org/schemas/kpmp_cde',
        'name':          'KPMP_CDESchema',
        'description':   (
            'A schema representing KPMP (Kidney Precision Medicine Project) '
            'data dictionary Common Data Elements (CDEs).'
        ),
        'version':       '1.0.0',
        'default_range': 'string',
        'license':       'https://creativecommons.org/publicdomain/zero/1.0/',
        'imports':       ['linkml:types'],
        'prefixes': {
            'linkml': 'https://w3id.org/linkml/',
            'schema': 'http://schema.org/',
            'xsd':    'http://www.w3.org/2001/XMLSchema#',
            'kpmp':   'https://kpmp.org/cde/',
        },
        'default_prefix': 'kpmp',
        'classes':  {},
        'slots':    {},
        'enums':    {},
    }

    # dedup enums across all files: choices_tuple -> enum_name
    _enum_registry: dict[tuple, str] = {}

    for csv_path in csv_files:
        try:
            data = pd.read_csv(csv_path, encoding='utf-8')
        except UnicodeDecodeError:
            data = pd.read_csv(csv_path, encoding='latin1')
        except Exception as e:
            print(f"WARNING: could not read {csv_path}: {e}")
            continue

        for _, row in data.iterrows():
            form_name     = row.get('Form Name')
            variable_name = row.get('Variable / Field Name')
            field_label   = row.get('Field Label', '')
            raw_choices   = row.get('Choices, Calculations, OR Slider Labels')
            text_val_type = row.get('Text Validation Type OR Show Slider Number')
            min_value     = row.get('Text Validation Min')
            max_value     = row.get('Text Validation Max')

            if pd.isna(variable_name) or not str(variable_name).strip():
                continue
            if pd.isna(form_name) or not str(form_name).strip():
                continue

            class_name = _to_pascal_case(str(form_name))
            if class_name not in linkml_schema['classes']:
                linkml_schema['classes'][class_name] = {
                    'title':       str(form_name).strip(),
                    'description': f'CDEs from KPMP form: {form_name}.',
                    'slots':       [],
                }

            slot_key = _to_snake_case(str(variable_name))
            title    = _slot_title(str(variable_name))
            range_val = _map_datatype(
                str(text_val_type) if pd.notna(text_val_type) else ''
            )

            slot: dict = {
                'title':       title,
                'description': str(field_label).strip() if pd.notna(field_label) else '',
                'range':       range_val,
                'annotations': {'source': 'https://kpmp.org'},
            }

            if pd.notna(min_value):
                slot['minimum_value'] = int(min_value) if str(min_value).isdigit() else min_value
            if pd.notna(max_value):
                slot['maximum_value'] = int(max_value) if str(max_value).isdigit() else max_value

            if pd.notna(raw_choices) and str(raw_choices).strip():
                labels = _parse_choices(str(raw_choices))
                if labels:
                    choices_key = tuple(labels)
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
                        linkml_schema['enums'][enum_name] = {
                            'permissible_values': {label: None for label in labels}
                        }
                    slot['range'] = enum_name

            if slot_key not in linkml_schema['slots']:
                linkml_schema['slots'][slot_key] = slot

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
        f"KPMP LinkML schema saved to {output_file} "
        f"({n_classes} classes, {n_slots} slots, {n_enums} enums)."
    )