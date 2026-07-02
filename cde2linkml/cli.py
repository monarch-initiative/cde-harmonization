import argparse
import glob
import os

from cde2linkml.radxup2linkml       import process_radxup_csv
from cde2linkml.nlm2linkml          import process_nih_nlm_json
from cde2linkml.phenx2linkml        import process_phenx_folder
from cde2linkml.heal2linkml         import process_heal_folder
from cde2linkml.connects2linkml     import process_connects_file
from cde2linkml.curegn2linkml       import process_curegn_file
from cde2linkml.kpmp2linkml         import process_kpmp_folder
from cde2linkml.neptune2linkml      import process_neptune_file
from cde2linkml.cric2linkml         import process_cric_folder
from cde2linkml.bdc2linkml          import process_bdc_folder
from cde2linkml.bundle_phenx2linkml import process_phenx_bundle
from cde2linkml.omop2linkml         import process_omop_bundle


DEFAULT_INPUTS = {
    "radx-up":      "data/cde-radx-up",
    "nih-nlm":      "data/cde-nlm",
    "phenx":        "data/cde-phenx",
    "heal":         "data/cde-heal",
    "connects":     "data/cde-connects",
    "curegn":       "data/dd-niddk-curegn",
    "kpmp":         "data/dd-niddk-kpmp",
    "neptune":      "data/dd-niddk-neptune",
    "cric":         "data/dd-niddk-cric",
    "bdc":          "data/BDC",
    # These two are *folders* — the actual xlsx filename is auto-discovered
    # at runtime by _resolve_xlsx_default(), since it varies (CDM version,
    # scrape date, etc.) and shouldn't be hardcoded here.
    "phenx-bundle": "data/bundle-phenx",
    "omop":         "data/cdm-omop",
}


# ─────────────────────────────────────────────────────────────────────────────
# Input validators
# ─────────────────────────────────────────────────────────────────────────────

def check_and_prompt_folder(folder_path, download_message):
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist.")
        print("Please download the data by running 'make' commands as follows:")
        print("  make download-radx-up-cde    # For RADx-UP data")
        print("  make download-nlm-cde        # For NIH NLM data")
        print("  make download-phenx-cde      # For PhenX data")
        print("  make download-heal-cde       # For HEAL data")
        print("  make download-connects-cde   # For CONNECTS data")
        print(download_message)
        return False
    return True


def check_and_prompt_file(file_path, download_message):
    if not file_path or not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        print(download_message)
        return False
    return True


def _resolve_xlsx_default(folder_path):
    """
    Return the most recently modified .xlsx file in folder_path, or None if
    the folder is missing/empty. Used so DEFAULT_INPUTS doesn't need to
    hardcode a version- or date-specific filename (e.g. omop_5.4.xlsx,
    phenx_2026.xlsx) — any xlsx dropped in the folder is picked up.
    """
    if not os.path.isdir(folder_path):
        return None
    candidates = glob.glob(os.path.join(folder_path, "*.xlsx"))
    if not candidates:
        return None
    if len(candidates) > 1:
        print(
            f"Note: multiple .xlsx files found in '{folder_path}', "
            f"using the most recently modified one. "
            f"Pass --input-folder to pick a specific file."
        )
    return max(candidates, key=os.path.getmtime)


# ─────────────────────────────────────────────────────────────────────────────
# Dispatch
# ─────────────────────────────────────────────────────────────────────────────

