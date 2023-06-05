import pathlib
import pytest
import shutil
import os
import json
from src.parse import parse, ledger_parser
from src.parsers.default_parser import DefaultParser
from src.parsers.dummy_parser import DummyParser
from src.parsers.cardano_parser import CardanoParser
from src.map import apply_mapping, ledger_mapping
from src.mappings.mapping import Mapping
from src.mappings.bitcoin import BitcoinMapping
from src.mappings.ethereum import EthereumMapping
from src.mappings.cardano import CardanoMapping
from src.mappings.tezos import TezosMapping
from src.helpers.helper import INPUT_DIR, OUTPUT_DIR


@pytest.fixture
def setup_and_cleanup():
    """
    This function can be used to set up the right conditions for a test and also clean up after the test is finished.
    The part before the yield command is run before the test (setup) and the part after the yield command is run
    after (cleanup)
    """
    print("Setting up")
    ledger_mapping['sample_bitcoin'] = BitcoinMapping
    ledger_parser['sample_bitcoin'] = DefaultParser
    ledger_mapping['sample_ethereum'] = EthereumMapping
    ledger_parser['sample_ethereum'] = DummyParser
    ledger_mapping['sample_cardano'] = CardanoMapping
    ledger_parser['sample_cardano'] = CardanoParser
    ledger_mapping['sample_tezos'] = TezosMapping
    ledger_parser['sample_tezos'] = DummyParser
    pool_info_dir = pathlib.Path(__file__).resolve().parent.parent / 'src' / 'helpers' / 'pool_information'  # todo maybe better to have separate helper files for the tests s.t. the tests don't break just because the info changes
    test_input_dir = INPUT_DIR
    test_output_dir = OUTPUT_DIR / "test_output"
    yield pool_info_dir, test_input_dir, test_output_dir
    print("Cleaning up")
    shutil.rmtree(test_output_dir)


def test_map(setup_and_cleanup):
    pool_info_dir, test_input_dir, test_output_dir = setup_and_cleanup
    project = 'sample_bitcoin'

    shutil.copy2(str(pool_info_dir / 'bitcoin.json'),
                 str(pool_info_dir / f'{project}.json'))  # Create a temp pool info file for sample

    timeframes = ['2010', '2018-02', '2018-03']
    force_map = True

    parse(project, test_input_dir, test_output_dir)
    apply_mapping(project, timeframes, test_output_dir, force_map)

    output_file = test_output_dir / project / f'{timeframes[0]}.csv'
    assert output_file.is_file()

    yearly_output_file = test_output_dir / project / f'{timeframes[0][:4]}.csv'
    assert yearly_output_file.is_file()

    os.remove(str(pool_info_dir / f'{project}.json'))  # Remove temp pool info file


