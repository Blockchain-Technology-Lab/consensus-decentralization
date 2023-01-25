import json
from collections import defaultdict
from src.parsers.default_parser import DefaultParser
from src.helpers.helper import INPUT_DIR

class CardanoParser(DefaultParser):
    """
    Parser used for Cardano
    """
    def __init__(self, project_name):
        super().__init__(project_name)

    def parse(self):
        filename = f'{self.project_name}_raw_data.json'
        filepath = INPUT_DIR / filename
        with open(filepath) as f:
            contents = f.read()
            data = [json.loads(str(item)) for item in contents.strip().split('\n')]
            data = sorted(data, key=lambda x: x['number'])

        # todo delete unused variables pool_tickers and address_tickers?
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

        self.write_parsed_data(data)
