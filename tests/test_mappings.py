import pathlib
import pytest
import shutil
import os
import json
from consensus_decentralization.parse import parse, ledger_parser
from consensus_decentralization.parsers.default_parser import DefaultParser
from consensus_decentralization.parsers.dummy_parser import DummyParser
from consensus_decentralization.parsers.ethereum_parser import EthereumParser
from consensus_decentralization.map import apply_mapping, ledger_mapping
from consensus_decentralization.mappings.default_mapping import DefaultMapping
from consensus_decentralization.mappings.ethereum_mapping import EthereumMapping
from consensus_decentralization.mappings.cardano_mapping import CardanoMapping
from consensus_decentralization.mappings.tezos_mapping import TezosMapping
from consensus_decentralization.helper import RAW_DATA_DIR, OUTPUT_DIR


@pytest.fixture
def setup_and_cleanup():
    """
    This function can be used to set up the right conditions for a test and also clean up after the test is finished.
    The part before the yield command is run before the test (setup) and the part after the yield command is run
    after (cleanup)
    """
    # Set up
    ledger_mapping['sample_bitcoin'] = DefaultMapping
    ledger_parser['sample_bitcoin'] = DefaultParser
    ledger_mapping['sample_ethereum'] = EthereumMapping
    ledger_parser['sample_ethereum'] = EthereumParser
    ledger_mapping['sample_cardano'] = CardanoMapping
    ledger_parser['sample_cardano'] = DummyParser
    ledger_mapping['sample_tezos'] = TezosMapping
    ledger_parser['sample_tezos'] = DummyParser
    test_raw_data_dir = RAW_DATA_DIR
    test_output_dir = OUTPUT_DIR / "test_output"
    mapping_info_dir = pathlib.Path(__file__).resolve().parent.parent / 'mapping_information'
    yield mapping_info_dir, test_raw_data_dir, test_output_dir
    # Clean up
    shutil.rmtree(test_output_dir)


@pytest.fixture
def prep_sample_bitcoin_mapping_info():
    mapping_info_dir = pathlib.Path(__file__).resolve().parent.parent / 'mapping_information'
    # Create temp mapping info files for sample project
    shutil.copy2(str(mapping_info_dir / 'addresses/bitcoin.json'),
                 str(mapping_info_dir / 'addresses/sample_bitcoin.json'))
    shutil.copy2(str(mapping_info_dir / 'identifiers/bitcoin.json'),
                 str(mapping_info_dir / 'identifiers/sample_bitcoin.json'))
    yield
    # Remove temp mapping info files
    os.remove(str(mapping_info_dir / 'addresses/sample_bitcoin.json'))
    os.remove(str(mapping_info_dir / 'identifiers/sample_bitcoin.json'))


@pytest.fixture
def prep_sample_ethereum_mapping_info():
    mapping_info_dir = pathlib.Path(__file__).resolve().parent.parent / 'mapping_information'
    # Create temp mapping info files for sample project
    shutil.copy2(mapping_info_dir / 'addresses/ethereum.json', mapping_info_dir / 'addresses/sample_ethereum.json')
    shutil.copy2(mapping_info_dir / 'identifiers/ethereum.json', mapping_info_dir / 'identifiers/sample_ethereum.json')
    yield
    # Remove temp mapping info files
    os.remove(mapping_info_dir / 'clusters/sample_ethereum.json')
    os.remove(mapping_info_dir / 'addresses/sample_ethereum.json')
    os.remove(mapping_info_dir / 'identifiers/sample_ethereum.json')


@pytest.fixture
def prep_sample_cardano_mapping_info():
    mapping_info_dir = pathlib.Path(__file__).resolve().parent.parent / 'mapping_information'
    # Create temp mapping info files for sample project
    shutil.copy2(mapping_info_dir / 'clusters/cardano.json', mapping_info_dir / 'clusters/sample_cardano.json')
    shutil.copy2(mapping_info_dir / 'identifiers/cardano.json', mapping_info_dir / 'identifiers/sample_cardano.json')
    yield
    # Remove temp mapping info files
    os.remove(mapping_info_dir / 'clusters/sample_cardano.json')
    os.remove(mapping_info_dir / 'identifiers/sample_cardano.json')


@pytest.fixture
def prep_sample_tezos_mapping_info():
    mapping_info_dir = pathlib.Path(__file__).resolve().parent.parent / 'mapping_information'
    # Create temp mapping info files for sample project
    shutil.copy2(mapping_info_dir / 'addresses/tezos.json', mapping_info_dir / 'addresses/sample_tezos.json')
    yield
    # Remove temp mapping info files
    os.remove(str(mapping_info_dir / 'clusters/sample_tezos.json'))
    os.remove(str(mapping_info_dir / 'addresses/sample_tezos.json'))


