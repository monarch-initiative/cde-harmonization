"""
Convert NIH HEAL CDE .xlsx files to a LinkML YAML schema.

Naming conventions (per https://linkml.io/linkml/schemas/models.html):
  - Classes:  PascalCase             e.g.  Phq4, PromisGlobalHealth
  - Slots:    snake_case             e.g.  phq4_item1, pain_intensity
  - Enums:    PascalCase + 'Enum'   e.g.  FrequencyEnum
  - PVs:      human-readable text   e.g.  'Never true', 'Always true'
                (spaces allowed; leading numeric code stripped to a
                 separate 'code' annotation so the PV key is clean)
"""

import os
import re
import yaml
import pandas as pd


# --------------------------------------------------------------------------- #
# Naming helpers
# --------------------------------------------------------------------------- #

def _to_pascal_case(text: str) -> str:
    """Convert any string to PascalCase, stripping non-alphanumeric chars."""
    text = re.sub(r'[^a-zA-Z0-9]+', ' ', str(text)).strip()
    return ''.join(w.capitalize() for w in text.split())


def _to_snake_case(text: str) -> str:
    """
    Convert any string to snake_case for use as a slot key.
    Preserves existing underscores, lowercases everything.
    """
    text = str(text).strip()
    # replace spaces/hyphens/dots with underscore
    text = re.sub(r'[\s\-\.]+', '_', text)
    # strip any remaining non-alphanumeric except underscore
    text = re.sub(r'[^a-zA-Z0-9_]', '', text)
    # collapse consecutive underscores
    text = re.sub(r'_+', '_', text).strip('_')
    return text.lower()


def _class_name_from_filename(filename: str) -> str:
    """
    Derive PascalCase class name from xlsx filename.
    'phq-4-cde.xlsx'                  -> 'Phq4'
    'promis-29-profile-v2.1-cde.xlsx' -> 'Promis29ProfileV21'
    """
    stem = os.path.splitext(filename)[0]       # drop .xlsx
    stem = re.sub(r'-cde$', '', stem)          # drop trailing -cde
    return _to_pascal_case(stem)


def _enum_name_from_slot(slot_key: str) -> str:
    """PascalCase enum name from snake_case slot key."""
    return _to_pascal_case(slot_key) + 'Enum'


# --------------------------------------------------------------------------- #
# PV description parser
# --------------------------------------------------------------------------- #

def _parse_pv_description(pv_desc: str) -> dict | None:
    """
    Parse strings like:
        '1 = Never true; 2 = Very seldom true; 3 = Seldom true'
    Returns an OrderedDict of  { pv_text: numeric_code_or_None }.
    PV keys are clean human-readable labels (spaces allowed per LinkML spec).
    Returns None if the string cannot be parsed as a value list.
    """
    if not isinstance(pv_desc, str) or not pv_desc.strip():
        return None

    items = [s.strip() for s in pv_desc.split(';') if s.strip()]
    result = {}
    for item in items:
        m = re.match(r'^(\S+)\s*=\s*(.+)$', item)
        if m:
            code  = m.group(1).strip()
            label = m.group(2).strip()
            result[label] = code          # label is the PV key
        else:
            result[item] = None           # no code – use text as-is
    return result if result else None


# --------------------------------------------------------------------------- #
# Type mapping
# --------------------------------------------------------------------------- #

_TYPE_MAP = {
    'integer':  'integer',
    'int':      'integer',
    'float':    'float',
    'double':   'float',
    'numeric':  'float',
    'number':   'float',
    'date':     'date',
    'datetime': 'datetime',
    'boolean':  'boolean',
    'string':   'string',
    'text':     'string',
    'char':     'string',
}


def _map_datatype(raw) -> str:
    if not isinstance(raw, str):
        return 'string'
    return _TYPE_MAP.get(raw.strip().lower(), 'string')


# --------------------------------------------------------------------------- #
# Main processor
# --------------------------------------------------------------------------- #

