import pandas as pd

# Replace 'your_file.xls' with the path to your XLS file
xls_file_path = 'optn-star-files-data-dictionary.xlsx'
output_dir = 'tsv/'

# Read the XLS file
xls = pd.ExcelFile(xls_file_path)

# Iterate over each sheet in the XLS file
for sheet_name in xls.sheet_names:
    # Read the sheet into a DataFrame
    df = pd.read_excel(xls, sheet_name=sheet_name)

    # Define the TSV file name
    base_name = xls_file_path.split('/')[-1].split('.')[0]
    tsv_file_name = f"{output_dir}{base_name}_{sheet_name}.tsv"

    # Write the DataFrame to a TSV file
    df.to_csv(tsv_file_name, sep='\t', index=False)

    print(f"Saved {sheet_name} to {tsv_file_name}")
