# ZenodoReports

## What it does

Fetch metadata and generate reports for a Zenodo community. See an example report [here](./examples/report/report.md).

## Installation

1. Clone this repository:

    ```
    git clone https://github.com/KBNLresearch/zenodoReports.git
    ```

2. Set working directory to repository root dir:

    ```
    cd zenodoReports
    ```

3. For a user install, run the below command:

    ```
    python3 setup.py install --user
    ```

## Fetch metadata

Usage:

```
zenodoReports fetch [-h] [--maxrecords MAXRECORDS] [--info]
                       accessToken communityID
```

Positional arguments:

- accessToken: Zenodo access token. You can create an access token [here](https://zenodo.org/account/settings/applications/tokens/new/).
- communityID: community identifier (e.g. "kbnl")

Optional arguments:
 
- -h, --help: show help message and exit
- --maxrecords MAXRECORDS, -m MAXRECORDS: maximum number of records to fetch (default: fetch all records)
- --info, -i: only show number of records in community (don't fetch anything)

## Generate report

Usage:

```
zenodoReports report [-h] metadataIn
```

Positional arguments:

- metadataIn: input metadata file (i.e. the file that results from running the fetch command as explained above)

Optional arguments:

- -h, --help: show help message and exit

## License

ZenodoReports is released under the Apache License 2.0.
