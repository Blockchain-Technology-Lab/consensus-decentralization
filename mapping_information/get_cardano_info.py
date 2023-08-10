import pathlib
import google.cloud.bigquery as bq
import json
import argparse
from collections import defaultdict
import logging


def get_pool_data(force_query):
    """
    Queries the BigQuery database for pool data and writes it to a json file.
    :param force_query: flag to specify whether to query for project data regardless if the relevant data already exist.
    """
    logging.info("Getting pool data..")
    filename = 'cardano_pool_data.json'
    file = io_dir / filename
    if not force_query and file.is_file():
        logging.info('Pool data already exists locally. '
                     'For querying anyway please run the script using the flag --force-query')
        return

    root_dir = pathlib.Path(__file__).parent.parent
    client = bq.Client.from_service_account_json(json_credentials_path=root_dir / "google-service-account-key.json")

    query = ('SELECT ticker_name, json as metadata FROM `iog-data-analytics.cardano_mainnet.pool_offline_data`')
    logging.info("Fetching pool data from BigQuery..")
    query_job = client.query(query)
    try:
        rows = query_job.result()
    except Exception as e:
        logging.info(f'The following exception was raised: {repr(e)}')
        return

    # write json lines to file
    with open(file, 'w') as f:
        for row in rows:
            f.write(json.dumps(dict(row), default=str) + "\n")
    logging.info('Pool data saved locally.')


def filter_homepage(homepage):
    """
    Filters out dummy homepages. Specifically, it ignores homepages that are empty, 'n/a' or contain 'foo.com'.
    :param homepage: the homepage to be filtered (string)
    :returns: the homepage (as it is) if it is not a dummy homepage, else None
    """
    if homepage and homepage != 'n/a' and 'foo.com' not in homepage:
        return homepage
    return None


def parse_pool_data():
    with open(io_dir / 'cardano_pool_data.json') as f:
        contents = f.read().splitlines()
    pool_data = [json.loads(item) for item in contents]

    logging.info("Parsing pool data..")

    identifiers = dict()
    pools_per_homepage = defaultdict(set)
    conflicts = defaultdict(set)

    for pool in pool_data:
        ticker = pool['ticker_name']
        metadata = json.loads(pool['metadata'])
        metadata.pop('ticker', None)

        if ticker in conflicts or (ticker in identifiers and metadata['homepage'] != identifiers[ticker]['homepage']):
            conflicts[ticker].add((metadata['name'], metadata['homepage']))
            if ticker in identifiers:
                prev_metadata = identifiers.pop(ticker)
                conflicts[ticker].add((prev_metadata['name'], prev_metadata['homepage']))
        else:
            identifiers[ticker] = metadata
            homepage = filter_homepage(metadata['homepage'])
            if homepage:
                pools_per_homepage[homepage].add(metadata['name'])

    with open(io_dir / 'cardano_identifiers.json', 'w') as f:
        json.dump(identifiers, f, indent=4)
        logging.info("Identifiers saved locally.")

    with open(io_dir / 'cardano_conflicts.json', 'w') as f:
        json.dump({ticker: list(info) for ticker, info in conflicts.items()}, f, indent=4)
        logging.info("Conflicts identified and saved locally. Please resolve manually.")

    make_clusters(pools_per_homepage)


def make_clusters(pools_per_homepage):
    logging.info("Detecting clusters..")
    clusters = {}

    for homepage, pool_names in pools_per_homepage.items():
        pool_names = list(pool_names)

        if len(pool_names) > 1:
            pool_names = sorted(pool_names, key=lambda x: (x[0].isdigit(), x))
            cluster_name = pool_names[0]
            clusters[cluster_name] = [{'name': name,'from': '', 'to': '', 'source': 'homepage'} for name in pool_names]

    with open(io_dir / 'cardano_clusters.json', 'w') as f:
        json.dump(clusters, f, indent=4)
        logging.info("Clusters detected and saved locally.")


if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--force-query',
        action='store_true',
        help='Flag to specify whether to query for project data regardless if the relevant data already exist.')
    args = parser.parse_args()

    io_dir = pathlib.Path(__file__).parent / 'cardano_preprocessing'
    io_dir.mkdir(parents=True, exist_ok=True)

    get_pool_data(force_query=args.force_query)
    parse_pool_data()
