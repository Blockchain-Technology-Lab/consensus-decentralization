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
from datetime import datetime

from consensus_decentralization.helper import ROOT_DIR


def collect_data(raw_data_dir, ledgers, from_block, to_date):
    data_collection_dir = ROOT_DIR / "data_collection_scripts"

    with open(data_collection_dir / "queries.yaml") as f:
        queries = safe_load(f)

    client = bq.Client.from_service_account_json(json_credentials_path=data_collection_dir / "google-service-account-key.json")

    for ledger in ledgers:
        file = raw_data_dir / f'{ledger}_raw_data.json'
        logging.info(f"Querying {ledger} from block {from_block[ledger]} until {to_date}..")

        query = (queries[ledger]).replace("{{block_number}}", str(from_block[ledger]) if from_block[ledger] else "-1").replace("{{timestamp}}", to_date)
        query_job = client.query(query)
        try:
            rows = query_job.result()
            logging.info(f'Done querying {ledger}')
        except Exception as e:
            if 'Quota exceeded' in repr(e):
                logging.info('Quota exceeded for this service account key. Aborting..')
                break
            else:
                logging.info(f'{ledger} query failed, please make sure it is properly defined.')
                logging.info(f'The following exception was raised: {repr(e)}\n')
                continue

        logging.info(f"Writing {ledger} data to file..")
        # Append result to file
        with open(file, 'a') as f:
            for row in rows:
                f.write(json.dumps(dict(row), default=str) + "\n")
        logging.info(f'Done writing {ledger} data to file.\n')


def get_last_block_collected(file):
    """
    Get the last block collected for a ledger. This is useful for knowing where to start collecting data from.
    Assumes that the data is stored in a json lines file, ordered in increasing block number.
    :param file: the file that corresponds to the ledger to get the last block collected for
    :returns: the number of the last ledger block collected in the file
    """
    if not file.is_file():
        return None
    with open(file) as f:
        for line in f:
            pass
    last_block = json.loads(line)
    return last_block['number']


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
        '--to_date',
        type=hlp.valid_date,
        default=datetime.today().strftime('%Y-%m-%d'),
        help='The date until which to get data for (YYYY-MM-DD format). Defaults to today.'
    )

    args = parser.parse_args()
    raw_data_dir = hlp.get_input_directories()[0]
    if not raw_data_dir.is_dir():
        raw_data_dir.mkdir()
    from_block = {ledger: get_last_block_collected(file=raw_data_dir / f'{ledger}_raw_data.json') for ledger in args.ledgers}
    collect_data(raw_data_dir=raw_data_dir, ledgers=args.ledgers, from_block=from_block, to_date=args.to_date)
