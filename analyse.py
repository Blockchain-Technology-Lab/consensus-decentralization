import json
from collections import defaultdict
from helpers import compute_gini, compute_nc
from bitcoin.parse import parse_raw_data as bitcoin_parse_raw_data
import config

print('[*] Pool clustering:', config.POOL_CLUSTERING, 'Legal links:', config.LEGAL_LINKS, 'Address links:', config.ADDRESS_LINKS)

with open('bitcoin/pools.json') as f:
    pool_data = json.load(f)

try:
    with open('bitcoin/parsed_data.json') as f:
        parsed_data = json.load(f)
except FileNotFoundError:
    bitcoin_parse_raw_data()
    with open('bitcoin/parsed_data.json') as f:
        parsed_data = json.load(f)

block_data = parsed_data['block_data']

data_range_blocks = defaultdict(list)
for block in block_data:
    if config.RANGE > 0:
        data_range_blocks[block['timestamp'][:config.RANGE]].append(block)
    else:
        data_range_blocks['all available'].append(block)

if config.TIME_SERIES_OUTPUT:
    time_series_data = ['Month,NC,NC (%),Gini,Creators']

for time_window in sorted(data_range_blocks.keys()):
    pool_links = {}
    try:
        if config.LEGAL_LINKS:
            pool_links.update(pool_data['legal_links'][time_window[:4]])
        if config.ADDRESS_LINKS:
            pool_links.update(pool_data['coinbase_address_links'][time_window[:4]])

        for key, val in pool_links.items():  # resolve chain links
            while val in pool_links.keys():
                val = pool_links[val]
            pool_links[key] = val
    except KeyError:  # if "all available"
        pass

    blocks_per_pool = defaultdict(int)
    for block in data_range_blocks[time_window]:
        coinbase_addresses = block['coinbase_addresses']
        
        if config.POOL_CLUSTERING:
            creator = block['creator']
            if 'pool' in block['creator']:
                name = block['creator'][7:].strip()
                creator = name
                if name in pool_links.keys():
                    creator = pool_links[name]
            elif 'addr' in block['creator']:
                creator = block['creator'][7:].strip()
        else:
            try:
                creator = coinbase_addresses[0]
            except IndexError:
                pass

        blocks_per_pool[creator] += 1

    if time_window == '2019':
        with open('bitcoin/output.csv', 'w') as f:
            f.write('\n'.join([
                ','.join([key, str(val)]) for (key, val) in sorted(blocks_per_pool.items(), key=lambda x: x[1], reverse=True)
            ]))

    if config.PRINT_DISTRIBUTION:
        print()
        print('[*] Blocks per pool in', time_window)
        for (name, blocks) in sorted(blocks_per_pool.items(), key=lambda x: x[1], reverse=True):
            print('    {0:45} {1:5} blocks ({2:.4f}%)'.format(name, blocks, blocks * 100 / sum([i[1] for i in blocks_per_pool.items()])))

    nc = compute_nc(blocks_per_pool)
    gini = compute_gini(list(blocks_per_pool.values()))

    print('[{}] Nakamoto: {} ({:.3f}%), Gini: {:.6f}, Block creators: {}'.format(time_window, nc[0], nc[1], gini, len(blocks_per_pool.keys())))
    if config.TIME_SERIES_OUTPUT:
        time_series_data.append('{},{},{:.3f},{:.6f},{}'.format(time_window, nc[0], nc[1], gini, len(blocks_per_pool.keys())))

if config.TIME_SERIES_OUTPUT:
    with open('bitcoin/time_series.csv', 'w') as f:
        f.write('\n'.join(time_series_data))
