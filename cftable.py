#!/usr/bin/env python3
"""
Script to collect cfchecks information into csv file.
"""
import argparse
import logging
import os
import sys

import dask
import pandas as pd

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
    "-o", "--output", type=str, default='cfchecks_output.csv',
    help="Output folder for skimmed files (default: %(default)s)")
parser.add_argument(
    "-s", "--skimmed", type=str, default='Skimmed',
    help="Skimmed folder for collecting files (default: %(default)s)")


# Script command actions --------------------------------------------
def run_command(verbosity, output, skimmed, **options):
    logging.basicConfig(
        level=getattr(logging, verbosity),
        format='%(asctime)s  %(levelname)-8s %(message)s'
    )
    
    # Common operations
    logging.info("Program start")
    logging.debug(f"Working directory:\n{os.getcwd()}")
    logging.debug(f"List directory:\n{os.listdir()}")

    # Collection skimmed sources
    logging.info("Collecting folders at %s", skimmed)
    is_dir = lambda n: os.path.isdir(os.path.join(skimmed, n))
    models = [m for m in os.listdir(skimmed) if is_dir(m)]
    logging.debug(f"Skimmed dir:\n{skimmed}")
    logging.debug(f"Models:\n{models}")

    # Define pool processes
    logging.info("Computing collection pool for models")
    checks_list = dask.compute(*[
        dask.delayed(worker_call)(skimmed, model) 
        for model in models
    ])

    # Saving into output file
    logging.info("Saving info to %s", output)
    checks = {k: v for d in checks_list for k, v in d.items()}
    pd.DataFrame(checks).transpose().to_csv(output, sep=';')


    # End of program
    logging.info("End of program")


# Worker actions ----------------------------------------------------
def worker_call(skimmed, model):
    try:
        return worker_command(skimmed, model)
    except FileNotFoundError:
        return {f"{skimmed}/{model}": {}}


def worker_command(skimmed, model):
    with open(f"{skimmed}/{model}/cfchecks_output.txt", 'r') as cfcheck:
        files_info = {}
        for line in cfcheck:
            if "CHECKING NetCDF FILE" in line:
                file_name = line[22:-1]
                logging.info("Found file info %s", file_name)            
                files_info[file_name] = decode(cfcheck)
                logging.debug("Collected file info %s", files_info[file_name])            
            else:
                raise RuntimeError("Unexpected file structure")
    return files_info


def decode(cfcheck):
    state={}
    return decode_versions(cfcheck, state)


def decode_versions(cfcheck, state):
    line = cfcheck.readline()
    if "Checking against CF Version" in line:
        state["cf_version"] = line[28:-1]
    elif "Using Standard Name Table Version" in line:
        state["stdname_tb"] = line[34:-1]
    elif "Using Area Type Table Version" in line:
        state["stdarea_tb"] = line[30:-1]
    elif "Using Standardized Region Name Table Version" in line:
        state["stdregn_tb"] = line[45:-1]
    elif "------------------" in line:
        return decode_variables(cfcheck, state)
    elif not line:
        return state
    return decode_versions(cfcheck, state)


def decode_variables(cfcheck, state):
    line = cfcheck.readline()
    if "Checking variable" in line:
        cfcheck.readline()  # Ignore next line
        variable_name = line[19:-1]
        variable_info = decode_vinfo(cfcheck)
        state[variable_name] = variable_info[:-1]
    elif "INFORMATION messages" in line:
        return state
    return decode_variables(cfcheck, state)


def decode_vinfo(cfcheck, info=""):
    line = cfcheck.readline()
    if any([x in line for x in ['ERROR:', 'WARN:', 'INFO:']]):
        return decode_vinfo(cfcheck, info + line)
    else:
        return info if info else "OK\n"


# Main call ---------------------------------------------------------
if __name__ == '__main__':
    args = parser.parse_args()
    # try:
    run_command(**vars(args))
    sys.exit(0)  # Shell return 0 == success

