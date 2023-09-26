from consensus_decentralization.mappings.default_mapping import DefaultMapping
import consensus_decentralization.helper as hlp


class CardanoMapping(DefaultMapping):
    """
    Mapping class tailored to Cardano data. Inherits from Mapping class.
    """

    def __init__(self, project_name, output_dir, data_to_map):
        super().__init__(project_name, output_dir, data_to_map)

    def map_from_known_identifiers(self, block):
        """
        Maps one block to its block producer (pool) based on known identifiers. Overrides the map_from_known_identifiers
        of the DefaultMapping class to tailor the process to Cardano
        :param block: dictionary with block information (block number, timestamp, identifiers, etc)
        :returns: the name of the pool that produced the block, if it was successfully mapped, otherwise None
        """
        block_identifier = block['identifiers']
        day = block['timestamp'][:10]
        pool_links = hlp.get_pool_links(self.project_name, day)  # todo move out of method after updating cardano data
        if block_identifier in pool_links.keys():
            return pool_links[block_identifier]
        if block_identifier in self.known_identifiers.keys():
            return self.known_identifiers[block_identifier]['name']
        return None

    def map_from_known_addresses(self, block):
        """
        Maps one block to its block producer (pool) based on the reward address of the block. Overrides the
        map_from_known_addresses of the DefaultMapping class to tailor the process to Cardano, specifically taking
        advantage of the fact that in Cardano we always have one reward address and only in blocks that were mined
        before a certain point there is no reward address, which we attribute to the development entity that was
        responsible for creating Cardano blocks at the time (Input Output)
        :param block: dictionary with block information (block number, timestamp, identifiers, etc)
        :returns: the reward address of the block, if such exists and is not "special". If there was no address
        associated with the block it returns 'Input Output (iohk.io)', as this only occurred pre-decentralization in
        Cardano where a single entity (Input Output) was producing all blocks. If there was an associated address
        but it was part of the project's "special addresses" then it returns '----- SPECIAL ADDRESS -----'

        """
        reward_addresses = self.get_reward_addresses(block)
        if reward_addresses is None:  # there was no reward address associated with the block
            return 'Input Output (iohk.io)'  # pre-decentralization
        if len(reward_addresses) == 0:  # the reward address was deemed "special" and thus removed
            return '----- SPECIAL ADDRESS -----'
        reward_address = reward_addresses[0]
        if reward_address in self.known_addresses.keys():
            return self.known_addresses[reward_address]
        return reward_address

    def perform_mapping(self):
        """
        Overrides process method of parent class to use project-specific information and extract the distribution of
        blocks to different entities.
        :returns: a dictionary with the entities and the number of blocks they have produced over the given timeframe
        """
        for block in self.data_to_map:
            entity = self.map_from_known_identifiers(block)

            if entity:
                mapping_method = 'known_identifiers'
            else:
                entity = self.map_from_known_addresses(block)
                mapping_method = 'known_addresses'

            self.mapped_data.append({
                "number": block['number'],
                "timestamp": block['timestamp'],
                "reward_addresses": block['reward_addresses'],
                "creator": entity,
                "mapping_method": mapping_method
            })

        if len(self.mapped_data) > 0:
            self.write_mapped_data()

        return self.mapped_data
