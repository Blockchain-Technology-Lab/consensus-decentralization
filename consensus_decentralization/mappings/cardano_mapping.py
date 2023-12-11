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
        :param block: dictionary with block information (block number, timestamp, identifiers, reward addresses)
        :returns: the name of the pool that produced the block, if it was successfully mapped, otherwise None
        """
        block_identifier = block['identifiers']
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
        :param block: dictionary with block information (block number, timestamp, identifiers, reward addresses)
        :returns: the reward address of the block, if such exists and is not "special". If there was no address
        associated with the block it returns 'Input Output (iohk.io)', as this only occurred pre-decentralization in
        Cardano where a single entity (Input Output) was producing all blocks. If there was an associated address
        but it was part of the project's "special addresses" then it returns '----- SPECIAL ADDRESS -----'. If there
        was an associated address but it could not be mapped to a pool then it returns None

        """
        reward_addresses = self.get_reward_addresses(block)
        if reward_addresses is None:  # there was no reward address associated with the block
            return 'Input Output (iohk.io)'  # pre-decentralization
        if len(reward_addresses) == 0:  # the reward address was deemed "special" and thus removed
            return '----- SPECIAL ADDRESS -----'
        reward_address = reward_addresses[0]
        if reward_address in self.known_addresses.keys():
            return self.known_addresses[reward_address]
        return None

    def map_from_known_clusters(self, block):
        """
        Maps one block to its block producer (pool cluster) based on known cluster information.
        Overrides the map_from_known_clusters of the DefaultMapping class to tailor the process to Cardano.
        Specifically, it takes advantage of the fact that in Cardano each block has one reward address and
        that this reward address (in fact, the pool hash) is used to retrieve cluster information from the relevant
        file.
        :param block: dictionary with block information (block number, timestamp, identifiers, reward addresses)
        :returns: string, which corresponds to the name of the cluster that produced the block, if it was successfully
        mapped, otherwise None
        """
        if len(self.known_clusters) > 0:
            reward_addresses = self.get_reward_addresses(block)
            if reward_addresses:
                reward_address = reward_addresses[0]
                if reward_address in self.known_clusters.keys():
                    return self.known_clusters[reward_address]['cluster']
        return None
