import pathlib
import google.cloud.bigquery as bq
import json
import argparse
from collections import defaultdict
import logging
import os
import re
from urllib.parse import urlparse


def get_pool_data_BQ(force_query):
    """
    Queries the BigQuery database for pool data and writes it to a json file.
    :param force_query: flag to specify whether to query for project data regardless if the relevant data already exist.
    :returns: dictionary, where each key is a pool's hash and the corresponding value is a dictionary with the
    pool's metadata (name, ticker, homepage, description)
    """
    logging.info("Getting pool data..")
    filename = 'cardano_pool_data_BQ.json'
    file = pathlib.Path(mapping_info_dir / "cardano_preprocessing" / filename)
    if not force_query and file.is_file():
        # logging.info('Pool data already exists locally. '
        #              'For querying anyway please run the script using the flag --force-query')
        with open(file) as f:
            pool_data = json.load(f)
        return pool_data

    client = bq.Client.from_service_account_json(json_credentials_path=mapping_info_dir / "google-service-account-key.json")

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


def get_pool_data_node():
    """
    Gets pool data that has been fetched from a Cardano node.
    :returns: dictionary, where each key is a pool's hash and the corresponding value is a dictionary with the
    pool's metadata (name, ticker, homepage, description)
    """
    filename = 'cardano_pool_data_node.json'
    file = pathlib.Path(mapping_info_dir / "cardano_preprocessing" / filename)
    with open(file) as f:
        pool_data = json.load(f)
    return pool_data


def merge_pool_data(pool_data_BQ, pool_data_node):
    """
    Merges pool data from BigQuery and from a Cardano node, giving priority to node data in case of conflicts.
    :param pool_data_BQ: dictionary with pool data that was fetched from BigQuery
    :param pool_data_node: dictionary with pool data that was fetched from a Cardano node
    :returns: dictionary, where each key is a pool's hash and the corresponding value is a dictionary with the
    pool's metadata (name, ticker, homepage, description).
    """
    logging.info("Merging pool data sources..")
    merged = pool_data_BQ | pool_data_node
    return merged


def parse_pool_identifiers(pool_data):
    """
    Extracts identifier information from pool data .
    Specifically, for each unique identifier (ticker) it saves the corresponding pool name and homepage and writes
    all of them to a json file.
    Conflicting tickers (same ticker, different domains) are flagged and
    excluded from identifiers to avoid false mapping.
    :param pool_data: dictionary, where each key is a pool's hash and the corresponding value is a dictionary with the
    pool's metadata (name, ticker, homepage, description)
    """
    logging.info("Parsing pool identifiers..")

    identifiers = dict()
    conflicts = dict()

    for pool in pool_data.values():
        ticker = pool.get('ticker', '').strip().upper()
        name = pool.get('name', '').strip()
        homepage = pool.get('homepage', '').strip()

        if not ticker:
            continue

        if ticker not in identifiers:
            identifiers[ticker] = {'name': name, 'link': homepage}
        else:
            existing = identifiers[ticker]
            same_domain = (
                get_domain(existing['link']) == get_domain(homepage)
                and bool(filter_homepage(homepage))
            )
            if not same_domain:
                # Genuine conflict — flag it
                if ticker not in conflicts:
                    conflicts[ticker] = [{'name': existing['name'], 'link': existing['link']}]
                conflicts[ticker].append({'name': name, 'link': homepage})

    # Remove conflicting tickers from identifiers to avoid false mapping
    for ticker in conflicts:
        identifiers.pop(ticker, None)

    return identifiers, conflicts


def normalise_ticker(ticker):
    """Strips trailing digits from a ticker for fuzzy matching, e.g. RAY1 -> RAY.
    If the ticker is entirely numeric, it's left unchanged."""
    stripped = re.sub(r'\d+$', '', ticker.strip().upper())
    return stripped if stripped else ticker.strip().upper()


def normalise_name(name):
    """Lowercases, strips trailing digits and whitespace for fuzzy name matching,
    e.g. 'Ray Network 1' -> 'ray network'."""
    return re.sub(r'\s*\d+$', '', name.strip().lower()).strip()


def score_same_entity(p1, p2):
    """
    Scores how likely two pools belong to the same operator entity.
    Returns a (score, signals) tuple where signals is a list of the signal
    names that contributed positively to the score (excluding penalties).

    Scoring:
      +3  same non-trivial domain
      +2  same ticker (after stripping trailing digits)
      +2  same name (after stripping trailing digits)
      +1  same (non-empty) description
      -1  different non-trivial domains (conflict signal)
    """
    score = 0
    signals = []

    # Domain match
    d1 = get_domain(p1.get('homepage', ''))
    d2 = get_domain(p2.get('homepage', ''))
    filtered_d1 = filter_homepage(p1.get('homepage', ''))
    filtered_d2 = filter_homepage(p2.get('homepage', ''))
    domains_valid = bool(filtered_d1 and filtered_d2 and d1 and d2)
    if domains_valid and d1 == d2:
        score += 3
        signals.append('homepage')
    elif domains_valid:
        score -= 1

    # Ticker match after normalisation (i.e. removing trailing digits, which often indicate different pools of the same operator)
    t1 = normalise_ticker(p1.get('ticker', ''))
    t2 = normalise_ticker(p2.get('ticker', ''))
    if bool(t1 and t2 and t1 == t2):
        score += 2
        signals.append('ticker')

    # Name similarity (strip trailing digits to catch "Pool1" vs "Pool2")
    n1 = normalise_name(p1.get('name', ''))
    n2 = normalise_name(p2.get('name', ''))
    if n1 and n2 and n1 == n2:
        score += 2
        signals.append('name')

    # Description match
    desc1 = p1.get('description', '').strip()
    desc2 = p2.get('description', '').strip()
    if desc1 and desc2 and desc1 == desc2:
        score += 1
        signals.append('description')

    return score, signals


