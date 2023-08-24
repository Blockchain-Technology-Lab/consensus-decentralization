import os
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
    if not os.path.exists(test_bitcoin_dir):
        os.makedirs(test_bitcoin_dir)
    # create files that would be the output of mapping
    csv_per_timeframes = {
        '2010': 'Entity Group,Entity,Resources',
        '2018': 'Entity Group,Entity,Resources\n'
                '1AM2f...9pJUx/3G7y1...gPPWb,1AM2f...9pJUx/3G7y1...gPPWb,4\n'
                'BTC.TOP,BTC.TOP,2\n'
                'GBMiners,GBMiners,2\n'
                'Unknown,1AM2fYfpY3ZeMeCKXmN66haoWxvB89pJUx,1',
        '2018-02': 'Entity Group,Entity,Resources\n'
                   '1AM2f...9pJUx/3G7y1...gPPWb,1AM2f...9pJUx/3G7y1...gPPWb,4\n'
                   'BTC.TOP,BTC.TOP,2\n'
                   'GBMiners,GBMiners,2',
        '2018-03': 'Entity Group,Entity,Resources\n'
                   'Unknown,1AM2fYfpY3ZeMeCKXmN66haoWxvB89pJUx,1'
    }
    for timeframe, content in csv_per_timeframes.items():
        with open(test_bitcoin_dir / f'{timeframe}.csv', 'w') as f:
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
            assert lines[0] == 'timeframe,sample_bitcoin,sample_bitcoin_unknowns_grouped\n'
            if metric == 'gini':
                assert lines[1] == '2018,0.25,0.25'
            elif metric == 'nakamoto_coefficient':
                assert lines[1] == '2018,2,2'
            elif metric == 'entropy':
                assert lines[1] == '2018,1.836591668108979,1.836591668108979'

    timeframes = ['2018-02']

    analyze(projects, timeframes, test_output_dir)

    metrics = ['gini', 'nakamoto_coefficient', 'entropy']
    for metric in metrics:
        output_file = test_output_dir / f'{metric}.csv'
        assert output_file.is_file()

        with open(output_file) as f:
            lines = f.readlines()
            assert lines[0] == 'timeframe,sample_bitcoin,sample_bitcoin_unknowns_grouped\n'
            if metric == 'gini':
                assert lines[1] == '2018-02,0.375,0.375'
            elif metric == 'nakamoto_coefficient':
                assert lines[1] == '2018-02,1,1'
            elif metric == 'entropy':
                assert lines[1] == '2018-02,1.5,1.5'

    timeframes = ['2018-03']

    analyze(projects, timeframes, test_output_dir)

    metrics = ['gini', 'nakamoto_coefficient', 'entropy']
    for metric in metrics:
        output_file = test_output_dir / f'{metric}.csv'
        assert output_file.is_file()

        with open(output_file) as f:
            lines = f.readlines()
            assert lines[0] == 'timeframe,sample_bitcoin,sample_bitcoin_unknowns_grouped\n'
            if metric == 'gini':
                assert lines[1] == '2018-03,0.75,0.75'
            elif metric == 'nakamoto_coefficient':
                assert lines[1] == '2018-03,1,1'
            elif metric == 'entropy':
                assert lines[1] == '2018-03,0.0,0.0'

    timeframes = ['2010']

    analyze(projects, timeframes, test_output_dir)

    metrics = ['gini', 'nakamoto_coefficient', 'entropy']
    for metric in metrics:
        output_file = test_output_dir / f'{metric}.csv'
        assert output_file.is_file()

        with open(output_file) as f:
            lines = f.readlines()
            assert len(lines) == 2
            assert lines[0] == 'timeframe,sample_bitcoin,sample_bitcoin_unknowns_grouped\n'
            assert lines[1] == '2010,,'