def process_heal_folder(input_folder: str, output_file: str) -> None:
    """
    Read every English .xlsx CDE file from *input_folder* and emit a
    single LinkML YAML schema to *output_file*.

    HEAL xlsx columns used:
        CDE Name | Variable Name | Definition | Short Description |
        Additional Notes (Question Text) | Permissible Values |
        PV Description | Data Type
    """

    linkml_schema = {
        'id':            'https://example.org/schemas/heal_cde',
        'name':          'HEAL_CDESchema',
        'description':   (
            'A schema representing NIH HEAL Initiative '
            'Common Data Elements (CDEs).'
        ),
        'version':       '1.0.0',
        'default_range': 'string',
        'license':       'https://creativecommons.org/publicdomain/zero/1.0/',
        'imports':       ['linkml:types'],
        'prefixes': {
            'linkml': 'https://w3id.org/linkml/',
            'schema': 'http://schema.org/',
            'xsd':    'http://www.w3.org/2001/XMLSchema#',
            'heal':   'https://heal.nih.gov/cde/',
        },
        'default_prefix': 'heal',
        'classes':  {},
        'slots':    {},
        'enums':    {},
    }

    # dedup enums across files: choices_tuple -> enum_name
    _enum_registry: dict[tuple, str] = {}

    xlsx_files = sorted(
        f for f in os.listdir(input_folder)
        if f.endswith('.xlsx') and '-spanish' not in f.lower()
    )

    if not xlsx_files:
        print(f"WARNING: No .xlsx files found in {input_folder}")
        return

    for filename in xlsx_files:
        filepath   = os.path.join(input_folder, filename)
        class_name = _class_name_from_filename(filename)

        try:
            df = pd.read_excel(filepath, engine='openpyxl')
        except Exception as e:
            print(f"WARNING: could not read {filename}: {e}")
            continue

        df.columns = [c.strip() for c in df.columns]

        if 'Variable Name' not in df.columns:
            print(f"WARNING: 'Variable Name' missing in {filename}, skipping.")
            continue

        slots_for_class: list[str] = []

        for _, row in df.iterrows():
            var_name = row.get('Variable Name')
            if pd.isna(var_name) or not str(var_name).strip():
                continue

            # --- slot key: snake_case ---
            slot_key = _to_snake_case(str(var_name))

            # --- slot title from CDE Name (human-readable) ---
            cde_name = row.get('CDE Name', var_name)
            title    = str(cde_name).strip() if pd.notna(cde_name) else slot_key

            # --- description from Definition, fallback Short Description ---
            definition = row.get('Definition') or row.get('Short Description', '')
            description = str(definition).strip() if pd.notna(definition) else ''

            # --- data type -> LinkML range ---
            range_val = _map_datatype(row.get('Data Type', 'string'))

            # --- build slot dict (LinkML SlotDefinition fields) ---
            slot: dict = {
                'title':       title,
                'description': description,
                'range':       range_val,
            }

            # --- question text as annotation ---
            question = row.get('Additional Notes (Question Text)')
            if pd.notna(question) and str(question).strip():
                slot['annotations'] = {
                    'question_text': str(question).strip()
                }

            # --- parse PV Description -> enum ---
            pv_desc  = row.get('PV Description')
            pv_parsed = _parse_pv_description(
                str(pv_desc) if pd.notna(pv_desc) else ''
            )

            if pv_parsed:
                choices_key = tuple(pv_parsed.keys())

                if choices_key not in _enum_registry:
                    enum_name = _enum_name_from_slot(slot_key)
                    # guard against accidental collisions
                    existing_names = set(_enum_registry.values())
                    suffix = 1
                    base_name = enum_name
                    while enum_name in existing_names:
                        enum_name = f"{base_name}{suffix}"
                        suffix += 1
                    _enum_registry[choices_key] = enum_name
                else:
                    enum_name = _enum_registry[choices_key]

                if enum_name not in linkml_schema['enums']:
                    # PV keys = human-readable labels (spaces OK per LinkML)
                    # numeric code stored as 'meaning' annotation on each PV
                    pv_entries: dict = {}
                    for label, code in pv_parsed.items():
                        pv_entry: dict = {}
                        if code is not None:
                            pv_entry['description'] = label
                            pv_entry['annotations'] = {'code': code}
                        pv_entries[label] = pv_entry or None

                    linkml_schema['enums'][enum_name] = {
                        'permissible_values': pv_entries
                    }

                slot['range'] = enum_name

            # first definition across files wins (slots are global)
            if slot_key not in linkml_schema['slots']:
                linkml_schema['slots'][slot_key] = slot

            if slot_key not in slots_for_class:
                slots_for_class.append(slot_key)

        if slots_for_class:
            # class name: PascalCase; description references source file
            linkml_schema['classes'][class_name] = {
                'description': f'CDEs sourced from {filename}.',
                'slots':       slots_for_class,
            }

    # ----------------------------------------------------------------------- #
    # YAML serialisation
    # ----------------------------------------------------------------------- #

    class _Dumper(yaml.SafeDumper):
        """Emit plain (unquoted) strings wherever possible."""
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
    # remove bare ': null' produced for None values
    raw = raw.replace(': null\n', ':\n')

    with open(output_file, 'w', encoding='utf-8') as fh:
        fh.write(raw)

    n_classes = len(linkml_schema['classes'])
    n_slots   = len(linkml_schema['slots'])
    n_enums   = len(linkml_schema['enums'])
    print(
        f"HEAL LinkML schema saved to {output_file} "
        f"({n_classes} classes, {n_slots} slots, {n_enums} enums)."
    )