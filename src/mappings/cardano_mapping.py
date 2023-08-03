from collections import defaultdict
from src.helpers.helper import get_pool_links, get_pool_identifiers, write_blocks_per_entity_to_file
from src.mappings.mapping import Mapping


class CardanoMapping(Mapping):
    """
    Mapping class tailored to Cardano data. Inherits from Mapping class.
    """

    def __init__(self, project_name, dataset):
        super().__init__(project_name, dataset)
        self.known_identifiers = get_pool_identifiers(project_name)

    def process(self, timeframe):
        """
        Overrides process method of parent class to use project-specific information and extract the distribution of
        blocks to different entities.
        :param timeframe: string that corresponds to the timeframe under consideration (in YYYY-MM-DD, YYYY-MM or YYYY
        format)
        :returns: a dictionary with the entities and the number of blocks they have produced over the given timeframe
        """
        blocks = [block for block in self.dataset if block['timestamp'][:len(timeframe)] == timeframe]
        blocks_per_entity = defaultdict(int)
        for block in blocks:
            day = block['timestamp'][:10]
            pool_links = get_pool_links(self.project_name, day)

            entity = block['identifiers']
            if entity:
                if entity in pool_links.keys():
                    entity = pool_links[entity]
                elif entity in self.known_identifiers.keys():
                    entity = self.known_identifiers[entity]['name']
            else:
                pool = block['reward_addresses']
                if pool:
                    entity = pool
                else:
                    entity = 'Input Output (iohk.io)'  # pre-decentralization

            blocks_per_entity[entity.replace(',', '')] += 1

        groups = self.map_block_creators_to_groups(blocks_per_entity.keys())
        write_blocks_per_entity_to_file(self.io_dir, blocks_per_entity, groups, timeframe)

        return blocks_per_entity
