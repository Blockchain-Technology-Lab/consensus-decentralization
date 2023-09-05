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
    mapping_info_dir = pathlib.Path(__file__).resolve().parent.parent / 'mapping_information'  # todo better to have separate helper files for the tests s.t. the tests don't break just because the info changes
    test_raw_data_dir = RAW_DATA_DIR
    test_output_dir = OUTPUT_DIR / "test_output"
    yield mapping_info_dir, test_raw_data_dir, test_output_dir
    # Clean up
    shutil.rmtree(test_output_dir)


def test_map(setup_and_cleanup):
    pool_info_dir, test_raw_data_dir, test_output_dir = setup_and_cleanup
    project = 'sample_bitcoin'

    try:
        shutil.copy2(str(pool_info_dir / 'clusters/bitcoin.json'),
                     str(pool_info_dir / f'clusters/{project}.json'))  # Create a temp pool info file for sample
    except FileNotFoundError:
        pass

    try:
        shutil.copy2(str(pool_info_dir / 'addresses/bitcoin.json'),
                     str(pool_info_dir / f'addresses/{project}.json'))  # Create a temp pool info file for sample
    except FileNotFoundError:
        pass

    try:
        shutil.copy2(str(pool_info_dir / 'identifiers/bitcoin.json'),
                     str(pool_info_dir / f'identifiers/{project}.json'))  # Create a temp pool info file for sample
    except FileNotFoundError:
        pass

    parse(project, test_raw_data_dir, test_output_dir)
    apply_mapping(project, test_output_dir, force_map=True)

    mapped_data_file = test_output_dir / project / 'mapped_data.json'
    assert mapped_data_file.is_file()

    try:
        os.remove(str(pool_info_dir / f'clusters/{project}.json'))  # Remove temp pool info file
    except FileNotFoundError:
        pass
    try:
        os.remove(str(pool_info_dir / f'addresses/{project}.json'))  # Remove temp pool info file
    except FileNotFoundError:
        pass
    try:
        os.remove(str(pool_info_dir / f'identifiers/{project}.json'))  # Remove temp pool info file
    except FileNotFoundError:
        pass


def test_bitcoin_mapping(setup_and_cleanup):
    pool_info_dir, test_raw_data_dir, test_output_dir = setup_and_cleanup
    project = 'sample_bitcoin'

    try:
        shutil.copy2(str(pool_info_dir / 'clusters/bitcoin.json'),
                     str(pool_info_dir / f'clusters/{project}.json'))  # Create a temp pool info file for sample
    except FileNotFoundError:
        pass

    try:
        shutil.copy2(str(pool_info_dir / 'addresses/bitcoin.json'),
                     str(pool_info_dir / f'addresses/{project}.json'))  # Create a temp pool info file for sample
    except FileNotFoundError:
        pass

    try:
        shutil.copy2(str(pool_info_dir / 'identifiers/bitcoin.json'),
                     str(pool_info_dir / f'identifiers/{project}.json'))  # Create a temp pool info file for sample
    except FileNotFoundError:
        pass

    try:
        with open(str(pool_info_dir / f'addresses/{project}.json')) as f:
            pool_addresses = json.load(f)
    except FileNotFoundError:
        pool_addresses = {}
    pool_addresses['0000000000000000000000000000000000000000'] = {'name': 'TEST2', 'source': ''}
    with open(str(pool_info_dir / f'addresses/{project}.json'), 'w') as f:
        f.write(json.dumps(pool_addresses))

    parse(project, test_raw_data_dir, test_output_dir)
    apply_mapping(project, test_output_dir, force_map=True)

    # todo add assertion for mapped data content

    try:
        os.remove(str(pool_info_dir / f'clusters/{project}.json'))  # Remove temp pool info file
    except FileNotFoundError:
        pass
    try:
        os.remove(str(pool_info_dir / f'addresses/{project}.json'))  # Remove temp pool info file
    except FileNotFoundError:
        pass
    try:
        os.remove(str(pool_info_dir / f'identifiers/{project}.json'))  # Remove temp pool info file
    except FileNotFoundError:
        pass


