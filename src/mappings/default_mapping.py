from collections import defaultdict
import json
import src.helpers.helper as hlp


class DefaultMapping:
    """
    The default mapping, used for Bitcoin, Litecoin, Zcash and others. Any project that requires different mapping
    methods must use a mapping class that inherits from this one.

    :ivar project_name: the name of the project associated with a specific mapping instance
    :ivar io_dir: the directory that includes the parsed data related to the project
    :ivar dataset: a dictionary with the parsed data of the project
    :ivar special_addresses: a set with the special addresses of the project (addresses that don't count in the
    context of out analysis)
    :ivar known_addresses: a dictionary with the known addresses of the project (addresses that are known to belong to
    a specific entity)
    :ivar known_identifiers: a dictionary with the known identifiers of the project (identifiers that are publicly
    associated with a specific entity)
    :ivar multi_pool_blocks: a list to be populated with blocks that were produced by multiple pools
    :ivar multi_pool_addresses: a list to be populated with addresses that were associated with multiple pools
    """

    def __init__(self, project_name, io_dir):
        self.project_name = project_name
        self.io_dir = io_dir
        self.dataset = None
        self.special_addresses = hlp.get_special_addresses(project_name)
        self.known_addresses = hlp.get_known_addresses(project_name)
        self.known_identifiers = hlp.get_pool_identifiers(project_name)
        self.multi_pool_blocks = list()
        self.multi_pool_addresses = list()

    def perform_mapping(self, timeframe):
        """
        Makes sure that the parsed data are loaded into the instance and calls process to perform the mapping
        :param timeframe: string that corresponds to the timeframe under consideration (in YYYY-MM-DD, YYYY-MM or YYYY
        format)
        :returns: a dictionary with the entities and the number of blocks they have produced over the given timeframe
        """
        if self.dataset is None:
            self.dataset = self.read_project_data()
        return self.process(timeframe)

    def read_project_data(self):
        """
        Reads the parsed data from the directory specified by the instance
        :returns: a dictionary with the parsed data
        """
        with open(self.io_dir / 'parsed_data.json') as f:
            data = json.load(f)
        return data

    def get_reward_addresses(self, block):
        """
        Determines which addresses are associated with a block in the context of our analysis, i.e. after removing
        any special addresses from those that received rewards for the block
        :param block: dictionary with block information
        :returns: a list with the address(es) that received rewards from the block and are not considered "special
        addresses", or None if there were no addresses associated with the block at all. Note that in the case of all
        reward addresses being "special" an empty list is returned (not None)
        """
        reward_addresses = block['reward_addresses']
        if reward_addresses:
            return list(set(reward_addresses.split(',')) - self.special_addresses)
        return None

    def map_from_known_identifiers(self, block):
        """
        Maps one block to its block producer (pool) based on known identifiers (tag, etc).
        If successful, it also updates the pool's known addresses with the reward addresses of the block and,
        if some address is found to also be associated with another pool, it adds it to the list of multi-pool addresses
        :param block: dictionary with block information (block number, timestamp, identifiers, etc)
        :returns: the name of the pool that produced the block, if it was successfully mapped, otherwise None
        """
        block_identifier = block['identifiers']
        for identifier in self.known_identifiers.keys():
            if identifier in block_identifier:
                entity = self.known_identifiers[identifier]['name']
                reward_addresses = self.get_reward_addresses(block)
                if reward_addresses:
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
        is no reward address, or '----- SPECIAL ADDRESS -----' if all reward addresses belong to the "special
        addresses" of the project
        """
        reward_addresses = self.get_reward_addresses(block)
        if reward_addresses is None:  # there was no reward address associated with the block
            return '----- UNDEFINED MINER -----'
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
            elif len(reward_addresses) == 0:  # the reward addresses associated with the block are all special
                entity = '----- SPECIAL ADDRESS -----'
            else:
                entity = '/'.join([
                    addr[:5] + '...' + addr[-5:] for addr in sorted(reward_addresses)
                ])
        return entity

    def map_block_creators_to_groups(self, block_producers):
        """
        Maps the project's block producers to groups. A group is either the name of the entity behind the block
        producer, or "Unknown" if we only have address information about the block producer
        :param blocks_per_entity:
        """
        known_entities = hlp.get_known_entities(self.project_name)
        groups = dict()
        for block_producer in block_producers:
            groups[block_producer] = block_producer if block_producer in known_entities else 'Unknown'
        return groups

    def write_multi_pool_files(self, timeframe):
        """
        Writes the files with the blocks that were produced by multiple pools and the addresses that were associated
        with multiple pools, if any such blocks/addresses were found for the project
        """
        if self.multi_pool_addresses:
            with open(self.io_dir / f'multi_pool_addresses_{timeframe}.csv', 'w') as f:
                f.write('Block No,Timestamp,Address,Entity\n' + '\n'.join(self.multi_pool_addresses))

        if self.multi_pool_blocks:
            with open(self.io_dir / f'multi_pool_blocks_{timeframe}.csv', 'w') as f:
                f.write('Block No,Timestamp,Entities\n' + '\n'.join(self.multi_pool_blocks))

    def process(self, timeframe):
        """
        Processes the parsed data and outputs the mapped data.
        :param timeframe: string that corresponds to the timeframe under consideration (in YYYY-MM-DD, YYYY-MM or YYYY
        format)
        :returns: a dictionary with the entities and the number of blocks they have produced over the given timeframe
        """
        blocks = [block for block in self.dataset if block['timestamp'][:len(timeframe)] == timeframe]
        blocks_per_entity = defaultdict(int)

        for block in blocks:
            entity = self.map_from_known_identifiers(block)

            if entity is None:
                entity = self.map_from_known_addresses(block)

            day = block['timestamp'][:10]
            pool_links = hlp.get_pool_links(self.project_name, day)
            if entity in pool_links.keys():
                entity = pool_links[entity]

            blocks_per_entity[entity.replace(',', '')] += 1

        groups = self.map_block_creators_to_groups(blocks_per_entity.keys())
        hlp.write_blocks_per_entity_to_file(self.io_dir, blocks_per_entity, groups, timeframe)

        if len(timeframe) == 4:  # If timeframe is a year, also write multi-pool addresses and blocks to file
            self.write_multi_pool_files(timeframe)
        return blocks_per_entity