def test_bitcoin_mapping(setup_and_cleanup):
    pool_info_dir, test_input_dir, test_output_dir = setup_and_cleanup
    project = 'sample_bitcoin'

    shutil.copy2(str(pool_info_dir / 'bitcoin.json'),
                 str(pool_info_dir / f'{project}.json'))  # Create a temp pool info file for sample

    with open(str(pool_info_dir / f'{project}.json')) as f:
        pool_info = json.load(f)
    pool_info['pool_addresses']['0000000000000000000000000000000000000000'] = {'name': 'TEST2', 'from': '2020-01-02',
                                                                               'to': '2020-09-20', 'source': ''}
    with open(str(pool_info_dir / f'{project}.json'), 'w') as f:
        f.write(json.dumps(pool_info))

    timeframes = ['2018-02']
    force_map = True

    parse(project, test_input_dir, test_output_dir)
    apply_mapping(project, timeframes, test_output_dir, force_map)

    expected_output = [
        'Entity Group,Entity,Resources\n',
        'Unknown,1AM2f...9pJUx/3G7y1...gPPWb,4\n',
        'BTC.TOP,BTC.TOP,2\n',
        'GBMiners,GBMiners,2'
    ]

    output_file = test_output_dir / project / f'{timeframes[0]}.csv'
    with open(output_file) as f:
        for idx, line in enumerate(f.readlines()):
            assert line == expected_output[idx]

    expected_output = [
        'Entity Group,Entity,Resources\n',
        'Unknown,1AM2f...9pJUx/3G7y1...gPPWb,4\n',
        'BTC.TOP,BTC.TOP,2\n',
        'GBMiners,GBMiners,2\n',
        'Unknown,1AM2fYfpY3ZeMeCKXmN66haoWxvB89pJUx,1'
    ]

    yearly_output_file = test_output_dir / project / f'{timeframes[0][:4]}.csv'
    with open(yearly_output_file) as f:
        for idx, line in enumerate(f.readlines()):
            assert expected_output[idx] == line

    timeframes = ['2020']
    force_map = True

    parse(project, test_input_dir, test_output_dir)
    apply_mapping(project, timeframes, test_output_dir, force_map)

    expected_output = [
        'Entity Group,Entity,Resources\n',
        'TEST2,TEST2,1\n',
        'Bitmain,Bitmain,1\n',
        'Unknown,0000000000000000000000000000000000000000,1'
    ]

    output_file = test_output_dir / project / f'{timeframes[0]}.csv'
    with open(output_file) as f:
        for idx, line in enumerate(f.readlines()):
            assert expected_output[idx] == line

    os.remove(str(pool_info_dir / f'{project}.json'))  # Remove temp pool info file


def test_ethereum_mapping(setup_and_cleanup):
    pool_info_dir, test_input_dir, test_output_dir = setup_and_cleanup
    project = 'sample_ethereum'

    shutil.copy2(str(pool_info_dir / 'ethereum.json'),
                 str(pool_info_dir / f'{project}.json'))  # Create a temp pool info file for sample

    with open(str(pool_info_dir / f'{project}.json')) as f:
        pool_info = json.load(f)
    pool_info['clusters']['TEST'] = [{'name': 'ezil.me', 'from': '', 'to': '', 'source': 'homepage'}]
    pool_info['pool_addresses']['0xe9b54a47e3f401d37798fc4e22f14b78475c2afc'] = {'name': 'TEST2', 'from': '2020',
                                                                                 'to': '2021-01', 'source': ''}
    with open(str(pool_info_dir / f'{project}.json'), 'w') as f:
        f.write(json.dumps(pool_info))

    timeframes = ['2020-11']
    force_map = True

    parse(project, test_input_dir, test_output_dir)
    apply_mapping(project, timeframes, test_output_dir, force_map)

    expected_output = [
        'Entity Group,Entity,Resources\n',
        'TEST2,TEST2,5\n',
        'TEST,TEST,3\n',
        'Unknown,0x45133a7e1cc7e18555ae8a4ee632a8a61de90df6,1'
    ]

    output_file = test_output_dir / project / f'{timeframes[0]}.csv'
    with open(output_file) as f:
        for idx, line in enumerate(f.readlines()):
            assert expected_output[idx] == line

    yearly_output_file = test_output_dir / project / f'{timeframes[0][:4]}.csv'
    with open(yearly_output_file) as f:
        for idx, line in enumerate(f.readlines()):
            assert expected_output[idx] == line

    timeframes = ['2023']
    force_map = True

    parse(project, test_input_dir, test_output_dir)
    apply_mapping(project, timeframes, test_output_dir, force_map)

    expected_output = [
        'Entity Group,Entity,Resources\n',
        'MEV Builder: 0x3B...436,MEV Builder: 0x3B...436,1'
    ]

    output_file = test_output_dir / project / f'{timeframes[0]}.csv'
    with open(output_file) as f:
        for idx, line in enumerate(f.readlines()):
            assert expected_output[idx] == line

    os.remove(str(pool_info_dir / f'{project}.json'))  # Remove temp pool info file


