import os
import pathlib
import shutil
from run import main
from src.parse import ledger_parser
from src.parsers.default_parser import DefaultParser
from src.parsers.cardano_parser import CardanoParser
from src.map import ledger_mapping
from src.mappings.bitcoin import BitcoinMapping
from src.mappings.cardano import CardanoMapping
from src.helpers.helper import OUTPUT_DIR
import pytest


@pytest.fixture
def setup_and_cleanup():
    """
    This function can be used to set up the right conditions for a test and also clean up after the test is finished.
    The part before the yield command is run before the test (setup) and the part after the yield command is run
    after (cleanup)
    """
    print("Setting up")
    test_output_dir = OUTPUT_DIR / "test_output"
    ledger_mapping['sample_bitcoin'] = BitcoinMapping
    ledger_parser['sample_bitcoin'] = DefaultParser
    ledger_mapping['sample_cardano'] = CardanoMapping
    ledger_parser['sample_cardano'] = CardanoParser
    yield test_output_dir
    print("Cleaning up")
    shutil.rmtree(test_output_dir)


def test_end_to_end(setup_and_cleanup):
    test_output_dir = setup_and_cleanup
    pool_info_dir = pathlib.Path(__file__).resolve().parent.parent / 'src' / 'helpers' / 'pool_information'
    projects = ['bitcoin', 'cardano']

    for project in projects:
        shutil.copy2(str(pool_info_dir / f'{project}.json'), str(pool_info_dir / f'sample_{project}.json'))

    timeframes = ['2010', '2018-02', '2018-03', '2020-12']
    force_parse = False
    entropy_alpha = 1

    projects = [f'sample_{i}' for i in projects]
    main(projects, timeframes, force_parse, entropy_alpha, False, test_output_dir)

    for project in projects:
        os.remove(str(pool_info_dir / f'{project}.json'))

    expected_entropy = [
        'timeframe,sample_bitcoin,sample_cardano\n',
        '2010,,\n',
        '2018-02,1.5,\n',
        '2018-03,0.0,\n',
        '2020-12,,2.321928094887362'
    ]
    with open(test_output_dir / 'entropy.csv') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            assert expected_entropy[idx] == line

    expected_gini = [
        'timeframe,sample_bitcoin,sample_cardano\n',
        '2010,,\n',
        '2018-02,0.375,\n',
        '2018-03,0.75,\n',
        '2020-12,,0.0'
    ]
    with open(test_output_dir / 'gini.csv') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            assert expected_gini[idx] == line

    expected_nc = [
        'timeframe,sample_bitcoin,sample_cardano\n',
        '2010,,\n',
        '2018-02,1,\n',
        '2018-03,1,\n',
        '2020-12,,3'
    ]
    with open(test_output_dir / 'nc.csv') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            assert expected_nc[idx] == line