def test_map(setup_and_cleanup, prep_sample_bitcoin_mapping_info):
    mapping_info_dir, test_raw_data_dir, test_output_dir = setup_and_cleanup

    parse('sample_bitcoin', test_raw_data_dir, test_output_dir)
    apply_mapping('sample_bitcoin', test_output_dir, force_map=True)

    mapped_data_file = test_output_dir / 'sample_bitcoin/mapped_data.json'
    assert mapped_data_file.is_file()


def test_bitcoin_mapping(setup_and_cleanup, prep_sample_bitcoin_mapping_info):
    mapping_info_dir, test_raw_data_dir, test_output_dir = setup_and_cleanup
    with open(mapping_info_dir / 'addresses/sample_bitcoin.json') as f:
        pool_addresses = json.load(f)
    pool_addresses['0000000000000000000000000000000000000000'] = {'name': 'TEST2', 'source': ''}
    with open(mapping_info_dir / 'addresses/sample_bitcoin.json', 'w') as f:
        f.write(json.dumps(pool_addresses))

    parse('sample_bitcoin', test_raw_data_dir, test_output_dir)
    apply_mapping('sample_bitcoin', test_output_dir, force_map=True)

    expected_block_creators = {
        '507715': 'GBMiners',
        '511342': 'GBMiners',
        '510888': 'BTC.TOP',
        '649064': 'TEST2'
    }
    expected_mapping_methods = {
        '507715': 'known_identifiers',
        '511342': 'known_identifiers',
        '510888': 'known_identifiers',
        '649064': 'known_addresses'
    }
    with open(test_output_dir / 'sample_bitcoin/mapped_data.json') as f:
        mapped_data = json.load(f)
    for block in mapped_data:
        if block['number'] in expected_block_creators:
            assert block['creator'] == expected_block_creators[block['number']]
            assert block['mapping_method'] == expected_mapping_methods[block['number']]


def test_ethereum_mapping(setup_and_cleanup, prep_sample_ethereum_mapping_info):
    mapping_info_dir, test_raw_data_dir, test_output_dir = setup_and_cleanup

    clusters = {'TEST': [{'name': 'ezil.me', 'from': '', 'to': '', 'source': 'homepage'}]}
    with open(mapping_info_dir / 'clusters/sample_ethereum.json', 'w') as f:
        f.write(json.dumps(clusters))
    with open(mapping_info_dir / 'addresses/sample_ethereum.json') as f:
        addresses = json.load(f)
    addresses['0xe9b54a47e3f401d37798fc4e22f14b78475c2afc'] = {'name': 'TEST2', 'source': ''}
    with open(mapping_info_dir / 'addresses/sample_ethereum.json', 'w') as f:
        f.write(json.dumps(addresses))

    parse('sample_ethereum', test_raw_data_dir, test_output_dir)
    apply_mapping('sample_ethereum', test_output_dir, force_map=True)

    expected_block_creators = {
        '16382083': 'MEV Builder: 0x3B...436',
        '11184490': '0x45133a7e1cc7e18555ae8a4ee632a8a61de90df6',
        '11183702': 'TEST2',
        '11183793': 'TEST'
    }
    expected_mapping_methods = {
        '16382083': 'known_addresses',
        '11184490': 'known_addresses',
        '11183702': 'known_addresses',
        '11183793': 'known_pool_links'
    }

    with open(test_output_dir / 'sample_ethereum/mapped_data.json') as f:
        mapped_data = json.load(f)
    for block in mapped_data:
        if block['number'] in expected_block_creators:
            assert block['creator'] == expected_block_creators[block['number']]
            assert block['mapping_method'] == expected_mapping_methods[block['number']]


def test_cardano_mapping(setup_and_cleanup, prep_sample_cardano_mapping_info):
    mapping_info_dir, test_raw_data_dir, test_output_dir = setup_and_cleanup

    parse('sample_cardano', test_raw_data_dir, test_output_dir)
    apply_mapping('sample_cardano', test_output_dir, force_map=True)

    expected_block_creators = {
        '17809932': 'CFLOW',
        '66666666666': '1d8988c2057d6efd6a094e468840a51942ab03b5b69b07a2bca71b53',
        '00000000001': 'Input Output (iohk.io)'
    }
    expected_mapping_methods = {
        '17809932': 'known_identifiers',
        '66666666666': 'known_addresses',
        '00000000001': 'known_addresses'
    }
    with open(test_output_dir / 'sample_cardano/mapped_data.json') as f:
        mapped_data = json.load(f)
    for block in mapped_data:
        if block['number'] in expected_block_creators:
            assert block['creator'] == expected_block_creators[block['number']]
            assert block['mapping_method'] == expected_mapping_methods[block['number']]


