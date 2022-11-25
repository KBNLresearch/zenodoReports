#! /usr/bin/env python3

"""
Analyses Zenodo JSON file generated by fetch.py, and generates reports in Markdown and HTML
"""

import sys
import os
import shutil
import codecs
import json
import datetime
import pandas as pd
import numpy as np
from matplotlib import pylab
import markdown
from tabulate import tabulate

# Set defaults for pyplot
params = {'legend.fontsize': 'x-large',
          'figure.figsize': (8, 6),
         'axes.labelsize': '18',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'x-large',
         'ytick.labelsize':'x-large'}
pylab.rcParams.update(params)


def dfToMarkdown(dataframe, headers='keys'):
    """Convert Data Frame to Markdown table with optionally custom headers"""
    mdOut = dataframe.pipe(tabulate, headers=headers, tablefmt='pipe')
    return mdOut


def iterateAggregation(aggregation):
    """Iterate over aggregation elements and return output table as list"""
    buckets = aggregation["buckets"]
    countOther = aggregation["sum_other_doc_count"]

    outTable = []

    for bucket in buckets:
        doc_count = bucket["doc_count"]
        key = bucket["key"]
        outTable.append([key, doc_count])

    outTable.append(['other', countOther])

    return outTable


def reportAccessRights(aggregations, mdString):
    """Report access right info"""
    access_right = aggregations["access_right"]
    outTable = iterateAggregation(access_right)

    # Create summary table
    tableHeader = ['Access type', 'number of publications']

    mdString += '\n\n## Access rights\n\n'
    mdString += tabulate(outTable, tableHeader, tablefmt='pipe')

    return mdString


def reportFileType(aggregations, mdString):
    """Report file type info"""
    file_type = aggregations["file_type"]
    outTable = iterateAggregation(file_type)

    # Create summary table
    tableHeader = ['File type', 'number of files']

    mdString += '\n\n## File types\n\n'
    mdString += tabulate(outTable, tableHeader, tablefmt='pipe')

    return mdString


def report(fileIn):
    """Create report from JSON file"""

    # Initialize empty string for Markdown output
    mdString = ""

    # Read JSON file
    with open(fileIn, 'r') as f:
        dataIn = json.load(f)

    aggregations = dataIn["aggregations"]
    mdString = reportAccessRights(aggregations, mdString)

    mdString = reportFileType(aggregations, mdString)

    print(mdString)
