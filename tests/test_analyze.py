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
    csv_per_timeframes = {'from_2018-01-01_to_2018-12-31': 'Entity,Resources\n'
                                  '1AM2f...9pJUx/3G7y1...gPPWb,4\n'
                                  'BTC.TOP,2\n'
                                  'GBMiners,2\n'
                                  '1AM2fYfpY3ZeMeCKXmN66haoWxvB89pJUx,1',
                          'from_2018-02-01_to_2018-02-28': 'Entity,Resources\n'
                                     '1AM2f...9pJUx/3G7y1...gPPWb,4\n'
                                     'BTC.TOP,2\n'
                                     'GBMiners,2',
                          'from_2018-03-01_to_2018-03-31': 'Entity,Resources\n'
                                     '1AM2fYfpY3ZeMeCKXmN66haoWxvB89pJUx,1'}
    aggregated_data_path = test_bitcoin_dir / 'blocks_per_entity'
    aggregated_data_path.mkdir(parents=True, exist_ok=True)
    for timeframe, content in csv_per_timeframes.items():
        with open(test_bitcoin_dir / f'blocks_per_entity/{timeframe}.csv', 'w') as f:
            f.write(content)
    yield test_io_dir
    # Clean up
    shutil.rmtree(test_io_dir)


def test_analyze(setup_and_cleanup):
    test_output_dir = setup_and_cleanup
    projects = ['sample_bitcoin']
    timeframes = ['2018']

    analyze(projects, timeframes, test_output_dir)

    metrics = ['gini', 'nakamoto_coefficient', 'entropy']
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
            elif metric == 'entropy':
                assert lines[1] == '2018,1.836591668108979\n'

    timeframes = ['2018-02']

    analyze(projects, timeframes, test_output_dir)

    metrics = ['gini', 'nakamoto_coefficient', 'entropy']
    for metric in metrics:
        output_file = test_output_dir / f'{metric}.csv'
        assert output_file.is_file()

        with open(output_file) as f:
            lines = f.readlines()
            assert lines[0] == 'timeframe,sample_bitcoin\n'
            if metric == 'gini':
                assert lines[1] == '2018-02,0.375\n'
            elif metric == 'nakamoto_coefficient':
                assert lines[1] == '2018-02,1\n'
            elif metric == 'entropy':
                assert lines[1] == '2018-02,1.5\n'

    timeframes = ['2018-03']

    analyze(projects, timeframes, test_output_dir)

    metrics = ['gini', 'nakamoto_coefficient', 'entropy']
    for metric in metrics:
        output_file = test_output_dir / f'{metric}.csv'
        assert output_file.is_file()

        with open(output_file) as f:
            lines = f.readlines()
            assert lines[0] == 'timeframe,sample_bitcoin\n'
            if metric == 'gini':
                assert lines[1] == '2018-03,0.75\n'
            elif metric == 'nakamoto_coefficient':
                assert lines[1] == '2018-03,1\n'
            elif metric == 'entropy':
                assert lines[1] == '2018-03,0.0\n'

    timeframes = ['2010']

    analyze(projects, timeframes, test_output_dir)

    metrics = ['gini', 'nakamoto_coefficient', 'entropy']
    for metric in metrics:
        output_file = test_output_dir / f'{metric}.csv'
        assert output_file.is_file()  # since there is no data for 2010

        with open(output_file) as f:
            lines = f.readlines()
            assert len(lines) == 2
            assert lines[0] == 'timeframe,sample_bitcoin\n'
            assert lines[1] == '2010,\n'
