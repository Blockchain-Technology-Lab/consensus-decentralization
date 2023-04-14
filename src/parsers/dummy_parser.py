from src.parsers.default_parser import DefaultParser


class DummyParser(DefaultParser):
    """
    Dummy parser that only sorts the raw data. Used when the data are already in the required format.
    """

    def __init__(self, project_name):
        super().__init__(project_name)

    def parse(self):
        """
        Sorts the data and writes the results into a file in a directory associated with the parser instance
        (specifically in <general output directory>/<project_name>)
        """
        data = self.read_and_sort_data()
        for block in data:
            if 'coinbase_addresses' not in block.keys():
                block['coinbase_addresses'] = None
        self.write_parsed_data(data)
