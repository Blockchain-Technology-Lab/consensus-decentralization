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
    Returns an integer score; higher = more likely same entity.

    Scoring:
      +3  same non-trivial domain
      +2  same ticker (after stripping trailing digits)
      +2  same name (after stripping trailing digits)
      +1  same (non-empty) description
      -1  different non-trivial domains (conflict signal)
    """
    score = 0

    # Domain match
    d1 = get_domain(p1.get('homepage', ''))
    d2 = get_domain(p2.get('homepage', ''))
    filtered_d1 = filter_homepage(p1.get('homepage', ''))
    filtered_d2 = filter_homepage(p2.get('homepage', ''))
    domains_valid = bool(filtered_d1 and filtered_d2 and d1 and d2)
    if domains_valid and d1 == d2:
        score += 3
    elif domains_valid:
        score -= 1

    # Ticker match after normalisation (i.e. removing trailing digits, which often indicate different pools of the same operator)
    t1 = normalise_ticker(p1.get('ticker', ''))
    t2 = normalise_ticker(p2.get('ticker', ''))
    if bool(t1 and t2 and t1 == t2):
        score += 2

    # Name similarity (strip trailing digits to catch "Pool1" vs "Pool2")
    n1 = normalise_name(p1.get('name', ''))
    n2 = normalise_name(p2.get('name', ''))
    if n1 and n2 and n1 == n2:
        score += 2

    # Description match
    desc1 = p1.get('description', '').strip()
    desc2 = p2.get('description', '').strip()
    if desc1 and desc2 and desc1 == desc2:
        score += 1

    return score


def parse_pool_clusters(pool_data, score_threshold=3):
    """
    Clusters pools by operator entity.
    Step 1: group pools that share the same valid domain (strong anchor).
    Step 2: merge any two domain-groups that share a ticker AND score >= threshold
            (catches operators with different domains but same ticker/name).
    Step 3: assign cluster names and return.
    :param pool_data: dictionary, where each key is a pool's hash and the corresponding value is a dictionary with the
    pool's metadata (name, ticker, homepage, description)
    :param score_threshold: the minimum score (as returned by score_same_entity) for two pools to be clustered together
    :returns: dictionary, where each key is a pool's hash and the corresponding value is a dictionary with the pool's name, the name of the cluster it belongs to and the source of the clustering information
    """
    logging.info("Clustering pools by operator entity..")

    pool_hashes = list(pool_data.keys())
    pools = list(pool_data.values())

    # --- Step 1: seed clusters from shared domain ---
    domain_to_indices = defaultdict(list)
    for i, pool in enumerate(pools):
        domain = get_domain(pool.get('homepage', ''))
        if domain and filter_homepage(pool.get('homepage', '')):
            domain_to_indices[domain].append(i)

    # Each cluster is a set of pool indices. Start one cluster per shared domain.
    # Pools with unique/no domain each get their own singleton cluster.
    clusters = []
    index_to_cluster = {}   # pool index -> cluster list index
    index_to_source = {}    # pool index -> how it was clustered

    for domain, indices in domain_to_indices.items():
        if len(indices) > 1:
            cluster_id = len(clusters)
            clusters.append(set(indices))
            for i in indices:
                index_to_cluster[i] = cluster_id
                index_to_source[i] = 'homepage'

    for i in range(len(pools)):
        if i not in index_to_cluster:
            cluster_id = len(clusters)
            clusters.append({i})
            index_to_cluster[i] = cluster_id
            index_to_source[i] = None

    # --- Step 2: merge clusters that share a ticker and score >= threshold
    ticker_to_cluster_ids = defaultdict(set)
    for i, pool in enumerate(pools):
        ticker = pool.get('ticker', '').strip().upper()
        if ticker:
            ticker_to_cluster_ids[ticker].add(index_to_cluster[i])

    def merge_clusters(id_a, id_b):
        """Merge cluster id_b into cluster id_a, updating index_to_cluster.
        Pools moving from id_b get source 'multi_signal' unless they already
        had a more specific source (e.g. 'homepage') assigned in Step 1."""
        if id_a == id_b:
            return
        for i in clusters[id_b]:
            index_to_cluster[i] = id_a
            if index_to_source[i] is None:
                index_to_source[i] = 'multi_signal'
        clusters[id_a].update(clusters[id_b])
        clusters[id_b] = set()

    for ticker, cluster_ids in ticker_to_cluster_ids.items():
        cluster_ids = list(cluster_ids)
        for a in range(len(cluster_ids)):
            for b in range(a + 1, len(cluster_ids)):
                if not clusters[cluster_ids[a]] or not clusters[cluster_ids[b]]:
                    continue
                id_a = index_to_cluster[next(iter(clusters[cluster_ids[a]]))]
                id_b = index_to_cluster[next(iter(clusters[cluster_ids[b]]))]
                if id_a == id_b:
                    continue
                rep_a = pools[next(iter(clusters[id_a]))]
                rep_b = pools[next(iter(clusters[id_b]))]
                if score_same_entity(rep_a, rep_b) >= score_threshold:
                    for i in clusters[id_a]:
                        if index_to_source[i] is None:
                            index_to_source[i] = 'multi_signal'
                    merge_clusters(id_a, id_b)

    # --- Step 3: build output ---
    output = {}
    for cluster in clusters:
        if not cluster:
            continue
        pool_names = [pools[i].get('name', '') for i in cluster]
        cluster_name = determine_cluster_name(pool_names)
        for i in cluster:
            pool_hash = pool_hashes[i]
            output[pool_hash] = {
                'cluster': cluster_name,
                'pool': pools[i].get('name', ''),
                'source': index_to_source[i] if index_to_source[i] is not None else 'singleton'
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
