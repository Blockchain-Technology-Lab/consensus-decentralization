from collections import defaultdict
from src.parsers.default_parser import DefaultParser

class CardanoParser(DefaultParser):
    """
    Parser used for Cardano
    """
    def __init__(self, project_name):
        super().__init__(project_name)

    def parse(self):
        data = self.read_and_sort_data()
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
