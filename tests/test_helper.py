import pathlib
from src.helpers.helper import get_pool_data, write_csv_file, get_blocks_per_entity_from_file


def test_pool_data():
    pool_data, pool_links = get_pool_data('test', '2022')

    assert all([
        pool_links['entity 1'] == 'cluster_3',
        pool_links['ent2'] == 'cluster_2',
        pool_links['entity_3'] == 'cluster_2',
        pool_links['AntPool'] == 'Bitmain',
        pool_links['NovaBlock'] == 'Poolin'
    ])

    assert all([
        pool_data['clusters']['2022']['cluster_1'] == [['entity 1', 'homepage']],
        pool_data['clusters']['all']['cluster_2'] == [['ent2', 'homepage'], ['entity_3', 'homepage']],
        pool_data['coinbase_tags']['entity 1']['name'] == 'Entity 1',
        pool_data['coinbase_tags']['entity 1']['link'] == 'https://www.entity.1',
        pool_data['coinbase_tags']['ent2']['name'] == 'Entity 2',
        pool_data['coinbase_tags']['ent2']['link'] == 'https://www.entity.2',
        pool_data['coinbase_tags']['entity_3']['name'] == 'Entity 3',
        pool_data['coinbase_tags']['entity_3']['link'] == 'https://www.entity.3',
        pool_data['coinbase_tags']['entity 4']['name'] == 'Entity 4',
        pool_data['coinbase_tags']['entity 4']['link'] == 'https://www.entity.4',
        pool_data['coinbase_tags']['entity_5']['name'] == 'Entity 5',
        pool_data['coinbase_tags']['entity_5']['link'] == 'https://www.entity.5',
        pool_data['pool_addresses']['2022']['address1'] == 'entity 4',
        pool_data['pool_addresses']['2022']['addr2'] == 'entity_5',
    ])

    pool_data, pool_links = get_pool_data('test', '2023')
    assert all([
        pool_links['ent2'] == 'cluster_2',
        pool_links['entity_3'] == 'cluster_2'
    ])

    assert all([
        pool_data['clusters']['2022']['cluster_1'] == [['entity 1', 'homepage']],
        pool_data['clusters']['all']['cluster_2'] == [['ent2', 'homepage'], ['entity_3', 'homepage']],
        pool_data['coinbase_tags']['entity 1']['name'] == 'Entity 1',
        pool_data['coinbase_tags']['entity 1']['link'] == 'https://www.entity.1',
        pool_data['coinbase_tags']['ent2']['name'] == 'Entity 2',
        pool_data['coinbase_tags']['ent2']['link'] == 'https://www.entity.2',
        pool_data['coinbase_tags']['entity_3']['name'] == 'Entity 3',
        pool_data['coinbase_tags']['entity_3']['link'] == 'https://www.entity.3',
        pool_data['coinbase_tags']['entity 4']['name'] == 'Entity 4',
        pool_data['coinbase_tags']['entity 4']['link'] == 'https://www.entity.4',
        pool_data['coinbase_tags']['entity_5']['name'] == 'Entity 5',
        pool_data['coinbase_tags']['entity_5']['link'] == 'https://www.entity.5',
        pool_data['pool_addresses']['2022']['address1'] == 'entity 4',
        pool_data['pool_addresses']['2022']['addr2'] == 'entity_5',
    ])


def test_write_read_blocks_per_entity():
    output_dir = pathlib.Path(__file__).resolve().parent.parent / 'output'

    blocks_per_entity = {'Entity 1': 1, 'Entity 2': 2}

    write_csv_file(output_dir, blocks_per_entity, 'test')
    bpe = get_blocks_per_entity_from_file(output_dir / 'test.csv')

    assert all([
        bpe['Entity 1'] == 1,
        bpe['Entity 2'] == 2,
    ])
