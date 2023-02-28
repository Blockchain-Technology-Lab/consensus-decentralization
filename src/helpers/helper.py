# module with helper functions
import pathlib
import json
import datetime
import calendar

YEAR_DIGITS = 4
INPUT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / 'input'
OUTPUT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / 'output'


def get_start_date(timeframe):
    time_list = [int(i) for i in timeframe.split('-')]
    if len(time_list) == 3:
        start = datetime.date(time_list[0], time_list[1], time_list[2])
    elif len(time_list) == 2:
        start = datetime.date(time_list[0], time_list[1], 1)
    elif len(time_list) == 1:
        start = datetime.date(time_list[0], 1, 1)
    return start


def get_timeframe_end(timeframe):
    time_list = [int(i) for i in timeframe.split('-')]
    if len(time_list) == 3:
        end = datetime.date(time_list[0], time_list[1], time_list[2])
    elif len(time_list) == 2:
        end = datetime.date(time_list[0], time_list[1], calendar.monthrange(time_list[0], time_list[1])[1])
    elif len(time_list) == 1:
        end = datetime.date(time_list[0], 12, 31)
    return end


def get_time_period(frm, to):
    if frm:
        start = get_start_date(frm)
    else:
        start = datetime.date(2000, 1, 1)

    if to:
        time_list = [int(i) for i in to.split('-')]
        if len(time_list) == 3:
            end = datetime.date(time_list[0], time_list[1], time_list[2]) - datetime.timedelta(1)
        elif len(time_list) == 2:
            if time_list[1] == 1:
                end = datetime.date(time_list[0]-1, 12, 31)
            else:
                end = datetime.date(time_list[0], time_list[1]-1, calendar.monthrange(time_list[0], time_list[1]-1)[1])
        elif len(time_list) == 1:
            end = datetime.date(time_list[0]-1, 12, 31)
    else:
        end = datetime.date(2100, 1, 1)

    return start, end


def get_pool_data(project_name, timeframe):
    helpers_path = str(pathlib.Path(__file__).parent.parent.resolve()) + '/helpers'

    start = get_start_date(timeframe)
    end = get_timeframe_end(timeframe)

    pool_links = {}

    with open(helpers_path + f'/pool_information/{project_name}.json') as f:
        pool_data = json.load(f)
        cluster_data = pool_data['clusters']
    with open(helpers_path + '/legal_links.json') as f:
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
    helpers_path = str(pathlib.Path(__file__).parent.parent.resolve()) + '/helpers'

    start = get_start_date(timeframe)
    end = get_timeframe_end(timeframe)

    with open(helpers_path + f'/pool_information/{project_name}.json') as f:
        address_data = json.load(f)['pool_addresses']

    if not address_data:
        return {}

    address_links = {}
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


def write_csv_file(project_dir, blocks_per_entity, timeframe):
    with open(project_dir / f'{timeframe}.csv', 'w') as f:
        csv_output = ['Entity,Resources']
        for key, val in sorted(blocks_per_entity.items(), key=lambda x: x[1], reverse=True):
            csv_output.append(','.join([key, str(val)]))
        f.write('\n'.join(csv_output))


def get_blocks_per_entity_from_file(filename):
    blocks_per_entity = {}
    with open(filename) as f:
        for idx, line in enumerate(f.readlines()):
            if idx > 0:
                row = (','.join([i for i in line.split(',')[:-1]]), line.split(',')[-1])
                blocks_per_entity[row[0]] = int(row[1])
    return blocks_per_entity
