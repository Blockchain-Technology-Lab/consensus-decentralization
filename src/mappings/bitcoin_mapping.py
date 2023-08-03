from collections import defaultdict
import codecs

from src.helpers.helper import write_blocks_per_entity_to_file, get_pool_identifiers, get_pool_links, \
    get_known_addresses, get_special_addresses
from src.mappings.mapping import Mapping


class BitcoinMapping(Mapping):
    """
    Mapping class tailored to Bitcoin data. Inherits from Mapping.
    """

    def __init__(self, project_name, dataset):
        super().__init__(project_name, dataset)
        self.special_addresses = get_special_addresses(project_name)
        self.known_addresses = get_known_addresses(project_name)
        self.known_identifiers = get_pool_identifiers(project_name)
        self.multi_pool_blocks = list()
        self.multi_pool_addresses = list()

    def map_from_known_identifiers(self, block):
        """
        Maps one block to its block producer (pool) based on known identifiers (tag, etc).
        If successful, it also updates the pool's known addresses with the reward addresses of the block and,
        if some address is found to also be associated with another pool, it adds it to the list of multi-pool addresses
        :param block: dictionary with block information (block number, timestamp, identifiers, etc)
        :returns: the name of the pool that produced the block, if it was successfully mapped, otherwise None
        """
        block_identifier = str(codecs.decode(block['identifiers'], 'hex'))
        for identifier in self.known_identifiers.keys():
            if identifier in block_identifier:
                entity = self.known_identifiers[identifier]['name']
                reward_addresses = list(set(block['reward_addresses'].split(',')) - self.special_addresses)
                for address in reward_addresses:
                    if address in self.known_addresses.keys() and self.known_addresses[address] != entity:
                        self.multi_pool_addresses.append(f'{block["number"]},{block["timestamp"]},{address},{entity}')
                    self.known_addresses[address] = entity
                return entity
        return None

    def map_from_known_addresses(self, block):
        """
        Maps one block to its block producer (pool) based on known addresses.
        :param block: dictionary with block information (block number, timestamp, identifiers, etc)
        :returns: the name of the pool that produced the block, if it was successfully mapped, otherwise the address
        or concatenation of addresses that received rewards for the block, or '----- UNDEFINED MINER -----' if there
        is no reward address
        """
        reward_addresses = list(set(block['reward_addresses'].split(',')) - self.special_addresses)
        block_pools = set()
        for address in reward_addresses:
            if address in self.known_addresses.keys():  # Check if address is associated with pool
                block_pools.add((address, self.known_addresses[address]))
        if block_pools:
            entities = sorted({i[1] for i in block_pools})
            if len(entities) > 1:
                multi_pool_info = '/'.join([f'{i[0]}({i[1]})' for i in block_pools])
                self.multi_pool_blocks.append(f'{block["number"]},{block["timestamp"]},{multi_pool_info}')
            entity = str('/'.join(entities))
        else:
            if len(reward_addresses) == 1:
                entity = reward_addresses[0]
            elif len(reward_addresses) == 0:
                entity = '----- UNDEFINED MINER -----'
            else:
                entity = '/'.join([
                    addr[:5] + '...' + addr[-5:] for addr in sorted(reward_addresses)
                ])
        return entity

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

            entity = self.map_from_known_identifiers(block)

            if entity is None:
                entity = self.map_from_known_addresses(block)

            if entity in pool_links.keys():
                entity = pool_links[entity]

            blocks_per_entity[entity.replace(',', '')] += 1

        groups = self.map_block_creators_to_groups(blocks_per_entity.keys())
        write_blocks_per_entity_to_file(self.io_dir, blocks_per_entity, groups, timeframe)

        if len(timeframe) == 4:  # If timeframe is a year, also write multi-pool addresses and blocks to file
            if self.multi_pool_addresses:
                with open(self.io_dir / f'multi_pool_addresses_{timeframe}.csv', 'w') as f:
                    f.write('Block No,Timestamp,Address,Entity\n' + '\n'.join(self.multi_pool_addresses))

            if self.multi_pool_blocks:
                with open(self.io_dir / f'multi_pool_blocks_{timeframe}.csv', 'w') as f:
                    f.write('Block No,Timestamp,Entities\n' + '\n'.join(self.multi_pool_blocks))
        return blocks_per_entity
