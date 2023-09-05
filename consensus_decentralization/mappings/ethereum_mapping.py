from consensus_decentralization.mappings.default_mapping import DefaultMapping


class EthereumMapping(DefaultMapping):
    """
    Mapping class tailored to Ethereum data. Inherits from Mapping.
    """

    def __init__(self, project_name, io_dir, data_to_map):
        super().__init__(project_name, io_dir, data_to_map)

    def map_from_known_addresses(self, block):
        """
        Maps one block to its block producer (pool) based on known addresses. Overrides the map_from_known_addresses
        of the DefaultMapping class to tailor the process to Ethereum, specifically taking advantage of the fact that in
        Ethereum we always have one reward address and not multiple like in other projects.
        :param block: dictionary with block information (block number, timestamp, identifiers, etc)
        :returns: the name of the pool that produced the block, if it was successfully mapped, otherwise the address
        that received rewards for the block. If there was no address associated with the block it returns
        '----- UNDEFINED MINER -----' and if there was an associated address but it was part of the project's
        "special addresses" it returns '----- SPECIAL ADDRESS -----'
        """
        reward_addresses = self.get_reward_addresses(block)
        if reward_addresses is None:  # there was no reward address associated with the block
            return '----- UNDEFINED MINER -----'
        if len(reward_addresses) == 0:  # the reward address was deemed "special" and thus removed
            return '----- SPECIAL ADDRESS -----'
        reward_address = reward_addresses[0]
        if reward_address in self.known_addresses.keys():
            return self.known_addresses[reward_address]
        return reward_address
