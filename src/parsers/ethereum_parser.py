from src.parsers.dummy_parser import DummyParser


class EthereumParser(DummyParser):
    """
    Parser for Ethereum. Inherits from DummyParser class.
    """

    def __init__(self, project_name, input_dir, output_dir):
        super().__init__(project_name, input_dir, output_dir)

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
