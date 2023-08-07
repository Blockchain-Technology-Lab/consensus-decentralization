from collections import defaultdict
from src.helpers.helper import get_pool_links, write_blocks_per_entity_to_file
from src.mappings.default_mapping import DefaultMapping


class EthereumMapping(DefaultMapping):
    """
    Mapping class tailored to Ethereum data. Inherits from Mapping.
    """

    def __init__(self, project_name, dataset):
        super().__init__(project_name, dataset)

    def map_from_known_addresses(self, block):
        """
        Maps one block to its block producer (pool) based on known addresses. Overrides the map_from_known_addresses
        of the DefaultMapping class to tailor the process to Ethereum, specifically taking advantage of the fact that in
        Ethereum we always have one reward address and not multiple like in other projects.
        :param block: dictionary with block information (block number, timestamp, identifiers, etc)
        :returns: the name of the pool that produced the block, if it was successfully mapped, otherwise the address
        that received rewards for the block
        """
        reward_address = self.get_reward_addresses(block)
        if reward_address:
            reward_address = reward_address[0]
            if reward_address in self.known_addresses.keys():
                return self.known_addresses[reward_address]
        return reward_address
