import datetime
import json
import shutil
import pytest
from consensus_decentralization.helper import OUTPUT_DIR
from consensus_decentralization.aggregate import aggregate, Aggregator, divide_timeframe


@pytest.fixture
def setup_and_cleanup():
    """
    This function can be used to set up the right conditions for a test and also clean up after the test is finished.
    The part before the yield command is run before the test (setup) and the part after the yield command is run
    after (cleanup)
    """
    # Set up
    test_io_dir = OUTPUT_DIR / "test_output"
    yield test_io_dir
    # Clean up
    shutil.rmtree(test_io_dir)


@pytest.fixture
def mock_sample_bitcoin_mapped_data(setup_and_cleanup):
    test_io_dir = setup_and_cleanup
    test_bitcoin_dir = test_io_dir / "sample_bitcoin"
    test_bitcoin_dir.mkdir(parents=True, exist_ok=True)
    # create a file that would be the output of the mapping
    mapped_data = '[' \
                  '{"number": "507516", "timestamp": "2018-02-04 02:36:23 UTC", "reward_addresses": "137YB5cpBLxLKvy8T6qXsycJ699iJjWCHH,1FVKW4rp5rN23dqFVk2tYGY4niAXMB8eZC","creator": "BTC.TOP", "mapping_method": "known_identifiers"},' \
                  '{"number": "507715", "timestamp": "2018-02-05 04:54:34 UTC", "reward_addresses": "131RUhDyyjxXSbSPxGRCm3t6vcei1TB6MB,1J7FCFaafPRxqu4X9VsaiMZr1XMemx69GR", "creator": "GBMiners", "mapping_method": "known_identifiers"},' \
                  '{"number": "508434", "timestamp": "2018-02-09 22:17:45 UTC", "reward_addresses": "1AM2fYfpY3ZeMeCKXmN66haoWxvB89pJUx,3G7y14BudP2a4kjPAuecg4iUKM84GgPPWb", "creator": "1AM2f...9pJUx/3G7y1...gPPWb", "mapping_method": "fallback_mapping"},' \
                  '{"number": "509373", "timestamp": "2018-02-15 23:50:04 UTC", "reward_addresses": "1AM2fYfpY3ZeMeCKXmN66haoWxvB89pJUx,3G7y14BudP2a4kjPAuecg4iUKM84GgPPWb", "creator": "1AM2f...9pJUx/3G7y1...gPPWb", "mapping_method": "fallback_mapping"},' \
                  '{"number": "509432", "timestamp": "2018-02-16 09:25:03 UTC", "reward_addresses": "1AM2fYfpY3ZeMeCKXmN66haoWxvB89pJUx,3G7y14BudP2a4kjPAuecg4iUKM84GgPPWb", "creator": "1AM2f...9pJUx/3G7y1...gPPWb", "mapping_method": "fallback_mapping"},' \
                  '{"number": "510199", "timestamp": "2018-02-21 06:43:35 UTC", "reward_addresses": "1AM2fYfpY3ZeMeCKXmN66haoWxvB89pJUx,3G7y14BudP2a4kjPAuecg4iUKM84GgPPWb", "creator": "1AM2f...9pJUx/3G7y1...gPPWb", "mapping_method": "fallback_mapping"},' \
                  '{"number": "510888", "timestamp": "2018-02-25 18:02:53 UTC", "reward_addresses": "137YB5cpBLxLKvy8T6qXsycJ699iJjWCHH,1FVKW4rp5rN23dqFVk2tYGY4niAXMB8eZC", "creator": "BTC.TOP", "mapping_method": "known_identifiers"},' \
                  '{"number": "511342", "timestamp": "2018-02-28 16:12:07 UTC", "reward_addresses": "131RUhDyyjxXSbSPxGRCm3t6vcei1TB6MB,1J7FCFaafPRxqu4X9VsaiMZr1XMemx69GR", "creator": "GBMiners", "mapping_method": "known_identifiers"},' \
                  '{"number": "508242", "timestamp": "2018-03-08 10:57:02 UTC", "reward_addresses": "1AM2fYfpY3ZeMeCKXmN66haoWxvB89pJUx", "creator": "1AM2fYfpY3ZeMeCKXmN66haoWxvB89pJUx", "mapping_method": "fallback_mapping"},' \
                  '{"number": "649062", "timestamp": "2020-09-19 11:17:00 UTC", "reward_addresses": "0000000000000000000000000000000000000000", "creator": "TEST2", "mapping_method": "known_identifiers"},' \
                  '{"number": "649061", "timestamp": "2020-09-19 11:17:15 UTC", "reward_addresses": "12dRugNcdxK39288NjcDV4GX7rMsKCGn6B", "creator": "Bitmain", "mapping_method": "known_legal_links"},' \
                  '{"number": "649064", "timestamp": "2020-09-20 11:17:00 UTC", "reward_addresses": "0000000000000000000000000000000000000000", "creator": "TEST2", "mapping_method": "known_identifiers"},' \
                  '{"number": "682736", "timestamp": "2021-05-09 11:12:32 UTC", "reward_addresses": "18cBEMRxXHqzWWCxZNtU91F5sbUNKhL5PX", "creator": "ViaBTC", "mapping_method": "known_identifiers"}' \
                  ']'
    with open(test_bitcoin_dir / 'mapped_data.json', 'w') as f:
        f.write(mapped_data)
    return json.loads(mapped_data)