def process_command(command, input_path, output_folder):

    if command == "radx-up":
        if not check_and_prompt_folder(input_path, "Download RADx-UP data to 'data/cde-radx-up'."):
            return
        process_radxup_csv(input_path, os.path.join(output_folder, "radx_up_schema.yaml"))

    elif command == "nih-nlm":
        if not check_and_prompt_folder(input_path, "Download NIH NLM data to 'data/cde-nlm'."):
            return
        process_nih_nlm_json(input_path, os.path.join(output_folder, "nih_nlm_schema.yaml"))

    elif command == "phenx":
        if not check_and_prompt_folder(input_path, "Download PhenX data to 'data/cde-phenx'."):
            return
        process_phenx_folder(input_path, os.path.join(output_folder, "phenx_schema.yaml"))

    elif command == "heal":
        if not check_and_prompt_folder(input_path, "Download HEAL data to 'data/cde-heal'."):
            return
        process_heal_folder(input_path, os.path.join(output_folder, "heal_schema.yaml"))

    elif command == "connects":
        if not check_and_prompt_folder(input_path, "Download CONNECTS data to 'data/cde-connects'."):
            return
        process_connects_file(input_path, os.path.join(output_folder, "connects_schema.yaml"))

    elif command == "curegn":
        if not check_and_prompt_folder(input_path, "Place CureGN xlsx file in 'data/dd-niddk-curegn'."):
            return
        process_curegn_file(input_path, os.path.join(output_folder, "curegn_schema.yaml"))

    elif command == "kpmp":
        if not check_and_prompt_folder(input_path, "Place KPMP CSV file(s) in 'data/dd-niddk-kpmp'."):
            return
        process_kpmp_folder(input_path, os.path.join(output_folder, "kpmp_schema.yaml"))

    elif command == "neptune":
        if not check_and_prompt_folder(input_path, "Place NEPTUNE xlsx file in 'data/dd-niddk-neptune'."):
            return
        process_neptune_file(input_path, os.path.join(output_folder, "neptune_schema.yaml"))

    elif command == "cric":
        if not check_and_prompt_folder(input_path, "Place CRIC xlsx file(s) in 'data/dd-niddk-cric'."):
            return
        process_cric_folder(input_path, os.path.join(output_folder, "cric_schema.yaml"))

    elif command == "bdc":
        if not check_and_prompt_folder(input_path, "Place BDC_*.csv files in 'data/BDC'."):
            return
        process_bdc_folder(input_path, output_folder)

    elif command == "phenx-bundle":
        if not check_and_prompt_file(
            input_path,
            "No xlsx file found in 'data/bundle-phenx'.\n"
            "Run: make download-phenx-protocols\n"
            "     (Or pass --input-folder with the full path to an existing xlsx file.)"
        ):
            return
        process_phenx_bundle(
            input_path,
            os.path.join(output_folder, "phenx_bundle_schema.yaml")
        )

    elif command == "omop":
        if not check_and_prompt_file(
            input_path,
            "No xlsx file found in 'data/cdm-omop'.\n"
            "Run: make download-omop-cdm OMOP_VERSION=5.4\n"
            "     (Or pass --input-folder with the full path to an existing xlsx file.)"
        ):
            return
        process_omop_bundle(
            input_path,
            os.path.join(output_folder, "omop_cdm_schema.yaml")
        )


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate LinkML schemas from CDE data."
    )

    # ── source flags ──────────────────────────────────────────────────────────
    parser.add_argument("--radx-up",      action="store_true", help="Process RADx-UP CDE data")
    parser.add_argument("--nih-nlm",      action="store_true", help="Process NIH NLM CDE data")
    parser.add_argument("--phenx",        action="store_true", help="Process PhenX CDE data (CSV files)")
    parser.add_argument("--heal",         action="store_true", help="Process HEAL CDE data")
    parser.add_argument("--connects",     action="store_true", help="Process NHLBI CONNECTS CDE data")
    parser.add_argument("--curegn",       action="store_true", help="Process CureGN SAF data dictionary")
    parser.add_argument("--kpmp",         action="store_true", help="Process KPMP data dictionary")
    parser.add_argument("--neptune",      action="store_true", help="Process NEPTUNE data dictionary")
    parser.add_argument("--cric",         action="store_true", help="Process CRIC data dictionary")
    parser.add_argument("--bdc",          action="store_true",
                        help="Process BioData Catalyst (BDC) CSV data dictionaries")
    parser.add_argument("--phenx-bundle", action="store_true",
                        help=(
                            "Generate bundle_phenx LinkML schema from the xlsx produced by "
                            "'make download-phenx-protocols' (auto-discovered in "
                            "data/bundle-phenx/). "
                            "Output: linkml/phenx_bundle_schema.yaml. "
                            "Used to build the bundle_phenx ChromaDB collection with CURATE "
                            "for mapping all other sources against PhenX protocols."
                        ))
    parser.add_argument("--omop",         action="store_true",
                        help=(
                            "Generate cdm_omop LinkML schema from the xlsx produced by "
                            "'make download-omop-cdm' (auto-discovered in data/cdm-omop/, "
                            "any CDM version). "
                            "Output: linkml/omop_cdm_schema.yaml. "
                            "Used to build the cdm_omop ChromaDB collection with CURATE "
                            "for mapping all other sources against OMOP CDM columns."
                        ))

    # ── path overrides ────────────────────────────────────────────────────────
    parser.add_argument(
        "--input-folder", type=str, default=None,
        help=(
            "Input path override (default varies by source). "
            "For --phenx-bundle: path to a specific xlsx file "
            "(default: auto-discovered in data/bundle-phenx/). "
            "For --omop: path to a specific xlsx file "
            "(default: auto-discovered in data/cdm-omop/). "
            "For all others: path to folder containing source data."
        )
    )
    parser.add_argument(
        "--output-folder", type=str, default="linkml",
        help="Output folder for generated YAML files (default: linkml/)"
    )

    args = parser.parse_args()

    # ── guard: at least one flag required ─────────────────────────────────────
    if not any([
        args.radx_up, args.nih_nlm, args.phenx, args.heal, args.connects,
        args.curegn, args.kpmp, args.neptune, args.cric, args.bdc,
        args.phenx_bundle, args.omop,
    ]):
        print(
            "Error: No dataset flag provided. Use one or more of:\n"
            "  --radx-up  --nih-nlm  --phenx  --heal  --connects\n"
            "  --curegn   --kpmp     --neptune --cric  --bdc\n"
            "  --phenx-bundle  --omop"
        )
        parser.print_help()
        return

    os.makedirs(args.output_folder, exist_ok=True)

    # ── dispatch ──────────────────────────────────────────────────────────────
    if args.radx_up:
        process_command("radx-up",  args.input_folder or DEFAULT_INPUTS["radx-up"],  args.output_folder)
    if args.nih_nlm:
        process_command("nih-nlm",  args.input_folder or DEFAULT_INPUTS["nih-nlm"],  args.output_folder)
    if args.phenx:
        process_command("phenx",    args.input_folder or DEFAULT_INPUTS["phenx"],    args.output_folder)
    if args.heal:
        process_command("heal",     args.input_folder or DEFAULT_INPUTS["heal"],     args.output_folder)
    if args.connects:
        process_command("connects", args.input_folder or DEFAULT_INPUTS["connects"], args.output_folder)
    if args.curegn:
        process_command("curegn",   args.input_folder or DEFAULT_INPUTS["curegn"],   args.output_folder)
    if args.kpmp:
        process_command("kpmp",     args.input_folder or DEFAULT_INPUTS["kpmp"],     args.output_folder)
    if args.neptune:
        process_command("neptune",  args.input_folder or DEFAULT_INPUTS["neptune"],  args.output_folder)
    if args.cric:
        process_command("cric",     args.input_folder or DEFAULT_INPUTS["cric"],     args.output_folder)
    if args.bdc:
        process_command("bdc",      args.input_folder or DEFAULT_INPUTS["bdc"],      args.output_folder)
    if args.phenx_bundle:
        process_command(
            "phenx-bundle",
            args.input_folder or _resolve_xlsx_default(DEFAULT_INPUTS["phenx-bundle"]),
            args.output_folder,
        )
    if args.omop:
        process_command(
            "omop",
            args.input_folder or _resolve_xlsx_default(DEFAULT_INPUTS["omop"]),
            args.output_folder,
        )


if __name__ == "__main__":
    main()