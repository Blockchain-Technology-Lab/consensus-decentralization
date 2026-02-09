import shutil
import pytest
import csv
from consensus_decentralization.helper import INTERIM_DIR, get_clustering_flag
from consensus_decentralization.analyze import analyze


@pytest.fixture
def setup_and_cleanup():
    """
    This function can be used to set up the right conditions for a test and also clean up after the test is finished.
    The part before the yield command is run before the test (setup) and the part after the yield command is run
    after (cleanup)
    """
    # Set up
    test_io_dir = INTERIM_DIR / "test_output"
    test_bitcoin_dir = test_io_dir / "sample_bitcoin"
    test_bitcoin_dir.mkdir(parents=True, exist_ok=True)
    # create files that would be the output of aggregation
    csv_per_file = {
        'year_from_2018-01-01_to_2018-12-31':
            'Entity \\ Date,2018\n'
            '1AM2f...9pJUx/3G7y1...gPPWb,4\n'
            'BTC.TOP,2\n'
            'GBMiners,2\n'
            '1AM2fYfpY3ZeMeCKXmN66haoWxvB89pJUx,1\n',
        'month_from_2018-02-01_to_2018-03-31':
            'Entity \\ Date,Feb-2018,Mar-2018\n'
            '1AM2f...9pJUx/3G7y1...gPPWb,4,0\n'
            'BTC.TOP,2,0\n'
            'GBMiners,2,0\n'
            '1AM2fYfpY3ZeMeCKXmN66haoWxvB89pJUx,0,1\n',
        'year_from_2010-01-01_to_2010-12-31':
            'Entity \\ Date,2010\n'
        }
    aggregated_data_path = test_bitcoin_dir / 'blocks_per_entity_clustered'
    aggregated_data_path.mkdir(parents=True, exist_ok=True)
    for filename, content in csv_per_file.items():
        with open(aggregated_data_path / f'{filename}.csv', 'w') as f:
            f.write(content)
    # Create metrics directory
    metrics_dir = test_io_dir / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    # Mock return value of get_clustering_flag
    get_clustering_flag.return_value = True
    yield test_io_dir
    # Clean up
    shutil.rmtree(test_io_dir)


def test_analyze(setup_and_cleanup):
    test_output_dir = setup_and_cleanup
    projects = ['sample_bitcoin']

    analyze(
        projects=projects,
        aggregated_data_filename='year_from_2018-01-01_to_2018-12-31.csv',
        input_dir=test_output_dir,
        output_dir=test_output_dir / 'metrics',
        population_windows=0
    )

    output_file = test_output_dir / 'metrics' / 'output_clustered.csv'
    assert output_file.is_file()

    with open(output_file) as f:
        reader = list(csv.reader(f))
    header = reader[0]
    # find metric column indices
    gini_idx = header.index('gini')
    nc_idx = header.index('nakamoto_coefficient')
    ent_idx = header.index('entropy=1')

    # find the row for sample_bitcoin and 2018
    data_row = None
    for row in reader[1:]:
        if row[0] == 'sample_bitcoin' and row[1] == '2018':
            data_row = row
            break
    assert data_row is not None
    assert data_row[gini_idx] == '0.25'
    assert data_row[nc_idx] == '2'
    assert data_row[ent_idx] == '1.836591668108979'

    analyze(
        projects=projects,
        aggregated_data_filename='month_from_2018-02-01_to_2018-03-31.csv',
        input_dir=test_output_dir,
        output_dir=test_output_dir / 'metrics',
        population_windows=0
    )

    output_file = test_output_dir / 'metrics' / 'output_clustered.csv'
    assert output_file.is_file()
    with open(output_file) as f:
        reader = list(csv.reader(f))
    header = reader[0]
    gini_idx = header.index('gini')
    nc_idx = header.index('nakamoto_coefficient')
    ent_idx = header.index('entropy=1')

    rows_for_project = {row[1]: row for row in reader[1:] if row[0] == 'sample_bitcoin'}
    assert rows_for_project['Feb-2018'][gini_idx] == '0.16666666666666666'
    assert rows_for_project['Mar-2018'][gini_idx] == '0.0'
    assert rows_for_project['Feb-2018'][nc_idx] == '1'
    assert rows_for_project['Mar-2018'][nc_idx] == '1'
    assert rows_for_project['Feb-2018'][ent_idx] == '1.5'
    assert rows_for_project['Mar-2018'][ent_idx] == '0.0'
