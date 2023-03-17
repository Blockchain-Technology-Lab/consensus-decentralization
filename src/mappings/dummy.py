from collections import defaultdict
from src.helpers.helper import write_csv_file
from src.mappings.mapping import Mapping


class DummyMapping(Mapping):

    def __init__(self, project_name, dataset):
        super().__init__(project_name, dataset)

    def process(self, timeframe):
        data = [tx for tx in self.dataset if tx['timestamp'][:len(timeframe)] == timeframe]

        blocks_per_entity = defaultdict(int)
        for tx in data:
            coinbase_addresses = tx['coinbase_addresses'].split(',')
            entity = coinbase_addresses[0]

            blocks_per_entity[entity] += 1

        write_csv_file(self.io_dir, blocks_per_entity, timeframe)

        return blocks_per_entity
