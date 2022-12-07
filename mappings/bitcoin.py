from collections import defaultdict
import json
import codecs
import pathlib


def process(project_name, dataset, timeframe):
    project_dir = str(pathlib.Path(__file__).parent.parent.resolve()) + '/ledgers/{}'.format(project_name)

    data = [tx for tx in dataset if tx['timestamp'][:len(timeframe)] == timeframe]
    data = sorted(data, key=lambda x: x['number'])

    helpers_path = str(pathlib.Path(__file__).parent.parent.resolve()) + '/helpers'

    with open(helpers_path + '/pool_information/{}.json'.format(project_name)) as f:
        pool_data = json.load(f)

    pool_links = {}

    try:
        pool_links.update(pool_data['coinbase_address_links'][timeframe[:4]])
    except KeyError:
        pass

    with open(helpers_path + '/legal_links.json') as f:
        legal_links = json.load(f)
    pool_links.update(legal_links[timeframe[:4]])

    for key, val in pool_links.items():  # resolve chain links
        while val in pool_links.keys():
            val = pool_links[val]
        pool_links[key] = val

    try:
        pool_addresses = pool_data['pool_addresses'][timeframe[:4]]
    except KeyError:
        pool_addresses = {}

    multi_pool_blocks = set()
    multi_pool_addresses = defaultdict(list)
    blocks_per_entity = defaultdict(int)
    for tx in data:
        block_year = tx['timestamp'][:4]

        coinbase_param = codecs.decode(tx['coinbase_param'], 'hex')
        coinbase_addresses = tx['coinbase_addresses'].split(',')

        pool_match = False
        for (tag, info) in pool_data['coinbase_tags'].items():  # Check if coinbase param contains known pool tag
            if tag in str(coinbase_param):
                entity = info['name']
                pool_match = True
                for addr in tx['coinbase_addresses'].split(','):
                    if addr in pool_addresses.keys() and pool_addresses[addr] != entity:
                        with open(project_dir + '/multi_pool_addresses.csv'.format(timeframe), 'a') as f:
                            f.write('{},{},{},{}\n'.format(tx['timestamp'], addr, pool_addresses[addr], entity))

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
                    multi_pool_blocks.add('{}: {}'.format(tx['number'], entity))
            else:
                if len(coinbase_addresses) == 1:
                    entity = coinbase_addresses[0]
                else:
                    entity = ' '.join([
                        addr[:5] + '...' + addr[-5:] for addr in coinbase_addresses
                    ])

        if entity in pool_links.keys():
            entity = pool_links[entity]

        blocks_per_entity[entity] += 1

    csv_output = ['Entity,Resources']
    for key, val in sorted(blocks_per_entity.items(), key=lambda x: x[1], reverse=True):
        csv_output.append(','.join([key, str(val)]))

    with open(project_dir + '/' + timeframe + '.csv', 'w') as f:
        f.write('\n'.join(csv_output))

    with open(project_dir + '/multi_pool_blocks.csv', 'a') as f:
        f.write('{},{}\n'.format(timeframe, '--'.join(multi_pool_blocks)))

    return blocks_per_entity
