from collections import defaultdict
from src.helpers.helper import get_pool_links, write_blocks_per_entity_to_file
from src.mappings.default_mapping import DefaultMapping


class EthereumMapping(DefaultMapping):
    """
    Mapping class tailored to Ethereum data. Inherits from Mapping.
    """

    def __init__(self, project_name, dataset):
        super().__init__(project_name, dataset)
        self.multi_pool_addresses = list()

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

            identifiers = block['identifiers']

            reward_addresses = block['reward_addresses']
            if reward_addresses in self.special_addresses:
                continue

            pool_match = False
            for (tag, info) in self.known_identifiers.items():  # Check if identifiers contain known pool tag
                if tag in str(identifiers):
                    entity = info['name']
                    self.known_addresses[reward_addresses] = entity
                    pool_match = True
                    if reward_addresses in self.known_addresses.keys() and self.known_addresses[reward_addresses] != entity:
                        self.multi_pool_addresses.append(f'{block["number"]},{block["timestamp"]},{reward_addresses}'
                                                         f',{entity}')
                    break

            if not pool_match:
                if reward_addresses in self.known_addresses.keys():
                    entity = self.known_addresses[reward_addresses]
                else:
                    entity = reward_addresses

            if entity in pool_links.keys():
                entity = pool_links[entity]

            blocks_per_entity[entity.replace(',', '')] += 1

        groups = self.map_block_creators_to_groups(blocks_per_entity.keys())
        write_blocks_per_entity_to_file(self.io_dir, blocks_per_entity, groups, timeframe)

        if len(timeframe) == 4 and self.multi_pool_addresses:
            with open(self.io_dir / f'multi_pool_addresses_{timeframe}.csv', 'w') as f:
                f.write('Block No,Timestamp,Address,Entity\n' + '\n'.join(self.multi_pool_addresses))

        return blocks_per_entity
