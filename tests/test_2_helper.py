import datetime
import argparse
import os
import shutil
import pytest
from src.helpers.helper import get_known_entities, get_pool_data, write_blocks_per_entity_to_file, \
    get_blocks_per_entity_from_file, get_blocks_per_entity_group_from_file, get_timeframe_beginning, \
    get_timeframe_end, get_time_period, get_default_ledgers, valid_date, OUTPUT_DIR
from src.map import ledger_mapping


@pytest.fixture
def setup_and_cleanup():
    """
    This function can be used to set up the right conditions for a test and also clean up after the test is finished.
    The part before the yield command is run before the test (setup) and the part after the yield command is run
    after (cleanup)
    """
    print("Setting up")
    test_output_dir = OUTPUT_DIR / "test_output"
    if not os.path.exists(test_output_dir):
        os.makedirs(test_output_dir)
    yield test_output_dir
    print("Cleaning up")
    shutil.rmtree(test_output_dir)


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
        pool_data['pool_addresses']['address1'] == {"name": "Entity 4", "source": ""},
        pool_data['pool_addresses']['addr2'] == {"name": "Entity 5", "source": ""},
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


def test_committed_pool_data():
    for project_name in ledger_mapping.keys() - ['sample_bitcoin', 'sample_ethereum', 'sample_cardano', 'sample_tezos']:
        for year in range(2018, 2024):
            pool_data, pool_links = get_pool_data(project_name, str(year))
            for month in range(1, 13):
                pool_data, pool_links = get_pool_data(project_name, f'{year}-{month:02d}')


def test_write_read_blocks_per_entity(setup_and_cleanup):
    output_dir = setup_and_cleanup

    blocks_per_entity = {'Entity 1': 1, 'Entity 2': 2}
    groups = {'Entity 1': 'Entity 1', 'Entity 2': 'Entity 2'}

    write_blocks_per_entity_to_file(output_dir, blocks_per_entity, groups, 'test')
    # test that reading works for filepaths in both pathlib.PosixPath and string formats
    get_blocks_per_entity_from_file(output_dir / 'test.csv')
    bpe = get_blocks_per_entity_from_file(str(output_dir) + '/test.csv')

    assert all([
        bpe['Entity 1'] == 1,
        bpe['Entity 2'] == 2,
    ])


def test_write_read_blocks_per_entity_group(setup_and_cleanup):
    output_dir = setup_and_cleanup

    blocks_per_entity = {
        'Entity 1': 1,
        'Entity 2': 2,
        'Entity 123456789012345678901234567': 2,
        'Entity 234567890123456789012345678': 3
    }
    groups = {'Entity 1': 'Entity 1', 'Entity 2': 'Entity 2', 'Entity 123456789012345678901234567': 'Unknown',
              'Entity 234567890123456789012345678': 'Unknown'}

    write_blocks_per_entity_to_file(output_dir, blocks_per_entity, groups, 'test')
    # test that reading works for filepaths in both pathlib.PosixPath and string formats
    get_blocks_per_entity_group_from_file(output_dir / 'test.csv')
    bpg = get_blocks_per_entity_group_from_file(str(output_dir) + '/test.csv')

    assert all([
        bpg['Entity 1'] == 1,
        bpg['Entity 2'] == 2,
        bpg['Unknown'] == 5
    ])


def test_valid_date():
    for d in [
        '2022',
        '2022-01',
        '2022-01-01'
    ]:
        assert valid_date(d)

    for d in [
        '2022/1/01',
        '2022/01/1',
        '2022/1',
        '2022/01',
        '2022.1.01',
        '2022.01.1',
        '2022.1',
        '2022.01',
        'blah',
        '2022-',
        '2022-1-1',
        '2022-1-01',
        '2022-1',
        '2022-01-1',
        '2022-02-29'
    ]:
        with pytest.raises(argparse.ArgumentTypeError) as e_info:
            valid_date(d)
        assert e_info.type == argparse.ArgumentTypeError


def test_get_start_date():  # currently not testing for invalid dates
    dates = {
        '2022': datetime.date(2022, 1, 1),
        '2022-03': datetime.date(2022, 3, 1),
        '2022-03-29': datetime.date(2022, 3, 29)
    }
    for date, start_date in dates.items():
        assert get_timeframe_beginning(date) == start_date


def test_get_timeframe_end():  # currently not testing for invalid dates
    dates = {
        '2022': datetime.date(2022, 12, 31),
        '2022-03': datetime.date(2022, 3, 31),
        '2022-03-29': datetime.date(2022, 3, 29)
    }
    for date, end_date in dates.items():
        assert get_timeframe_end(date) == end_date


def test_get_time_period():  # currently not testing for invalid dates
    from_to = [
        ('2018', '2022'),
        ('2018-01-23', '2022-03'),
        ('2018-06', '2019-01'),
        ('', '2019-03-09'),
        ('2019-02-09', '')
    ]
    time_periods = [
        (datetime.date(2018, 1, 1), datetime.date(2021, 12, 31)),
        (datetime.date(2018, 1, 23), datetime.date(2022, 2, 28)),
        (datetime.date(2018, 6, 1), datetime.date(2018, 12, 31)),
        (datetime.date(1, 1, 1), datetime.date(2019, 3, 8)),
        (datetime.date(2019, 2, 9), datetime.date(9999, 12, 31))
    ]

    for i, (frm, to) in enumerate(from_to):
        assert get_time_period(frm, to) == time_periods[i]


def test_get_known_entities():
    known_entities = get_known_entities(ledger='test')

    # check pool data
    assert "cluster_1" in known_entities
    assert "Entity 1" in known_entities
    assert "Entity 5" in known_entities

    assert "entity 5" not in known_entities
    assert "entity_5" not in known_entities
    assert "ent2" not in known_entities

    # check legal links
    assert "Bitmain" in known_entities
    assert "NovaBlock" in known_entities


def test_get_default_ledgers():
    ledgers = get_default_ledgers()
    assert type(ledgers) == list
    assert len(ledgers) > 0
