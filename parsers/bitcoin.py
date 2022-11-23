import json


def parse(project_dir):
    with open(project_dir + '/data.json') as f:
        data = json.load(f)
        data = sorted(data, key=lambda x: x['number'])

    for tx in data:
        tx['coinbase_addresses'] = list(set([i['addresses'][0] for i in tx['outputs'] if (i['addresses'] and int(i['value']) > 0 and i['type'] != 'nonstandard')]))
        del tx['outputs']

    with open(project_dir + '/parsed_data.json', 'w') as f:
        f.write(json.dumps({'blocks': data}))
