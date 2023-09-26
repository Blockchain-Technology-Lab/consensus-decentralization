import os
import pathlib
import shutil
from run import main
from consensus_decentralization.parse import ledger_parser
from consensus_decentralization.parsers.default_parser import DefaultParser
from consensus_decentralization.parsers.dummy_parser import DummyParser
from consensus_decentralization.map import ledger_mapping
from consensus_decentralization.mappings.default_mapping import DefaultMapping
from consensus_decentralization.mappings.cardano_mapping import CardanoMapping
from consensus_decentralization.helper import OUTPUT_DIR
import pytest


@pytest.fixture
def setup_and_cleanup():
    """
    This function can be used to set up the right conditions for a test and also clean up after the test is finished.
    The part before the yield command is run before the test (setup) and the part after the yield command is run
    after (cleanup)
    """
    # Set up
    test_output_dir = OUTPUT_DIR / "test_output"
    ledger_mapping['sample_bitcoin'] = DefaultMapping
    ledger_parser['sample_bitcoin'] = DefaultParser
    ledger_mapping['sample_cardano'] = CardanoMapping
    ledger_parser['sample_cardano'] = DummyParser

    mapping_info_dir = pathlib.Path(__file__).resolve().parent.parent / 'mapping_information'
    for project in ['bitcoin', 'cardano']:
        try:
            shutil.copy2(
                str(mapping_info_dir / f'clusters/{project}.json'),
                str(mapping_info_dir / f'clusters/sample_{project}.json')
            )
        except FileNotFoundError:
            pass
        try:
            shutil.copy2(
                str(mapping_info_dir / f'addresses/{project}.json'),
                str(mapping_info_dir / f'addresses/sample_{project}.json')
            )
        except FileNotFoundError:
            pass
        try:
            shutil.copy2(
                str(mapping_info_dir / f'identifiers/{project}.json'),
                str(mapping_info_dir / f'identifiers/sample_{project}.json')
            )
        except FileNotFoundError:
            pass
    yield test_output_dir
    # Clean up
    shutil.rmtree(test_output_dir)
    for project in ['sample_bitcoin', 'sample_cardano']:
        try:
            os.remove(str(mapping_info_dir / f'clusters/{project}.json'))
        except FileNotFoundError:
            pass
        try:
            os.remove(str(mapping_info_dir / f'addresses/{project}.json'))
        except FileNotFoundError:
            pass
        try:
            os.remove(str(mapping_info_dir / f'identifiers/{project}.json'))
        except FileNotFoundError:
            pass


def test_end_to_end(setup_and_cleanup):
    test_output_dir = setup_and_cleanup

    timeframes = ['2010', '2018-02', '2018-03', '2020-12']

    main(projects=['sample_bitcoin', 'sample_cardano'], timeframes=timeframes, force_map=True,
         make_plots=False, make_animated_plots=False, output_dir=test_output_dir)

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
            assert line == expected_entropy[idx]

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
            assert line == expected_gini[idx]

    expected_nc = [
        'timeframe,sample_bitcoin,sample_cardano\n',
        '2010,,\n',
        '2018-02,1,\n',
        '2018-03,1,\n',
        '2020-12,,3'
    ]
    with open(test_output_dir / 'nakamoto_coefficient.csv') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            assert line == expected_nc[idx]
