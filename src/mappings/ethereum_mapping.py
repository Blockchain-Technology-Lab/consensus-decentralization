from collections import defaultdict
from src.helpers.helper import get_pool_links, write_blocks_per_entity_to_file, get_pool_tags, get_pool_addresses, get_special_addresses
from src.mappings.mapping import Mapping


class EthereumMapping(Mapping):
    """
    Mapping class tailored for Ethereum data. Inherits from Mapping.
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

        special_addresses = get_special_addresses(self.project_name)

        pool_addresses = get_pool_addresses(self.project_name)
        pool_tags = get_pool_tags(self.project_name)

        multi_pool_addresses = list()
        blocks_per_entity = defaultdict(int)
        for tx in data:
            day = tx['timestamp'][:10]
            pool_links = get_pool_links(self.project_name, day)

            try:
                identifiers = bytes.fromhex(tx['identifiers'][2:]).decode('utf-8')
            except (UnicodeDecodeError, ValueError):
                identifiers = tx['identifiers']

            reward_addresses = tx['reward_addresses']
            if reward_addresses in special_addresses:
                continue

            pool_match = False
            for (tag, info) in pool_tags.items():  # Check if identifiers contain known pool tag
                if tag in str(identifiers):
                    entity = info['name']
                    pool_addresses[reward_addresses] = entity
                    pool_match = True
                    if reward_addresses in pool_addresses.keys() and pool_addresses[reward_addresses] != entity:
                        multi_pool_addresses.append(f'{tx["number"]},{tx["timestamp"]},{reward_addresses},{entity}')
                    break

            if not pool_match:
                if reward_addresses in pool_addresses.keys():
                    entity = pool_addresses[reward_addresses]
                else:
                    entity = reward_addresses

            if entity in pool_links.keys():
                entity = pool_links[entity]

            blocks_per_entity[entity.replace(',', '')] += 1

        groups = self.map_block_producers_to_groups(blocks_per_entity.keys())
        write_blocks_per_entity_to_file(self.io_dir, blocks_per_entity, groups, timeframe)

        if len(timeframe) == 4 and multi_pool_addresses:
            with open(self.io_dir / f'multi_pool_addresses_{timeframe}.csv', 'w') as f:
                f.write('Block No,Timestamp,Address,Entity\n' + '\n'.join(multi_pool_addresses))

        return blocks_per_entity
