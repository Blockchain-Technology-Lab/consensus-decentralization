import json


def parse_raw_data(project_dir):
    with open(project_dir + '/data.json') as f:
        data = json.load(f)

    block_data = []
    for tx in sorted(data, key=lambda x: x['slot_no']):
        block_data.append({
            'number': tx['slot_no'],
            'timestamp': tx['block_time'].replace('T', ' ') + ' UTC',
            'creator': '[pool] ' + tx['ticker_name'],
            'coinbase_addresses': [tx['pool_hash']]
        })

    with open(project_dir + '/parsed_data.json', 'w') as f:
        f.write(json.dumps({'block_data': block_data, 'addresses_in_multiple_pools': {}}))
