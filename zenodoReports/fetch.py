#!/usr/bin/env python3

"""Fetch metadata of all Zenodo records in community"""

import io
import math
import json
import requests
import datetime


def merge_json_files(file_paths, output_file):
    merged_data = []
    for path in file_paths:
        with open(path, 'r') as file:
            data = json.load(file)
            merged_data.append(data)
    with open(output_file, 'w') as outfile:
        json.dump(merged_data, outfile)

def fetchMeta(ACCESS_TOKEN, communityID, maxRecords, infoFlag):

    # Get info about available dumps
    response = requests.get('https://zenodo.org/api/exporter')

    # First fetch 1 record to establish total number of records
    response = requests.get('https://zenodo.org/api/records',
                            params={'access_token': ACCESS_TOKEN,
                            'communities': communityID,
                            'size': '1'},
                            timeout=None)

    noRecords = response.json()["hits"]["total"]

    # Print number of records
    print('Found ' + str(noRecords) + ' records')

    # As of November 2025, Zenodo API has a rate limit of max 100 records per
    # page, so to fetch everything we have to split across pages
    noPages = math.ceil(noRecords/100)
    print(str(noPages) + ' pages')

    if not infoFlag:
        thisDateTime = datetime.date.today().isoformat()
        # List with combined JSON data for all pages
        pagesData = []
        fNameOut = communityID + '-' + thisDateTime + '.json'
        for page in range(noPages):
            pageNo = page + 1

            # Fetch all records
            noRecords = 100

            thisDateTime = datetime.date.today().isoformat()
            fNameIn = communityID + '-' + thisDateTime + '-' + str(pageNo) + '.json'

            with io.open(fNameIn, 'r', encoding='utf-8') as fIn:
                pageData = json.load(fIn)
                pagesData.append(pageData)

        with io.open(fNameOut, 'w', encoding='utf-8') as fOut:
            json.dump(pagesData, fOut)   

def fetchMetaRestoreMeLater(ACCESS_TOKEN, communityID, maxRecords, infoFlag):

    # Get info about available dumps
    response = requests.get('https://zenodo.org/api/exporter')

    # First fetch 1 record to establish total number of records
    response = requests.get('https://zenodo.org/api/records',
                            params={'access_token': ACCESS_TOKEN,
                            'communities': communityID,
                            'size': '1'},
                            timeout=None)

    noRecords = response.json()["hits"]["total"]

    # Print number of records
    print('Found ' + str(noRecords) + ' records')

    # As of November 2025, Zenodo API has a rate limit of max 100 records per
    # page, so to fetch everything we have to split across pages
    noPages = math.ceil(noRecords/100)
    print(str(noPages) + ' pages')

    if not infoFlag:
        for page in range(noPages):
            pageNo = page + 1

            # Fetch all records
            noRecords = 100

            response = requests.get('https://zenodo.org/api/records',
                                    params={'access_token': ACCESS_TOKEN,
                                    'communities': communityID,
                                    'page': pageNo,
                                    'size': noRecords},
                                    timeout=None)
            thisDateTime = datetime.date.today().isoformat()

            fName = communityID + '-' + thisDateTime + '-' + str(pageNo) + '.json'

            with io.open(fName, 'w', encoding='utf-8') as f:
                json.dump(response.json(), f)
        
            print('Wrote records to file ' + fName)