def test_tezos_mapping(setup_and_cleanup, prep_sample_tezos_mapping_info):
    mapping_info_dir, test_raw_data_dir, test_output_dir = setup_and_cleanup
    clusters = {'TEST': [{'name': 'TzNode', 'from': '2021', 'to': '2022', 'source': 'homepage'}]}
    with open(mapping_info_dir / 'clusters/sample_tezos.json', 'w') as f:
        f.write(json.dumps(clusters))

    parse('sample_tezos', test_raw_data_dir, test_output_dir)
    apply_mapping('sample_tezos', test_output_dir, force_map=True)

    expected_block_creators = {
        '1649812': 'Tezos Seoul',
        '1650474': 'TEST',
        '1651794': '----- UNDEFINED MINER -----',
        '0000000': 'tz0000000000000000000000000000000000'
    }
    expected_mapping_methods = {
        '1649812': 'known_addresses',
        '1650474': 'known_pool_links',
        '1651794': 'known_addresses',
        '0000000': 'known_addresses'
    }
    with open(test_output_dir / 'sample_tezos/mapped_data.json') as f:
        mapped_data = json.load(f)
    for block in mapped_data:
        if block['number'] in expected_block_creators:
            assert block['creator'] == expected_block_creators[block['number']]
            assert block['mapping_method'] == expected_mapping_methods[block['number']]


def test_get_reward_addresses():
    default_mapping = DefaultMapping("sample_bitcoin", io_dir=pathlib.Path(), data_to_map=None)

    block = {
        "number": 625113,
        "timestamp": "2020-04-09 10:48:38+00:00",
        "identifiers": "b'\\x03\\xd9\\x89\\t\\x04\\x89\\xfd\\x8e^/poolin.com/\\xfa\\xbemmL\\xd6\\xe82[\\xc7}\\x07\\x89\\xe5\\xbf.\\xdb\\xed\\xac\\xfd\\xff\\xe6\\xff\\x8a\\t\\xccQ\\xb8\\x11\\x97\\xea\\xae\\t\\xea\\xd3_\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\xb1\\xe3t\\xf7\\xaf\\xa4\\xcf\\x81\\x8c&\\xdf\\xd6s9\\x19o\\x12\\xf3t\\x1b`\\x00\\xbb\\x0bC\\x00\\xff\\xff\\xff\\xff'",
        "reward_addresses": "3HqH1qGAqNWPpbrvyGjnRxNEjcUKD4e6ea"
    }
    reward_addresses = default_mapping.get_reward_addresses(block)
    assert reward_addresses == ['3HqH1qGAqNWPpbrvyGjnRxNEjcUKD4e6ea']

    block = {"number": -1, "timestamp": "2023-08-07 10:34:38+00:00", "identifiers": "b'mined by Lady X'",
             "reward_addresses": "hello1,hello2,hello3"}
    default_mapping.special_addresses.add("hello2")
    reward_addresses = default_mapping.get_reward_addresses(block)
    assert reward_addresses == ["hello1", "hello3"] or reward_addresses == ["hello3", "hello1"]

    block = {
        "number": -2,
        "timestamp": "2023-08-07 17:52:38+00:00",
        "identifiers": "b'mined by Lady X'",
        "reward_addresses": "hello2"
    }
    reward_addresses = default_mapping.get_reward_addresses(block)
    assert reward_addresses == []

    block = {
        "number": -3,
        "timestamp": "2023-08-07 17:53:38+00:00",
        "identifiers": "b'mined by Lady X'",
        "reward_addresses": None
    }
    reward_addresses = default_mapping.get_reward_addresses(block)
    assert reward_addresses is None

    eth_mapping = EthereumMapping("sample_ethereum", io_dir=pathlib.Path(), data_to_map=None)
    block = {
        "number": 6982695,
        "timestamp": "2018-12-31 00:00:12+00:00",
        "reward_addresses": "0x5a0b54d5dc17e0aadc383d2db43b0a0d3e029c4c",
        "identifiers": "sparkpool-eth-cn-hz2"
    }
    reward_addresses = eth_mapping.get_reward_addresses(block)
    assert reward_addresses == ["0x5a0b54d5dc17e0aadc383d2db43b0a0d3e029c4c"]


def test_from_known_addresses():
    cardano_mapping = CardanoMapping("sample_cardano", io_dir=pathlib.Path(), data_to_map=None)

    block = {
        "number": 92082690,
        "identifiers": "WAV7",
        "timestamp": "2023-05-09 16:16:21",
        "reward_addresses": "e14a650c7a58d229bbb663cb42fffb36d68c2a6cecf0fd7b9c47e399"
    }
    entity = cardano_mapping.map_from_known_addresses(block)
    assert entity == "e14a650c7a58d229bbb663cb42fffb36d68c2a6cecf0fd7b9c47e399"

    block = {
        "number": -1,
        "identifiers": "bla",
        "timestamp": "2023-08-10 16:16:21",
        "reward_addresses": ""
    }
    entity = cardano_mapping.map_from_known_addresses(block)
    assert entity == "Input Output (iohk.io)"

    cardano_mapping.special_addresses.add('very special address')
    block = {
        "number": -2,
        "identifiers": "spcl",
        "timestamp": "2023-08-10 17:16:21",
        "reward_addresses": "very special address"
    }
    entity = cardano_mapping.map_from_known_addresses(block)
    assert entity == "----- SPECIAL ADDRESS -----"
