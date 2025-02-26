import os
import pandas as pd
import yaml

def get_enum_name(slot_name, choices, encountered_enum_sets):
    """Generate or retrieve an enum name based on permissible values."""
    choices_tuple = tuple(choices)
    if choices_tuple not in encountered_enum_sets:
        enum_name = f"{slot_name.replace('_', '')}Enum"
        encountered_enum_sets[choices_tuple] = enum_name
    else:
        enum_name = encountered_enum_sets[choices_tuple]
    return enum_name

def process_phenx_folder(input_folder, output_file):
    """Process the PhenX CDE files from the input folder and generate LinkML schema."""
    linkml_schema = {
        'id': 'https://example.org/schemas/phenx_cde',
        'name': 'PhenX_CDESchema',
        'description': 'A schema representing PhenX Common Data Elements (CDEs).',
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

    encountered_enum_sets = {}

    # Counters for processed, multi-indexed files, and files without slots
    processed_files_count = 0
    multi_indexed_files_count = 0
    no_slot_files_count = 0

    for file_name in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file_name)
        if file_name.endswith(('.csv', '.tsv')):
            delimiter = ',' if file_name.endswith('.csv') else '\t'

            # Handle encoding errors by using 'latin1' or 'ignore'
            try:
                df = pd.read_csv(file_path, delimiter=delimiter, encoding='utf-8', on_bad_lines='skip', quotechar='"')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, delimiter=delimiter, encoding='latin1', on_bad_lines='skip')

            # Check if the dataframe is multi-indexed and ignore if true
            if isinstance(df.index, pd.MultiIndex):
                multi_indexed_files_count += 1
                continue  # Skip this file if it's multi-indexed

            class_name = os.path.splitext(file_name)[0]

            linkml_schema['classes'][class_name] = {
                'description': f'{class_name} class generated from PhenX CDE file.',
                'slots': []
            }

            # Flag to check if any slots are added for this class
            has_slots = False

            for _, row in df.iterrows():
                varname = row.get('VARNAME')
                vardesc = row.get('VARDESC', '')
                var_type = row.get('TYPE', 'string')
                max_value = row.get('MAX', None)
                min_value = row.get('MIN', None)
                choices = []

                value = row.get('VALUES', None)

                # Check if the value is a string and concatenate with values to the right
                if isinstance(value, str) and pd.notna(value):
                    concatenated_value = value  # Start with the VALUE column

                    # Concatenate with the values to the right of 'VALUE'
                    value_start_idx = df.columns.get_loc('VALUES') + 1  # Get the index of the first column after 'VALUE'
                    for col in df.columns[value_start_idx:]:
                        value_right = row.get(col)
                        if pd.notna(value_right):
                            concatenated_value += f"|{str(value_right)}"

                    # Split the concatenated string by '|' and add choices
                    choices.extend(concatenated_value.split('|'))

                choices = list(set(choices))  # Remove duplicates if any

                # Skip row if 'VARNAME' is missing
                if pd.isna(varname):
                    continue

                # Ensure var_type is a string before calling .lower()
                if isinstance(var_type, str):
                    var_type = var_type.lower() if var_type.lower() in ['integer', 'float', 'string', 'date'] else 'string'
                else:
                    var_type = 'string'

                # Create the slot entry (Only for VARNAME)
                slot = {
                    'description': vardesc,
                    'range': var_type,
                }

                # Set min and max constraints if provided
                if var_type in ['integer', 'float']:
                    if pd.notna(min_value):
                        slot['minimum_value'] = min_value
                    if pd.notna(max_value):
                        slot['maximum_value'] = max_value

                # If choices exist, add an enum
                if choices:
                    enum_name = get_enum_name(varname, choices, encountered_enum_sets)
                    if enum_name not in linkml_schema['enums']:
                        linkml_schema['enums'][enum_name] = {
                            'permissible_values': {choice: None for choice in choices}
                        }
                    slot['range'] = enum_name

                # Add the slot to the schema
                linkml_schema['slots'][varname] = slot
                linkml_schema['classes'][class_name]['slots'].append(varname)

                # Mark as having slots
                has_slots = True

            # If no slots, increment the counter and discard this class
            if not has_slots:
                no_slot_files_count += 1
                del linkml_schema['classes'][class_name]  # Discard the class with no slots
            else:
                processed_files_count += 1

    # YAML Dumper customization
    class CustomDumper(yaml.SafeDumper):
        def represent_str(self, data):
            return self.represent_scalar('tag:yaml.org,2002:str', data)

    CustomDumper.add_representer(str, CustomDumper.represent_str)

    def save_to_yaml_file(data, file_path):
        linkml_yaml = yaml.dump(data, Dumper=CustomDumper, sort_keys=False, default_flow_style=False)
        linkml_yaml = linkml_yaml.replace(': null', ':')
        with open(file_path, 'w') as file:
            file.write(linkml_yaml)

    # Save the schema
    save_to_yaml_file(linkml_schema, output_file)

    # Print the final counts
    #print(f"Total processed files: {processed_files_count}")
    #print(f"Total multi-indexed files (not processed): {multi_indexed_files_count}")
    #print(f"Total no slot files (not processed): {no_slot_files_count}")

    print(f"LinkML schema for PhenX CDE generated and saved to {output_file} successfully.")
