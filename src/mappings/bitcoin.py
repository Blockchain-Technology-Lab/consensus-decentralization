from collections import defaultdict
import codecs
from src.helpers.helper import get_pool_data, write_csv_file
from src.mappings.mapping import Mapping

YEAR_DIGITS = 4


class BitcoinMapping(Mapping):

    def __init__(self, project_name, dataset):
        super().__init__(project_name, dataset)

    def process(self, timeframe):
        pool_data, pool_links = get_pool_data(self.project_name, timeframe)
        try:
            pool_addresses = pool_data['pool_addresses'][timeframe[:YEAR_DIGITS]]
        except KeyError:
            pool_addresses = {}

        data = [tx for tx in self.dataset if tx['timestamp'][:len(timeframe)] == timeframe]

        multi_pool_blocks = list()
        multi_pool_addresses = list()
        blocks_per_entity = defaultdict(int)
        for tx in data:
            coinbase_param = codecs.decode(tx['coinbase_param'], 'hex')
            coinbase_addresses = tx['coinbase_addresses'].split(',')

            pool_match = False
            for (tag, info) in pool_data['coinbase_tags'].items():  # Check if coinbase param contains known pool tag
                if tag in str(coinbase_param):
                    entity = info['name']
                    pool_match = True
                    for addr in tx['coinbase_addresses'].split(','):
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
                    entity = str('/'.join(sorted([i[1] for i in block_pools])))
                    if len(set([i[1] for i in block_pools])) > 1:
                        multi_pool_info = '/'.join([f'{i[0]}({i[1]})' for i in block_pools])
                        multi_pool_blocks.append(f'{tx["number"]},{tx["timestamp"]},{multi_pool_info}')
                else:
                    if len(coinbase_addresses) == 1:
                        entity = coinbase_addresses[0]
                    else:
                        entity = '/'.join([
                            addr[:5] + '...' + addr[-5:] for addr in coinbase_addresses
                        ])

            if entity in pool_links.keys():
                entity = pool_links[entity]

            blocks_per_entity[entity.replace(',', '')] += 1

        write_csv_file(self.io_dir, blocks_per_entity, timeframe)

        if len(timeframe) == 4:
            if multi_pool_addresses:
                with open(f'{self.io_dir}/multi_pool_addresses_{timeframe}.csv', 'w') as f:
                    f.write('Block No,Timestamp,Address,Entity\n' + '\n'.join(multi_pool_addresses))

            if multi_pool_blocks:
                with open(f'{self.io_dir}/multi_pool_blocks_{timeframe}.csv', 'w') as f:
                    f.write('Block No,Timestamp,Entities\n' + '\n'.join(multi_pool_blocks))

        return blocks_per_entity