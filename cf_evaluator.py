#!/usr/bin/env python3
"""
Script to perform cfchecks on the o3as database.
"""
import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

import dask
import yaml

# Initialize environment --------------------------------------------
def set_verbosity(value):
    global VERBOSITY
    VERBOSITY = value
    logging.basicConfig(
        level=getattr(logging, VERBOSITY),
        format='%(asctime)s main ---- %(levelname)-8s %(message)s',
    )

def set_output(value):
    global OUTPUT
    OUTPUT = Path(value)

def set_sources(value):
    global SOURCES
    SOURCES = Path(value)

def set_source_file(value):
    global SOURCE_FILE
    SOURCE_FILE = Path(value)     


# Script arguments definition ---------------------------------------
parser = argparse.ArgumentParser(
    prog='PROG', description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="See '<command> --help' to read about a specific sub-command.")
parser.add_argument(
    "-v", "--verbosity", type=str, default='INFO', 
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    help="Sets the logging level (default: %(default)s)")
parser.add_argument(
    "-o", "--output", type=str, default='Skimmed',
    help="Output folder for cfcheck files (default: %(default)s)")
parser.add_argument(
    "-s", "--sources", type=str, default='Sources',
    help="Sources folder for input paths (default: %(default)s)")
parser.add_argument(
    "--source_file", type=str, default='sources.yaml',
    help="Path to source file with skimming configurations")


# Script command actions --------------------------------------------
def run_command(
    verbosity, output, sources, source_file, **options
):
    # Common operations
    set_verbosity(verbosity)
    logging.info("Program start")
    logging.debug(f"Working directory:\n{os.getcwd()}")
    logging.debug(f"List directory:\n{os.listdir()}")
    set_output(output)
    logging.debug(f"Output dir files:\n{os.listdir(OUTPUT)}")
    set_sources(sources)
    logging.debug(f"Source dir files:\n{os.listdir(SOURCES)}")
    set_source_file(source_file)

    # Read source file
    logging.info("Reading source files %s", SOURCE_FILE)
    with open(SOURCE_FILE, 'r') as stream:
        models = yaml.safe_load(stream)
    logging.debug(f"Source file:\n{models}")

    # Define pool processes
    logging.info("Computing cfcheck pool of models")
    dask.compute(*[
        dask.delayed(worker_call)(model, **kwargs) 
        for model, kwargs in models.items()
    ])

    # End of program
    logging.info("End of program")


# Worker actions ----------------------------------------------------
def worker_call(model, tco3_zm, **kwargs):
    logger = logging.getLogger(f"Checking:{model}")
    output_folder = Path(f"{OUTPUT}/{model}")
    logger.info(f"Checking output on directory:\n{output_folder}")
    eval_tco3(output_folder, **tco3_zm)


def eval_tco3(
    output_folder,  # Output location for the check file
    paths,  # Path with the CF netCDF files
    **kwargs,  # Unused arguments
):
    # Common operations
    output_file = f"{output_folder}/cfchecks_output.txt"
    os.makedirs(Path(output_folder), exist_ok=True)

    # Loading of DataArray and attributes
    paths = f"{SOURCES}/{paths}"
    call = f"cfchecks --version=auto {paths}"
    with open(output_file, "w") as f:
        subprocess.run(call, shell=True, stdout=f)

    # End of program
    return None


# Main call ---------------------------------------------------------
if __name__ == "__main__":
    args = parser.parse_args()
    # try:
    run_command(**vars(args))
    sys.exit(0)  # Shell return 0 == success