def test_cardano_mapping(setup_and_cleanup):
    pool_info_dir, test_input_dir, test_output_dir = setup_and_cleanup
    project = 'sample_cardano'

    shutil.copy2(str(pool_info_dir / 'cardano.json'),
                 str(pool_info_dir / f'{project}.json'))  # Create a temp pool info file for sample

    ledger_mapping[project] = CardanoMapping
    ledger_parser[project] = CardanoParser

    timeframes = ['2020-12']
    force_map = True

    parse(project, test_input_dir, test_output_dir)
    apply_mapping(project, timeframes, test_output_dir, force_map)

    expected_output = [
        'Entity Group,Entity,Resources\n',
        'CFLOW,CFLOW,1\n',
        'Unknown,1d8988c2057d6efd6a094e468840a51942ab03b5b69b07a2bca71b53,1\n',
        'Input Output (iohk.io),Input Output (iohk.io),1\n',
        'Arrakis,Arrakis,1\n',
        '1percentpool,1percentpool,1'
    ]

    output_file = test_output_dir / project / f'{timeframes[0]}.csv'
    with open(output_file) as f:
        for idx, line in enumerate(f.readlines()):
            assert expected_output[idx] == line

    yearly_output_file = test_output_dir / project / f'{timeframes[0][:4]}.csv'
    with open(yearly_output_file) as f:
        for idx, line in enumerate(f.readlines()):
            assert expected_output[idx] == line

    os.remove(str(pool_info_dir / f'{project}.json'))  # Remove temp pool info file


def test_tezos_mapping(setup_and_cleanup):
    pool_info_dir, test_input_dir, test_output_dir = setup_and_cleanup
    project = 'sample_tezos'

    shutil.copy2(str(pool_info_dir / 'tezos.json'),
                 str(pool_info_dir / f'{project}.json'))  # Create a temp pool info file for sample
    with open(str(pool_info_dir / f'{project}.json')) as f:
        pool_info = json.load(f)
    pool_info['clusters']['TEST'] = [{'name': 'TzNode', 'from': '2021', 'to': '2022', 'source': 'homepage'}]
    with open(str(pool_info_dir / f'{project}.json'), 'w') as f:
        f.write(json.dumps(pool_info))

    ledger_mapping[project] = TezosMapping
    ledger_parser[project] = DummyParser

    timeframes = ['2021-08']
    force_map = True

    parse(project, test_input_dir, test_output_dir)
    apply_mapping(project, timeframes, test_output_dir, force_map)

    expected_output = [
        'Entity Group,Entity,Resources\n',
        'Tezos Seoul,Tezos Seoul,2\n',
        'Unknown,tz1Kt4P8BCaP93AEV4eA7gmpRryWt5hznjCP,1\n',
        'TEST,TEST,1\n',
        'Unknown,----- UNDEFINED MINER -----,1'
    ]

    output_file = test_output_dir / project / f'{timeframes[0]}.csv'
    with open(output_file) as f:
        for idx, line in enumerate(f.readlines()):
            assert expected_output[idx] == line

    yearly_output_file = test_output_dir / project / f'{timeframes[0][:4]}.csv'
    with open(yearly_output_file) as f:
        for idx, line in enumerate(f.readlines()):
            assert expected_output[idx] == line

    timeframes = ['2018']
    force_map = True

    parse(project, test_input_dir, test_output_dir)
    apply_mapping(project, timeframes, test_output_dir, force_map)

    expected_output = [
        'Entity Group,Entity,Resources\n',
        'Unknown,tz0000000000000000000000000000000000,1'
    ]

    output_file = test_output_dir / project / f'{timeframes[0]}.csv'
    with open(output_file) as f:
        for idx, line in enumerate(f.readlines()):
            assert expected_output[idx] == line

    os.remove(str(pool_info_dir / f'{project}.json'))  # Remove temp pool info file


def test_not_implemented_process():
    class TestMap(Mapping):
        def __init__(self, project_name, dataset):
            super().__init__(project_name, dataset)

    test_map = TestMap('test', 'test')
    with pytest.raises(NotImplementedError) as e_info:
        test_map.process('test')
    assert e_info.type == NotImplementedError
