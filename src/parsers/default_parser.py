import json

MIN_TX_VALUE = 0

with open('raw_data.json') as f:
    data = json.load(f)
data = sorted(data, key=lambda x: x['number'])

for block in data:
    block['coinbase_addresses'] = ','.join(set([tx['addresses'][0] for tx in block['outputs']
                                                if (tx['addresses'] and int(tx['value']) > MIN_TX_VALUE)]))
    del block['outputs']

with open('data.json', 'w') as f:
    f.write('[' + ',\n'.join(json.dumps(i) for i in data) + ']\n')
