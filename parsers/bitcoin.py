import json

with open('raw_data.json') as f:
    data = json.load(f)
    data = sorted(data, key=lambda x: x['number'])

for tx in data:
    tx['coinbase_addresses'] = ','.join(list(set([i['addresses'][0] for i in tx['outputs'] if (i['addresses'] and int(i['value']) > 0)])))
    del tx['outputs']

with open('data.json', 'w') as f:
    f.write('[' + ',\n'.join(json.dumps(i) for i in data) + ']\n')
