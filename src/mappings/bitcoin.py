from collections import defaultdict
import codecs
from src.helpers.helper import get_pool_data, write_blocks_per_entity_to_file, get_pool_addresses, get_special_addresses
from src.mappings.mapping import Mapping

YEAR_DIGITS = 4


class BitcoinMapping(Mapping):
    """
    Mapping class tailored for Bitcoin data. Inherits from Mapping.
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

        daily_helper_data = {}
        multi_pool_blocks = list()
        multi_pool_addresses = list()
        blocks_per_entity = defaultdict(int)
        for tx in data:
            day = tx['timestamp'][:10]
            try:
                pool_data = daily_helper_data[day]['pool_data']
                pool_links = daily_helper_data[day]['pool_links']
                pool_addresses = daily_helper_data[day]['pool_addresses']
            except KeyError:
                pool_data, pool_links = get_pool_data(self.project_name, day)
                pool_addresses = get_pool_addresses(self.project_name)
                daily_helper_data[day] = {}
                daily_helper_data[day]['pool_data'] = pool_data
                daily_helper_data[day]['pool_links'] = pool_links
                daily_helper_data[day]['pool_addresses'] = pool_addresses

            coinbase_param = codecs.decode(tx['coinbase_param'], 'hex')
            coinbase_addresses = list(set(tx['coinbase_addresses'].split(',')) - special_addresses)

            pool_match = False
            for (tag, info) in pool_data['coinbase_tags'].items():  # Check if coinbase param contains known pool tag
                if tag in str(coinbase_param):
                    entity = info['name']
                    pool_match = True
                    for addr in coinbase_addresses:
                        if addr in pool_addresses.keys() and pool_addresses[addr] != entity:
                            multi_pool_addresses.append(f'{tx["number"]},{tx["timestamp"]},{addr},{entity}')
                        pool_addresses[addr] = entity
                    break

            if not pool_match:
                block_pools = set()
                for addr in coinbase_addresses:  # Check if address is associated with pool
                    if addr in pool_addresses.keys():
                        block_pools.add((addr, pool_addresses[addr]))
                if block_pools:
                    entities = sorted({i[1] for i in block_pools})
                    entity = str('/'.join(entities))
                    if len(entities) > 1:
                        multi_pool_info = '/'.join([f'{i[0]}({i[1]})' for i in block_pools])
                        multi_pool_blocks.append(f'{tx["number"]},{tx["timestamp"]},{multi_pool_info}')
                else:
                    if len(coinbase_addresses) == 1:
                        entity = coinbase_addresses[0]
                    elif len(coinbase_addresses) == 0:
                        entity = '----- UNDEFINED MINER -----'
                    else:
                        entity = '/'.join([
                            addr[:5] + '...' + addr[-5:] for addr in sorted(coinbase_addresses)
                        ])

            if entity in pool_links.keys():
                entity = pool_links[entity]

            blocks_per_entity[entity.replace(',', '')] += 1

        groups = self.map_block_producers_to_groups(blocks_per_entity.keys())
        write_blocks_per_entity_to_file(self.io_dir, blocks_per_entity, groups, timeframe)

        if len(timeframe) == 4:
            if multi_pool_addresses:
                with open(f'{self.io_dir}/multi_pool_addresses_{timeframe}.csv', 'w') as f:
                    f.write('Block No,Timestamp,Address,Entity\n' + '\n'.join(multi_pool_addresses))

            if multi_pool_blocks:
                with open(f'{self.io_dir}/multi_pool_blocks_{timeframe}.csv', 'w') as f:
                    f.write('Block No,Timestamp,Entities\n' + '\n'.join(multi_pool_blocks))

        return blocks_per_entity
