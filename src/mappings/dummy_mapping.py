from collections import defaultdict
from src.helpers.helper import write_blocks_per_entity_to_file
from src.mappings.mapping import Mapping


class DummyMapping(Mapping):

    def __init__(self, project_name, dataset):
        super().__init__(project_name, dataset)

    def process(self, timeframe):
        data = [tx for tx in self.dataset if tx['timestamp'][:len(timeframe)] == timeframe]

        blocks_per_entity = defaultdict(int)
        for tx in data:
            reward_addresses = tx['reward_addresses'].split(',')
            entity = reward_addresses[0]

            blocks_per_entity[entity] += 1

        write_blocks_per_entity_to_file(self.io_dir, blocks_per_entity, blocks_per_entity.keys, timeframe)

        return blocks_per_entity
