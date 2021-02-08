#!/usr/bin/env python3
"""Script to generate source file from different formats
"""
import argparse
import csv
import json
import logging
import sys
import warnings
import yaml


# Script configuration
warnings.simplefilter(action='ignore', category=FutureWarning)
key_parameters = ['name', 'paths', 'coordinates']
output_name = "sources.yaml"


def main():
    parser = argparse.ArgumentParser(
        prog='PROG', description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "-v", "--verbosity", type=str, default='ERROR',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Sets the logging level (default: %(default)s)")
    parser.add_argument(
        "-f", "--format", type=str, default='csv',
        choices=['csv'],
        help="Expected input file format (default: %(default)s)")
    parser.add_argument(
        "document",
        action='store', nargs=1, type=str,
        help="Document to convert to sources.yaml")

    # Return arguments
    args = parser.parse_args()
    run_command(args)
    sys.exit(0)  # Shell return 0 == success


def run_command(args):
    # Set logging level
    logging.basicConfig(
        level=getattr(logging, args.verbosity),
        format='%(asctime)s  %(levelname)-8s %(message)s'
    )

    # Call for function
    logging.info("Reading document")
    document = []
    if args.format == 'csv':
        document = from_csv(args.document[0])

    # Group sources
    logging.info("Grouping document sources")
    sources = group_models(document)

    # Saving into sources.yaml
    logging.info("Saving file to %s", output_name)
    with open(output_name, 'w') as output_file:
        yaml.dump(sources, output_file, allow_unicode=True)

    # End of program
    logging.info("End of program")


def from_csv(document):
    """Returns a list of standardized dictionaries from a csv"""
    logging.debug("loading document: %s, as csv", document)
    with open(document, mode='r') as sources:
        reader = csv.reader(sources)
        return format(next(reader), reader)


def format(head, rows_iter):
    """Returns a list of standardized dictionaries"""
    logging.debug("Formating document into list of dicts")
    document = []
    for row in rows_iter:
        dictionary = dict(zip(head, row))
        document.append(dictionary)
    return document


def group_models(document):
    """Groups the rows into sources, models and variable"""
    output = {}
    for row in document:
        s = row.pop('source')
        m = row.pop('model')
        v = row.pop('variable')
        try:
            structure_model(row)
            add_subdict([s, m, v], row, output)
        except Exception:
            message = "Adding source: '{}', model: '{}', var: '{}'"
            logging.error(message.format(s, m, v), exc_info=True)
    return output


def structure_model(row):
    """Structures a model row"""
    row['coordinates'] = json.loads(row['coordinates'])
    set_metadata(row)


def set_metadata(row):
    """Set row metadata from non key parameters"""
    metadata = row.copy()
    {k: metadata.pop(k) for k in key_parameters}
    logging.debug("Set row metadata: %s", metadata)
    {k: row.pop(k) for k in metadata}
    logging.debug("Set row key parameters: %s", row)
    row['metadata'] = metadata


def add_subdict(keys, value, dictionary):
    """Adds a key-value to a recursive dict of dicts"""
    keys.reverse()
    add_subdict_reversed(keys, value, dictionary)


def add_subdict_reversed(keys, value, dictionary):
    key = keys.pop()
    if keys == []:
        dictionary[key] = value
    else:
        if key not in dictionary:
            dictionary[key] = {}
        add_subdict_reversed(keys, value, dictionary[key])


if __name__ == '__main__':
    main()
