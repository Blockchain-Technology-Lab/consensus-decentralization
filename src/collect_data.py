"""
    This script can be used to run queries on BigQuery for any number of blockchains, and save the results in the input
    directory of the project.
    The relevant queries must be stored in a file named 'queries.yaml' in the root directory of the project.

    Attention! Before running this script, you need to generate service account credentials from Google, as described
    here (https://developers.google.com/workspace/guides/create-credentials#service-account) and save your key in the
    root directory of the project under the name 'google-service-account-key.json'
"""
import google.cloud.bigquery as bq
import json
import argparse
from yaml import safe_load
from time import time

from helpers.helper import ROOT_DIR, INPUT_DIR


def collect_data(force_query):
    if not INPUT_DIR.is_dir():
        INPUT_DIR.mkdir()

    with open(ROOT_DIR / "queries.yaml") as f:
        queries = safe_load(f)

    client = bq.Client.from_service_account_json(json_credentials_path=ROOT_DIR / "google-service-account-key.json")

    for ledger in queries.keys():
        filename = f'{ledger}_raw_data.json'
        file = INPUT_DIR / filename
        if not force_query and file.is_file():
            print(f'{ledger} data already exists locally. '
                  f'For querying {ledger} anyway please run the script using the flag --force-query')
            continue
        print(f"Querying {ledger}..")
        start = time()
        query = (queries[ledger])
        query_job = client.query(query)
        try:
            rows = query_job.result()
            print(f'Done querying {ledger} (took about {round(time() - start)} seconds)')
        except Exception as e:
            print(f'{ledger} query failed, please make sure it is properly defined.')
            print(f'The following exception was raised: {repr(e)}')
            continue

        print(f"Writing {ledger} data to file..")
        start = time()
        # write json lines to file
        with open(file, 'w') as f:
            for row in rows:
                f.write(json.dumps(dict(row), default=str) + "\n")
        print(f'Done writing {ledger} data (took about {round(time() - start)} seconds)')
        print(50 * '-')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--force-query',
        action='store_true',
        help='Flag to specify whether to query for project data regardless if the relevant data already exist.'
    )
    args = parser.parse_args()
    collect_data(args.force_query)
