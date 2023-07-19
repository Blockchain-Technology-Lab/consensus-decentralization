from collections import defaultdict
from src.helpers.helper import get_pool_data, write_blocks_per_entity_to_file
from src.mappings.mapping import Mapping


class CardanoMapping(Mapping):
    """
    Mapping class tailored for Cardano data. Inherits from Mapping class.
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
        pool_data, pool_links = get_pool_data(self.project_name, timeframe)

        data = [tx for tx in self.dataset if tx['timestamp'][:len(timeframe)] == timeframe]

        daily_helper_data = {}
        blocks_per_entity = defaultdict(int)
        for tx in data:
            day = tx['timestamp'][:10]
            try:
                pool_data = daily_helper_data[day]['pool_data']
                pool_links = daily_helper_data[day]['pool_links']
            except KeyError:
                pool_data, pool_links = get_pool_data(self.project_name, day)
                daily_helper_data[day] = {}
                daily_helper_data[day]['pool_data'] = pool_data
                daily_helper_data[day]['pool_links'] = pool_links

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
                    entity = 'Input Output (iohk.io)'  # pre-decentralization

            blocks_per_entity[entity.replace(',', '')] += 1

        groups = self.map_block_producers_to_groups(blocks_per_entity.keys())
        write_blocks_per_entity_to_file(self.io_dir, blocks_per_entity, groups, timeframe)

        return blocks_per_entity
