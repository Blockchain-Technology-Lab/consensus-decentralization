import codecs
import json

MIN_TX_VALUE = 0


class DefaultParser:
    """
    The default parser, used for Bitcoin, Litecoin, Zcash and others. Any project that requires different parsing
    must use a parser class that inherits from this one.

    :ivar ledger: the name of the ledger associated with a specific parser instance
    :ivar input_dirs: the directories where the raw block data are stored
    """

    def __init__(self, ledger, input_dirs):
        self.ledger = ledger
        self.input_dirs = input_dirs

    @staticmethod
    def parse_identifiers(block_identifiers):
        """
        Parses (decodes) the "identifiers" field of a block. Should be overridden by a project-specific parser if
        necessary (e.g. when no or different decoding is needed).
        :param block_identifiers: the content of the "identifiers" field of a block (string)
        :returns: the parsed (decoded) identifiers (string)
        """
        return str(codecs.decode(block_identifiers, 'hex'))

    def get_input_file(self):
        """
        Determines the file that contains the raw data for the project. The file is expected to be named
        <ledger>_raw_data.json and to be located in (exactly) one of the input directories.
        :returns: a Path object that corresponds to the file containing the raw data
        :raises FileNotFoundError: if the file does not exist in any of the input directories
        """
        filename = f'{self.ledger}_raw_data.json'
        for input_dir in self.input_dirs:
            filepath = input_dir / filename
            if filepath.is_file():
                return filepath
        raise FileNotFoundError(f'File {self.ledger}_raw_data.json not found in the input directories. Skipping '
                                f'{self.ledger}..')

    def read_and_sort_data(self):
        """
        Reads the "raw" block data associated with the project
        :returns: a list of dictionaries (block data) sorted by timestamp
        """
        try:
            filepath = self.get_input_file()
        except FileNotFoundError as e:
            raise e
        with open(filepath) as f:
            contents = f.read()
        data = [json.loads(item) for item in contents.strip().split('\n')]
        data = sorted(data, key=lambda x: x['timestamp'])
        return data

    def parse(self):
        """
        Parses the data and writes the results into a file in a directory associated with the parser instance
        (specifically in <general output directory>/<project_name>)
        :returns: a list of dictionaries (the parsed data of the project)
        """
        data = self.read_and_sort_data()

        for block in data:
            block['reward_addresses'] = ','.join(sorted([tx['addresses'][0] for tx in block['outputs'] if
                                                         (tx['addresses'] and int(tx['value']) > MIN_TX_VALUE)]))
            del block['outputs']
            block['identifiers'] = self.parse_identifiers(block['identifiers'])
        return data