def parse_pool_clusters(pool_data, score_threshold=3):
    """
    Clusters pools by operator entity using a multi-signal scoring approach.
    All pools are included in the output keyed by pool hash, since
    map_from_known_clusters looks up by reward address (pool hash).

    Any two pools that score >= score_threshold are placed in the same cluster.
    Transitivity is handled via union-find: if A clusters with B and B with C,
    all three end up in the same cluster.

    All pairs of pools are compared, which means that the complexity is O(n^2)
    but should be fine since it only runs once as a preprocessing step.

    Source for each pool reflects the signals from the comparison that first
    caused it to be clustered, or ['singleton'] if it was never grouped.
    """

    pool_hashes = list(pool_data.keys())
    pools = list(pool_data.values())
    n = len(pools)

    # --- Union-Find ---
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]  # path compression
            x = parent[x]
        return x

    def union(x, y):
        parent[find(x)] = find(y)

    # source[i] = signals that caused pool i to be clustered, or None if not yet
    source = [None] * n

    # --- Compare all pairs and merge if above threshold ---
    for i in range(n):
        for j in range(i + 1, n):
            score, signals = score_same_entity(pools[i], pools[j])
            if score >= score_threshold:
                if find(i) != find(j):
                    union(i, j)
                    for idx in [i, j]:
                        if source[idx] is None:
                            source[idx] = signals

    # --- Build clusters ---
    clusters = defaultdict(list)
    for i in range(n):
        clusters[find(i)].append(i)

    # --- Build output ---
    output = {}
    for members in clusters.values():
        pool_names = [pools[i].get('name', '') for i in members]
        cluster_name = determine_cluster_name(pool_names)
        for i in members:
            output[pool_hashes[i]] = {
                'cluster': cluster_name,
                'pool': pools[i].get('name', ''),
                'source': source[i] if source[i] is not None else ['singleton']
            }

    return output


def get_domain(url):
    """Extracts the domain from a URL, stripping www."""
    try:
        domain = urlparse(url).netloc.lower()
        return re.sub(r'^www\.', '', domain)
    except Exception:
        return ''


def filter_homepage(homepage):
    """
    Filters out dummy homepages. Specifically, it ignores homepage entries that are empty,
    have an 'empty' name (e.g. 'n/a') or include a dummy keyword in their name (e.g. foo.com)
    :param homepage: the homepage to be filtered (string)
    :returns: the homepage (as it is) if it is not a dummy homepage, else None
    """
    if not homepage:
        return None
    homepage = homepage.strip()
    if not homepage:
        return None

    homepage_lower = homepage.lower()

    INVALID_EXACT = {
        'https://', 'http://', 'n/a', 'na', '-', '--', '---', '....', '...',
        'tbd', 'coming', 'coming soon', 'in process', 'no webside', 'no website',
        'none', 'null', 'undefined', 'unknown'
    }
    if homepage_lower in INVALID_EXACT:
        return None

    INVALID_SUBSTRINGS = [
        'foo.com', 'example.com', 'invalidurl', 'test.com',
        'localhost', '127.0.0.1', 'yourdomain', 'yoursite',
        'mysite.com', 'mypool.com', 'poolname.com'
    ]

    if any(kw in homepage_lower for kw in INVALID_SUBSTRINGS):
        return None

    return homepage


def determine_cluster_name(pool_names):
    """
    Determines the name of a cluster of pools.
    First, it checks if there is a common prefix among all pool names. If there is, it uses that as the cluster name.
    If no common prefix exists, then it names the cluster after the first pool name (in alphabetical order and
    prioritizing names that don't start with a digit)
    :param pool_names: list of pool names that belong to the same cluster
    :returns: the name of the cluster
    """
    # make sure pool names have consistent case and filter out empty names
    pool_names = [pool_name.title() for pool_name in pool_names if pool_name]
    if not pool_names:
        return ''
    common_prefix = os.path.commonprefix(pool_names)
    if common_prefix:
        common_prefix = common_prefix.strip()
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
        default=False,
        help='Flag to specify whether to query for project data regardless if the relevant data already exist.'
    )
    args = parser.parse_args()

    mapping_info_dir = pathlib.Path(__file__).parent.parent
    pool_data_dir = pathlib.Path(__file__).parent

    pool_data_BQ = get_pool_data_BQ(force_query=args.force_query)
    pool_data_node = get_pool_data_node()

    merged_pool_data = merge_pool_data(pool_data_BQ, pool_data_node)

    identifiers, conflicts = parse_pool_identifiers(merged_pool_data)
    clusters = parse_pool_clusters(merged_pool_data)

    identifiers_dir = mapping_info_dir / 'identifiers'
    with open(identifiers_dir / 'cardano.json', 'w') as f:
        json.dump(identifiers, f, indent=4)

    clusters_dir = mapping_info_dir / 'clusters'
    with open(clusters_dir / 'cardano.json', 'w') as f:
        json.dump(clusters, f, indent=4)

    with open(mapping_info_dir / 'cardano_preprocessing' / 'ticker_conflicts.json', 'w') as f:
        json.dump(conflicts, f, indent=4)

    logging.info(f"Done. {len(identifiers)} identifiers, {len(clusters)} clustered pools, {len(conflicts)} conflicts.")
