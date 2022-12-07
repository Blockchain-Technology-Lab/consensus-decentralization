from collections import defaultdict
import pathlib
from .lib import get_pool_data, write_csv_file


def process(project_name, dataset, timeframe):
    pool_data = get_pool_data(project_name, timeframe)
    try:
        pool_addresses = pool_data['pool_addresses'][timeframe[:4]]
    except KeyError:
        pool_addresses = {}

    data = [tx for tx in dataset if tx['timestamp'][:len(timeframe)] == timeframe]
    data = sorted(data, key=lambda x: x['number'])

    blocks_per_entity = defaultdict(int)
    for tx in data:
        block_year = tx['timestamp'][:4]

        try:
            coinbase_addresses = tx['coinbase_addresses']
        except KeyError:
            coinbase_addresses = '----- UNDEFINED MINER -----'

        if coinbase_addresses in pool_addresses.keys():
            entity = pool_addresses[coinbase_addresses]
        else:
            entity = coinbase_addresses

        if entity in pool_links.keys():
            entity = pool_links[entity]

        blocks_per_entity[entity] += 1

    write_csv_file(str(pathlib.Path(__file__).parent.parent.resolve()) + '/ledgers/{}'.format(project_name), blocks_per_entity, timeframe)

    return blocks_per_entity
