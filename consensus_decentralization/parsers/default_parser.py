import codecs
import json

MIN_TX_VALUE = 0


class DefaultParser:
    """
    The default parser, used for Bitcoin, Litecoin, Zcash and others. Any project that requires different parsing
    must use a parser class that inherits from this one.

    :ivar project_name: the name of the project associated with a specific parser instance
    """

    def __init__(self, project_name, input_dir):
        self.project_name = project_name
        self.input_dir = input_dir

    @staticmethod
    def parse_identifiers(block_identifiers):
        """
        Parses (decodes) the "identifiers" field of a block. Should be overridden by a project-specific parser if
        necessary (e.g. when no or different decoding is needed).
        :param block_identifiers: the content of the "identifiers" field of a block (string)
        :returns: the parsed (decoded) identifiers (string)
        """
        return str(codecs.decode(block_identifiers, 'hex'))

    def read_and_sort_data(self):
        """
        Reads the "raw" block data associated with the project
        :returns: a list of dictionaries (block data) sorted by timestamp
        """
        filename = f'{self.project_name}_raw_data.json'
        filepath = self.input_dir / filename
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
            block['reward_addresses'] = ','.join(sorted([tx['addresses'][0] for tx in block['outputs']
                                                      if (tx['addresses'] and int(tx['value']) > MIN_TX_VALUE)]))
            del block['outputs']
            block['identifiers'] = self.parse_identifiers(block['identifiers'])
        return data
