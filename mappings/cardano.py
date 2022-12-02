from collections import defaultdict
import json


def process(project_dir, timeframe):
    with open(project_dir + '/data.json') as f:
        data = json.load(f)
        data = [tx for tx in data if tx['timestamp'][:len(timeframe)] == timeframe]
        data = sorted(data, key=lambda x: x['number'])

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
    
    blocks_per_entity = defaultdict(int)
    for tx in data:
        entity = tx['coinbase_param']
        if entity:
            if entity in pool_links.keys():
                entity = pool_links[entity]
            elif entity in pool_data['coinbase_tags'].keys():
                entity = pool_data['coinbase_tags'][entity]['name']
        else:
            pool = tx['coinbase_addresses']
            if pool:
                entity = pool
            else:
                entity = '[!] IOG (core nodes, pre-decentralization)'

        blocks_per_entity[entity] += 1

    csv_output = ['Entity,Resources']
    for key, val in sorted(blocks_per_entity.items(), key=lambda x: x[1], reverse=True):
        csv_output.append(','.join([key, str(val)]))

    with open(project_dir + '/' + timeframe + '.csv', 'w') as f:
        f.write('\n'.join(csv_output))

    return blocks_per_entity
