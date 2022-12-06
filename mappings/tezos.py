from collections import defaultdict
import json
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

    csv_output = ['Entity,Resources']
    for key, val in sorted(blocks_per_entity.items(), key=lambda x: x[1], reverse=True):
        csv_output.append(','.join([key, str(val)]))

    with open(project_dir + '/' + timeframe + '.csv', 'w') as f:
        f.write('\n'.join(csv_output))

    return blocks_per_entity
