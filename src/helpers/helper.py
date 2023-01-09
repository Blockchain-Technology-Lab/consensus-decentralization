# module with helper functions
import pathlib
import json

YEAR_DIGITS = 4

def get_pool_data(project_name, timeframe):
    helpers_path = str(pathlib.Path(__file__).parent.parent.resolve()) + '/helpers'

    with open(helpers_path + '/pool_information/{}.json'.format(project_name)) as f:
        pool_data = json.load(f)

    pool_links = {}

    try:
        pool_links.update(pool_data['coinbase_address_links'][timeframe[:YEAR_DIGITS]])
    except KeyError:
        pass

    with open(helpers_path + '/legal_links.json') as f:
        legal_links = json.load(f)
    pool_links.update(legal_links[timeframe[:YEAR_DIGITS]])

    for key, val in pool_links.items():  # resolve chain links
        while val in pool_links.keys():
            val = pool_links[val]
        pool_links[key] = val

    try:
        pool_addresses = pool_data['pool_addresses'][timeframe[:YEAR_DIGITS]] #todo remove unused variable or is it sth we might need in the future?
    except KeyError:
        pool_addresses = {}

    return pool_data, pool_links


def write_csv_file(project_dir, blocks_per_entity, timeframe):
    with open(project_dir + '/' + timeframe + '.csv', 'w') as f:
        csv_output = ['Entity,Resources']
        for key, val in sorted(blocks_per_entity.items(), key=lambda x: x[1], reverse=True):
            csv_output.append(','.join([key, str(val)]))
        f.write('\n'.join(csv_output))


def get_blocks_per_entity_from_file(filename):
    blocks_per_entity = {}
    with open(filename) as f:
        for idx, line in enumerate(f.readlines()):
            if idx > 0:
                row = (','.join([i for i in line.split(',')[:-1]]), line.split(',')[-1])
                blocks_per_entity[row[0]] = int(row[1])
    return blocks_per_entity