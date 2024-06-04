"""
    This script can be used to run queries on BigQuery for any number of blockchains, and save the results in the
    raw_block_data directory of the project.
    The relevant queries must be stored in a file named 'queries.yaml' in the `data_collection_scripts` directory of
    the project.

    Attention! Before running this script, you need to generate service account credentials from Google, as described
    here (https://developers.google.com/workspace/guides/create-credentials#service-account) and save your key in the
    `data_collection_scripts` directory of the project under the name 'google-service-account-key.json'
"""
import consensus_decentralization.helper as hlp
import google.cloud.bigquery as bq
import json
import argparse
import logging
from yaml import safe_load

from consensus_decentralization.helper import ROOT_DIR, RAW_DATA_DIR


def collect_data(ledgers, force_query):
    if not RAW_DATA_DIR.is_dir():
        RAW_DATA_DIR.mkdir()

    data_collection_dir = ROOT_DIR / "data_collection_scripts"

    with open(data_collection_dir / "queries.yaml") as f:
        queries = safe_load(f)

    client = bq.Client.from_service_account_json(json_credentials_path=data_collection_dir /
                                                                       "google-service-account-key.json")

    for ledger in ledgers:
        file = RAW_DATA_DIR / f'{ledger}_raw_data.json'
        if not force_query and file.is_file():
            logging.info(f'{ledger} data already exists locally. '
                         f'For querying {ledger} anyway please run the script using the flag --force-query')
            continue
        logging.info(f"Querying {ledger}..")
        query = (queries[ledger])
        query_job = client.query(query)
        try:
            rows = query_job.result()
            logging.info(f'Done querying {ledger}')
        except Exception as e:
            logging.info(f'{ledger} query failed, please make sure it is properly defined.')
            logging.info(f'The following exception was raised: {repr(e)}')
            continue

        logging.info(f"Writing {ledger} data to file..")
        # Write json lines to file
        with open(file, 'w') as f:
            for row in rows:
                f.write(json.dumps(dict(row), default=str) + "\n")
        logging.info(f'Done writing {ledger} data to file.\n')


if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)

    default_ledgers = hlp.get_ledgers()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--ledgers',
        nargs="*",
        type=str.lower,
        default=default_ledgers,
        choices=[ledger for ledger in default_ledgers],
        help='The ledgers to collect data for.'
    )
    parser.add_argument(
        '--force-query',
        action='store_true',
        help='Flag to specify whether to query for project data regardless if the relevant data already exist.'
    )
    args = parser.parse_args()
    collect_data(ledgers=args.ledgers, force_query=args.force_query)
