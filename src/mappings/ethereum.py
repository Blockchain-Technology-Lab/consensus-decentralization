from collections import defaultdict
import pathlib
from src.helpers.helper import get_pool_data, write_csv_file


def process(project_name, dataset, timeframe):
    pool_data, pool_links = get_pool_data(project_name, timeframe)
    try:
        pool_addresses = pool_data['pool_addresses'][timeframe[:4]]
    except KeyError:
        pool_addresses = {}

    project_dir = str(pathlib.Path(__file__).parent.parent.resolve()) + '/ledgers/{}'.format(project_name)

    data = [tx for tx in dataset if tx['timestamp'][:len(timeframe)] == timeframe]
    data = sorted(data, key=lambda x: x['number'])

    blocks_per_entity = defaultdict(int)
    for tx in data:
        try:
            coinbase_param = bytes.fromhex(tx['coinbase_param'][2:]).decode('utf-8')
        except (UnicodeDecodeError, ValueError):
            coinbase_param = tx['coinbase_param']

        coinbase_addresses = tx['coinbase_addresses']

        pool_match = False
        for (tag, info) in pool_data['coinbase_tags'].items():  # Check if coinbase param contains known pool tag
            if tag in str(coinbase_param):
                entity = info['name']
                pool_addresses[coinbase_addresses] = entity
                pool_match = True
                if coinbase_addresses in pool_addresses.keys() and pool_addresses[coinbase_addresses] != entity:
                    with open(project_dir + '/multi_pool_addresses.csv', 'a') as f:
                        f.write('{},{},{},{}\n'.format(tx['timestamp'], coinbase_addresses, pool_addresses[coinbase_addresses], entity))
                break

        if not pool_match:
            if coinbase_addresses in pool_addresses.keys():
                entity = pool_addresses[coinbase_addresses]
            else:
                entity = coinbase_addresses

        if entity in pool_links.keys():
            entity = pool_links[entity]

        blocks_per_entity[entity.replace(',', '')] += 1

    write_csv_file(project_dir, blocks_per_entity, timeframe)

    return blocks_per_entity
