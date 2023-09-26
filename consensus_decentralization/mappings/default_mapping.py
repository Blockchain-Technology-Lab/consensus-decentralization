import json
import consensus_decentralization.helper as hlp


class DefaultMapping:
    """
    The default mapping, used for Bitcoin, Litecoin, Zcash and others. Any project that requires different mapping
    methods must use a mapping class that inherits from this one.

    :ivar project_name: the name of the project associated with a specific mapping instance
    :ivar output_dir: the directory that includes the parsed data related to the project
    :ivar mapped_data_dir: the directory to save the mapped data files in
    :ivar multi_pool_dir: the directory to save the multi pool data files in
    :ivar data_to_map: a list with the parsed data of the project (list of dictionaries with block information
    :ivar special_addresses: a set with the special addresses of the project (addresses that don't count in the
    context of out analysis)
    :ivar known_addresses: a dictionary with the known addresses of the project (addresses that are known to belong to
    a specific entity)
    :ivar known_identifiers: a dictionary with the known identifiers of the project (identifiers that are publicly
    associated with a specific entity)
    :ivar multi_pool_blocks: a list to be populated with blocks that were produced by multiple pools
    :ivar multi_pool_addresses: a list to be populated with addresses that were associated with multiple pools
    """

    def __init__(self, project_name, output_dir, data_to_map):
        self.project_name = project_name
        self.output_dir = output_dir
        self.data_to_map = data_to_map
        self.mapped_data = list()
        self.special_addresses = hlp.get_special_addresses(project_name)
        self.known_addresses = hlp.get_known_addresses(project_name)
        self.known_identifiers = hlp.get_pool_identifiers(project_name)
        self.multi_pool_blocks = list()
        self.multi_pool_addresses = list()

    def perform_mapping(self):
        """
        Processes the parsed data and outputs the mapped data. The mapped data is a list that contains an entry
        (dictionary) for each block with the number of the block, its timestamp, the addresses that received rewards
        for it, the name of the entity that it was mapped to and the mapping method that was used to identify the entity.
        The mapped data is also saved in a file in the project's output directory.
        Also outputs a file with the blocks that were produced by multiple pools and a file
        with the addresses that were associated with multiple pools, if any such blocks/addresses were found for the
        project.
        :returns: a list of mapped block data
        """
        for block in self.data_to_map:
            entity = self.map_from_known_identifiers(block)
            if entity:
                mapping_method = 'known_identifiers'
            else:
                entity = self.map_from_known_addresses(block)
                mapping_method = 'known_addresses'  # todo add separate clause for unmapped blocks?

            day = block['timestamp'][:10]
            pool_links = hlp.get_pool_links(self.project_name, day)
            if entity in pool_links.keys():
                entity = pool_links[entity]
                mapping_method = 'known_pool_links'
            self.mapped_data.append({
                "number": block['number'],
                "timestamp": block['timestamp'],
                "reward_addresses": block['reward_addresses'],
                "creator": entity,
                "mapping_method": mapping_method
            })

        if len(self.mapped_data) > 0:
            self.write_mapped_data()
        self.write_multi_pool_files()

        return self.mapped_data

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
                            self.multi_pool_addresses.append(
                                f'{block["number"]},{block["timestamp"]},{address},{entity}')
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
                entity = '/'.join([addr[:5] + '...' + addr[-5:] for addr in sorted(reward_addresses)])
        return entity

    def write_multi_pool_files(self):
        """
        Writes the files with the blocks that were produced by multiple pools and the addresses that were associated
        with multiple pools, if any such blocks/addresses were found for the project
        """
        if self.multi_pool_addresses:
            with open(self.output_dir / 'multi_pool_addresses.csv', 'w') as f:
                f.write('Block No,Timestamp,Address,Entity\n' + '\n'.join(self.multi_pool_addresses))

        if self.multi_pool_blocks:
            with open(self.output_dir / 'multi_pool_blocks.csv', 'w') as f:
                f.write('Block No,Timestamp,Entities\n' + '\n'.join(self.multi_pool_blocks))

    def write_mapped_data(self):
        """
        Writes the mapped data into a file in a directory associated with the mapping instance. Specifically,
        into a folder named after the project, inside the general output directory
        """
        filename = 'mapped_data.json'
        with open(self.output_dir / filename, 'w') as f:
            json.dump(self.mapped_data, f, indent=4)
