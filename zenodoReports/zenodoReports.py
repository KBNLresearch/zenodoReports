#!/usr/bin/env python3

"""Fetch metadata and generate reports for a Zenodo community"""

import os
import io
import json
import sys
import argparse
from . import fetch
from . import report

__version__ = "0.1.0a1"

# Create parser
parser = argparse.ArgumentParser(
    description="Fetch metadata and generate reports for a Zenodo community")


def parseCommandLine():
    """Parse command-line arguments"""

    # Sub-parsers for fetch and report commands

    subparsers = parser.add_subparsers(help='sub-command help',
                                       dest='subcommand')
    parser_fetch = subparsers.add_parser('fetch',
                                          help='fetch metadata from all records in Zenodo community')
    parser_fetch.add_argument('accessToken',
                               action="store",
                               type=str,
                               help='Zenodo access token')

    parser_fetch.add_argument('communityID',
                               action='store',
                               type=str,
                               help='community identifier')

    parser_fetch.add_argument('--maxrecords', '-m',
                               action='store',
                               dest='maxRecords',
                               default='all',
                               help='maximum number of records to fetch')

    parser_report = subparsers.add_parser('report',
                                         help='generate a report')

    parser_report.add_argument('metadataIn',
                              action="store",
                              type=str,
                              help="input metadata file")

    parser.add_argument('--version', '-v',
                        action='version',
                        version=__version__)

    # Parse arguments
    args = parser.parse_args()

    return args


def printHelpAndExit():
    """Print usage message and exit"""
    print('')
    parser.print_help()
    sys.exit()


def main():
    """Main command line interface"""
    # Get input from command line
    args = parseCommandLine()

    action = args.subcommand

    if action == "fetch":
        accessToken = args.accessToken
        communityID = args.communityID
        maxRecords = args.maxRecords
        fetch.fetchMeta(accessToken, communityID, maxRecords)

    elif action == "report":
        metadataIn = args.metadataIn
        report.report(metadataIn)
    elif action is None:
        printHelpAndExit()


if __name__ == "__main__":
    main()