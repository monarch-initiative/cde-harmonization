# python3 -m cde2linkml.cli -h
# python3 -m cde2linkml.cli phenx/nih-nlm/radx-up

import argparse
import os
from cde2linkml.radxup2linkml import process_radxup_csv
from cde2linkml.nlm2linkml import process_nih_nlm_json
from cde2linkml.phenx2linkml import process_phenx_folder

DEFAULT_INPUTS = {
    "radx-up": "data/cde-radx-up",
    "nih-nlm": "data/cde-nlm",
    "phenx": "data/cde-phenx",
}


def check_and_prompt_folder(folder_path, download_message):
    """Check if folder exists; if not, prompt user to download."""
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist.")
        print(f"Please download the data by running 'make' commands as follows:")
        print(f"  make download-radx-up    # For RADx-UP data")
        print(f"  make download-nih-nlm    # For NIH NLM data")
        print(f"  make download-phenx      # For PhenX data")
        print(download_message)
        return False
    return True


def ensure_output_folder(output_folder):
    """Ensure the output folder exists."""
    os.makedirs(output_folder, exist_ok=True)
    print(f"Output folder set to: {output_folder}")


def process_command(command, input_folder, output_folder):
    """Process the selected command with input and output folders."""
    if command == "radx-up":
        if not check_and_prompt_folder(input_folder, "Download RADx-UP data to 'data/cde-radx-up'."):
            return
        process_radxup_csv(input_folder, os.path.join(output_folder, "radx_up_schema.yaml"))

    elif command == "nih-nlm":
        if not check_and_prompt_folder(input_folder, "Download NIH NLM data to 'data/cde-nlm'."):
            return
        process_nih_nlm_json(input_folder, os.path.join(output_folder, "nih_nlm_schema.yaml"))

    elif command == "phenx":
        if not check_and_prompt_folder(input_folder, "Download PhenX data to 'data/cde-phenx'."):
            return
        process_phenx_folder(input_folder, os.path.join(output_folder, "phenx_schema.yaml"))


def main():
    parser = argparse.ArgumentParser(description="Generate LinkML schemas from CDE data.")

    # Flags for the datasets
    parser.add_argument('--radx-up', action='store_true', help="Process RADx-UP CDE data")
    parser.add_argument('--nih-nlm', action='store_true', help="Process NIH NLM CDE data")
    parser.add_argument('--phenx', action='store_true', help="Process PhenX CDE data")

    # Flags for input and output directories (optional)
    parser.add_argument('--input-folder', type=str, default=None, help="Input folder")
    parser.add_argument('--output-folder', type=str, default="linkml", help="Output folder")

    args = parser.parse_args()

    # Ensure at least one flag is selected
    if not (args.radx_up or args.nih_nlm or args.phenx):
        print("Error: No dataset flag provided. Use '--radx-up', '--nih-nlm', or '--phenx'.")
        parser.print_help()
        return

    # Process flags for each dataset
    if args.radx_up:
        input_folder = args.input_folder or DEFAULT_INPUTS["radx-up"]
        ensure_output_folder(args.output_folder)
        process_command("radx-up", input_folder, args.output_folder)

    if args.nih_nlm:
        input_folder = args.input_folder or DEFAULT_INPUTS["nih-nlm"]
        ensure_output_folder(args.output_folder)
        process_command("nih-nlm", input_folder, args.output_folder)

    if args.phenx:
        input_folder = args.input_folder or DEFAULT_INPUTS["phenx"]
        ensure_output_folder(args.output_folder)
        process_command("phenx", input_folder, args.output_folder)


if __name__ == "__main__":
    main()
