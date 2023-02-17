from src.parsers.default_parser import DefaultParser


class CardanoParser(DefaultParser):
    """
    Parser used for Cardano
    """

    def __init__(self, project_name):
        super().__init__(project_name)

    def parse(self):
        data = self.read_and_sort_data()
        for tx in data:
            try:
                tx['coinbase_addresses'] = tx['pool_hash']
                del tx['pool_hash']
            except KeyError:
                tx['coinbase_addresses'] = ''

            try:
                tx['coinbase_param']
            except KeyError:
                tx['coinbase_param'] = ''

        self.write_parsed_data(data)
