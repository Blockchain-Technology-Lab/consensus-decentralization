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
from consensus_decentralization.helper import INTERIM_DIR, config
import pytest
import csv


@pytest.fixture
def setup_and_cleanup():
    """
    This function can be used to set up the right conditions for a test and also clean up after the test is finished.
    The part before the yield command is run before the test (setup) and the part after the yield command is run
    after (cleanup)
    """
    # Set up
    test_output_dir = INTERIM_DIR / "test_output"
    test_metrics_subdir = test_output_dir / "metrics"
    ledger_mapping['sample_bitcoin'] = DefaultMapping
    ledger_parser['sample_bitcoin'] = DefaultParser
    ledger_mapping['sample_cardano'] = CardanoMapping
    ledger_parser['sample_cardano'] = DummyParser

    config['clustering'] = True

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
    yield test_output_dir, test_metrics_subdir
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
    test_output_dir, test_metrics_dir = setup_and_cleanup

    main(
        ['sample_bitcoin', 'sample_cardano'],
        (datetime.date(2018, 2, 1), datetime.date(2018, 3, 31)),
        estimation_window=30,
        frequency=30,
        interim_dir=test_output_dir,
        results_dir=test_output_dir,
        population_windows=0,
        force_map=True
    )

    # todo fix test (remake calculations from sample files given the new window/frequency)
    # expected_gini = [
    #     'timeframe,sample_bitcoin,sample_cardano\n',
    #     '2018-02-15,0.375,\n',
    #     '2018-03-17,0.75,\n'
    # ]
    # with open(test_metrics_dir / 'gini.csv') as f:
    #     lines = f.readlines()
    #     for idx, line in enumerate(lines):
    #         assert line == expected_gini[idx]

    output_file = test_metrics_dir / 'output_clustered.csv'
    assert output_file.is_file()
    with open(output_file) as f:
        rows = list(csv.reader(f))
    header = rows[0]
    ent_idx = header.index('entropy=1')
    nc_idx = header.index('nakamoto_coefficient')

    # build mapping ledger+date -> row
    row_map = {(r[0], r[1]): r for r in rows[1:]}
    assert row_map[('sample_bitcoin', '2018-02-15')][ent_idx] == '1.5'
    assert row_map[('sample_bitcoin', '2018-02-15')][nc_idx] == '1'

    # main(
    #     ['sample_bitcoin', 'sample_cardano'],
    #     (datetime.date(2020, 12, 1), datetime.date(2020, 12, 31)),
    #     estimation_window=31,
    #     frequency=31,
    #     interim_dir=test_output_dir,
    #     results_dir=test_output_dir,
    #     population_windows=0,
    #     force_map=True
    # )

    # output_file = test_metrics_dir / 'output_clustered.csv'
    # assert output_file.is_file()
    # with open(output_file) as f:
    #     rows = list(csv.reader(f))
    # header = rows[0]
    # ent_idx = header.index('entropy=1')
    # gini_idx = header.index('gini')
    # nc_idx = header.index('nakamoto_coefficient')
    # row_map = {(r[0], r[1]): r for r in rows[1:]}
    # assert row_map[('sample_cardano', '2020-12-16')][ent_idx] == '1.9219280948873623'
    # assert row_map[('sample_cardano', '2020-12-16')][gini_idx] == '0.15'
    # assert row_map[('sample_cardano', '2020-12-16')][nc_idx] == '2'
