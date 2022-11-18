#!/usr/bin/env python3

"""Fetch metadata of all Zenodo records in community"""

import io
import json
import requests
import datetime

def fetchMeta(ACCESS_TOKEN, communityID, maxRecords):

    response = requests.get('https://zenodo.org/api/records',
                            params={'access_token': ACCESS_TOKEN,
                            'communities': communityID,
                            'size': maxRecords},
                            timeout=None)
    thisDateTime = datetime.date.today().isoformat()

    fName = communityID + '-' + thisDateTime + '.json'

    with io.open(fName, 'w', encoding='utf-8') as f:
        json.dump(response.json(), f)
