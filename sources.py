#!/usr/bin/env python3
"""Script to generate source file from different formats
"""
import argparse
import csv
import logging
import sys
import yaml


# Main script arguments
parser = argparse.ArgumentParser(
    prog='PROG', description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument(
    "-v", "--verbosity", type=str, default='ERROR',
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    help="Sets the logging level (default: %(default)s)")
parser.add_argument(
    "-o", "--output", type=str, default="sources.yaml",
    help="Output file name (default: %(default)s)")
parser.add_argument(
    "-f", "--format", type=str, default='csv',
    choices=['csv'],
    help="Expected input file format (default: %(default)s)")
parser.add_argument(
    "document",
    action='store', nargs=1, type=str,
    help="Document to convert to sources.yaml")

# Available operations group
operations = parser.add_argument_group('operations')
operations.add_argument(
    "--lon_mean", action='append_const',
    dest='operations', const='lon_mean',
    help="Adds longitudinal mean to file operations")
operations.add_argument(
    "--lat_mean", action='append_const',
    dest='operations', const='lat_mean',
    help="Adds latitudinal mean to file operations")
operations.add_argument(
    "--year_mean", action='append_const',
    dest='operations', const='year_mean',
    help="Adds time average to file operations")


def main():
    args = parser.parse_args()
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

    # Cleaning sources
    logging.info("Cleaning bad document sources")
    sources.pop('_', None)

    # Add operations to models
    logging.info("Adding sources operations")
    logging.debug("Operations: %s", args.operations)
    if args.operations:
        for model in sources:
            sources[model]['operations'] = args.operations.copy()

    # Saving into sources.yaml
    logging.info("Saving file to %s", args.output)
    with open(args.output, 'w') as output_file:
        yaml.dump(sources, output_file, allow_unicode=True)

    # End of program
    logging.info("End of program")
    sys.exit(0)  # Shell return 0 == success


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
        row = {k: v.strip() for k, v in row.items()}  # Strip spaces
        s = row.pop('source')
        m = row.pop('model')
        v = row.pop('parameter')
        try:
            add_subdict([s + '_' + m, 'source'], s, output)
            add_subdict([s + '_' + m, v], row, output)
        except Exception:
            message = "Adding source: '{}', model: '{}', var: '{}'"
            logging.error(message.format(s, m, v), exc_info=True)
    return output


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
