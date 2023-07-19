"""
Module with helper functions
"""
import pathlib
import json
import datetime
import calendar
import argparse
from collections import defaultdict
from yaml import safe_load

YEAR_DIGITS = 4
ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
INPUT_DIR = ROOT_DIR / 'input'
OUTPUT_DIR = ROOT_DIR / 'output'
HELPERS_DIR = ROOT_DIR / 'src/helpers'


def valid_date(date_string):
    """
    Validates the given string if it corresponds to a correct date and is in YYYY-MM-DD, YYYY-MM or YYYY format
    :param date_string: a string representation of a date
    :returns: the string as it was given, if it corresponds to a valid date in the specified format
    :raises argparse.ArgumentTypeError: if the wrong format is used or if the date_string doesn't correspond to a valid
    date
    """
    try:
        get_timeframe_beginning(date_string)
    except ValueError:
        raise argparse.ArgumentTypeError("Please use the format YYYY-MM-DD for the timeframe argument "
                                         "(day and month can be omitted).")
    return date_string


def get_timeframe_beginning(timeframe):
    """
    Determines the first day of a given timeframe
    :param timeframe: a string representation of the timeframe in YYYY-MM-DD, YYYY-MM or YYYY format
    :returns: a date object corresponding to the first day of the timeframe
    """
    return datetime.date.fromisoformat(timeframe.ljust(10, 'x').replace('xxx', '-01'))


def get_timeframe_end(timeframe):
    """
    Determines the last day of a given timeframe
    :param timeframe: a string representation of the timeframe in YYYY-MM-DD, YYYY-MM or YYYY format
    :returns: a date object corresponding to the last day of the timeframe
    """
    timeframe_with_month = timeframe.ljust(7, 'x').replace('xxx', '-12')
    year, month = [int(i) for i in timeframe_with_month.split('-')][:2]
    days_in_month = calendar.monthrange(year, month)[1]
    timeframe_with_day = timeframe_with_month.ljust(10, 'x').replace('xxx', f'-{days_in_month}')
    return datetime.date.fromisoformat(timeframe_with_day)


def get_time_period(frm, to):
    """
    Determines the first day and last day of a time period defined by frm and to
    :param frm: a string representation of the starting date in YYYY-MM-DD, YYYY-MM or YYYY format, or the empty string
    :param to: a string representation of the end date plus one day in YYYY-MM-DD, YYYY-MM or YYYY format, or the empty
    string
    :returns: a tuple of date objects with the first and last day of the time period
    """
    start = get_timeframe_beginning(frm) if frm else datetime.date.min
    end = get_timeframe_beginning(to) - datetime.timedelta(1) if to else datetime.date.max
    return start, end


def get_known_entities(ledger):
    known_entities = set()
    try:
        with open(HELPERS_DIR / f'pool_information/coinbase_tags/{ledger}.json') as f:
            coinbase_tags = json.load(f)
        for info in coinbase_tags.values():
            known_entities.add(info['name'])
    except FileNotFoundError:
        pass

    try:
        with open(HELPERS_DIR / f'pool_information/clusters/{ledger}.json') as f:
            clusters = json.load(f)
        for cluster in clusters.keys():
            known_entities.add(cluster)
    except FileNotFoundError:
        pass

    try:
        with open(HELPERS_DIR / f'pool_information/addresses/{ledger}.json') as f:
            pool_addresses = json.load(f)
        for address_info in pool_addresses.values():
            known_entities.add(address_info['name'])
    except FileNotFoundError:
        pass

    with open(HELPERS_DIR / 'legal_links.json') as f:
        legal_links = json.load(f)
    for parent, children in legal_links.items():
        known_entities.add(parent)
        for child in children:
            known_entities.add(child['name'])

    return known_entities


def get_pool_tags(project_name):
    """
    Retrieves coinbase tag data regarding the pools of a project.
    :param project_name: string that corresponds to the project under consideration
    :returns: pool_tags, a dictionary with the tags information of each pool
    """
    try:
        with open(HELPERS_DIR / f'pool_information/coinbase_tags/{project_name}.json') as f:
            coinbase_tags = json.load(f)
    except FileNotFoundError:
        coinbase_tags = {}

    return coinbase_tags


def get_pool_links(project_name, timeframe):
    """
    Retrieves data regarding the links between the pools of a project.
    :param project_name: string that corresponds to the project under consideration
    :param timeframe: string that corresponds to the timeframe under consideration (in YYYY-MM-DD, YYYY-MM or YYYY
    format)
    :returns: (pool_data, pool_links) where pool_data is a dictionary with the tags, addresses and cluster
    information of each pool, and pool_links is a dictionary that reveals the ownership of pools
    """
    start = get_timeframe_beginning(timeframe)
    end = get_timeframe_end(timeframe)

    pool_links = {}

    try:
        with open(HELPERS_DIR / f'pool_information/clusters/{project_name}.json') as f:
            cluster_data = json.load(f)
    except FileNotFoundError:
        cluster_data = {}

    with open(HELPERS_DIR / 'legal_links.json') as f:
        legal_data = json.load(f)

    for data in [cluster_data, legal_data]:
        for cluster_name, pools in data.items():
            for pool_info in pools:
                link_start, link_end = get_time_period(pool_info['from'], pool_info['to'])

                check_list = [  # Check if two periods overlap at any point
                    start <= link_start <= end,
                    start <= link_end <= end,
                    link_start <= start <= link_end,
                    link_start <= end <= link_end
                ]
                if any(check_list):
                    pool_links[pool_info['name']] = cluster_name

    for parent, child in pool_links.items():  # resolve chain links
        while child in pool_links.keys():
            next_child = pool_links[child]
            if next_child == child:
                # Cluster's name is the same as the primary pool's name
                break
            elif next_child == parent:
                raise AssertionError(f'Circular dependency: {parent}, {child}')
            else:
                child = next_child
        pool_links[parent] = child

    return pool_links


