from collections import defaultdict
import codecs
import pathlib
from src.helpers.helper import get_pool_data, write_csv_file


def process(project_name, dataset, timeframe):
    pool_data, pool_links = get_pool_data(project_name, timeframe)
    try:
        pool_addresses = pool_data['pool_addresses'][timeframe[:4]]
    except KeyError:
        pool_addresses = {}

    project_dir = str(pathlib.Path(__file__).parent.parent.resolve()) + f'/ledgers/{project_name}'

    data = [tx for tx in dataset if tx['timestamp'][:len(timeframe)] == timeframe]
    data = sorted(data, key=lambda x: x['number'])

    multi_pool_blocks = set()
    blocks_per_entity = defaultdict(int)
    for tx in data:
        coinbase_param = codecs.decode(tx['coinbase_param'], 'hex')
        coinbase_addresses = tx['coinbase_addresses'].split(',')

        pool_match = False
        for (tag, info) in pool_data['coinbase_tags'].items():  # Check if coinbase param contains known pool tag
            if tag in str(coinbase_param):
                entity = info['name']
                pool_match = True
                for addr in tx['coinbase_addresses'].split(','):
                    if addr in pool_addresses.keys() and pool_addresses[addr] != entity:
                        with open(project_dir + '/multi_pool_addresses.csv', 'a') as f:
                            f.write(f'{tx["timestamp"]},{addr},{pool_addresses[addr]},{entity}\n')

                    pool_addresses[addr] = entity
                break

        if not pool_match:
            block_pools = set()
            for addr in coinbase_addresses:  # Check if address is associated with pool
                if addr in pool_addresses.keys():
                    block_pools.add(pool_addresses[addr])
            if block_pools:
                entity = str('/'.join(sorted(block_pools)))
                if len(block_pools) > 1:
                    multi_pool_blocks.add(f'{tx["number"]}: {entity}')
            else:
                if len(coinbase_addresses) == 1:
                    entity = coinbase_addresses[0]
                else:
                    entity = '/'.join([
                        addr[:5] + '...' + addr[-5:] for addr in coinbase_addresses
                    ])

        if entity in pool_links.keys():
            entity = pool_links[entity]

        blocks_per_entity[entity.replace(',', '')] += 1

    write_csv_file(project_dir, blocks_per_entity, timeframe)

    with open(project_dir + '/multi_pool_blocks.csv', 'a') as f:
        f.write(f'{timeframe},{"--".join(multi_pool_blocks)}\n')

    return blocks_per_entity
