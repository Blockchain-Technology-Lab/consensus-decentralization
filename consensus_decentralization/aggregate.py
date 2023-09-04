import json


class Aggregator:
    """
    Class used to aggregate the results of the mapping process. A mapping for a certain ledger returns a json file
    named "maped_data.json" in the ledger's output directory. This file contains an entry for each block with the
    number of the block, its timestamp, the address that received rewards for it, the name of the entity that it was
    mapped to and the mapping method that was used to identify the entity. This class then reads a json file like
    that and aggregates the results for a given timeframe (e.g. month) by counting the number of blocks produced by
    each entity. The result is a dictionary of entities that produced blocks in the given timeframe and the number of
    blocks they produced
    """

    def __init__(self, project, io_dir, granularity):
        """
        :param project: str. Name of the project
        :param io_dir: Path. Path to the project's output directory
        """
        self.project = project
        self.io_dir = io_dir
        self.mapped_data_file = self.io_dir / 'mapped_data.json'
        self.granularity = granularity

    def aggregate(self):
        """
        Aggregates the mapping results for a given timeframe
        :param timeframe: str. The timeframe that will be analyzed
        :returns: a dictionary with the entities and the number of blocks they have produced over the given timeframe
        """
        pass

    def read_mapped_data(self):
        """
        Reads the mapped data from the directory specified by the instance
        :returns: a dictionary with the mapped data
        """
        with open(self.mapped_data_file) as f:
            data = json.load(f)
        return data

    def process(self, timeframe):
        """
        Processes the mapped data to aggregate the results for the given timeframe
        :param timeframe: str. The timeframe that will be analyzed
        :returns: a dictionary with the entities and the number of blocks they have produced over the given timeframe
        """
        timeframe_data = {}
        for block in self.dataset:
            if timeframe in block['timeframe']:
                entity = block['entity']
                if entity not in timeframe_data:
                    timeframe_data[entity] = 0
                timeframe_data[entity] += 1
        return timeframe_data


# todo replace commas in entity names with empty strings

