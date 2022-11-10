import json
from collections import defaultdict
from parse import parse_raw_data
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


def compute_nc(blocks_per_pool):
    nakamoto_coefficient = [0, 0]
    for (name, blocks) in sorted(blocks_per_pool.items(), key=lambda x: x[1], reverse=True):
        if nakamoto_coefficient[1] < 50:
            nakamoto_coefficient[0] += 1
            nakamoto_coefficient[1] += 100 * blocks / sum([i[1] for i in blocks_per_pool.items()])
        else:
            return nakamoto_coefficient

RANGE = 4  # 0: all, 4: years, 7: months, 10: days

ADDRESS_LINKS = True
KNOWN_LINKS = True
PARTIAL_LINKS = False

PRINT_DISTRIBUTION = False

with open('bitcoin_pools.json') as f:
    pool_data = json.load(f)
    pool_links = {}
    if ADDRESS_LINKS:
        pool_links.update(pool_data['coinbase_address_links'])
    if KNOWN_LINKS:
        pool_links.update(pool_data['known_links'])
    if PARTIAL_LINKS:
        pool_links.update(pool_data['partial_links'])
    for key, val in pool_links.items():
        while val in pool_links.keys():
            val = pool_links[val]
        pool_links[key] = val

try:
    with open('bitcoin_parsed_data.json') as f:
        parsed_data = json.load(f)
except FileNotFoundError:
    parse_raw_data('bitcoin')
    with open('bitcoin_parsed_data.json') as f:
        parsed_data = json.load(f)

block_data = parsed_data['block_data']

data_range_blocks = defaultdict(list)
for block in block_data:
    if RANGE > 0:
        data_range_blocks[block['timestamp'][:RANGE]].append(block)
    else:
        data_range_blocks['all available'].append(block)

for time_window in sorted(data_range_blocks.keys()):
    blocks_per_pool = defaultdict(int)
    for block in data_range_blocks[time_window]:
        creator = block['creator']
        if 'pool' in block['creator']:
            name = block['creator'][7:].strip()
            if name in pool_links.keys():
                creator = '[pool] ' + pool_links[name]

        blocks_per_pool[creator] += 1

    if PRINT_DISTRIBUTION:
        print()
        print('[*] Blocks per pool in', time_window)
        for (name, blocks) in sorted(blocks_per_pool.items(), key=lambda x: x[1], reverse=True):
            print('    {0:45} {1:5} blocks ({2:.4f}%)'.format(name, blocks, blocks * 100 / sum([i[1] for i in blocks_per_pool.items()])))

    v = list(blocks_per_pool.values())
    nc = compute_nc(blocks_per_pool)

    print('[{}] Nakamoto: {} ({:.3f}%), Gini: {:.6f}, Block creators: {}'.format(time_window, nc[0], nc[1], gini(v), len(blocks_per_pool.keys())))


# addresses_in_multiple_pools = parsed_data['addresses_in_multiple_pools']
# for (addr, pools) in addresses_in_multiple_pools.items():
#     print('[!] Address {} in multiple pools: {}'.format(addr, ', '.join(pools)))