def test_ethereum_mapping(setup_and_cleanup):
    pool_info_dir, test_raw_data_dir, test_output_dir = setup_and_cleanup
    project = 'sample_ethereum'

    try:
        shutil.copy2(str(pool_info_dir / 'clusters/ethereum.json'),
                     str(pool_info_dir / f'clusters/{project}.json'))  # Create a temp pool info file for sample
    except FileNotFoundError:
        pass

    try:
        shutil.copy2(str(pool_info_dir / 'addresses/ethereum.json'),
                     str(pool_info_dir / f'addresses/{project}.json'))  # Create a temp pool info file for sample
    except FileNotFoundError:
        pass

    try:
        shutil.copy2(str(pool_info_dir / 'identifiers/ethereum.json'),
                     str(pool_info_dir / f'identifiers/{project}.json'))  # Create a temp pool info file for sample
    except FileNotFoundError:
        pass

    try:
        with open(str(pool_info_dir / f'clusters/{project}.json')) as f:
            clusters = json.load(f)
    except FileNotFoundError:
        clusters = {}
    clusters['TEST'] = [{'name': 'ezil.me', 'from': '', 'to': '', 'source': 'homepage'}]
    with open(str(pool_info_dir / f'clusters/{project}.json'), 'w') as f:
        f.write(json.dumps(clusters))

    try:
        with open(str(pool_info_dir / f'addresses/{project}.json')) as f:
            addresses = json.load(f)
    except FileNotFoundError:
        addresses = {}
    addresses['0xe9b54a47e3f401d37798fc4e22f14b78475c2afc'] = {'name': 'TEST2', 'source': ''}
    with open(str(pool_info_dir / f'addresses/{project}.json'), 'w') as f:
        f.write(json.dumps(addresses))

    parse(project, test_raw_data_dir, test_output_dir)
    apply_mapping(project, test_output_dir, force_map=True)

    # todo add assertion for mapped data content

    try:
        os.remove(str(pool_info_dir / f'clusters/{project}.json'))  # Remove temp pool info file
    except FileNotFoundError:
        pass
    try:
        os.remove(str(pool_info_dir / f'addresses/{project}.json'))  # Remove temp pool info file
    except FileNotFoundError:
        pass
    try:
        os.remove(str(pool_info_dir / f'identifiers/{project}.json'))  # Remove temp pool info file
    except FileNotFoundError:
        pass


def test_cardano_mapping(setup_and_cleanup):
    pool_info_dir, test_raw_data_dir, test_output_dir = setup_and_cleanup
    project = 'sample_cardano'

    try:
        shutil.copy2(str(pool_info_dir / 'clusters/cardano.json'),
                     str(pool_info_dir / f'clusters/{project}.json'))  # Create a temp pool info file for sample
    except FileNotFoundError:
        pass

    try:
        shutil.copy2(str(pool_info_dir / 'addresses/cardano.json'),
                     str(pool_info_dir / f'addresses/{project}.json'))  # Create a temp pool info file for sample
    except FileNotFoundError:
        pass

    try:
        shutil.copy2(str(pool_info_dir / 'identifiers/cardano.json'),
                     str(pool_info_dir / f'identifiers/{project}.json'))  # Create a temp pool info file for sample
    except FileNotFoundError:
        pass

    ledger_mapping[project] = CardanoMapping
    ledger_parser[project] = DummyParser

    parse(project, test_raw_data_dir, test_output_dir)
    apply_mapping(project, test_output_dir, force_map=True)

    # todo add assertion for mapped data content

    try:
        os.remove(str(pool_info_dir / f'clusters/{project}.json'))  # Remove temp pool info file
    except FileNotFoundError:
        pass
    try:
        os.remove(str(pool_info_dir / f'addresses/{project}.json'))  # Remove temp pool info file
    except FileNotFoundError:
        pass
    try:
        os.remove(str(pool_info_dir / f'identifiers/{project}.json'))  # Remove temp pool info file
    except FileNotFoundError:
        pass


def test_tezos_mapping(setup_and_cleanup):
    pool_info_dir, test_raw_data_dir, test_output_dir = setup_and_cleanup
    project = 'sample_tezos'

    try:
        shutil.copy2(str(pool_info_dir / 'clusters/tezos.json'),
                     str(pool_info_dir / f'clusters/{project}.json'))  # Create a temp pool info file for sample
    except FileNotFoundError:
        pass

    try:
        shutil.copy2(str(pool_info_dir / 'addresses/tezos.json'),
                     str(pool_info_dir / f'addresses/{project}.json'))  # Create a temp pool info file for sample
    except FileNotFoundError:
        pass

    try:
        shutil.copy2(str(pool_info_dir / 'identifiers/tezos.json'),
                     str(pool_info_dir / f'identifiers/{project}.json'))  # Create a temp pool info file for sample
    except FileNotFoundError:
        pass

    try:
        with open(str(pool_info_dir / f'clusters/{project}.json')) as f:
            clusters = json.load(f)
    except FileNotFoundError:
        clusters = {}
    clusters['TEST'] = [{'name': 'TzNode', 'from': '2021', 'to': '2022', 'source': 'homepage'}]
    with open(str(pool_info_dir / f'clusters/{project}.json'), 'w') as f:
        f.write(json.dumps(clusters))

    ledger_mapping[project] = TezosMapping
    ledger_parser[project] = DummyParser

    parse(project, test_raw_data_dir, test_output_dir)
    apply_mapping(project, test_output_dir, force_map=True)

    # todo add assertion for mapped data content

    try:
        os.remove(str(pool_info_dir / f'clusters/{project}.json'))  # Remove temp pool info file
    except FileNotFoundError:
        pass
    try:
        os.remove(str(pool_info_dir / f'addresses/{project}.json'))  # Remove temp pool info file
    except FileNotFoundError:
        pass
    try:
        os.remove(str(pool_info_dir / f'identifiers/{project}.json'))  # Remove temp pool info file
    except FileNotFoundError:
        pass


