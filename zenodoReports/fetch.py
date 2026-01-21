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

    # As of November 2025, Zenodo API has a rate limit of max 100 records per
    # page, so to fetch everything we have to split across pages
    noPages = math.ceil(noRecords/100)

    # Print number of records, pages
    print("Found {} records".format(noRecords))
    print("Fetching {} pages".format(noPages))

    if not infoFlag:
        # List with combined JSON data for all pages
        pagesData = []
        for page in range(noPages):
            pageNo = page + 1
            print("Fetching page {}/{}".format(pageNo, noPages))

            # Fetch all records for this page
            noRecords = 100

            response = requests.get('https://zenodo.org/api/records',
                                    params={'access_token': ACCESS_TOKEN,
                                    'communities': communityID,
                                    'page': pageNo,
                                    'size': noRecords},
                                    timeout=None)
            
            # Add data to combined list
            pagesData.append(response.json())

        thisDateTime = datetime.date.today().isoformat()
        fName = communityID + '-' + thisDateTime + '-' + str(pageNo) + '.json'

        with io.open(fName, 'w', encoding='utf-8') as fOut:
           json.dump(pagesData, fOut)
    
        print("Wrote records to file {}".format(fName))
