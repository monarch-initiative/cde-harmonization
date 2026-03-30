"""
Convert PhenX CDE CSV/TSV files to a LinkML YAML schema.

Naming conventions (per https://linkml.io/linkml/schemas/models.html):
  - Classes:  PascalCase            e.g.  PhysicalActivity, Demographics
  - Slots:    snake_case            e.g.  bmi, age_at_enrollment
  - Enums:    PascalCase + 'Enum'   e.g.  SmokingStatusEnum
  - PVs:      human-readable text   e.g.  'Never', 'Current', 'Former'

CSV/TSV column mapping:
  Filename (minus extension)  -> class name (PascalCase)
  VARNAME                     -> slot key (snake_case)
  VARDESC                     -> slot.description
  TYPE                        -> slot.range
  MIN                         -> slot.minimum_value
  MAX                         -> slot.maximum_value
  VALUES (+ columns to right) -> enum.permissible_values (pipe-separated)
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

_TYPE_MAP = {
    'integer':        'integer',
    'int':            'integer',
    'float':          'float',
    'double':         'float',
    'date':           'date',
    'datetime':       'datetime',
    'boolean':        'boolean',
    'string':         'string',
    'text':           'string',
    'encoded values': 'string',  # overridden to enum when VALUES present
}


def _map_datatype(raw) -> str:
    if not isinstance(raw, str):
        return 'string'
    return _TYPE_MAP.get(raw.strip().lower(), 'string')


# --------------------------------------------------------------------------- #
# Main processor
# --------------------------------------------------------------------------- #

def process_phenx_folder(input_folder: str, output_file: str) -> None:
    """
    Read every .csv/.tsv PhenX CDE file from *input_folder* and emit a
    single LinkML YAML schema to *output_file*.
    """

    linkml_schema = {
        'id':            'https://example.org/schemas/phenx_cde',
        'name':          'PhenX_CDESchema',
        'description':   'A schema representing PhenX Common Data Elements (CDEs).',
        'version':       '1.0.0',
        'default_range': 'string',
        'license':       'https://creativecommons.org/publicdomain/zero/1.0/',
        'imports':       ['linkml:types'],
        'prefixes': {
            'linkml': 'https://w3id.org/linkml/',
            'schema': 'http://schema.org/',
            'xsd':    'http://www.w3.org/2001/XMLSchema#',
            'phenx':  'https://www.phenxtoolkit.org/cde/',
        },
        'default_prefix': 'phenx',
        'classes':  {},
        'slots':    {},
        'enums':    {},
    }

    # dedup enums across files: choices_tuple -> enum_name
    _enum_registry: dict[tuple, str] = {}

    processed = skipped_multiindex = skipped_empty = 0

    for file_name in sorted(os.listdir(input_folder)):
        if not file_name.endswith(('.csv', '.tsv')):
            continue

        file_path = os.path.join(input_folder, file_name)
        delimiter = ',' if file_name.endswith('.csv') else '\t'

        try:
            df = pd.read_csv(
                file_path, delimiter=delimiter,
                encoding='utf-8', on_bad_lines='skip', quotechar='"'
            )
        except UnicodeDecodeError:
            df = pd.read_csv(
                file_path, delimiter=delimiter,
                encoding='latin1', on_bad_lines='skip'
            )
        except Exception as e:
            print(f"WARNING: could not read {file_name}: {e}")
            continue

        if isinstance(df.index, pd.MultiIndex):
            skipped_multiindex += 1
            continue

        if 'VARNAME' not in df.columns:
            continue

        # class name from filename (PascalCase)
        class_name = _to_pascal_case(os.path.splitext(file_name)[0])
        slots_for_class: list[str] = []

        for _, row in df.iterrows():
            varname     = row.get('VARNAME')
            if pd.isna(varname) or not str(varname).strip():
                continue

            slot_key    = _to_snake_case(str(varname))
            vardesc     = row.get('VARDESC', '')
            var_type    = row.get('TYPE', 'string')
            min_value   = row.get('MIN', None)
            max_value   = row.get('MAX', None)
            source      = row.get('VARIABLE_SOURCE', None)
            source_id   = row.get('SOURCE_VARIABLE_ID', None)
            comment     = row.get('COMMENT1', None)

            range_val = _map_datatype(var_type)

            slot: dict = {
                'description': str(vardesc).strip() if pd.notna(vardesc) else '',
                'range':       range_val,
            }

            # --- annotations: source, source_variable_id, comment ---
            annotations: dict = {}
            if pd.notna(source) and str(source).strip():
                annotations['source'] = str(source).strip()
            if pd.notna(source_id) and str(source_id).strip():
                annotations['source_variable_id'] = str(source_id).strip()
            if pd.notna(comment) and str(comment).strip():
                annotations['comment'] = str(comment).strip()
            if annotations:
                slot['annotations'] = annotations

            # min / max constraints
            if range_val in ('integer', 'float'):
                if pd.notna(min_value):
                    slot['minimum_value'] = min_value
                if pd.notna(max_value):
                    slot['maximum_value'] = max_value

            # --- collect choices from VALUES + columns to the right ---
            choices: list[str] = []
            if 'VALUES' in df.columns:
                value = row.get('VALUES')
                if isinstance(value, str) and pd.notna(value):
                    concatenated = value
                    val_idx = df.columns.get_loc('VALUES') + 1
                    for col in df.columns[val_idx:]:
                        extra = row.get(col)
                        if pd.notna(extra):
                            concatenated += f"|{extra}"
                    choices = [c.strip() for c in concatenated.split('|') if c.strip()]
                    choices = list(dict.fromkeys(choices))  # dedup preserving order

            if choices:
                choices_key = tuple(choices)
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
                        'permissible_values': {c: None for c in choices}
                    }
                slot['range'] = enum_name

            # first definition wins across files
            if slot_key not in linkml_schema['slots']:
                linkml_schema['slots'][slot_key] = slot

            if slot_key not in slots_for_class:
                slots_for_class.append(slot_key)

        if slots_for_class:
            linkml_schema['classes'][class_name] = {
                'description': f'CDEs from PhenX file {file_name}.',
                'slots':       slots_for_class,
            }
            processed += 1
        else:
            skipped_empty += 1

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
        f"PhenX LinkML schema saved to {output_file} "
        f"({n_classes} classes, {n_slots} slots, {n_enums} enums)."
    )