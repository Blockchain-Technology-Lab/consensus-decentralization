import datetime
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

    main(
        projects=['sample_bitcoin', 'sample_cardano'],
        timeframe=(datetime.date(2010, 1, 1), datetime.date(2010, 12, 31)),
        aggregate_by='year',
        force_map=True,
        make_plots=False,
        make_animated_plots=False,
        output_dir=test_output_dir
    )

    expected_entropy = [
        'timeframe,sample_bitcoin,sample_cardano\n',
        '2010,,\n'
    ]
    with open(test_output_dir / 'entropy=1.csv') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            assert line == expected_entropy[idx]

    expected_gini = [
        'timeframe,sample_bitcoin,sample_cardano\n',
        '2010,,\n'
    ]
    with open(test_output_dir / 'gini.csv') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            assert line == expected_gini[idx]

    expected_nc = [
        'timeframe,sample_bitcoin,sample_cardano\n',
        '2010,,\n'
    ]
    with open(test_output_dir / 'nakamoto_coefficient.csv') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            assert line == expected_nc[idx]

    main(
        projects=['sample_bitcoin', 'sample_cardano'],
        timeframe=(datetime.date(2018, 2, 1), datetime.date(2018, 3, 31)),
        aggregate_by='month',
        force_map=True,
        make_plots=False,
        make_animated_plots=False,
        output_dir=test_output_dir
    )

    expected_entropy = [
        'timeframe,sample_bitcoin,sample_cardano\n',
        'Feb-2018,1.5,\n',
        'Mar-2018,0.0,\n',
        ]
    with open(test_output_dir / 'entropy=1.csv') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            assert line == expected_entropy[idx]

    expected_gini = [
        'timeframe,sample_bitcoin,sample_cardano\n',
        'Feb-2018,0.375,\n',
        'Mar-2018,0.75,\n'
    ]
    with open(test_output_dir / 'gini.csv') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            assert line == expected_gini[idx]

    expected_nc = [
        'timeframe,sample_bitcoin,sample_cardano\n',
        'Feb-2018,1,\n', 'Mar-2018,1,\n'
    ]
    with open(test_output_dir / 'nakamoto_coefficient.csv') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            assert line == expected_nc[idx]

    main(
        projects=['sample_bitcoin', 'sample_cardano'],
        timeframe=(datetime.date(2020, 12, 1), datetime.date(2020, 12, 31)),
        aggregate_by='month',
        force_map=True,
        make_plots=False,
        make_animated_plots=False,
        output_dir=test_output_dir
    )

    expected_entropy = [
        'timeframe,sample_bitcoin,sample_cardano\n',
        'Dec-2020,,1.9219280948873623\n'
    ]
    with open(test_output_dir / 'entropy=1.csv') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            assert line == expected_entropy[idx]

    expected_gini = [
        'timeframe,sample_bitcoin,sample_cardano\n',
        'Dec-2020,,0.15\n'
    ]
    with open(test_output_dir / 'gini.csv') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            assert line == expected_gini[idx]

    expected_nc = [
        'timeframe,sample_bitcoin,sample_cardano\n',
        'Dec-2020,,2\n'
    ]
    with open(test_output_dir / 'nakamoto_coefficient.csv') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            assert line == expected_nc[idx]
