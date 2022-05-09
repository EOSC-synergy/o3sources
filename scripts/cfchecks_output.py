#!/usr/bin/env python3
"""Script to perform sources cf evaluation on the o3as database.
"""
import argparse
import glob
import logging
import os
import subprocess
import sys
from pathlib import Path

import dask
import pandas as pd

# Logger definition -------------------------------------------------
logger = logging.getLogger(__name__)
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class WorkLogger(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        source, model = self.extra["source"], self.extra["model"]
        return "[%s_%s] %s" % (source, model, msg), kwargs


# Script arguments definition ---------------------------------------
parser = argparse.ArgumentParser(
    prog="PROG",
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="See '<command> --help' to read about a specific sub-command.",
)
parser.add_argument(
    *["-v", "--verbosity"],
    help="Sets the logging level (default: %(default)s)",
    type=str,
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    default="INFO",
)
parser.add_argument(
    *["-o", "--output"],
    help="Output folder for skimmed files (default: %(default)s)",
    type=str,
    default="Skimmed",
)
parser.add_argument(
    *["-s", "--sources"],
    help="Sources folder for input paths (default: %(default)s)",
    type=str,
    default="Sources",
)
parser.add_argument(
    "--source_file",
    help="Path to CSV source file with skimming configurations",
    type=str,
    default="Data sources - Sources.csv",
)


# Script command actions --------------------------------------------
def run_command(verbosity, output, sources, source_file, **options):

    # Common operations
    logging.basicConfig(format=format, level=verbosity)
    logger.info("Program start")

    # Read source file
    logger.info("Reading source file %s", source_file)
    models = pd.read_csv(source_file, index_col=[0, 1])
    logger.debug(f"Source file:\n{models.to_string()}")

    # Define pool processes
    logger.info("Computing 'tco3_zm' skimming pool of models")
    checks_list = dask.compute(
        *[
            dask.delayed(worker)(index, sources, output, **row)
            for index, row in models.iterrows()
        ]
    )

    # Saving produced files into a summary output file
    logging.info("Saving info to %s", output)
    output_file = f"{output}/Data sources - cf_errors.csv"
    checks = {k: v for d in checks_list for k, v in d.items()}
    pd.DataFrame(checks).transpose().to_csv(output_file, sep=";")

    # End of program
    logger.info("End of program")


# Worker actions ----------------------------------------------------
def worker(index, sources, output, paths=None, **_):
    logger = logging.getLogger(__name__)
    logger = WorkLogger(logger, {"source": index[0], "model": index[1]})

    # Common operations
    output_folder = Path(f"{output}/{index[0]}_{index[1]}")
    os.makedirs(Path(output_folder), exist_ok=True)

    # Subprocess to evaluate source on CF conventions
    logger.info(f"CF Checking {paths} with cfchecks")
    call = ["cfchecks", "--version=auto"] + glob.glob(f"{sources}/{paths}")
    with open(f"{output_folder}/cfchecks_output.txt", "w") as f:
        logger.debug(f"Calling proccess: ${call}")
        p = subprocess.run(call, stdout=f, stderr=subprocess.PIPE)
        logger.info(p.stderr.decode())

    # Collect output information into dictionary
    logger.info(f"Collecting cf info from {output_folder}")
    files_info = {}
    with open(f"{output_folder}/cfchecks_output.txt", "r") as cfcheck:
        for line in cfcheck:
            if "CHECKING NetCDF FILE" in line:
                file_name = line[22:-1]
                logging.info("Found file info %s", file_name)
                files_info[file_name] = decode(cfcheck)
                logging.debug("Collected file info %s", files_info[file_name])
            else:
                raise RuntimeError("Unexpected file structure")

    # End of program
    return files_info


# CF Decoding functions ---------------------------------------------
def decode(cfcheck):
    state = {}
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
    if any([x in line for x in ["ERROR:", "WARN:", "INFO:"]]):
        return decode_vinfo(cfcheck, info + line)
    else:
        return info if info else "OK\n"


# Main call ---------------------------------------------------------
if __name__ == "__main__":
    args = parser.parse_args()
    run_command(**vars(args))
    sys.exit(0)  # Shell return 0 == success
