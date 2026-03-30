"""
Convert NIH NLM CDE JSON export to a LinkML YAML schema.

Naming conventions (per https://linkml.io/linkml/schemas/models.html):
  - Classes:  PascalCase             e.g.  NationalCancerInstitute
  - Slots:    snake_case             e.g.  patient_age, tumor_size
  - Enums:    PascalCase + 'Enum'    e.g.  GenderEnum
  - PVs:      human-readable text    e.g.  'Male', 'Female'

JSON field mapping:
  steward                              -> class name (PascalCase)
  designations[0].designation          -> slot key (snake_case), slot.title
  definitions[0].definition            -> slot.description
  valueDomain.datatype                 -> slot.range
  valueDomain.permissibleValues        -> enum.permissible_values
  tinyId                               -> slot_uri (nlmcde:<tinyId>)
  designations[*] with tag
    'Preferred Question Text'          -> slot.annotations
"""

import os
import re
import yaml


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
    'text':       'string',
    'string':     'string',
    'char':       'string',
    'integer':    'integer',
    'int':        'integer',
    'float':      'float',
    'double':     'float',
    'date':       'date',
    'datetime':   'datetime',
    'boolean':    'boolean',
    'value list': 'string',   # overridden to enum when PVs present
}


def _map_datatype(raw: str) -> str:
    return _TYPE_MAP.get(str(raw).strip().lower(), 'string')


# --------------------------------------------------------------------------- #
# Main processor
# --------------------------------------------------------------------------- #

def process_nih_nlm_json(input_folder: str, output_file: str) -> None:
    """
    Read SearchExport.json from *input_folder* and emit a
    single LinkML YAML schema to *output_file*.
    """
    import json

    json_path = os.path.join(input_folder, 'SearchExport.json')
    with open(json_path, 'r', encoding='utf-8', errors='ignore') as fh:
        json_data = json.load(fh)

    linkml_schema = {
        'id':            'https://example.org/schemas/nih_nlm_cde',
        'name':          'NIH_NLM_CDESchema',
        'description':   'A schema representing NIH NLM Common Data Elements (CDEs).',
        'version':       '1.0.0',
        'default_range': 'string',
        'license':       'https://creativecommons.org/publicdomain/zero/1.0/',
        'imports':       ['linkml:types'],
        'prefixes': {
            'linkml': 'https://w3id.org/linkml/',
            'schema': 'http://schema.org/',
            'xsd':    'http://www.w3.org/2001/XMLSchema#',
            'NCIT':   'http://purl.obolibrary.org/obo/NCIT_',
            'UMLS':   'http://purl.bioontology.org/ontology/UMLS/',
            'nlmcde': 'http://example.org/nlmcde/',
        },
        'default_prefix': 'nlmcde',
        'classes':  {},
        'slots':    {},
        'enums':    {},
    }

    # dedup enums: choices_tuple -> enum_name
    _enum_registry: dict[tuple, str] = {}

    for entry in json_data:
        steward      = entry.get('steward', '').strip()
        value_domain = entry.get('valueDomain', {})
        value_type   = value_domain.get('datatype', 'Text')
        pvs          = value_domain.get('permissibleValues', [])
        tiny_id      = entry.get('tinyId', '')

        # --- designation -> slot key + title ---
        designations = entry.get('designations', [])
        if not designations:
            continue
        designation = designations[0].get('designation', '').strip()
        if not designation:
            continue

        slot_key = _to_snake_case(designation)
        title    = designation   # preserve original casing as human-readable title

        # --- definition -> slot.description ---
        definitions = entry.get('definitions', [])
        description = (
            definitions[0].get('definition', '').strip()
            if definitions else ''
        )

        # --- class from steward ---
        class_name = _to_pascal_case(steward) if steward else 'UnclassifiedCde'

        if class_name not in linkml_schema['classes']:
            linkml_schema['classes'][class_name] = {
                'description': f'CDEs stewarded by {steward}.',
                'slots': [],
            }

        # --- slot range ---
        range_val = _map_datatype(value_type)

        # --- slot ---
        slot: dict = {
            'title':       title,
            'description': description,
            'range':       range_val,
        }

        # --- slot_uri from tinyId ---
        if tiny_id:
            slot['slot_uri'] = f'nlmcde:{tiny_id}'

        # --- annotations ---
        annotations: dict = {}

        # preferred question text
        for des in designations:
            if 'Preferred Question Text' in des.get('tags', []):
                annotations['preferred_question_text'] = des.get('designation', '').strip()

        # registration status
        reg_state = entry.get('registrationState', {})
        if reg_state.get('registrationStatus'):
            annotations['registration_status'] = reg_state['registrationStatus']
        if reg_state.get('administrativeStatus'):
            annotations['administrative_status'] = reg_state['administrativeStatus']

        # copyright
        if entry.get('copyrightStatus'):
            annotations['copyright_status'] = entry['copyrightStatus']

        # NIH endorsed flag
        if entry.get('nihEndorsed'):
            annotations['nih_endorsed'] = 'true'

        # tags/keywords from properties
        for prop in entry.get('properties', []):
            if prop.get('key') == 'Tags/Keywords' and prop.get('value'):
                annotations['tags'] = prop['value']
                break

        # steward org name
        steward_org = entry.get('stewardOrg', {}).get('name', '')
        if steward_org:
            annotations['steward_org'] = steward_org

        # sources — collect source names
        sources = entry.get('sources', [])
        if sources:
            annotations['sources'] = ', '.join(
                s['sourceName'] for s in sources if s.get('sourceName')
            )

        # classification — collect element names
        classification = entry.get('classification', [])
        if classification:
            class_elements = []
            for c in classification:
                for el in c.get('elements', []):
                    if el.get('name'):
                        class_elements.append(el['name'])
            if class_elements:
                annotations['classification'] = ', '.join(class_elements)

        # part of bundles
        bundles = entry.get('partOfBundles', [])
        if bundles:
            annotations['part_of_bundles'] = ', '.join(str(b) for b in bundles)

        # created date
        if entry.get('created'):
            annotations['created'] = entry['created']

        if annotations:
            slot['annotations'] = annotations

        # --- permissible values -> enum ---
        if pvs:
            pv_labels = [pv['permissibleValue'] for pv in pvs]
            choices_key = tuple(pv_labels)

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
                for pv in pvs:
                    label = pv['permissibleValue']
                    pv_entry: dict = {}
                    # description from valueMeaningDefinition
                    defn = pv.get('valueMeaningDefinition')
                    if defn:
                        pv_entry['description'] = defn
                    # meaning URI — use first available concept only
                    source  = pv.get('conceptSource', '')
                    concept = pv.get('conceptId', '')
                    if concept and ':' not in concept:   # skip already-concatenated ids
                        if source == 'NCI Thesaurus':
                            pv_entry['meaning'] = f'NCIT:{concept}'
                        elif source == 'UMLS':
                            pv_entry['meaning'] = f'UMLS:{concept}'
                    pv_entries[label] = pv_entry or None

                linkml_schema['enums'][enum_name] = {
                    'permissible_values': pv_entries
                }

            slot['range'] = enum_name

        # first definition wins
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
        f"NIH NLM LinkML schema saved to {output_file} "
        f"({n_classes} classes, {n_slots} slots, {n_enums} enums)."
    )