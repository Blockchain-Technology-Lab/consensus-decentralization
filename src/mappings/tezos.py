from collections import defaultdict
from src.helpers.helper import get_pool_data, write_csv_file, get_pool_addresses
from src.mappings.mapping import Mapping


class TezosMapping(Mapping):

    def __init__(self, project_name, dataset):
        super().__init__(project_name, dataset)

    def process(self, timeframe):
        pool_data, pool_links = get_pool_data(self.project_name, timeframe)
        pool_addresses = get_pool_addresses(self.project_name, timeframe)

        data = [tx for tx in self.dataset if tx['timestamp'][:len(timeframe)] == timeframe]

        blocks_per_entity = defaultdict(int)
        for tx in data:
            try:
                coinbase_addresses = tx['coinbase_addresses']
            except KeyError:
                coinbase_addresses = '----- UNDEFINED MINER -----'

            if coinbase_addresses in pool_addresses.keys():
                entity = pool_addresses[coinbase_addresses]
            else:
                entity = coinbase_addresses

            if entity in pool_links.keys():
                entity = pool_links[entity]

            blocks_per_entity[entity.replace(',', '')] += 1

        write_csv_file(self.io_dir, blocks_per_entity, timeframe)

        return blocks_per_entity
