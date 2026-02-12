"""
    This script can be used to run queries on BigQuery/Blockchair for any number of blockchains, and save the results in the
    raw_block_data directory of the project.
    The relevant queries must be stored in a file named 'queries.yaml' in the `data_collection_scripts` directory of
    the project.

    Attention! Before running this script, if using BigQuery, you need to generate service account credentials from Google, as described
    here (https://developers.google.com/workspace/guides/create-credentials#service-account) and save your key in the
    `data_collection_scripts` directory of the project under the name 'google-service-account-key.json'
"""
import consensus_decentralization.helper as hlp
import google.cloud.bigquery as bq
import argparse
import csv
import gzip
import io
import json
import logging
from datetime import datetime, timedelta
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from yaml import safe_load

from consensus_decentralization.helper import ROOT_DIR


BLOCKCHAIR_ZCASH_OUTPUTS_URL = "https://gz.blockchair.com/zcash/outputs/blockchair_zcash_outputs_{date}.tsv.gz"
BLOCKCHAIR_ZCASH_DAYS = 30


def _parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return 0


def _date_range(end_date, days):
    start_date = end_date - timedelta(days=days - 1)
    for offset in range(days):
        yield start_date + timedelta(days=offset)


def collect_zcash_from_blockchair(raw_data_dir, from_block, to_date):
    """
    Collect Zcash data from Blockchair transaction output dumps.
    Fetches outputs marked with is_from_coinbase=1 and groups them by block_id to reconstruct
    miner addresses and their rewards.
    """
    file = raw_data_dir / "zcash_raw_data.json"
    end_date = datetime.strptime(to_date, "%Y-%m-%d").date()
    logging.info(f"Querying zcash from Blockchair output dumps for the last {BLOCKCHAIR_ZCASH_DAYS} days..")

    # Temporary in-memory storage for block data while processing
    blocks_data = {}

    for day in _date_range(end_date, BLOCKCHAIR_ZCASH_DAYS):
        day_stamp = day.strftime("%Y%m%d")
        url = BLOCKCHAIR_ZCASH_OUTPUTS_URL.format(date=day_stamp)
        logging.info(f"Fetching {url}")
        try:
            with urlopen(url) as response:
                with gzip.GzipFile(fileobj=response) as gz_file:
                    text_stream = io.TextIOWrapper(gz_file, encoding="utf-8")
                    reader = csv.DictReader(text_stream, delimiter="\t")
                    
                    for row in reader:
                        # Only process coinbase outputs (miner rewards)
                        is_coinbase = row.get("is_from_coinbase", "0").strip()
                        if is_coinbase != "1":
                            continue
                        
                        block_id = _parse_int(row.get("block_id"))
                        if from_block is not None and block_id <= from_block:
                            continue
                        
                        # Extract output information
                        recipient = (row.get("recipient") or "").strip()
                        value = _parse_int(row.get("value"))
                        
                        # Accumulate outputs by block
                        if block_id not in blocks_data:
                            blocks_data[block_id] = {
                                "outputs": [],
                                "timestamp": row.get("time"),
                            }
                        
                        if recipient:  # Only add if we have a recipient address
                            blocks_data[block_id]["outputs"].append({
                                "addresses": [recipient],
                                "value": str(value),
                            })
        except HTTPError as exc:
            logging.info(f"Skipping {url}: {exc}")
        except URLError as exc:
            logging.info(f"Failed to fetch {url}: {exc}")
        except Exception as exc:
            logging.info(f"Failed to parse {url}: {repr(exc)}")

    # Write accumulated blocks to file
    with open(file, "a") as out_file:
        for block_id in sorted(blocks_data.keys()):
            block_data = blocks_data[block_id]
            block = {
                "number": block_id,
                "timestamp": block_data["timestamp"],
                "identifiers": "",  # Not available from outputs dump
                "outputs": block_data["outputs"],
            }
            out_file.write(json.dumps(block, default=str) + "\n")


def collect_data(raw_data_dir, ledgers, from_block, to_date):
    data_collection_dir = ROOT_DIR / "data_collection_scripts"

    ledgers_for_bigquery = [ledger for ledger in ledgers if ledger != "zcash"]
    queries = None
    client = None
    if ledgers_for_bigquery:
        with open(data_collection_dir / "queries.yaml") as f:
            queries = safe_load(f)
        client = bq.Client.from_service_account_json(
            json_credentials_path=data_collection_dir / "google-service-account-key.json"
        )

    for ledger in ledgers:
        if ledger == "zcash":
            collect_zcash_from_blockchair(raw_data_dir=raw_data_dir, from_block=from_block.get("zcash"), to_date=to_date)
            continue
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
