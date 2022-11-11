from collections import defaultdict
import json
import numpy as np


def gini(x):
    # (Warning: This is a concise implementation, but it is O(n**2)
    # in time and memory, where n = len(x).  *Don't* pass in huge
    # samples!)

    # Mean absolute difference
    mad = np.abs(np.subtract.outer(x, x)).mean()
    # Relative mean absolute difference
    rmad = mad/np.mean(x)
    # Gini coefficient
    g = 0.5 * rmad
    return g


def compute_nc(blocks):
    nakamoto_coefficient = [0, 0]
    for (name, value) in sorted(blocks.items(), key=lambda x: x[1], reverse=True):
        if nakamoto_coefficient[1] < 50:
            nakamoto_coefficient[0] += 1
            nakamoto_coefficient[1] += 100 * value / sum([i[1] for i in blocks.items()])
        else:
            return nakamoto_coefficient


def parse_raw_data(project_name):
    with open(project_name + '_data.json') as f:
        data = json.load(f)
        data = sorted(data, key=lambda x: x['number'])

    with open('{}_pools.json'.format(project_name)) as f:  # Pool tags: https://github.com/0xB10C/known-mining-pools
        pool_data = json.load(f)

    pool_addresses = {}
    addresses_in_multiple_pools = defaultdict(set)
    for tx in data:
        address = tx['miner']
        try:
            tag = bytes.fromhex(tx['extra_data'][2:]).decode('utf-8')
            if tag:
                creator = '[pool] ' + tag

                for (partial_tag, info) in pool_data['coinbase_tags'].items():  # Check if coinbase param contains known pool tag
                    if partial_tag in tag:
                        creator = '[pool] ' + info['name']
                        break
                
                if address in pool_addresses.keys() and pool_addresses[address] != creator:
                    match = False
                    for known_link in pool_data['coinbase_address_links'].keys():
                        if known_link in tag:
                            creator = '[pool] ' + pool_data['coinbase_address_links'][known_link]
                            match = True
                            break
                    if not match:
                        addresses_in_multiple_pools[address].add(creator)
                        addresses_in_multiple_pools[address].add(pool_addresses[address])

            pool_addresses[address] = creator
        except UnicodeDecodeError:
            pass
    
    # for (_, val) in addresses_in_multiple_pools.items():
    #     print(','.join(val))

    # with open('{}_pool_addresses.json'.format(project_name), 'w') as f:
    #     f.write(json.dumps(pool_addresses, indent=4))


    RANGE = 4  # 0: all, 4: years, 7: months, 10: days

    PRINT_DISTRIBUTION = False

    data_range_blocks = defaultdict(list)
    for block in data:
        if RANGE > 0:
            data_range_blocks[block['timestamp'][:RANGE]].append(block)
        else:
            data_range_blocks['all available'].append(block)

    for time_window in sorted(data_range_blocks.keys()):
        blocks_per_creator = defaultdict(int)
        for tx in data_range_blocks[time_window]:
            match = False
            try:
                tag = bytes.fromhex(tx['extra_data'][2:]).decode('utf-8')

                for (partial_tag, info) in pool_data['coinbase_tags'].items():  # Check if coinbase param contains known pool tag
                    if partial_tag in tag:
                        tag = info['name']
                        match = True
                        break

                if not match:
                    for (partial_tag, name) in pool_data['coinbase_address_links'].items():  # Check if tag is known associated with pool
                        if partial_tag in tag:
                            tag = name
                            match = True
                            break

                if not match and tx['miner'] in pool_addresses.keys():  # Check if address is associated with pool
                    creator = pool_addresses[tx['miner']]

                creator = '[pool] ' + tag

            except UnicodeDecodeError:
                creator = '[addr] ' + tx['miner']

            blocks_per_creator[creator] += 1

        if PRINT_DISTRIBUTION:
            print('[*] Blocks per creator')
            for (name, blocks) in sorted(blocks_per_creator.items(), key=lambda x: x[1], reverse=True):
                print('    {0:55} {1:8} blocks ({2:.4f}%)'.format(name, blocks, blocks * 100 / sum([i[1] for i in blocks_per_creator.items()])))

        v = list(blocks_per_creator.values())
        nc = compute_nc(blocks_per_creator)
        print('[*] Nakamoto: {} ({:.3f}%), Gini: {:.6f}, Block creators: {}'.format(nc[0], nc[1], gini(v), len(blocks_per_creator.keys())))


if __name__ == '__main__':
    parse_raw_data('ethereum')
