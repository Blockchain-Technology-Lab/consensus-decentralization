from collections import defaultdict
from src.helpers.helper import get_pool_data, write_csv_file
from src.mappings.mapping import Mapping


class CardanoMapping(Mapping):

    def __init__(self, project_name, dataset):
        super().__init__(project_name, dataset)

    def process(self, timeframe):
        pool_data, pool_links = get_pool_data(self.project_name, timeframe)

        data = [tx for tx in self.dataset if tx['timestamp'][:len(timeframe)] == timeframe]

        blocks_per_entity = defaultdict(int)
        for tx in data:
            entity = tx['coinbase_param']
            if entity:
                if entity in pool_links.keys():
                    entity = pool_links[entity]
                elif entity in pool_data['coinbase_tags'].keys():
                    entity = pool_data['coinbase_tags'][entity]['name']
            else:
                pool = tx['coinbase_addresses']
                if pool:
                    entity = pool
                else:
                    entity = '[!] IOG (core nodes pre-decentralization)'

            blocks_per_entity[entity.replace(',', '')] += 1

        write_csv_file(self.io_dir, blocks_per_entity, timeframe)

        return blocks_per_entity
