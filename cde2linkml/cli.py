import argparse
import os

from cde2linkml.radxup2linkml import process_radxup_csv
from cde2linkml.nlm2linkml import process_nih_nlm_json
from cde2linkml.phenx2linkml import process_phenx_folder
from cde2linkml.heal2linkml import process_heal_folder

DEFAULT_INPUTS = {
    "radx-up": "data/cde-radx-up",
    "nih-nlm":  "data/cde-nlm",
    "phenx":    "data/cde-phenx",
    "heal":     "data/cde-heal",
}


def check_and_prompt_folder(folder_path, download_message):
    """Check if folder exists; if not, prompt user to download."""
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist.")
        print("Please download the data by running 'make' commands as follows:")
        print("  make download-radx-up-cde   # For RADx-UP data")
        print("  make download-nlm-cde       # For NIH NLM data")
        print("  make download-phenx-cde     # For PhenX data")
        print("  make download-heal-cde      # For HEAL data")
        print(download_message)
        return False
    return True


def ensure_output_folder(output_folder):
    """Ensure the output folder exists."""
    os.makedirs(output_folder, exist_ok=True)


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

    elif command == "heal":
        if not check_and_prompt_folder(input_folder, "Download HEAL data to 'data/cde-heal'."):
            return
        process_heal_folder(input_folder, os.path.join(output_folder, "heal_schema.yaml"))


def main():
    parser = argparse.ArgumentParser(description="Generate LinkML schemas from CDE data.")

    parser.add_argument('--radx-up',  action='store_true', help="Process RADx-UP CDE data")
    parser.add_argument('--nih-nlm',  action='store_true', help="Process NIH NLM CDE data")
    parser.add_argument('--phenx',    action='store_true', help="Process PhenX CDE data")
    parser.add_argument('--heal',     action='store_true', help="Process HEAL CDE data")

    parser.add_argument('--input-folder',  type=str, default=None,    help="Input folder (overrides default)")
    parser.add_argument('--output-folder', type=str, default="linkml", help="Output folder (default: linkml/)")

    args = parser.parse_args()

    if not any([args.radx_up, args.nih_nlm, args.phenx, args.heal]):
        print("Error: No dataset flag provided. Use '--radx-up', '--nih-nlm', '--phenx', or '--heal'.")
        parser.print_help()
        return

    ensure_output_folder(args.output_folder)

    if args.radx_up:
        process_command("radx-up", args.input_folder or DEFAULT_INPUTS["radx-up"], args.output_folder)

    if args.nih_nlm:
        process_command("nih-nlm", args.input_folder or DEFAULT_INPUTS["nih-nlm"], args.output_folder)

    if args.phenx:
        process_command("phenx", args.input_folder or DEFAULT_INPUTS["phenx"], args.output_folder)

    if args.heal:
        process_command("heal", args.input_folder or DEFAULT_INPUTS["heal"], args.output_folder)


if __name__ == "__main__":
    main()