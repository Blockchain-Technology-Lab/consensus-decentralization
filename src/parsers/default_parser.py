import json
from src.helpers.helper import INPUT_DIR, OUTPUT_DIR

MIN_TX_VALUE = 0

class DefaultParser:
    """
    The default parser, used for Bitcoin, Litecoin, Zcash and others
    """
    def __init__(self, project_name):
        self.project_name = project_name

    def read_and_sort_data(self):
        filename = f'{self.project_name}_raw_data.json'
        filepath = INPUT_DIR / filename
        with open(filepath) as f:
            contents = f.read()
        data = [json.loads(item) for item in contents.strip().split('\n')]
        data = sorted(data, key=lambda x: x['number'])
        return data

    def parse(self):
        data = self.read_and_sort_data()

        for block in data:
            block['coinbase_addresses'] = ','.join(set([tx['addresses'][0] for tx in block['outputs']
                                                        if (tx['addresses'] and int(tx['value']) > MIN_TX_VALUE)]))
            del block['outputs']

        self.write_parsed_data(data)

    def write_parsed_data(self, data):
        path = OUTPUT_DIR / self.project_name
        path.mkdir(parents=True, exist_ok=True)  # create project output directory if it doesn't already exist
        filename = 'parsed_data.json'
        with open(path / filename, 'w') as f:
            f.write('[' + ',\n'.join(json.dumps(i) for i in data) + ']\n')




