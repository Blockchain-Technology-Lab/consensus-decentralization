import json
from collections import defaultdict

with open('raw_data.json') as f:
    data = json.load(f)
    #contents = f.read() #todo check which one is needed for cardano
    #data = [json.loads(str(item)) for item in contents.strip().split('\n')]
    data = sorted(data, key=lambda x: x['number'])

#todo delete unused variables pool_tickers and address_tickers?
pool_tickers = defaultdict(set)
address_tickers = defaultdict(set)
for tx in data:
    try:
        tx['coinbase_addresses'] = tx['pool_hash']
        del tx['pool_hash']
    except KeyError:
        tx['coinbase_addresses'] = ''

    try:
        ticker = tx['coinbase_param']
    except KeyError:
        tx['coinbase_param'] = ''

with open('data.json', 'w') as f:
    f.write('[' + ',\n'.join(json.dumps(i) for i in data) + ']\n')
