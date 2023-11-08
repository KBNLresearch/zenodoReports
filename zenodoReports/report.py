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


def  reduceCategories(dataFrame, categories):
    """Returns version of dataframe where all categories
    outside of top number are grouped as 'other' category
    Adapted from https://stackoverflow.com/a/48589225/1209004"""

    # Top categories
    dfTop = dataFrame[:categories].copy()

    if len(dataFrame) > len(dfTop):
        # Row with grouped remaining categories
        dfOther = pd.DataFrame(data = {
                'frequency' : [dataFrame['frequency'][categories:].sum()]
        })

        # Change index value from '0' to 'other'
        dfOther.rename(index={0:'other'},inplace=True)

        # Combine both into new dataframe
        dfOut = pd.concat([dfTop, dfOther])

    else:
        # Return unmodified dataFrame
        dfOut = dataFrame

    return dfOut


def countByValue(listIn, varName):
    """Report frequencies for values in a list"""

    vCount = Counter(listIn)
    vFrame = pd.DataFrame.from_dict(vCount, orient='index', columns=['frequency'])
    vFrame.sort_values(by='frequency', ascending=False, inplace=True)
    vFrame = vFrame.rename_axis(index=varName)

    return vFrame


def reportCategories(listIn, varName, prefixOut, noCategories):
    """Report info on list of categorised items"""

    # Count frequencies of each value and store result as dataframe
    df = countByValue(listIn, varName)

    # Create simplified version with only most prevalent categories
    dfSimplified = reduceCategories(df, noCategories) 

    # Name of output image and CSV file
    imgOut = os.path.join(config.dirImg, prefixOut + '.png')
    csvOut = os.path.join(config.dirCSV, prefixOut + '.csv')

    # Create pie chart, using simplified data
    plotDfPie(dfSimplified, 'frequency', imgOut)

    # Write unmodified dataframe to a CSV file
    df.to_csv(csvOut, encoding='utf-8', index=True)

    # Generate Markdown
    mdString = '![](./img/' + os.path.basename(imgOut) + ')\n\n'
    mdString += dfToMarkdown(dfSimplified, headers=[varName, 'Count'])
    mdString += '\n\n[Download data as CSV](./csv/' + os.path.basename(csvOut) + ')\n\n'

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


def plotDfPie(dataFrame, yCol, imageOut):
    """Plot data frame column as pie chart"""

    myPlot = dataFrame.plot(kind='pie',
                            y=yCol,
                            figsize=(10,8))
    myPlot.yaxis.set_visible(False)
    fig = myPlot.get_figure()
    fig.savefig(imageOut)


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


def reportDates(dates, prefixOut, xLabel):
    """Report dates info"""

    # Analyse dates
    dfDates, yearMin, yearMax = frequenciesByMonth(dates)

    # Name of output image and CSV file
    imgOut = os.path.join(config.dirImg, prefixOut + '.png')
    imgOutCum = os.path.join(config.dirImg, prefixOut + '-cum.png')
    csvOut = os.path.join(config.dirCSV, prefixOut + '.csv')

    # Export data frame to a CSV file
    dfDates.to_csv(csvOut, encoding='utf-8', index=False)

    yLabel = 'Count'

    # Plot frequencies
    plotDfTime(dfDates, 'date', 'freq', xLabel, yLabel, yearMin, yearMax, imgOut)

    # Plot cumulative frequencies
    plotDfTime(dfDates, 'date', 'freqCum', xLabel, yLabel + ' (cumulative)', yearMin, yearMax, imgOutCum)

    mdString = '![](./img/' + os.path.basename(imgOut) + ')'
    mdString += '\n\n'
    mdString += '![](./img/' + os.path.basename(imgOutCum) + ')'
    mdString += '\n\n[Download data as CSV](./csv/' + os.path.basename(csvOut) + ')\n\n'

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
    # TEST - created dates of all "Entangled Histories" transcriptions
    createdDatesEH = []
    fileTypes = []
    accessRights = []
    authors = []
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
            try:
                ftype = file["type"]
                fileTypes.append(ftype)
            except KeyError:
                pass
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
            creators = metadata["creators"]
        except KeyError:
            creators = []
        for creator in creators:
            authors.append(creator["name"])
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

        if "Entangled Histories" in keywords and "HTR-transcriptions" in keywords:
            # TEST - add created date of "Entangled Histories" transcription
            createdDatesEH.append(created)

    # TEST - list of all createdDates that are not "Entangled Histories" transcriptions
    createdDatesReduced = [item for item in createdDates if item not in createdDatesEH]  

    # Generate report
    # Initialize string for Markdown output
    reportString = '# Zenodo community report\n\n'
    reportString += 'Created: ' + str(datetime.datetime.now())
    reportString += '\n\n'
    reportString += 'Input file: ' + fileIn
    reportString += '\n\n'

    #reportString += '## File types\n\n'
    #mdString = reportCategories(fileTypes, 'fileType', 'file-types', 8)
    #reportString += mdString

    reportString += '## Access rights\n\n'
    mdString = reportCategories(accessRights, 'accessRight', 'access-rights', 8)
    reportString += mdString

    reportString += '## Licenses\n\n'
    mdString = reportCategories(licenses, 'license', 'licenses', 8)
    reportString += mdString

    """
    reportString += '## Authors\n\n'
    mdString = reportCategories(authors, 'author', 'authors', 8)
    reportString += mdString
    """

    reportString += '## Keywords\n\n'
    mdString = reportCategories(keyWords, 'keyword', 'keywords', 8)
    reportString += mdString
  
    reportString += '## Languages\n\n'
    mdString = reportCategories(languages, 'language', 'languages', 8)
    reportString += mdString
  
    reportString += '## Publication types\n\n'
    mdString = reportCategories(resourceTypes, 'type', 'pub-types', 8)
    reportString += mdString

    reportString += '## Publication subtypes\n\n'
    mdString = reportCategories(resourceSubtypes, 'subtype', 'pub-subtypes', 8)
    reportString += mdString

    reportString += '## Created dates\n\n'
    mdString = reportDates(createdDates, 'created', 'Created date')
    reportString += mdString
    
    reportString += '## Created dates (excluding EH transcriptions)\n\n'
    mdString = reportDates(createdDatesReduced, 'created-noeh', 'Created date')
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