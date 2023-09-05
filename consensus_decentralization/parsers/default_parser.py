import codecs
import json

MIN_TX_VALUE = 0


class DefaultParser:
    """
    The default parser, used for Bitcoin, Litecoin, Zcash and others. Any project that requires different parsing
    must use a parser class that inherits from this one.

    :ivar project_name: the name of the project associated with a specific parser instance
    """

    def __init__(self, project_name, input_dir, output_dir):
        self.project_name = project_name
        self.input_dir = input_dir
        self.output_dir = output_dir

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
        :returns: a list of block data sorted by timestamp
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
        """
        data = self.read_and_sort_data()

        for block in data:
            block['reward_addresses'] = ','.join(set([tx['addresses'][0] for tx in block['outputs']
                                                      if (tx['addresses'] and int(tx['value']) > MIN_TX_VALUE)]))
            del block['outputs']
            block['identifiers'] = self.parse_identifiers(block['identifiers'])

        self.write_parsed_data(data)

    def write_parsed_data(self, data):
        """
        Writes the parsed data into a file in a directory associated with the parser instance. Specifically,
        into a folder named after the project, inside the general output directory. If the project folder doesn't
        already exist then it is created here.
        :param data: the parsed data of the project
        """
        path = self.output_dir / self.project_name
        path.mkdir(parents=True, exist_ok=True)  # create project output directory if it doesn't already exist
        filename = 'parsed_data.json'
        with open(path / filename, 'w') as f:
            f.write('[' + ',\n'.join(json.dumps(block) for block in data) + ']\n')
