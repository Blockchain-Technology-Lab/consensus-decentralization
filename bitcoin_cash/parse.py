from collections import defaultdict
import json
import codecs
import pathlib


def param2ascii(coinbase_param):
    param = ''
    for i in coinbase_param:
        param += chr(i) if i in range(32, 128) else ' '
    return param

def parse_raw_data():
    current_dir = str(pathlib.Path(__file__).parent.resolve())
    with open(current_dir + '/data.json') as f:
        data = json.load(f)

    with open(current_dir + '/pools.json') as f:  # Original pool tags: https://github.com/0xB10C/known-mining-pools
        pool_data = json.load(f)

    try:
        with open(current_dir + '/pool_addresses.json') as f:
            pool_addresses = json.load(f)
    except FileNotFoundError:
        pool_addresses = {}
        for tx in sorted(data, key=lambda x: x['block_number']):
            block_year = tx['timestamp'][:4]
            if block_year not in pool_addresses.keys():
                pool_addresses[block_year] = {}

            coinbase_addresses = [i['addresses'][0] for i in tx['outputs'] if (int(i['value']) > 0 and i['type'] != 'nonstandard')]
            coinbase_param = codecs.decode(tx['coinbase_param'], 'hex')
            for (tag, info) in pool_data['coinbase_tags'].items():  # Check if coinbase param contains known pool tag
                if tag in str(coinbase_param):
                    name = info['name']
                    for addr in coinbase_addresses:
                        if addr not in pool_addresses[block_year].keys():
                            pool_addresses[block_year][addr] = name
                    break
        with open(current_dir + '/pool_addresses.json', 'w') as f:
            f.write(json.dumps(pool_addresses, indent=4))

    unmatched_tags = []
    addresses_in_multiple_pools = {}
    block_data = []
    for tx in sorted(data, key=lambda x: x['block_number']):
        block_year = tx['timestamp'][:4]
        if block_year not in addresses_in_multiple_pools.keys():
            addresses_in_multiple_pools[block_year] = defaultdict(set)

        block_data.append({
            'number': tx['block_number'],
            'timestamp': tx['timestamp']
        })

        coinbase_addresses = [i['addresses'][0] for i in tx['outputs'] if (int(i['value']) > 0 and i['type'] != 'nonstandard')]
        block_data[-1]['coinbase_addresses'] = list(set(coinbase_addresses))

        coinbase_param = codecs.decode(tx['coinbase_param'], 'hex')

        pool_match = False
        for (tag, info) in pool_data['coinbase_tags'].items():  # Check if coinbase param contains known pool tag
            if tag in str(coinbase_param):
                name = info['name']

                block_data[-1]['creator']= '[pool] ' + name
                pool_match = True
                for addr in coinbase_addresses:
                    if pool_addresses[block_year][addr] != name:  # Check if address associated with multiple pools
                        addresses_in_multiple_pools[block_year][addr].add(name)
                        addresses_in_multiple_pools[block_year][addr].add(pool_addresses[block_year][addr])
                break

        if not pool_match:
            for addr in coinbase_addresses:  # Check if address is associated with pool
                if addr in pool_addresses[block_year].keys():
                    block_data[-1]['creator']= '[pool] ' + pool_addresses[block_year][addr]
                    pool_match = True
                    break
            if not pool_match:
                unmatched_tags.append([tx['block_number'], ','.join(coinbase_addresses), coinbase_param])
                if len(coinbase_addresses) == 1:
                    block_data[-1]['creator'] = '[addr] ' + addr
                else:
                    identifier = ' '.join([
                        addr[:5] + '...' + addr[-5:] for addr in coinbase_addresses
                    ])
                    block_data[-1]['creator'] = '[multi] ' + identifier

    for year in addresses_in_multiple_pools.keys():
        for (address, val) in addresses_in_multiple_pools[year].items():
            addresses_in_multiple_pools[year][address] = list(val)

    with open(current_dir + '/parsed_data.json', 'w') as f:
        f.write(json.dumps({'block_data': block_data, 'addresses_in_multiple_pools': addresses_in_multiple_pools}))

    with open(current_dir + '/unmatched_tags', 'w') as f:
        f.write('\n'.join([
            ' --- '.join([tag[0], tag[1], tag[2].hex(), param2ascii(tag[2])]) for tag in unmatched_tags
        ]))

if __name__ == '__main__':
    parse_raw_data()