@pytest.fixture
def mock_sample_ethereum_mapped_data(setup_and_cleanup):
    test_io_dir = setup_and_cleanup
    test_ethereum_dir = test_io_dir / "sample_ethereum"
    test_ethereum_dir.mkdir(parents=True, exist_ok=True)
    # create a file that would be the output of the mapping
    mapped_data = '[' \
                  '{"number":"16382083","timestamp":"2023-01-11 07:29:47 UTC","reward_addresses":"0x3bee5122e2a2fbe11287aafb0cb918e22abb5436","creator":"MEV Builder: 0x3B...436", "mapping_method": "known_addresses"},' \
                  '{"number":"11184490","timestamp":"2020-11-03 13:33:18 UTC","reward_addresses":"0x45133a7e1cc7e18555ae8a4ee632a8a61de90df6","creator":"0x45133a7e1cc7e18555ae8a4ee632a8a61de90df6", "mapping_method": "fallback_mapping"},' \
                  '{"number":"11183739","timestamp":"2020-11-03 10:44:14 UTC","reward_addresses":"0xe9b54a47e3f401d37798fc4e22f14b78475c2afc","creator":"TEST2", "mapping_method": "known_identifiers"},' \
                  '{"number":"11185799","timestamp":"2020-11-03 18:34:11 UTC","reward_addresses":"0xe9b54a47e3f401d37798fc4e22f14b78475c2afc","creator":"TEST2", "mapping_method": "known_identifiers"},' \
                  '{"number":"11186643","timestamp":"2020-11-03 21:33:27 UTC","reward_addresses":"0xe9b54a47e3f401d37798fc4e22f14b78475c2afc","creator":"TEST2", "mapping_method": "known_identifiers"},' \
                  '{"number":"11183702","timestamp":"2020-11-03 10:37:32 UTC","reward_addresses":"0xe9b54a47e3f401d37798fc4e22f14b78475c2afc","creator":"TEST2", "mapping_method": "known_identifiers"},' \
                  '{"number":"11181062","timestamp":"2020-11-03 00:56:48 UTC","reward_addresses":"0xe9b54a47e3f401d37798fc4e22f14b78475c2afc","creator":"TEST2", "mapping_method": "known_identifiers"},' \
                  '{"number":"11183969","timestamp":"2020-11-03 11:33:44 UTC","reward_addresses":"0x8595dd9e0438640b5e1254f9df579ac12a86865f","creator":"TEST", "mapping_method": "known_identifiers"},' \
                  '{"number":"11184329","timestamp":"2020-11-03 12:56:41 UTC","reward_addresses":"0x8595dd9e0438640b5e1254f9df579ac12a86865f","creator":"TEST", "mapping_method": "known_identifiers"},' \
                  '{"number":"11183793","timestamp":"2020-11-03 10:56:07 UTC","reward_addresses":"0x8595dd9e0438640b5e1254f9df579ac12a86865f","creator":"TEST", "mapping_method": "known_identifiers"}' \
                  ']'
    with open(test_ethereum_dir / 'mapped_data.json', 'w') as f:
        f.write(mapped_data)


