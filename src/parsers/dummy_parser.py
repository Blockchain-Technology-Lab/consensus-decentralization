from src.parsers.default_parser import DefaultParser


class DummyParser(DefaultParser):
    """
    Dummy parser that only sorts the raw data. Used when the data are already in the required format.
    """

    def __init__(self, project_name, input_dir, output_dir):
        super().__init__(project_name, input_dir, output_dir)

    def parse(self):
        """
        Sorts the data, makes sure that each entry includes all required fields and writes the results into a file in a
        directory associated with the parser instance (specifically in <general output directory>/<project_name>)
        """
        data = self.read_and_sort_data()
        for block in data:
            if 'identifiers' not in block.keys():
                block['identifiers'] = None
            if 'reward_addresses' not in block.keys():
                block['reward_addresses'] = None
        self.write_parsed_data(data)
