from consensus_decentralization.parsers.dummy_parser import DummyParser
import json


class EthereumParser(DummyParser):
    """
    Parser for Ethereum. Inherits from DummyParser class.
    """

    def __init__(self, project_name, input_dir):
        super().__init__(project_name, input_dir)

    @staticmethod
    def parse_identifiers(block_identifiers):
        """
        Overrides the parse_identifiers method of the DummyParser class. Decodes the identifiers from hex to utf-8.
        :param block_identifiers: the content of the "identifiers" field of a block (string)
        :returns: the decoded identifiers of the block (string)
        """
        try:
            return bytes.fromhex(block_identifiers[2:]).decode('utf-8')
        except (UnicodeDecodeError, ValueError):
            return block_identifiers

    def read_and_sort_data(self):
        """
        Reads the "raw" block data associated with the project
        :returns: a list of dictionaries (block data) sorted by timestamp
        Note that the current version does not sort the data (because it is too memory-intensive) but assumes that the
        data are already sorted (which is generally the case given the suggested queries).
        """
        filename = f'{self.project_name}_raw_data.json'
        filepath = self.input_dir / filename

        def generate_data():
            with open(filepath) as f:
                for line in f:
                    yield json.loads(line.strip())

        return generate_data()