@pytest.fixture
def mock_sample_cardano_mapped_data(setup_and_cleanup):
    test_io_dir = setup_and_cleanup
    test_cardano_dir = test_io_dir / "sample_cardano"
    test_cardano_dir.mkdir(parents=True, exist_ok=True)
    # create a file that would be the output of the mapping
    mapped_data = '[' \
                  '{"number":"17809932","timestamp":"2020-12-31T00:57:03","reward_addresses":"e7b605b72af41d6e8e6894274dedd18114f1759fea500b6d07031535","creator":"CFLOW", "mapping_method": "known_identifiers"},' \
                  '{"number":"66666666666","timestamp":"2020-12-31T04:42:01","reward_addresses":"1d8988c2057d6efd6a094e468840a51942ab03b5b69b07a2bca71b53","creator":"1d8988c2057d6efd6a094e468840a51942ab03b5b69b07a2bca71b53", "mapping_method": "fallback_mapping"},' \
                  '{"number":"00000000001","timestamp":"2020-12-31T06:00:00", "creator":"Input Output (iohk.io)", "mapping_method": "known_addresses"},' \
                  '{"number":"00000000000","timestamp":"2020-12-31T06:42:00","creator":"Arrakis", "mapping_method": "known_identifiers"},' \
                  '{"number":"55555555555","timestamp":"2020-12-31T06:42:01","creator":"1percentpool", "mapping_method": "known_identifiers"}' \
                  ']'
    with open(test_cardano_dir / 'mapped_data.json', 'w') as f:
        f.write(mapped_data)


@pytest.fixture
def mock_sample_tezos_mapped_data(setup_and_cleanup):
    test_io_dir = setup_and_cleanup
    test_tezos_dir = test_io_dir / "sample_tezos"
    test_tezos_dir.mkdir(parents=True, exist_ok=True)
    # create a file that would be the output of the mapping
    mapped_data = '[' \
                  '{"number": "0000000", "timestamp": "2018-08-30 00:36:18 UTC", "reward_addresses": "tz0000000000000000000000000000000000", "creator": "tz0000000000000000000000000000000000", "mapping_method": "fallback_mapping"},' \
                  '{"number": "1649812", "timestamp": "2021-08-30 00:36:18 UTC", "reward_addresses": "tz1Kf25fX1VdmYGSEzwFy1wNmkbSEZ2V83sY", "creator": "Tezos Seoul", "mapping_method": "known_addresses"},' \
                  '{"number": "1649839", "timestamp": "2021-08-30 00:49:48 UTC", "reward_addresses": "tz1Kt4P8BCaP93AEV4eA7gmpRryWt5hznjCP", "creator": "tz1Kt4P8BCaP93AEV4eA7gmpRryWt5hznjCP", "mapping_method": "fallback_mapping"},' \
                  '{"number": "1650309", "timestamp": "2021-08-30 04:49:28 UTC", "reward_addresses": "tz1Kf25fX1VdmYGSEzwFy1wNmkbSEZ2V83sY", "creator": "Tezos Seoul", "mapping_method": "known_addresses"},' \
                  '{"number": "1650474", "timestamp": "2021-08-30 06:11:58 UTC", "reward_addresses": "tz1Vd1rXpV8hTHbFXCXN3c3qzCsgcU5BZw1e", "creator": "TEST", "mapping_method": "known_addresses"},' \
                  '{"number": "1651794", "timestamp": "2021-08-30 17:41:08 UTC", "reward_addresses": "None", "creator": "----- UNDEFINED BLOCK PRODUCER -----", "mapping_method": "fallback_mapping"}' \
                  ']'
    with open(test_tezos_dir / 'mapped_data.json', 'w') as f:
        f.write(mapped_data)


