from src.parsers.default_parser import DefaultParser


class DummyParser(DefaultParser):
    """
    Dummy parser that only sorts the raw data. Used when the data are already in the required format.
    """

    def __init__(self, project_name):
        super().__init__(project_name)

    def parse(self):
        """
        "Parses" the data and writes the results into a file
        """
        data = self.read_and_sort_data()
        self.write_parsed_data(data)
