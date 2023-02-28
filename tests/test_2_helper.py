import pathlib
from src.helpers.helper import get_pool_data, write_csv_file, get_blocks_per_entity_from_file


def test_pool_data():
    pool_data, pool_links = get_pool_data('test', '2022')

    assert all([
        pool_links['entity 1'] == 'cluster_3',
        pool_links['ent2'] == 'cluster_2',
        pool_links['entity_3'] == 'cluster_2',
        pool_links['cluster_1'] == 'cluster_3',
        pool_links['AntPool'] == 'Bitmain',
        pool_links['NovaBlock'] == 'Poolin',
        pool_links['BTC.COM'] == 'BIT Mining',
        pool_links['Bitdeer'] == 'BIT Mining',
    ])

    assert all([
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
        pool_data['pool_addresses']['address1'] == {"name": "entity 4", "from": "", "to": "2023", "source": ""},
        pool_data['pool_addresses']['addr2'] == {"name": "entity_5", "from": "", "to": "2023", "source": ""},
    ])

    pool_data, pool_links = get_pool_data('test', '2021-03-12')
    assert all([
        pool_links['entity 1'] == 'cluster_3',
        pool_links['ent2'] == 'cluster_2',
        pool_links['entity_3'] == 'cluster_2',
        pool_links['AntPool'] == 'Bitmain',
        pool_links['NovaBlock'] == 'Poolin',
        pool_links['BTC.COM'] == 'Bitdeer',
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
