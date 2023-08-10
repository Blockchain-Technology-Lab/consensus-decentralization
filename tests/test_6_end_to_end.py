import os
import pathlib
import shutil
from run import main
from src.parse import ledger_parser
from src.parsers.default_parser import DefaultParser
from src.parsers.dummy_parser import DummyParser
from src.map import ledger_mapping
from src.mappings.default_mapping import DefaultMapping
from src.mappings.cardano_mapping import CardanoMapping
from src.helper import OUTPUT_DIR
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
    yield test_output_dir
    # Clean up
    shutil.rmtree(test_output_dir)


def test_end_to_end(setup_and_cleanup):
    test_output_dir = setup_and_cleanup
    mapping_info_dir = pathlib.Path(__file__).resolve().parent.parent / 'mapping_information'
    projects = ['bitcoin', 'cardano']

    for project in projects:
        try:
            shutil.copy2(str(mapping_info_dir / f'clusters/{project}.json'), str(mapping_info_dir / f'clusters/sample_{project}.json'))
        except FileNotFoundError:
            pass
        try:
            shutil.copy2(str(mapping_info_dir / f'addresses/{project}.json'), str(mapping_info_dir / f'addresses/sample_{project}.json'))
        except FileNotFoundError:
            pass
        try:
            shutil.copy2(str(mapping_info_dir / f'identifiers/{project}.json'), str(mapping_info_dir / f'identifiers/sample_{project}.json'))
        except FileNotFoundError:
            pass

    timeframes = ['2010', '2018-02', '2018-03', '2020-12']
    force_parse = False
    force_map = False

    test_projects = [f'sample_{i}' for i in projects]
    main(test_projects, timeframes, force_parse, force_map, False, False, test_output_dir)

    for project in test_projects:
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

    expected_entropy = [
        'timeframe,sample_bitcoin,sample_bitcoin_unknowns_grouped,sample_cardano,sample_cardano_unknowns_grouped\n',
        '2010,,,,\n',
        '2018-02,1.5,1.5,,\n',
        '2018-03,0.0,0.0,,\n',
        '2020-12,,,2.321928094887362,2.321928094887362'
    ]
    with open(test_output_dir / 'entropy.csv') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            assert line == expected_entropy[idx]

    expected_gini = [
        'timeframe,sample_bitcoin,sample_bitcoin_unknowns_grouped,sample_cardano,sample_cardano_unknowns_grouped\n',
        '2010,,,,\n',
        '2018-02,0.375,0.16666666666666666,,\n',
        '2018-03,0.75,0.6666666666666666,,\n',
        '2020-12,,,0.0,0.0'
    ]
    with open(test_output_dir / 'gini.csv') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            assert line == expected_gini[idx]

    expected_nc = [
        'timeframe,sample_bitcoin,sample_bitcoin_unknowns_grouped,sample_cardano,sample_cardano_unknowns_grouped\n',
        '2010,,,,\n',
        '2018-02,1,1,,\n',
        '2018-03,1,1,,\n',
        '2020-12,,,3,3'
    ]
    with open(test_output_dir / 'nakamoto_coefficient.csv') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            assert line == expected_nc[idx]
