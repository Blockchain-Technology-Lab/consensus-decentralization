import pathlib
import shutil
import os
import json
from src.parse import parse, ledger_parser
from src.parsers.default_parser import DefaultParser
from src.parsers.dummy_parser import DummyParser
from src.parsers.cardano_parser import CardanoParser
from src.map import apply_mapping, ledger_mapping
from src.mappings.bitcoin import BitcoinMapping
from src.mappings.ethereum import EthereumMapping
from src.mappings.cardano import CardanoMapping
from src.mappings.tezos import TezosMapping
from src.helpers.helper import OUTPUT_DIR


def test_map():
    pool_info_dir = pathlib.Path(__file__).resolve().parent.parent / 'src' / 'helpers' / 'pool_information'

    project = 'sample_bitcoin'

    shutil.copy2(str(pool_info_dir / 'bitcoin.json'), str(pool_info_dir / f'{project}.json'))

    timeframes = '2018-02'
    ledger_mapping[project] = BitcoinMapping
    ledger_parser[project] = DefaultParser

    parse(project)
    apply_mapping(project, timeframes)

    output_file = OUTPUT_DIR / project / f'{timeframes[0]}.csv'
    assert output_file.is_file()

    yearly_output_file = OUTPUT_DIR / project / f'{timeframes[0][:4]}.csv'
    assert yearly_output_file.is_file()

    os.remove(str(pool_info_dir / f'{project}.json'))


def test_bitcoin_mapping():
    pass


def test_ethereum_mapping():
    pool_info_dir = pathlib.Path(__file__).resolve().parent.parent / 'src' / 'helpers' / 'pool_information'

    project = 'sample_ethereum'

    shutil.copy2(str(pool_info_dir / 'ethereum.json'), str(pool_info_dir / f'{project}.json'))
    with open(str(pool_info_dir / f'{project}.json')) as f:
        pool_info = json.load(f)
    pool_info['clusters']['all'] = {}
    pool_info['clusters']['all']['TEST'] = [['ezil.me', 'homepage']]
    pool_info['pool_addresses']['2020'] = {}
    pool_info['pool_addresses']['2020']['0xe9b54a47e3f401d37798fc4e22f14b78475c2afc'] = 'TEST2'
    with open(str(pool_info_dir / f'{project}.json'), 'w') as f:
        f.write(json.dumps(pool_info))

    ledger_mapping[project] = EthereumMapping
    ledger_parser[project] = DummyParser

    timeframes = ['2020-11']

    parse(project)
    apply_mapping(project, timeframes)

    expected_output = [
        'Entity,Resources\n',
        'TEST2,5\n',
        'TEST,3\n',
        '0x45133a7e1cc7e18555ae8a4ee632a8a61de90df6,1'
    ]

    output_file = OUTPUT_DIR / project / f'{timeframes[0]}.csv'
    with open(output_file) as f:
        for idx, line in enumerate(f.readlines()):
            assert expected_output[idx] == line

    yearly_output_file = OUTPUT_DIR / project / f'{timeframes[0][:4]}.csv'
    with open(yearly_output_file) as f:
        for idx, line in enumerate(f.readlines()):
            assert expected_output[idx] == line

    timeframes = ['2023']

    parse(project)
    apply_mapping(project, timeframes)

    expected_output = [
        'Entity,Resources\n',
        '0x3bee5122e2a2fbe11287aafb0cb918e22abb5436,1'
    ]

    output_file = OUTPUT_DIR / project / f'{timeframes[0]}.csv'
    with open(output_file) as f:
        for idx, line in enumerate(f.readlines()):
            assert expected_output[idx] == line

    os.remove(str(pool_info_dir / f'{project}.json'))


def test_cardano_mapping():
    pass


def test_tezos_mapping():
    pass
