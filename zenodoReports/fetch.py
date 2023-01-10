#!/usr/bin/env python3

"""Fetch metadata of all Zenodo records in community"""

import io
import json
import requests
import datetime

def fetchMeta(ACCESS_TOKEN, communityID, maxRecords, infoFlag):

    # First fetch 1 record to establish total number of records
    response = requests.get('https://zenodo.org/api/records',
                            params={'access_token': ACCESS_TOKEN,
                            'communities': communityID,
                            'size': '1'},
                            timeout=None)

    noRecords = response.json()["hits"]["total"]

    # Print number of records
    print('Found ' + str(noRecords) + ' records')

    if not infoFlag:
        # Fetch all records (or number set by maxRecords)
        if maxRecords != 'all':
            noRecords = maxRecords

        response = requests.get('https://zenodo.org/api/records',
                                params={'access_token': ACCESS_TOKEN,
                                'communities': communityID,
                                'size': noRecords},
                                timeout=None)
        thisDateTime = datetime.date.today().isoformat()

        fName = communityID + '-' + thisDateTime + '.json'

        with io.open(fName, 'w', encoding='utf-8') as f:
            json.dump(response.json(), f)
    
        print('Wrote records to file ' + fName)

