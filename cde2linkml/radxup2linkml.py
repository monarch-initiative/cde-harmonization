import pandas as pd
import os
import yaml

# Dictionary to store sets of permissible values encountered
encountered_enum_sets = {}


# Function to check and return existing or new enum name based on choices
def get_enum_name(choices, slot_title):
    # Ensure slot_title is a string
    if not isinstance(slot_title, str):
        slot_title = str(slot_title) if slot_title is not None else "UnnamedSlot"

    # Clean choices by removing commas and keeping only the descriptive part
    cleaned_choices = [choice.split(',')[1].strip() if ',' in choice else choice.strip() for choice in choices]

    # Convert list of choices into a tuple for immutability
    choices_tuple = tuple(cleaned_choices)

    # Check if this set of choices already has an enum
    if choices_tuple not in encountered_enum_sets:
        # Generate unique enum name based on PascalCase slot title
        enum_name = ''.join(word.capitalize() for word in slot_title.split()) + "Enum"
        encountered_enum_sets[choices_tuple] = {'enum_name': enum_name, 'choices': cleaned_choices}
    else:
        enum_name = encountered_enum_sets[choices_tuple]['enum_name']

    return enum_name, cleaned_choices


# Type mapping for text validation
type_mapping = {
    'integer': 'integer',
    'float': 'float',
    'date': 'date',
    'datetime': 'datetime'
}


# Function to convert snake_case to PascalCase
def to_pascal_case(snake_str):
    components = snake_str.split('_')
    return ''.join(x.capitalize() for x in components)


# Function to generate a human-readable title from the slot name (variable_name)
def get_slot_title(variable_name):
    return ' '.join(word.capitalize() for word in variable_name.split('_'))


# Function to process RADx-UP CSV and generate the LinkML schema
def process_radxup_csv(input_folder, output_file):
    # Path to the RADx-UP CSV file (assuming it is located in the input folder)
    csv_file_path = os.path.join(input_folder, 'RADxUP_1.7_Phase3_Tier1_Tier2_DataDictionary-1.csv')

    # Read the CSV file
    data = pd.read_csv(csv_file_path, encoding='latin1')  # Try 'latin1' or 'ISO-8859-1'

    # Initialize LinkML schema
    linkml_schema = {
        'id': 'https://example.org/schemas/radxup_cde',
        'name': 'RADxUP_CDESchema',
        'description': 'A schema representing RADxUP Common Data Elements (CDEs).',
        'version': '1.0.0',
        'default_range': 'string',
        'source': 'https://example.org/source_of_the_cde',
        'imports': ['https://w3id.org/linkml/types'],
        'prefixes': {
            'linkml': 'https://w3id.org/linkml/',
            'schema': 'http://schema.org/',
            'xsd': 'http://www.w3.org/2001/XMLSchema#'
        },
        'classes': {},
        'slots': {},
        'enums': {}
    }

    # Iterate through each row in the dataset
    for index, row in data.iterrows():
        form_name = row['Form Name']
        variable_name = row['Variable / Field Name']
        field_label = row['Field Label']
        choices = row['Choices, Calculations, OR Slider Labels'].split('|') if pd.notna(
            row['Choices, Calculations, OR Slider Labels']) else []
        text_validator = row['Text Validation Type OR Show Slider Number']
        min_value = row['Text Validation Min'] if pd.notna(row['Text Validation Min']) else None
        max_value = row['Text Validation Max'] if pd.notna(row['Text Validation Max']) else None

        # Convert form name to PascalCase for class naming
        class_name = to_pascal_case(form_name)

        # Create class if it does not exist
        if class_name not in linkml_schema['classes']:
            linkml_schema['classes'][class_name] = {
                'title': form_name,
                'description': f'Description of {form_name}.',
                'slots': []
            }

        # Add slot name to the form class
        linkml_schema['classes'][class_name]['slots'].append(variable_name)

        # Get a more human-readable title for the slot
        slot_title = get_slot_title(variable_name)

        # Create slot definition with title for the slot
        slot = {
            'title': slot_title,
            'description': field_label,
            'range': None,
        }

        # Add min/max value constraints if present
        if min_value:
            slot['minimum_value'] = min_value
        if max_value:
            slot['maximum_value'] = max_value

        # Generate a unique enum name based on choices and set the range
        if choices:
            enum_name, cleaned_choices = get_enum_name(choices, slot_title)

            # If it's a new enum, create a new enum definition without description
            if enum_name not in linkml_schema['enums']:
                linkml_schema['enums'][enum_name] = {
                    'permissible_values': {choice: None for choice in cleaned_choices}
                }

            # Set the slot's range to the enum name with the 'Enum' suffix
            slot['range'] = enum_name

        # Add the slot definition
        linkml_schema['slots'][variable_name] = slot

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

    print(f"LinkML schema for RADxUP CDE generated and saved successfully to {output_file}.")
