import requests
import pathlib
import logging
import json
import time
import sys

def get_pool_data():
    """
    Queries the Balance Pool Groups API and Cardanoscan to get pool data and write it to a json file.
    :returns: dictionary, where each key is a pool's hash and the corresponding value is a dictionary with the
    pool's metadata (name, ticker, homepage, description)
    :returns: list of dictionaries, where each each dictionary contains metadata (pool_hash, pool_id, pool_group, pool_ticker) 
    representing a pool.
    """
    logging.info("Getting pool data..")
    filename = 'cardano_pool_data.json'
    
    request_interval = 1 / 5  # 5 requests per second
    last_request_time = time.time()

    pools = requests.get("https://www.balanceanalytics.io/api/groupdata.json").json()[0]['pool_group_json']
    pool_data = {}
    pool_groups = []
    for pool in pools:
        current_time = time.time()
        elapsed_time = current_time - last_request_time
        if elapsed_time < request_interval: # Trying to stay within Cardanoscan's rate limits.
            time.sleep(request_interval - elapsed_time)

        try:
            pool_response = requests.get(f"https://cardanoscan.io/search?filter=all&value={pool['pool_hash']}", allow_redirects=False)
        except Exception as e:
            sys.exit(f"An error occurred while trying to fetch data for pool hash {pool['pool_hash']}: {e}")
        last_request_time = time.time()

        if pool_response.status_code == 302:  # We can grab the pool_id using the redirect from Cardanoscan
            redirect_url = pool_response.headers['Location']
            pool_id = redirect_url.split('/')[-1]

            logging.debug(f"{pool['pool_hash']} -> {pool_id}")
            pool_data[pool_id] = {
                "description": pool['pool_ticker'],  # Filler.  Need to get this info elsewhere.
                "homepage": pool['pool_ticker'],     # Filler.  Need to get this info elsewhere.
                "name": pool['pool_ticker'],         # Filler.  Need to get this info elsewhere.
                "ticker": pool['pool_ticker']
            }

            pool_groups.append({
                "pool_hash": pool['pool_hash'],
                "pool_id": pool_id,
                "pool_group": pool['pool_group'],
                "pool_ticker": pool['pool_ticker']
            })

    with open(filename, 'w') as f:
        json.dump(pool_data, f, indent=4)
    logging.info('Pool data saved locally.')
    return pool_data, pool_groups

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

def parse_pool_clusters(pool_groups):
    """
    Extracts cluster information from pool data.
    :param pool_groups: list of dictionaries, where each each dictionary contains metadata (pool_hash, pool_group, pool_ticker, pool_id) 
    representing a pool.
    """
    logging.info("Parsing pool clusters..")
    clusters = {}
    for pool in pool_groups:
        if pool['pool_group'] != "SINGLEPOOL":
            clusters[pool['pool_id']] = {
                "cluster": pool['pool_group'],
                "pool": pool['pool_ticker'],
                "source": "Balance Pool Groups API"
            }

    clusters_dir = mapping_info_dir / 'clusters'
    with open(clusters_dir / 'cardano.json', 'w') as f:
        json.dump(clusters, f, indent=4)
    logging.info("Clusters detected and saved locally.")

if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)

    #mapping_info_dir = pathlib.Path(__file__).parent.parent
    mapping_info_dir = pathlib.Path(__file__).parent

    pool_data, pool_groups = get_pool_data()
    if pool_data:
        parse_pool_identifiers(pool_data)
    if pool_groups:
        parse_pool_clusters(pool_groups)
