from src.parsers.default_parser import DefaultParser


class DummyParser(DefaultParser):
    """
    Dummy parser that only sorts the raw data. Used when the data are already in the required format.
    """

    def __init__(self, project_name, input_dir, output_dir):
        super().__init__(project_name, input_dir, output_dir)

    @staticmethod
    def parse_identifiers(block_identifiers):
        """
        Overrides the parse_identifiers method of the DefaultParser class. Does nothing (returns the input as is).
        :param block_identifiers: the content of the "identifiers" field of a block (string)
        :returns: the content of the "identifiers" field of a block (string)
        """
        return block_identifiers

    def parse(self):
        """
        Sorts the data, makes sure that each entry includes all required fields and writes the results into a file in a
        directory associated with the parser instance (specifically in <general output directory>/<project_name>)
        """
        data = self.read_and_sort_data()
        for block in data:
            if 'identifiers' not in block.keys():
                block['identifiers'] = None
            else:
                block['identifiers'] = self.parse_identifiers(block['identifiers'])
            if 'reward_addresses' not in block.keys():
                block['reward_addresses'] = None
        self.write_parsed_data(data)
