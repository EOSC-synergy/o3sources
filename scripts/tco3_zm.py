#!/usr/bin/env python3
"""Script to perform tco3 skimming on the o3as database.
"""
import argparse
import logging
import os
import sys
from pathlib import Path

import dask
import o3skim
import o3skim.loads
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
    "--sources_file",
    help="Path to CSV source file with skimming configurations",
    type=str,
    default="sources.csv",
)


# Script command actions --------------------------------------------
def run_command(verbosity, output, sources, sources_file, **options):

    # Common operations
    logging.basicConfig(format=format, level=verbosity)
    logger.info("Program start")

    # Read source file
    logger.info("Reading source file %s", sources_file)
    models = pd.read_csv(sources_file, index_col=[0, 1])
    logger.debug(f"Source file:\n{models.to_string()}")

    # Define pool processes
    logger.info("Computing 'tco3_zm' skimming pool of models")
    dask.compute(
        *[
            dask.delayed(worker)(index, sources, output, **row)
            for index, row in models.iterrows()
            if row["parameter"] == "tco3_zm"
        ]
    )

    # End of program
    logger.info("End of program")


# Worker actions ----------------------------------------------------
def worker(index, sources, output, load_function=None, paths=None, **_):
    logger = logging.getLogger(__name__)
    logger = WorkLogger(logger, {"source": index[0], "model": index[1]})

    # Common operations
    if not load_function:
        raise ValueError("Undefined model load_function in kwargs")
    output_folder = Path(f"{output}/{index[0]}_{index[1]}")
    os.makedirs(Path(output_folder), exist_ok=True)

    # Loading and skimming of dataset
    logger.info(f"Skimming {paths} with {load_function}")
    dataset = o3skim.loads.__dict__[load_function](f"{sources}/{paths}")
    skimmed = o3skim.lon_mean(dataset)

    # Variable name standardization
    logger.debug(f"Renaming var 'tco3' to 'tco3_zm'")
    skimmed = skimmed.cf.rename({'tco3': "tco3_zm"})

    # Skimming file saving
    logger.info(f"Saving skimmed dataset at {output_folder}")
    skimmed.to_netcdf(f"{output_folder}/tco3_zm.nc")

    # End of program
    return None


# Main call ---------------------------------------------------------
if __name__ == "__main__":
    args = parser.parse_args()
    run_command(**vars(args))
    sys.exit(0)  # Shell return 0 == success
