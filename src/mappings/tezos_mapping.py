from collections import defaultdict
from src.helpers.helper import get_pool_links, write_blocks_per_entity_to_file
from src.mappings.default_mapping import DefaultMapping


class TezosMapping(DefaultMapping):
    """
    Mapping class tailored to Tezos data. Inherits from Mapping.
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
        data = [block for block in self.dataset if block['timestamp'][:len(timeframe)] == timeframe]
        blocks_per_entity = defaultdict(int)

        for block in data:
            day = block['timestamp'][:10]
            pool_links = get_pool_links(self.project_name, day)

            reward_addresses = block['reward_addresses']
            if reward_addresses is None:
                reward_addresses = '----- UNDEFINED MINER -----'

            if reward_addresses in self.known_addresses.keys():
                entity = self.known_addresses[reward_addresses]
            else:
                entity = reward_addresses

            if entity in pool_links.keys():
                entity = pool_links[entity]

            blocks_per_entity[entity.replace(',', '')] += 1

        groups = self.map_block_creators_to_groups(blocks_per_entity.keys())
        write_blocks_per_entity_to_file(self.io_dir, blocks_per_entity, groups, timeframe)

        return blocks_per_entity
