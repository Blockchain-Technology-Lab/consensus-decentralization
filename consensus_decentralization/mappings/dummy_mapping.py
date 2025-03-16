from consensus_decentralization.mappings.default_mapping import DefaultMapping
import consensus_decentralization.helper as hlp


class DummyMapping(DefaultMapping):
    """
    "Dummy" mapping class that simply maps a block to the address that received rewards for it (if multiple addresses
    then to the first one). Inherits from Mapping class.
    """

    def __init__(self, project_name, output_dir, data_to_map):
        super().__init__(project_name, output_dir, data_to_map)

    def perform_mapping(self):
        """
        Overrides perform_mapping method of parent class.
        :returns: a list of dictionaries ("mapped" block data)
        """
        for block in self.data_to_map:
            reward_addresses = block['reward_addresses'].split(',')
            entity = reward_addresses[0]

            self.mapped_data.append({
                "number": block['number'],
                "timestamp": block['timestamp'],
                "reward_addresses": block['reward_addresses'],
                "creator": entity,
                "mapping_method": 'no_mapping'
            })

        if len(self.mapped_data) > 0:
            self.write_mapped_data(hlp.get_clustering_flag())

        return self.mapped_data
