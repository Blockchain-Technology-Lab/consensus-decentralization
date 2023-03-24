"""
Module with helper functions
"""
import pathlib
import json
import datetime
import calendar
import argparse

YEAR_DIGITS = 4
ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
INPUT_DIR = ROOT_DIR / 'input'
OUTPUT_DIR = ROOT_DIR / 'output'


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


def get_pool_data(project_name, timeframe):
    """
    Retrieves data regarding the pools of a project and the links between them.
    :param project_name: string that corresponds to the project under consideration
    :param timeframe: string that corresponds to the timeframe under consideration (in YYYY-MM-DD, YYYY-MM or YYYY
    format)
    :returns: (pool_data, pool_links) where pool_data is a dictionary with the tags, addresses and cluster
    information of each pool, and pool_links is a dictionary that reveals the ownership of pools
    """
    helpers_path = ROOT_DIR / '/helpers'

    start = get_timeframe_beginning(timeframe)
    end = get_timeframe_end(timeframe)

    pool_links = {}

    with open(helpers_path / f'/pool_information/{project_name}.json') as f:
        pool_data = json.load(f)
        cluster_data = pool_data['clusters']
    with open(helpers_path / '/legal_links.json') as f:
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

    return pool_data, pool_links


def get_pool_addresses(project_name, timeframe):
    """
    Retrieves the addresses associated with pools of a certain project over a given timeframe
    :param project_name: string that corresponds to the project under consideration
    :param timeframe: string that corresponds to the timeframe under consideration (in YYYY-MM-DD, YYYY-MM or YYYY
    format)
    :returns: a dictionary with known addresses and the names of the pools that own them (given that the timeframe of
    the ownership overlaps with the timeframe under consideration)
    """
    helpers_path = ROOT_DIR / '/helpers'

    start = get_timeframe_beginning(timeframe)
    end = get_timeframe_end(timeframe)

    with open(helpers_path / f'/pool_information/{project_name}.json') as f:
        address_data = json.load(f)['pool_addresses']

    address_links = {}
    if address_data:
        for address, addr_info in address_data.items():
            link_start, link_end = get_time_period(addr_info['from'], addr_info['to'])

            check_list = [  # Check if two periods overlap at any point
                start <= link_start <= end,
                start <= link_end <= end,
                link_start <= start <= link_end,
                link_start <= end <= link_end
            ]
            if any(check_list):
                address_links[address] = addr_info['name']
    return address_links


def write_blocks_per_entity_to_file(project_dir, blocks_per_entity, timeframe):
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
        csv_output = ['Entity,Resources']
        for key, val in sorted(blocks_per_entity.items(), key=lambda x: x[1], reverse=True):
            csv_output.append(','.join([key, str(val)]))
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
        for idx, line in enumerate(f.readlines()):
            if idx > 0:
                row = (','.join([i for i in line.split(',')[:-1]]), line.split(',')[-1])
                blocks_per_entity[row[0]] = int(row[1])
    return blocks_per_entity