def test_get_reward_addresses():
    default_mapping = DefaultMapping("sample_bitcoin", io_dir=pathlib.Path(), data_to_map=None)

    block = {"number": 625113, "timestamp": "2020-04-09 10:48:38+00:00",
             "identifiers": "b'\\x03\\xd9\\x89\\t\\x04\\x89\\xfd\\x8e^/poolin.com/\\xfa\\xbemmL\\xd6\\xe82[\\xc7}\\x07\\x89\\xe5\\xbf.\\xdb\\xed\\xac\\xfd\\xff\\xe6\\xff\\x8a\\t\\xccQ\\xb8\\x11\\x97\\xea\\xae\\t\\xea\\xd3_\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\xb1\\xe3t\\xf7\\xaf\\xa4\\xcf\\x81\\x8c&\\xdf\\xd6s9\\x19o\\x12\\xf3t\\x1b`\\x00\\xbb\\x0bC\\x00\\xff\\xff\\xff\\xff'",
             "reward_addresses": "3HqH1qGAqNWPpbrvyGjnRxNEjcUKD4e6ea"}
    reward_addresses = default_mapping.get_reward_addresses(block)
    assert reward_addresses == ['3HqH1qGAqNWPpbrvyGjnRxNEjcUKD4e6ea']

    block = {"number": -1, "timestamp": "2023-08-07 10:34:38+00:00", "identifiers": "b'mined by Lady X'",
             "reward_addresses": "hello1,hello2,hello3"}
    default_mapping.special_addresses.add("hello2")
    reward_addresses = default_mapping.get_reward_addresses(block)
    assert reward_addresses == ["hello1", "hello3"] or reward_addresses == ["hello3", "hello1"]

    block = {"number": -2, "timestamp": "2023-08-07 17:52:38+00:00", "identifiers": "b'mined by Lady X'",
             "reward_addresses": "hello2"}
    reward_addresses = default_mapping.get_reward_addresses(block)
    assert reward_addresses == []

    block = {"number": -3, "timestamp": "2023-08-07 17:53:38+00:00", "identifiers": "b'mined by Lady X'",
             "reward_addresses": None}
    reward_addresses = default_mapping.get_reward_addresses(block)
    assert reward_addresses is None

    some_path = pathlib.Path()
    eth_mapping = EthereumMapping("sample_ethereum", io_dir=pathlib.Path(), data_to_map=None)
    block = {"number": 6982695, "timestamp": "2018-12-31 00:00:12+00:00",
             "reward_addresses": "0x5a0b54d5dc17e0aadc383d2db43b0a0d3e029c4c", "identifiers": "sparkpool-eth-cn-hz2"}
    reward_addresses = eth_mapping.get_reward_addresses(block)
    assert reward_addresses == ["0x5a0b54d5dc17e0aadc383d2db43b0a0d3e029c4c"]


def test_from_known_addresses():
    cardano_mapping = CardanoMapping("sample_cardano", io_dir=pathlib.Path(), data_to_map=None)

    block = {"number": 92082690, "identifiers": "WAV7", "timestamp": "2023-05-09 16:16:21",
             "reward_addresses": "e14a650c7a58d229bbb663cb42fffb36d68c2a6cecf0fd7b9c47e399"}
    entity = cardano_mapping.map_from_known_addresses(block)
    assert entity == "e14a650c7a58d229bbb663cb42fffb36d68c2a6cecf0fd7b9c47e399"

    block = {"number": -1, "identifiers": "bla", "timestamp": "2023-08-10 16:16:21", "reward_addresses": ""}
    entity = cardano_mapping.map_from_known_addresses(block)
    assert entity == "Input Output (iohk.io)"

    cardano_mapping.special_addresses.add('very special address')
    block = {"number": -2, "identifiers": "spcl", "timestamp": "2023-08-10 17:16:21",
             "reward_addresses": "very special address"}
    entity = cardano_mapping.map_from_known_addresses(block)
    assert entity == "----- SPECIAL ADDRESS -----"
