import datetime
import argparse
import shutil
import pytest
from consensus_decentralization.helper import get_pool_identifiers, get_pool_links, get_known_addresses, \
    write_blocks_per_entity_to_file, get_blocks_per_entity_from_file, get_timeframe_beginning, get_timeframe_end, \
    get_time_period, get_default_ledgers, valid_date, OUTPUT_DIR
from consensus_decentralization.map import ledger_mapping


@pytest.fixture
def setup_and_cleanup():
    """
    This function can be used to set up the right conditions for a test and also clean up after the test is finished.
    The part before the yield command is run before the test (setup) and the part after the yield command is run
    after (cleanup)
    """
    # Setting up
    test_output_dir = OUTPUT_DIR / "test_output"
    test_output_dir.mkdir(parents=True, exist_ok=True)
    yield test_output_dir
    # Cleaning up
    shutil.rmtree(test_output_dir)


def test_pool_data():
    pool_tags = get_pool_identifiers('test')
    pool_addresses = get_known_addresses('test')
    pool_links = get_pool_links('test', '2022')

    assert all([pool_links['entity 1'] == 'cluster_3', pool_links['ent2'] == 'cluster_2',
                pool_links['entity_3'] == 'cluster_2', pool_links['cluster_1'] == 'cluster_3',
                pool_links['AntPool'] == 'Bitmain', pool_links['NovaBlock'] == 'Poolin',
                pool_links['BTC.COM'] == 'BIT Mining', pool_links['Bitdeer'] == 'BIT Mining', ])

    assert all([pool_tags['entity 1']['name'] == 'Entity 1', pool_tags['entity 1']['link'] == 'https://www.entity.1',
                pool_tags['ent2']['name'] == 'Entity 2', pool_tags['ent2']['link'] == 'https://www.entity.2',
                pool_tags['entity_3']['name'] == 'Entity 3', pool_tags['entity_3']['link'] == 'https://www.entity.3',
                pool_tags['entity 4']['name'] == 'Entity 4', pool_tags['entity 4']['link'] == 'https://www.entity.4',
                pool_tags['entity_5']['name'] == 'Entity 5', pool_tags['entity_5']['link'] == 'https://www.entity.5',
                pool_addresses['address1'] == "Entity 4", pool_addresses['addr2'] == "Entity 5", ])

    pool_links = get_pool_links('test', '2021-03-12')
    assert all([pool_links['entity 1'] == 'cluster_3', pool_links['ent2'] == 'cluster_2',
                pool_links['entity_3'] == 'cluster_2', pool_links['AntPool'] == 'Bitmain',
                pool_links['NovaBlock'] == 'Poolin', pool_links['BTC.COM'] == 'Bitdeer', ])


def test_committed_pool_data():
    for project_name in ledger_mapping.keys() - ['sample_bitcoin', 'sample_ethereum', 'sample_cardano', 'sample_tezos']:
        get_pool_identifiers(project_name)
        get_known_addresses(project_name)
        for year in range(2018, 2024):
            get_pool_links(project_name, str(year))
            for month in range(1, 13):
                get_pool_links(project_name, f'{year}-{month:02d}')


def test_write_read_blocks_per_entity(setup_and_cleanup):
    output_dir = setup_and_cleanup

    blocks_per_entity = {'Entity 1': {'2018': 1, '2019': 3}, 'Entity 2': {'2018': 2, '2019': 2}}

    write_blocks_per_entity_to_file(output_dir=output_dir, blocks_per_entity=blocks_per_entity,
                                    time_chunks=['2018', '2019'], filename='test.csv')

    time_chunks, bpe = get_blocks_per_entity_from_file(output_dir / 'test.csv')

    assert all(len(nblocks) == len(time_chunks) for nblocks in bpe.values())
    assert time_chunks == ['2018', '2019']
    assert all([bpe['Entity 1'] == {'2018': 1, '2019': 3}, bpe['Entity 2'] == {'2018': 2, '2019': 2}])


def test_valid_date():
    for d in ['2022', '2022-01', '2022-01-01']:
        assert valid_date(d)

    for d in ['2022/1/01', '2022/01/1', '2022/1', '2022/01', '2022.1.01', '2022.01.1', '2022.1', '2022.01', 'blah',
              '2022-', '2022-1-1', '2022-1-01', '2022-1', '2022-01-1', '2022-02-29']:
        with pytest.raises(argparse.ArgumentTypeError) as e_info:
            valid_date(d)
        assert e_info.type == argparse.ArgumentTypeError


def test_get_start_date():  # currently not testing for invalid dates
    dates = {'2022': datetime.date(2022, 1, 1), '2022-03': datetime.date(2022, 3, 1),
             '2022-03-29': datetime.date(2022, 3, 29)}
    for date, start_date in dates.items():
        assert get_timeframe_beginning(date) == start_date


def test_get_timeframe_end():  # currently not testing for invalid dates
    dates = {'2022': datetime.date(2022, 12, 31), '2022-03': datetime.date(2022, 3, 31),
             '2022-03-29': datetime.date(2022, 3, 29)}
    for date, end_date in dates.items():
        assert get_timeframe_end(date) == end_date


def test_get_time_period():  # currently not testing for invalid dates
    from_to = [('2018', '2022'), ('2018-01-23', '2022-03'), ('2018-06', '2019-01'), ('', '2019-03-09'),
               ('2019-02-09', '')]
    time_periods = [(datetime.date(2018, 1, 1), datetime.date(2021, 12, 31)),
                    (datetime.date(2018, 1, 23), datetime.date(2022, 2, 28)),
                    (datetime.date(2018, 6, 1), datetime.date(2018, 12, 31)),
                    (datetime.date(1, 1, 1), datetime.date(2019, 3, 8)),
                    (datetime.date(2019, 2, 9), datetime.date(9999, 12, 31))]

    for i, (frm, to) in enumerate(from_to):
        assert get_time_period(frm, to) == time_periods[i]


def test_get_default_ledgers():
    ledgers = get_default_ledgers()
    assert type(ledgers) == list
    assert len(ledgers) > 0
