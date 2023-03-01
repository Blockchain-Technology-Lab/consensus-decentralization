from collections import defaultdict
from src.helpers.helper import get_pool_data, write_blocks_per_entity_to_file, get_pool_addresses
from src.mappings.mapping import Mapping


class EthereumMapping(Mapping):

    def __init__(self, project_name, dataset):
        super().__init__(project_name, dataset)

    def process(self, timeframe):
        data = [tx for tx in self.dataset if tx['timestamp'][:len(timeframe)] == timeframe]

        multi_pool_addresses = list()
        daily_helper_data = {}
        blocks_per_entity = defaultdict(int)
        for tx in data:
            day = tx['timestamp'][:10]
            try:
                pool_data = daily_helper_data[day]['pool_data']
                pool_links = daily_helper_data[day]['pool_links']
                pool_addresses = daily_helper_data[day]['pool_addresses']
            except KeyError:
                pool_data, pool_links = get_pool_data(self.project_name, day)
                pool_addresses = get_pool_addresses(self.project_name, day)
                daily_helper_data[day] = {}
                daily_helper_data[day]['pool_data'] = pool_data
                daily_helper_data[day]['pool_links'] = pool_links
                daily_helper_data[day]['pool_addresses'] = pool_addresses

            try:
                coinbase_param = bytes.fromhex(tx['coinbase_param'][2:]).decode('utf-8')
            except (UnicodeDecodeError, ValueError):
                coinbase_param = tx['coinbase_param']

            coinbase_addresses = tx['coinbase_addresses']

            pool_match = False
            for (tag, info) in pool_data['coinbase_tags'].items():  # Check if coinbase param contains known pool tag
                if tag in str(coinbase_param):
                    entity = info['name']
                    pool_addresses[coinbase_addresses] = entity
                    pool_match = True
                    if coinbase_addresses in pool_addresses.keys() and pool_addresses[coinbase_addresses] != entity:
                        multi_pool_addresses.append(f'{tx["number"]},{tx["timestamp"]},{coinbase_addresses},{entity}')
                    break

            if not pool_match:
                if coinbase_addresses in pool_addresses.keys():
                    entity = pool_addresses[coinbase_addresses]
                else:
                    entity = coinbase_addresses

            if entity in pool_links.keys():
                entity = pool_links[entity]

            blocks_per_entity[entity.replace(',', '')] += 1

        write_blocks_per_entity_to_file(self.io_dir, blocks_per_entity, timeframe)

        if len(timeframe) == 4 and multi_pool_addresses:
            with open(f'{self.io_dir}/multi_pool_addresses_{timeframe}.csv', 'w') as f:
                f.write('Block No,Timestamp,Address,Entity\n' + '\n'.join(multi_pool_addresses))

        return blocks_per_entity
