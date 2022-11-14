from collections import defaultdict
import json


def parse_raw_data(project_dir):
    with open(project_dir + '/data.json') as f:
        data = json.load(f)
        data = sorted(data, key=lambda x: x['number'])

    with open(project_dir + '/pools.json') as f:
        pool_data = json.load(f)

    try:
        with open(project_dir + '/pool_addresses.json') as f:
            pool_addresses = json.load(f)
    except FileNotFoundError:
        pool_addresses = {}
        for tx in data:
            block_year = tx['timestamp'][:4]
            if block_year not in pool_addresses.keys():
                pool_addresses[block_year] = {}

            coinbase_address = tx['miner']

            try:
                coinbase_param = bytes.fromhex(tx['extra_data'][2:]).decode('utf-8')
            except UnicodeDecodeError:
                continue

            for (tag, info) in pool_data['coinbase_tags'].items():  # Check if coinbase param contains known pool tag
                if tag in coinbase_param:
                    name = info['name']
                    if coinbase_address not in pool_addresses[block_year].keys():
                        pool_addresses[block_year][coinbase_address] = name
                    break
        with open(project_dir + '/pool_addresses.json', 'w') as f:
            f.write(json.dumps(pool_addresses, indent=4))


    unmatched_tags = []
    addresses_in_multiple_pools = {}
    for tx in data:
        block_year = tx['timestamp'][:4]
        if block_year not in addresses_in_multiple_pools.keys():
            addresses_in_multiple_pools[block_year] = defaultdict(set)

        coinbase_address = tx['miner']
        tx['coinbase_addresses'] = [coinbase_address]

        try:
            coinbase_param = bytes.fromhex(tx['extra_data'][2:]).decode('utf-8')
        except UnicodeDecodeError:
            coinbase_param = tx['extra_data']

        pool_match = False
        for (tag, info) in pool_data['coinbase_tags'].items():  # Check if coinbase param contains known pool tag
            if tag in coinbase_param:
                name = info['name']

                tx['creator'] = '[pool] ' + name
                pool_match = True
                if coinbase_address in pool_addresses[block_year].keys() and pool_addresses[block_year][coinbase_address] != name:  # Check if address associated with multiple pools
                    addresses_in_multiple_pools[block_year][coinbase_address].add(name)
                    addresses_in_multiple_pools[block_year][coinbase_address].add(pool_addresses[block_year][coinbase_address])
                break

        if not pool_match:
            if coinbase_address in pool_addresses[block_year].keys():  # Check if address is associated with pool
                tx['creator']= '[pool] ' + pool_addresses[block_year][coinbase_address]
            else:
                unmatched_tags.append([tx['number'], coinbase_address, coinbase_param])
                tx['creator'] = '[addr] ' + coinbase_address

    for year in addresses_in_multiple_pools.keys():
        for (address, val) in addresses_in_multiple_pools[year].items():
            addresses_in_multiple_pools[year][address] = list(val)

    with open(project_dir + '/parsed_data.json', 'w') as f:
        f.write(json.dumps({'block_data': data, 'addresses_in_multiple_pools': addresses_in_multiple_pools}))

    with open(project_dir + '/unmatched_tags', 'w') as f:
        f.write('\n'.join([
            ' --- '.join([tag[0], tag[1], tag[2]]) for tag in unmatched_tags
        ]))
