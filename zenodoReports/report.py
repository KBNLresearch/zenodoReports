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
from collections import Counter
import pandas as pd
from matplotlib import pylab
from matplotlib import pyplot as plt
from matplotlib import dates as mdates
from matplotlib.dates import DateFormatter
from tabulate import tabulate
from . import config

# Set defaults for pyplot
params = {'legend.fontsize': 'large',
          'figure.figsize': (16, 9),
         'axes.labelsize': '18',
         'axes.titlesize':'large',
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


def countByValue(listIn):
    """Report frequencies for values in a list"""

    vCount = Counter(listIn)
    vFrame = pd.DataFrame.from_dict(vCount, orient='index', columns=['frequency'])
    vFrame.sort_values(by='frequency', ascending=False, inplace=True)

    return vFrame


def reportAccessRights(accessRights):
    """Report access rights info"""

    arFrame = countByValue(accessRights)
    arMd = dfToMarkdown(arFrame, headers=['Access type', 'Count'])
    mdString = '\n\n## Access rights\n\n'
    mdString += arMd
    return mdString


def reportFileTypes(fileTypes):
    """Report file type info"""

    ftFrame = countByValue(fileTypes)
    ftMd = dfToMarkdown(ftFrame, headers=['File type', 'Count'])
    mdString = '\n\n## File types\n\n'
    mdString += ftMd
    return mdString


def reportKeywords(keywords):
    """Report keyword info"""

    kwFrame = countByValue(keywords)
    kwMd = dfToMarkdown(kwFrame, headers=['Keyword', 'Count'])
    mdString = '\n\n## Keywords\n\n'
    mdString += kwMd
    return mdString


def reportPublicationTypes(publicationTypes):
    """Report publication type info"""

    pTypeFrame = countByValue(publicationTypes)
    pTypeMd = dfToMarkdown(pTypeFrame, headers=['Publication type', 'Count'])
    mdString = '\n\n## Publication types\n\n'
    mdString += pTypeMd
    return mdString


def reportPublicationSubtypes(publicationSubtypes):
    """Report publication subtype info"""

    sTypeFrame = countByValue(publicationSubtypes)
    sTypeMd = dfToMarkdown(sTypeFrame, headers=['Publication subtype', 'Count'])
    mdString = '\n\n## Publication subtypes\n\n'
    mdString += sTypeMd
    return mdString


def reportPublicationLanguages(publicationLanguages):
    """Report publication language info"""

    lTypeFrame = countByValue(publicationLanguages)
    lTypeMd = dfToMarkdown(lTypeFrame, headers=['Publication language', 'Count'])
    mdString = '\n\n## Publication languages\n\n'
    mdString += lTypeMd
    return mdString


def reportPublicationLicenses(publicationLicenses):
    """Report publication license info"""

    licTypeFrame = countByValue(publicationLicenses)
    licTypeMd = dfToMarkdown(licTypeFrame, headers=['Publication license', 'Count'])
    mdString = '\n\n## Publication licenses\n\n'
    mdString += licTypeMd
    return mdString


def frequenciesByMonth(datesIn):
    """Takes list of datetime strings, and returns data frame
    with frequencies and cumulative frequencies by month"""

    dates = []
    # First convert ISO datetime strings to date values
    for dateIn in datesIn:
        dates.append(datetime.datetime.fromisoformat(dateIn).date())
    
    # Sort dates and get lower/upper bounds
    dates.sort()
    yearMin = dates[0].year
    monthMin = dates[0].month
    yearMax = dates[len(dates) - 1].year
    monthMax = dates[len(dates) - 1].month

    # List of all months between dateMin and dateMax
    dateRange = []

    year = yearMin
    month = monthMin

    while year <= yearMax:
        myDate = datetime.date(year, month, 1)
        dateRange.append(myDate)
        if year == yearMax:
            if month < monthMax:
                month += 1
            else:
                # Increase year index to force break from loop
                year += 1
        else:
            month +=1
        if month > 12:
            month = 1
            year += 1

        dateCounts = []
        dateCountsCum = []

    countCumPrev = 0

    # For each month in dateRange, count number of dates
    # and keep track of cumulative count
    for month in dateRange:
        count = 0
        for date in dates:
            if date.year == month.year and date.month == month.month:
                count += 1
        dateCounts.append(count)
        countCum = countCumPrev + count
        dateCountsCum.append(countCum)
        countCumPrev = countCum

    datesFrame = pd.DataFrame({'date': dateRange,
                                'freq': dateCounts,
                                'freqCum': dateCountsCum})

    return datesFrame, yearMin, yearMax


def plotDfTime(dataFrame, xCol, yCol, xLabel, yLabel, yearMin, yearMax, imageOut):
    """Plot time-based data frame"""
    myPlot = dataFrame.plot(kind='line',
                                x=xCol,
                                y=yCol,
                                lw=2.5,
                                figsize=(16,9))

    # Note: setting 'kind' to 'box' above results in weird
    # behaviour if date_form is used (all years are set to 1970)!
    # Might be related to this bug: https://github.com/pandas-dev/pandas/issues/26253

    date_form = DateFormatter("%Y-%m")
    myPlot.axes.xaxis.set_major_formatter(date_form)

    locator = mdates.AutoDateLocator(minticks = 16, maxticks = 24)
    formatter = mdates.ConciseDateFormatter(locator)
    formatter.formats = ['%Y', '%b', '%d']

    myPlot.axes.xaxis.set_major_locator(locator)
    myPlot.axes.xaxis.set_major_formatter(formatter)

    myPlot.set_xlabel(xLabel)
    myPlot.set_ylabel(yLabel)
    myPlot.set_xlim([datetime.date(yearMin, 1, 1), datetime.date(yearMax, 12, 31)])
    myPlot.get_legend().remove()
    fig = myPlot.get_figure()
    fig.savefig(imageOut)


def reportCreatedDates(createdDates):
    """Report created dates info"""

    # Analyse created dates
    cDatesFrame, yearMin, yearMax = frequenciesByMonth(createdDates)

    # Export data frame to a CSV file
    cDatesFrame.to_csv(os.path.join(config.dirCSV, 'createdDates.csv'), encoding='utf-8', index=False)

    # Plot frequencies
    xLabel = 'Created date'
    yLabel = 'Count'
    imgCreated = os.path.join(config.dirImg, 'publications-created.png')
    plotDfTime(cDatesFrame, 'date', 'freq', xLabel, yLabel, yearMin, yearMax, imgCreated)

    # Plot cumulative frequencies
    xLabel = 'Created date'
    yLabel = 'Count (cumulative)'
    imgCreatedCum = os.path.join(config.dirImg, 'publications-created-cum.png')
    plotDfTime(cDatesFrame, 'date', 'freqCum', xLabel, yLabel, yearMin, yearMax, imgCreatedCum)

    mdString = '\n\n## Created dates\n\n'
    mdString += '![](./img/' + os.path.basename(imgCreated) + ')'
    mdString += '\n\n## Created dates (cumulative)\n\n'
    mdString += '![](./img/' + os.path.basename(imgCreatedCum) + ')'

    return mdString


def reportPublicationDates(publicationDates):
    """Report publication dates info"""

    # Analyse publication dates
    pDatesFrame, yearMin, yearMax = frequenciesByMonth(publicationDates)

    # Export data frame to a CSV file
    pDatesFrame.to_csv(os.path.join(config.dirCSV, 'publicationDates.csv'), encoding='utf-8', index=False)

    # Plot frequencies
    xLabel = 'Publication date'
    yLabel = 'Count'
    imgPub = os.path.join(config.dirImg, 'publications-published.png')
    plotDfTime(pDatesFrame, 'date', 'freq', xLabel, yLabel, yearMin, yearMax, imgPub)

    # Plot cumulative frequencies
    xLabel = 'Publication date'
    yLabel = 'Count (cumulative)'
    imgPubCum = os.path.join(config.dirImg, 'publications-published-cum.png')
    plotDfTime(pDatesFrame, 'date', 'freqCum', xLabel, yLabel, yearMin, yearMax, imgPubCum)

    mdString = '\n\n## Publication dates\n\n'
    mdString += '![](./img/' + os.path.basename(imgPub) + ')'
    mdString += '\n\n## Publication dates (cumulative)\n\n'
    mdString += '![](./img/' + os.path.basename(imgPubCum) + ')'

    return mdString

def report(fileIn):
    """Create report from JSON file"""

    dirOut = os.path.join('.', 'report')
    if not os.path.isdir(dirOut):
        os.makedirs(dirOut)

    config.dirCSS = os.path.join(dirOut, 'css')
    config.dirCSV = os.path.join(dirOut, 'csv')
    config.dirImg = os.path.join(dirOut, 'img')

    if not os.path.isdir(config.dirCSS):
        os.makedirs(config.dirCSS)

    if not os.path.isdir(config.dirCSV):
        os.makedirs(config.dirCSV)

    if not os.path.isdir(config.dirImg):
        os.makedirs(config.dirImg)

    # Copy style sheet to CSS dir
    try:
        cssIn = os.path.join(sys.path[0], 'css', 'github-markdown.css')
        cssOut = os.path.join(config.dirCSS, 'github-markdown.css')
        shutil.copyfile(cssIn, cssOut)
    except:
        sys.stderr.write("Cannot copy style sheet\n")
        sys.exit()

    # Read JSON file
    with open(fileIn, 'r') as f:
        dataIn = json.load(f)

    # Report detailed statistics from individual hits
    hits = dataIn["hits"]["hits"]
    createdDates = []
    fileTypes = []
    accessRights = []
    keyWords = []
    languages = []
    licenses = []
    publicationDates = []
    resourceTypes = []
    resourceSubtypes = []

    # Parse metadata and store interesting bits to lists
    for hit in hits:
        created = hit["created"]
        createdDates.append(created)
        try:
            files = hit["files"]
        except KeyError:
            # Closed access publications can have no files
            files = []
        for file in files:
            ftype = file["type"]
            fileTypes.append(ftype)
        metadata = hit["metadata"]
        access_right = metadata["access_right"]
        accessRights.append(access_right)
        try:
            keywords = metadata["keywords"]
        except KeyError:
            keywords = []
        for keyword in keywords:
            keyWords.append(keyword)
        try:
            language = metadata["language"]
            languages.append(language)
        except KeyError:
            languages.append("unknown")
        try:
            license = metadata["license"]["id"]
            licenses.append(license)
        except KeyError:
            licenses.append("unknown")
        try:
            publicationDate = metadata["publication_date"]
            publicationDates.append(publicationDate)
        except KeyError:
            publicationDates.append("unknown")
        resource_type = metadata["resource_type"]
        
        try:
            type = resource_type["type"]
            resourceTypes.append(type)
        except KeyError:
            pass
        try:
            subtype = resource_type["subtype"]
            resourceSubtypes.append(subtype)
        except KeyError:
            pass

    # Generate report
    # Initialize string for Markdown output
    reportString = '# Zenodo community report\n\n'
    reportString += 'Created: ' + str(datetime.datetime.now())
    mdString = reportFileTypes(fileTypes)
    reportString += mdString
    mdString = reportAccessRights(accessRights)
    reportString += mdString
    mdString = reportKeywords(keyWords)
    reportString += mdString
    mdString = reportPublicationLanguages(languages)
    reportString += mdString
    mdString = reportPublicationLicenses(licenses)
    reportString += mdString
    mdString = reportPublicationTypes(resourceTypes)
    reportString += mdString
    mdString = reportPublicationSubtypes(resourceSubtypes)
    reportString += mdString
    mdString = reportCreatedDates(createdDates)
    reportString += mdString
    mdString = reportPublicationDates(publicationDates)
    reportString += mdString

    # Open output report (Markdown format) for writing
    try:
        reportMD = os.path.join(dirOut, 'report.md')
        fOut = codecs.open(reportMD, "w", "utf-8")
    except:
        sys.stderr.write("Cannot write output report\n")
        sys.exit()

    fOut.write(reportString)
    fOut.close()