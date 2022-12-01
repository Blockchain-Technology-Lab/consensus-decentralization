from collections import defaultdict
import json


def process(project_dir, timeframe):
    with open(project_dir + '/data.json') as f:
        data = json.load(f)
        data = sorted(data, key=lambda x: x['number'])

    for (idx, tx) in enumerate(data):
        block_year = tx['timestamp'][:4]
        block_month = int(tx['timestamp'][5:7])
        if int(block_year) > 2021 and block_month > 8:  # Exclude PoS blocks (after Aug 22)
            break
    data = data[:idx]

    data = [tx for tx in data if tx['timestamp'][:len(timeframe)] == timeframe]

    with open(project_dir + '/pools.json') as f:
        pool_data = json.load(f)

    pool_links = {}
    try:
        pool_links.update(pool_data['legal_links'][timeframe[:4]])
    except KeyError:
        pass
    try:
        pool_links.update(pool_data['coinbase_address_links'][timeframe[:4]])
    except KeyError:
        pass

    for key, val in pool_links.items():  # resolve chain links
        while val in pool_links.keys():
            val = pool_links[val]
        pool_links[key] = val

    try:
        pool_addresses = pool_data['pool_addresses'][timeframe[:4]]
    except KeyError:
        pool_addresses = {}
    for tx in data:
        try:
            coinbase_param = bytes.fromhex(tx['coinbase_param'][2:]).decode('utf-8')
        except (UnicodeDecodeError, ValueError):
            continue

        for (tag, info) in pool_data['coinbase_tags'].items():  # Check if coinbase param contains known pool tag
            if tag in str(coinbase_param):
                name = info['name']
                for addr in tx['coinbase_addresses']:
                    if addr not in pool_addresses.keys():
                        pool_addresses[addr] = name
                break

    blocks_per_entity = defaultdict(int)
    for tx in data:
        block_year = tx['timestamp'][:4]

        try:
            coinbase_param = bytes.fromhex(tx['coinbase_param'][2:]).decode('utf-8')
        except (UnicodeDecodeError, ValueError):
            coinbase_param = tx['coinbase_param']

        coinbase_addresses = tx['coinbase_addresses']

        pool_match = False
        for (tag, info) in pool_data['coinbase_tags'].items():  # Check if coinbase param contains known pool tag
            if tag in str(coinbase_param):
                entity = info['name']
                pool_match = True
                break

        if not pool_match:
            if coinbase_addresses in pool_addresses.keys():
                entity = pool_addresses[addr]
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