def get_pool_addresses(project_name):
    """
    Retrieves the addresses associated with pools of a certain project over a given timeframe
    :param project_name: string that corresponds to the project under consideration
    :returns: a dictionary with known addresses and the names of the pools that own them (given that the timeframe of
    the ownership overlaps with the timeframe under consideration)
    """
    try:
        with open(HELPERS_DIR / f'pool_information/addresses/{project_name}.json') as f:
            address_data = json.load(f)
    except FileNotFoundError:
        address_data = {}

    address_links = {address: addr_info['name'] for address, addr_info in address_data.items()}

    return address_links


def write_blocks_per_entity_to_file(project_dir, blocks_per_entity, groups, timeframe):
    """
    Produces a csv file with information about the resources (blocks) that each entity controlled over some timeframe.
    The entries are sorted so that the entities that controlled the most resources appear first.
    :param project_dir: pathlib.PosixPath object of the output directory corresponding to the project. This is where
    the produced csv file is written to.
    :param blocks_per_entity: a dictionary with entities and the number of blocks they produced over the given timeframe
    :param timeframe: string that corresponds to the timeframe under consideration (in YYYY-MM-DD, YYYY-MM or YYYY
    format). Also used for naming the produced file.
    """
    with open(project_dir / f'{timeframe}.csv', 'w') as f:
        csv_output = ['Entity Group,Entity,Resources']
        for entity, resources in sorted(blocks_per_entity.items(), key=lambda x: x[1], reverse=True):
            csv_output.append(','.join([groups[entity], entity, str(resources)]))
        f.write('\n'.join(csv_output))


def get_blocks_per_entity_from_file(filepath):
    """
    Retrieves information about the number of blocks that each entity produced over some timeframe for some project.
    :param filepath: the path to the file with the relevant information. It can be either an absolute or a relative
    path in either a pathlib.PosixPath object or a string.
    :returns: a dictionary with entities and the number of blocks they produced
    """
    blocks_per_entity = {}
    with open(filepath) as f:
        for idx, line in enumerate(f.readlines()[1:]):
            group, entity, resources = line.split(',')
            blocks_per_entity[entity] = int(resources)
    return blocks_per_entity


def get_blocks_per_entity_group_from_file(filepath):
    """
    Retrieves information about the number of blocks that each entity group produced over some timeframe for some
    project. Note that all unidentified addresses are merged into one 'Unknown' group
    :param filepath: the path to the file with the relevant information. It can be either an absolute or a relative
    path in either a pathlib.PosixPath object or a string.
    :returns: a dictionary with entity groups and the number of blocks they produced
    """
    blocks_per_entity_group = defaultdict(int)
    with open(filepath) as f:
        for idx, line in enumerate(f.readlines()[1:]):
            group, entity, resources = line.split(',')
            blocks_per_entity_group[group] += int(resources)
    return blocks_per_entity_group


def get_special_addresses(project_name):
    """
    Retrieves special addresses of a project, such as treasury addresses, protocol related smart contracts, etc.
    :param project_name: string that corresponds to the project under consideration
    :returns: special_addresses, which is a set of addresses
    """
    with open(HELPERS_DIR / 'special_addresses.json') as f:
        special_address_data = json.load(f)

    try:
        special_addresses = special_address_data[project_name]
    except KeyError:
        return set()

    return set([addr['address'] for addr in special_addresses])


def get_config_data():
    """
    Reads the configuration data of the project. This data is read from a file named "confing.yaml" located at the
    root directory of the project.
    :returns: a dictionary of configuration keys and values
    """
    with open(ROOT_DIR / "config.yaml") as f:
        config = safe_load(f)
    return config


def get_metrics_config():
    """
    Reads data about the metrics that will be used from the project's config file. All metrics that are mentioned in
    the file (not in comments) will be used at the "analyze" and "plot" stages. If a metric is parameterized, then the
    values of its parameters are also given in this file. To add a new metric, one can add a new entry in the file, and
    to disable a metric it suffices to comment out the relevant line(s).
    :returns: a dictionary where the keys correspond to metric names and the values to their configurations
    (dictionary of parameter - value pairs for each parameter that the metric takes)
    :raises AssertionError if the file defines different parameter values for metrics that are supposed to be
    consistent (e.g. entropy and entropy percentage)
    """
    config = get_config_data()
    metrics = config['metrics']
    metric_families = [['entropy', 'entropy_percentage']]
    for metric_family in metric_families:
        # ensure that parameter values that correspond to the same family of metrics are consistent
        params = None
        for metric in metric_family:
            if params is None:
                params = metrics[metric]
            else:
                assert metrics[metric] == params, "Metrics that belong in the same family (e.g. entropy and entropy " \
                                                  "percentage) must use the same parameter values. " \
                                                  "Please update your config.yaml file accordingly."
    return metrics


def get_default_ledgers():
    """
    Retrieves data regarding the default ledgers to use
    :returns: a list of strings that correspond to the ledgers that will be used (unless overriden by the relevant cmd
    arg)
    """
    config = get_config_data()
    ledgers = config['default_ledgers']
    return ledgers
