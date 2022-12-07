from collections import defaultdict
import pathlib
from .lib import get_pool_data, write_csv_file


def process(project_name, dataset, timeframe):
    pool_data, pool_links = get_pool_data(project_name, timeframe)

    data = [tx for tx in dataset if tx['timestamp'][:len(timeframe)] == timeframe]
    data = sorted(data, key=lambda x: x['number'])

    blocks_per_entity = defaultdict(int)
    for tx in data:
        entity = tx['coinbase_param']
        if entity:
            if entity in pool_links.keys():
                entity = pool_links[entity]
            elif entity in pool_data['coinbase_tags'].keys():
                entity = pool_data['coinbase_tags'][entity]['name']
        else:
            pool = tx['coinbase_addresses']
            if pool:
                entity = pool
            else:
                entity = '[!] IOG (core nodes pre-decentralization)'

        blocks_per_entity[entity] += 1

    write_csv_file(str(pathlib.Path(__file__).parent.parent.resolve()) + '/ledgers/{}'.format(project_name), blocks_per_entity, timeframe)

    return blocks_per_entity
