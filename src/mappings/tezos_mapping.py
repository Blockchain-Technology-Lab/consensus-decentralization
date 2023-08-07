from collections import defaultdict
from src.helpers.helper import get_pool_links, write_blocks_per_entity_to_file
from src.mappings.default_mapping import DefaultMapping


class TezosMapping(DefaultMapping):
    """
    Mapping class tailored to Tezos data. Inherits from Mapping.
    """

    def __init__(self, project_name, dataset):
        super().__init__(project_name, dataset)

    def map_from_known_identifiers(self, block):
        """
        Overrides map_from_known_identifiers of the DefaultMapping class.
        Always returns None as Tezos block data does not include identifiers
        :param block: dictionary with block information (block number, timestamp, identifiers, etc)
        :returns: None
        """
        return None

    def map_from_known_addresses(self, block):
        reward_address = self.get_reward_addresses(block)
        if reward_address:
            reward_address = reward_address[0]
            if reward_address in self.known_addresses.keys():
                return self.known_addresses[reward_address]
            return reward_address
        return '----- UNDEFINED MINER -----'
