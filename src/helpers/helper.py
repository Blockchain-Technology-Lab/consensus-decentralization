# module with helper functions
import pathlib
import json

YEAR_DIGITS = 4
INPUT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / 'input'
OUTPUT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / 'output'


def get_pool_data(project_name, timeframe):
    helpers_path = str(pathlib.Path(__file__).parent.parent.resolve()) + '/helpers'

    pool_links = {}

    with open(helpers_path + f'/pool_information/{project_name}.json') as f:
        pool_data = json.load(f)
        clusters = {}
        if 'all' in pool_data['clusters']:
            clusters.update(pool_data['clusters']['all'])
        if timeframe[:YEAR_DIGITS] in pool_data['clusters']:
            clusters.update(pool_data['clusters'][timeframe[:YEAR_DIGITS]])
        for cluster, pools in clusters.items():
            for (pool, _) in pools:
                pool_links[pool] = cluster

    with open(helpers_path + '/legal_links.json') as f:
        legal_links = json.load(f)
        try:
            for cluster, pools in legal_links[timeframe[:YEAR_DIGITS]].items():
                for (pool, _) in pools:
                    pool_links[pool] = cluster
        except KeyError:
            pass

    for parent, child in pool_links.items():  # resolve chain links
        while child in pool_links.keys():
            next_child = pool_links[child]
            if next_child == child:
                # Cluster's name is the same as the primary pool's name
                break
            elif next_child == parent:
                raise AssertionError(f'Circular dependency: {parent}, {child}')
            else:
                child = next_child
        pool_links[parent] = child

    return pool_data, pool_links


def write_csv_file(project_dir, blocks_per_entity, timeframe):
    with open(project_dir / f'{timeframe}.csv', 'w') as f:
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