def test_aggregate(setup_and_cleanup, mock_sample_bitcoin_mapped_data):
    test_io_dir = setup_and_cleanup

    timeframe = (datetime.date(2010, 1, 1), datetime.date(2010, 12, 31))
    aggregate(project='sample_bitcoin', output_dir=test_io_dir, timeframe=timeframe, estimation_window=31,
                  frequency=31, force_aggregate=True)

    output_file = test_io_dir / ('sample_bitcoin/blocks_per_entity/31_day_window_from_2010-01-01_to_2010-12'
                                 '-31_sampled_every_31_days.csv')
    assert output_file.is_file()  # there is no data from 2010 in the sample but the aggregator still creates the file when called with this timeframe

    timeframe = (datetime.date(2018, 2, 1), datetime.date(2018, 2, 28))
    # an error should be raised in this case because the estimation window is larger than the timeframe
    with pytest.raises(ValueError):
        aggregate(project='sample_bitcoin', output_dir=test_io_dir, timeframe=timeframe, estimation_window=30, frequency=30,
                  force_aggregate=True)

    output_file = test_io_dir / 'sample_bitcoin/blocks_per_entity/30_day_window_from_2018-02-01_to_2018-02-28_sampled_every_30_days.csv'
    assert not output_file.is_file()

    timeframe = (datetime.date(2018, 3, 1), datetime.date(2018, 3, 31))
    aggregate(project='sample_bitcoin', output_dir=test_io_dir, timeframe=timeframe, estimation_window=31, frequency=31,
              force_aggregate=True)
    output_file = test_io_dir / ('sample_bitcoin/blocks_per_entity/31_day_window_from_2018-03-01_to_2018-03'
                                 '-31_sampled_every_31_days.csv')
    assert output_file.is_file()

    timeframe = (datetime.date(2021, 1, 1), datetime.date(2021, 12, 31))
    aggregate(project='sample_bitcoin', output_dir=test_io_dir, timeframe=timeframe, estimation_window=31, frequency=31,
              force_aggregate=True)
    output_file = test_io_dir / ('sample_bitcoin/blocks_per_entity/31_day_window_from_2021-01-01_to_2021-12'
                                 '-31_sampled_every_31_days.csv')
    assert output_file.is_file()


def test_aggregate_method(setup_and_cleanup, mock_sample_bitcoin_mapped_data):
    aggregator = Aggregator(project='sample_bitcoin', io_dir=setup_and_cleanup / 'sample_bitcoin')

    blocks_per_entity = aggregator.aggregate(datetime.date(2018, 2, 1), datetime.date(2018, 2, 28))
    assert sum(blocks_per_entity.values()) == 8

    blocks_per_entity = aggregator.aggregate(datetime.date(2020, 9, 19), datetime.date(2020, 9, 19))
    assert sum(blocks_per_entity.values()) == 2

    blocks_per_entity = aggregator.aggregate(datetime.date(2021, 1, 1), datetime.date(2021, 12, 31))
    assert sum(blocks_per_entity.values()) == 1

    blocks_per_entity = aggregator.aggregate(datetime.date(2023, 1, 1), datetime.date(2023, 12, 31))
    assert sum(blocks_per_entity.values()) == 0


def test_bitcoin_aggregation(setup_and_cleanup, mock_sample_bitcoin_mapped_data):
    test_io_dir = setup_and_cleanup

    aggregate(
        project='sample_bitcoin',
        output_dir=test_io_dir,
        timeframe=(datetime.date(2018, 2, 1), datetime.date(2018, 3, 2)),
        estimation_window=30,
        frequency=30,
        force_aggregate=True
    )

    expected_output = {
        'Entity \\ Date': '2018-02-15\n',
        '1AM2f...9pJUx/3G7y1...gPPWb': '4\n',
        'BTC.TOP': '2\n',
        'GBMiners': '2\n'
    }

    output_file = test_io_dir / ('sample_bitcoin/blocks_per_entity/30_day_window_from_2018-02-01_to_2018-03'
                                 '-02_sampled_every_30_days.csv')
    with open(output_file) as f:
        for line in f.readlines():
            col_1, col_2 = line.split(',')
            assert col_2 == expected_output[col_1]

    aggregate(
        project='sample_bitcoin',
        output_dir=test_io_dir,
        timeframe=(datetime.date(2020, 1, 1), datetime.date(2020, 12, 31)),
        estimation_window=None,
        frequency=None,
        force_aggregate=True
    )

    expected_output = {
        'Entity \\ Date': '2020-07-01\n',
        'TEST2': '2\n',
        'Bitmain': '1\n'
    }

    output_file = test_io_dir / ('sample_bitcoin/blocks_per_entity/all_from_2020-01-01_to_2020-12-31.csv')
    with open(output_file) as f:
        for line in f.readlines():
            col_1, col_2 = line.split(',')
            assert col_2 == expected_output[col_1]


