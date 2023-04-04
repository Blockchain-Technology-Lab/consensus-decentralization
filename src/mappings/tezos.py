from collections import defaultdict
from src.helpers.helper import get_pool_data, write_blocks_per_entity_to_file, get_pool_addresses
from src.mappings.mapping import Mapping


class TezosMapping(Mapping):
    """
    Mapping class tailored for Tezos data. Inherits from Mapping.
    """

    def __init__(self, project_name, dataset):
        super().__init__(project_name, dataset)

    def process(self, timeframe):
        """
        Overrides process method of parent class to use project-specific information and extract the distribution of
        blocks to different entities.
        :param timeframe: string that corresponds to the timeframe under consideration (in YYYY-MM-DD, YYYY-MM or YYYY
        format)
        :returns: a dictionary with the entities and the number of blocks they have produced over the given timeframe
        """
        data = [tx for tx in self.dataset if tx['timestamp'][:len(timeframe)] == timeframe]

        daily_helper_data = {}
        blocks_per_entity = defaultdict(int)
        for tx in data:
            day = tx['timestamp'][:10]
            try:
                pool_data = daily_helper_data[day]['pool_data']
                pool_links = daily_helper_data[day]['pool_links']
                pool_addresses = daily_helper_data[day]['pool_addresses']
            except KeyError:
                pool_data, pool_links = get_pool_data(self.project_name, day)
                pool_addresses = get_pool_addresses(self.project_name, day)
                daily_helper_data[day] = {}
                daily_helper_data[day]['pool_data'] = pool_data
                daily_helper_data[day]['pool_links'] = pool_links
                daily_helper_data[day]['pool_addresses'] = pool_addresses

            try:
                coinbase_addresses = tx['coinbase_addresses']
                if coinbase_addresses is None:
                    coinbase_addresses = '----- UNDEFINED MINER -----'
            except KeyError:
                coinbase_addresses = '----- UNDEFINED MINER -----'

            if coinbase_addresses in pool_addresses.keys():
                entity = pool_addresses[coinbase_addresses]
            else:
                entity = coinbase_addresses

            if entity in pool_links.keys():
                entity = pool_links[entity]

            blocks_per_entity[entity.replace(',', '')] += 1

        write_blocks_per_entity_to_file(self.io_dir, blocks_per_entity, timeframe)

        return blocks_per_entity
