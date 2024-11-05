import shutil
import pytest
from consensus_decentralization.helper import OUTPUT_DIR
from consensus_decentralization.analyze import analyze


@pytest.fixture
def setup_and_cleanup():
    """
    This function can be used to set up the right conditions for a test and also clean up after the test is finished.
    The part before the yield command is run before the test (setup) and the part after the yield command is run
    after (cleanup)
    """
    # Set up
    test_io_dir = OUTPUT_DIR / "test_output"
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
    aggregated_data_path = test_bitcoin_dir / 'blocks_per_entity'
    aggregated_data_path.mkdir(parents=True, exist_ok=True)
    for filename, content in csv_per_file.items():
        with open(test_bitcoin_dir / f'blocks_per_entity/{filename}.csv', 'w') as f:
            f.write(content)
    yield test_io_dir
    # Clean up
    shutil.rmtree(test_io_dir)


def test_analyze(setup_and_cleanup):
    test_output_dir = setup_and_cleanup
    projects = ['sample_bitcoin']

    analyze(
        projects=projects,
        aggregated_data_filename='year_from_2018-01-01_to_2018-12-31.csv',
        output_dir=test_output_dir
    )

    metrics = ['gini', 'nakamoto_coefficient', 'entropy=1']
    for metric in metrics:
        output_file = test_output_dir / f'{metric}.csv'
        assert output_file.is_file()

        with open(output_file) as f:
            lines = f.readlines()
            assert lines[0] == 'timeframe,sample_bitcoin\n'
            if metric == 'gini':
                assert lines[1] == '2018,0.25\n'
            elif metric == 'nakamoto_coefficient':
                assert lines[1] == '2018,2\n'
            elif metric == 'entropy=1':
                assert lines[1] == '2018,1.836591668108979\n'

    analyze(
        projects=projects,
        aggregated_data_filename='month_from_2018-02-01_to_2018-03-31.csv',
        output_dir=test_output_dir
    )

    metrics = ['gini', 'nakamoto_coefficient', 'entropy=1']
    for metric in metrics:
        output_file = test_output_dir / f'{metric}.csv'
        assert output_file.is_file()

        with open(output_file) as f:
            lines = f.readlines()
            assert lines[0] == 'timeframe,sample_bitcoin\n'
            if metric == 'gini':
                assert lines[1] == 'Feb-2018,0.16666666666666666\n'
                assert lines[2] == 'Mar-2018,0.0\n'
            elif metric == 'nakamoto_coefficient':
                assert lines[1] == 'Feb-2018,1\n'
                assert lines[2] == 'Mar-2018,1\n'
            elif metric == 'entropy=1':
                assert lines[1] == 'Feb-2018,1.5\n'
                assert lines[2] == 'Mar-2018,0.0\n'

    analyze(
        projects=projects,
        aggregated_data_filename='year_from_2010-01-01_to_2010-12-31.csv',
        output_dir=test_output_dir
    )

    metrics = ['gini', 'nakamoto_coefficient', 'entropy=1']
    for metric in metrics:
        output_file = test_output_dir / f'{metric}.csv'
        assert output_file.is_file()

        with open(output_file) as f:
            lines = f.readlines()
            assert len(lines) == 2
            assert lines[0] == 'timeframe,sample_bitcoin\n'
            assert lines[1] == '2010,\n'