def test_ethereum_aggregation(setup_and_cleanup, mock_sample_ethereum_mapped_data):
    test_io_dir = setup_and_cleanup

    aggregate(
        project='sample_ethereum',
        output_dir=test_io_dir,
        timeframe=(datetime.date(2020, 11, 1), datetime.date(2020, 11, 30)),
        estimation_window=30,
        frequency=30,
        force_aggregate=True
    )

    expected_output = {
        'Entity \\ Date': '2020-11-15\n',
        'TEST2': '5\n',
        'TEST': '3\n',
        '0x45133a7e1cc7e18555ae8a4ee632a8a61de90df6': '1\n'
    }

    output_file = test_io_dir / ('sample_ethereum/blocks_per_entity/30_day_window_from_2020-11-01_to_2020-11'
                                 '-30_sampled_every_30_days.csv')
    with open(output_file) as f:
        for line in f.readlines():
            col_1, col_2 = line.split(',')
            assert col_2 == expected_output[col_1]

    aggregate(
        project='sample_ethereum',
        output_dir=test_io_dir,
        timeframe=(datetime.date(2023, 1, 1), datetime.date(2023, 12, 31)),
        estimation_window=365,
        frequency=365,
        force_aggregate=True
    )

    expected_output = {
        'Entity \\ Date': '2023-07-02\n',
        'MEV Builder: 0x3B...436': '1\n'
    }

    output_file = test_io_dir / ('sample_ethereum/blocks_per_entity/365_day_window_from_2023-01-01_to_2023-12'
                                 '-31_sampled_every_365_days.csv')
    with open(output_file) as f:
        for line in f.readlines():
            col_1, col_2 = line.split(',')
            assert col_2 == expected_output[col_1]


def test_cardano_aggregation(setup_and_cleanup, mock_sample_cardano_mapped_data):
    test_io_dir = setup_and_cleanup

    aggregate(
        project='sample_cardano',
        output_dir=test_io_dir,
        timeframe=(datetime.date(2020, 12, 1), datetime.date(2020, 12, 31)),
        estimation_window=31,
        frequency=31,
        force_aggregate=True
    )

    expected_output = {
        'Entity \\ Date': '2020-12-16\n',
        'CFLOW': '1\n',
        '1d8988c2057d6efd6a094e468840a51942ab03b5b69b07a2bca71b53': '1\n',
        'Input Output (iohk.io)': '1\n',
        'Arrakis': '1\n',
        '1percentpool': '1\n'
    }

    output_file = test_io_dir / ('sample_cardano/blocks_per_entity/31_day_window_from_2020-12-01_to_2020-12'
                                 '-31_sampled_every_31_days.csv')
    with open(output_file) as f:
        for line in f.readlines():
            col_1, col_2 = line.split(',')
            assert col_2 == expected_output[col_1]


