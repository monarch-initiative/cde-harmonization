import json
import os
import yaml


# Function to check if the folder exists and prompt the user
def check_and_prompt_folder(folder_path, prompt_message):
    if not os.path.exists(folder_path):
        print(prompt_message)
        return False
    return True


# Function to ensure the output folder exists
def ensure_output_folder(output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)


# NIH NLM CDE parser
def process_nih_nlm_json(input_folder, output_file):

    # Load the JSON data
    json_file_path = os.path.join(input_folder, "SearchExport.json")
    with open(json_file_path, "r", encoding="utf-8", errors="ignore") as file:
        json_data = json.load(file)

    # Initialize LinkML schema
    linkml_schema = {
        'id': 'https://example.org/schemas/nih_nlm_cde',
        'name': 'NIH_NLM_CDESchema',
        'description': 'A schema representing NIH and NLM Common Data Elements (CDEs).',
        'version': '1.0.0',
        'default_range': 'string',
        'source': 'https://example.org/source_of_the_cde',
        'imports': ['https://w3id.org/linkml/types'],
        'prefixes': {
            'linkml': 'https://w3id.org/linkml/',
            'schema': 'http://schema.org/',
            'xsd': 'http://www.w3.org/2001/XMLSchema#',
            'NCIT': 'http://purl.obolibrary.org/obo/NCIT_',
            'nlmcde': 'http://example.org/nlmcde/'
        },
        'classes': {},
        'slots': {},
        'enums': {}
    }

    # Dictionary to store sets of permissible values encountered and their associated slot titles
    encountered_enum_sets = {}

    # Function to check and return existing or new enum name based on choices
    def get_enum_name(choices, slot_title):
        choices_tuple = tuple(choices)
        if choices_tuple not in encountered_enum_sets:
            enum_name = ''.join(word.capitalize() for word in slot_title.split()) + "Enum"
            encountered_enum_sets[choices_tuple] = {'enum_name': enum_name, 'titles': [slot_title]}
        else:
            enum_name = encountered_enum_sets[choices_tuple]['enum_name']
            encountered_enum_sets[choices_tuple]['titles'].append(slot_title)

        return enum_name

    # Type mapping for value types
    type_mapping = {
        'Text': 'string',
        'Integer': 'float',  # Integer mapped to float
        'Float': 'float',
        'Date': 'date',
        'Value List': 'string',  # Value List will be handled by enum creation
    }

    # Function to format class names and titles
    def format_class_name(name):
        formatted_name = ''.join(word.capitalize() for word in name.split())
        title = name.replace('_', ' ').title()  # Create title from the original name
        return formatted_name, title

    # Function to process each entry in the JSON data
    def process_json_entry(entry):
        steward = entry.get('steward', '')
        value_domain = entry.get('valueDomain', {})
        value_type = value_domain.get('datatype', 'Text')
        permissible_values = value_domain.get('permissibleValues', [])

        # Extract the first designation name if available
        designations = entry.get('designations', [])
        designation = designations[0].get('designation', '') if designations else ''

        if not designation:  # Ensure there's a valid name
            return

            # Extract the first definition if available
        definitions = entry.get('definitions', [])
        definition = definitions[0].get('definition', '') if definitions else f"Description for {designation}"

        tiny_id = entry.get('tinyId', '')

        # Format steward as class name and title
        class_name, class_title = format_class_name(steward)

        # Create class for Steward if not already created
        if class_name not in linkml_schema['classes']:
            linkml_schema['classes'][class_name] = {
                'title': steward,
                'description': f'{steward} description.',
                'slots': []
            }

        # Create slot definition
        slot = {
            'title': designation.replace('_', ' ').title(),
            'description': definition,  # Use extracted definition
            'range': type_mapping.get(value_type, 'string'),
            'slot_uri': f'nlmcde:{tiny_id}' if tiny_id else ''
        }

        # Add annotations if the designation has the "Preferred Question Text" tag
        annotations = {}
        for des in designations:
            if "Preferred Question Text" in des.get('tags', []):
                annotations["Preferred_Question_Text"] = {
                    'tag': 'Preferred_Question_Text',
                    'value': des.get('designation', '')
                }

        if annotations:
            slot['annotations'] = annotations

        if permissible_values:
            enum_name = get_enum_name([pv['permissibleValue'] for pv in permissible_values], slot['title'])
            if enum_name not in linkml_schema['enums']:
                linkml_schema['enums'][enum_name] = {
                    'permissible_values': {
                        pv['permissibleValue'].replace(' ', '%20'): {
                            'title': pv['permissibleValue'],
                            **({'description': pv['valueMeaningDefinition']} if pv.get(
                                'valueMeaningDefinition') not in [None, ''] else {}),
                            **({'meaning': f"NCIT:{pv['conceptId']}"} if pv.get(
                                'conceptSource') == 'NCI Thesaurus' and pv.get('conceptId') else {})
                        } for pv in permissible_values
                    }
                }

                # Remove empty descriptions
                linkml_schema['enums'][enum_name]['permissible_values'] = {
                    key: {k: v for k, v in value.items() if k != 'description' or v}
                    for key, value in linkml_schema['enums'][enum_name]['permissible_values'].items()
                }

            slot['range'] = enum_name

        # Add the slot definition to the 'slots' dictionary using the processed name
        slot_key = designation.replace(" ", "_")
        linkml_schema['slots'][slot_key] = slot

        # Add the slot name to the steward's class
        linkml_schema['classes'][class_name]['slots'].append(slot_key)

    # Process only the first 100 entries in the JSON data
    for entry in json_data:
        process_json_entry(entry)

    # Custom YAML dumper to remove quotes from permissible values
    class CustomDumper(yaml.SafeDumper):
        def represent_str(self, data):
            return self.represent_scalar('tag:yaml.org,2002:str', data)

    CustomDumper.add_representer(str, CustomDumper.represent_str)

    # Save the LinkML schema to a YAML file
    def save_to_yaml_file(data, file_path):
        linkml_yaml = yaml.dump(data, Dumper=CustomDumper, sort_keys=False, default_flow_style=False)
        linkml_yaml = linkml_yaml.replace(': null', ':')  # Remove ": null" from YAML
        with open(file_path, 'w') as file:
            file.write(linkml_yaml)

    # Save the schema
    save_to_yaml_file(linkml_schema, output_file)

    print(f"LinkML schema for NIH NLM CDE generated and saved to {output_file}.")
