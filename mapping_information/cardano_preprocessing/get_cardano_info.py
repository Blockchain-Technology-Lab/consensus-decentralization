import pathlib
import google.cloud.bigquery as bq
import json
import argparse
from collections import defaultdict
import logging
import os


def get_pool_data(force_query):
    """
    Queries the BigQuery database for pool data and writes it to a json file.
    :param force_query: flag to specify whether to query for project data regardless if the relevant data already exist.
    :returns: dictionary, where each key is a pool's hash and the corresponding value is a dictionary with the
    pool's metadata (name, ticker, homepage, description)
    """
    logging.info("Getting pool data..")
    filename = 'cardano_pool_data.json'
    file = pathlib.Path(filename)
    if not force_query and file.is_file():
        logging.info('Pool data already exists locally. '
                     'For querying anyway please run the script using the flag --force-query')
        with open(file) as f:
            pool_data = json.load(f)
        return pool_data

    root_dir = pathlib.Path(__file__).parent.parent.parent
    client = bq.Client.from_service_account_json(json_credentials_path=root_dir / "google-service-account-key.json")

    query = ('SELECT pool_hash, json as metadata FROM `iog-data-analytics.cardano_mainnet.pool_offline_data`')
    logging.info("Fetching pool data from BigQuery..")
    query_job = client.query(query)
    try:
        rows = query_job.result()
    except Exception as e:
        logging.info(f'The following exception was raised: {repr(e)}')
        return None
    pool_data = {row[0]: eval(row[1]) for row in rows}
    # write json to file
    with open(file, 'w') as f:
        json.dump(pool_data, f, indent=4)
    logging.info('Pool data saved locally.')
    return pool_data


def parse_pool_identifiers(pool_data):
    """
    Extracts identifier information from pool data .
    Specifically, for each unique identifier (ticker) it saves the corresponding pool name and homepage and writes
    all of them to a json file.
    Duplicate tickers are ignored.
    :param pool_data: dictionary, where each key is a pool's hash and the corresponding value is a dictionary with the
    pool's metadata (name, ticker, homepage, description)
    """
    logging.info("Parsing pool identifiers..")

    identifiers = dict()
    conflicts = set()

    for pool_metadata in pool_data.values():
        ticker = pool_metadata['ticker']
        name = pool_metadata['name']
        homepage = pool_metadata['homepage']

        if ticker in conflicts:
            continue

        if ticker in identifiers:
            # duplicate ticker, remove from identifiers to avoid false classification
            identifiers.pop(ticker)
            conflicts.add(ticker)
            continue

        identifiers[ticker] = {'name': name, 'link': homepage}

    identifiers_dir = mapping_info_dir / 'identifiers'
    with open(identifiers_dir / 'cardano.json', 'w') as f:
        json.dump(identifiers, f, indent=4)
        logging.info("Identifiers saved locally.")


def parse_pool_clusters(pool_data):
    """
    Extracts cluster information from pool data.
    Specifically, it detects clusters of pools that share the same homepage and writes them to a json file.
    :param pool_data: dictionary, where each key is a pool's hash and the corresponding value is a dictionary with the
    pool's metadata (name, ticker, homepage, description)
    """
    logging.info("Detecting pool clusters..")
    pools_per_homepage = defaultdict(set)
    for pool_hash, pool_metadata in pool_data.items():
        pool_name = pool_metadata['name']
        homepage = pool_metadata['homepage']
        homepage = filter_homepage(homepage)
        if homepage:
            pools_per_homepage[homepage].add((pool_hash, pool_name))

    clusters = dict()
    for pools in pools_per_homepage.values():
        pool_names = [pool_name for _, pool_name in pools]

        if len(pool_names) > 1:
            cluster_name = determine_cluster_name(pool_names)
            clusters.update(
                {
                    pool_hash: {'cluster': cluster_name, 'pool': pool_name, 'source': 'homepage'}
                    for pool_hash, pool_name in pools
                }
            )

    clusters_dir = mapping_info_dir / 'clusters'
    with open(clusters_dir / 'cardano.json', 'w') as f:
        json.dump(clusters, f, indent=4)
        logging.info("Clusters detected and saved locally.")


def filter_homepage(homepage):
    """
    Filters out dummy homepages. Specifically, it ignores homepage entries that are empty,
    have an 'empty' name (e.g. 'n/a') or include a dummy keyword in their name (e.g. foo.com)
    :param homepage: the homepage to be filtered (string)
    :returns: the homepage (as it is) if it is not a dummy homepage, else None
    """
    empty_names = [
        'n/a', 'N/A', 'NA', 'https://', 'http://', '-', '---', 'coming', 'TBD', '...', 'In Process',
        'no webside', 'Coming Soon'
    ]
    placeholder_keywords = ['foo.com', 'example.com', 'invalidurl']
    if homepage:
        homepage = homepage.strip()
        if any(homepage == empty_name for empty_name in empty_names):
            return None
        if any(placeholder_keyword in homepage.lower() for placeholder_keyword in placeholder_keywords):
            return None
        return homepage
    return None


def determine_cluster_name(pool_names):
    """
    Determines the name of a cluster of pools.
    First, it checks if there is a common prefix among all pool names. If there is, it uses that as the cluster name.
    If no common prefix exists, then it names the cluster after the first pool name (in alphabetical order and
    prioritizing names that don't start with a digit)
    :param pool_names: list of pool names that belong to the same cluster
    :returns: the name of the cluster
    """
    pool_names = [pool_name.title() for pool_name in pool_names]  # make sure pool names have consistent case
    common_prefix = os.path.commonprefix(pool_names)
    if common_prefix:
        return common_prefix
    # if there is no common prefix, sort pool names alphabetically, prioritizing names that don't start with a digit
    # and use the first one as the cluster name
    pool_names = sorted(pool_names, key=lambda x: (x[0].isdigit(), x))
    return pool_names[0]


if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--force-query',
        action='store_true',
        help='Flag to specify whether to query for project data regardless if the relevant data already exist.'
    )
    args = parser.parse_args()

    mapping_info_dir = pathlib.Path(__file__).parent.parent

    pool_data = get_pool_data(force_query=args.force_query)
    if pool_data:
        parse_pool_identifiers(pool_data)
        parse_pool_clusters(pool_data)