def test_tezos_aggregation(setup_and_cleanup, mock_sample_tezos_mapped_data):
    test_io_dir = setup_and_cleanup

    aggregate(
        project='sample_tezos',
        output_dir=test_io_dir,
        timeframe=(datetime.date(2021, 8, 1), datetime.date(2021, 8, 31)),
        estimation_window=31,
        frequency=31,
        force_aggregate=True
    )

    expected_output = {
        'Entity \\ Date': '2021-08-16\n',
        'Tezos Seoul': '2\n',
        'tz1Kt4P8BCaP93AEV4eA7gmpRryWt5hznjCP': '1\n',
        'TEST': '1\n',
        '----- UNDEFINED BLOCK PRODUCER -----': '1\n'
    }

    output_file = test_io_dir / ('sample_tezos/blocks_per_entity/31_day_window_from_2021-08-01_to_2021-08'
                                 '-31_sampled_every_31_days.csv')
    with open(output_file) as f:
        for line in f.readlines():
            col_1, col_2 = line.split(',')
            assert col_2 == expected_output[col_1]

    aggregate(
        project='sample_tezos',
        output_dir=test_io_dir,
        timeframe=(datetime.date(2018, 1, 1), datetime.date(2018, 12, 31)),
        estimation_window=365,
        frequency=365,
        force_aggregate=True
    )

    expected_output = {
        'Entity \\ Date': '2018-07-02\n',
        'tz0000000000000000000000000000000000': '1\n'
    }

    output_file = test_io_dir / ('sample_tezos/blocks_per_entity/365_day_window_from_2018-01-01_to_2018-12'
                                 '-31_sampled_every_365_days.csv')
    with open(output_file) as f:
        for line in f.readlines():
            col_1, col_2 = line.split(',')
            assert col_2 == expected_output[col_1]


def test_divide_timeframe():
    time_chunks = divide_timeframe(timeframe=(datetime.date(2022, 2, 1), datetime.date(2022, 3, 1)),
                                   estimation_window=1, frequency=1)
    assert len(time_chunks) == 29
    assert time_chunks[-1][0] == datetime.date(2022, 3, 1)
    assert time_chunks[-1][-1] == datetime.date(2022, 3, 1)

    time_chunks = divide_timeframe(timeframe=(datetime.date(2022, 1, 1), datetime.date(2022, 1, 31)), estimation_window=7, frequency=7)
    assert len(time_chunks) == 4
    assert time_chunks[-1][-1] == datetime.date(2022, 1, 28)

    time_chunks = divide_timeframe(timeframe=(datetime.date(2022, 2, 1), datetime.date(2022, 3, 1)), estimation_window=30, frequency=30)
    assert len(time_chunks) == 0

    time_chunks = divide_timeframe(timeframe=(datetime.date(2022, 1, 31), datetime.date(2023, 1, 2)), estimation_window=30, frequency=30)
    assert len(time_chunks) == 11
    assert time_chunks[-1][-1] == datetime.date(2022, 12, 26)

    time_chunks = divide_timeframe(timeframe=(datetime.date(2022, 2, 1), datetime.date(2022, 2, 1)), estimation_window=30, frequency=30)
    assert len(time_chunks) == 0

    time_chunks = divide_timeframe(timeframe=(datetime.date(2018, 1, 16), datetime.date(2023, 3, 30)), estimation_window=365, frequency=365)
    assert len(time_chunks) == 5
    assert time_chunks[-1][-1] == datetime.date(2023, 1, 14)

    # test sliding windows by using a frequency that is smaller than the estimation window
    time_chunks = divide_timeframe(timeframe=(datetime.date(2022, 1, 1), datetime.date(2022, 1, 31)), estimation_window=7, frequency=1)
    assert len(time_chunks) == 25
    assert time_chunks[-1][-1] == datetime.date(2022, 1, 31)

    time_chunks = divide_timeframe(timeframe=(datetime.date(2022, 1, 1), datetime.date(2022, 1, 31)),
                                   estimation_window=7, frequency=3)
    assert len(time_chunks) == 9
    assert time_chunks[-1][-1] == datetime.date(2022, 1, 31)

    # test using the entire timeframe by having estimation window and frequency set to None
    time_chunks = divide_timeframe(timeframe=(datetime.date(2022, 1, 1), datetime.date(2022, 1, 31)), estimation_window=None, frequency=None)
    assert len(time_chunks) == 1
    assert time_chunks[0][0] == datetime.date(2022, 1, 1)
    assert time_chunks[0][-1] == datetime.date(2022, 1, 31)
