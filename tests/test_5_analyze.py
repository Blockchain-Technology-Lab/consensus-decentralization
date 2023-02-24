from src.helpers.helper import OUTPUT_DIR
from src.analyze import analyze


def test_analyze():
    projects = ['sample_bitcoin']
    timeframes = ['2018']
    entropy_alpha = 1

    analyze(projects, timeframes, entropy_alpha)

    metrics = ['gini', 'nc', 'entropy']
    for metric in metrics:
        output_file = OUTPUT_DIR / f'{metric}.csv'
        assert output_file.is_file()

        with open(output_file) as f:
            lines = f.readlines()
            assert lines[0] == 'timeframe,sample_bitcoin\n'
            if metric == 'gini':
                assert lines[1] == '2018,0.25'
            elif metric == 'nc':
                assert lines[1] == '2018,2'
            elif metric == 'entropy':
                assert lines[1] == '2018,1.836591668108979'

    timeframes = ['2018-02']
    entropy_alpha = 1

    analyze(projects, timeframes, entropy_alpha)

    metrics = ['gini', 'nc', 'entropy']
    for metric in metrics:
        output_file = OUTPUT_DIR / f'{metric}.csv'
        assert output_file.is_file()

        with open(output_file) as f:
            lines = f.readlines()
            assert lines[0] == 'timeframe,sample_bitcoin\n'
            if metric == 'gini':
                assert lines[1] == '2018-02,0.375'
            elif metric == 'nc':
                assert lines[1] == '2018-02,1'
            elif metric == 'entropy':
                assert lines[1] == '2018-02,1.5'

    timeframes = ['2018-03']
    entropy_alpha = 1

    analyze(projects, timeframes, entropy_alpha)

    metrics = ['gini', 'nc', 'entropy']
    for metric in metrics:
        output_file = OUTPUT_DIR / f'{metric}.csv'
        assert output_file.is_file()

        with open(output_file) as f:
            lines = f.readlines()
            assert lines[0] == 'timeframe,sample_bitcoin\n'
            if metric == 'gini':
                assert lines[1] == '2018-03,0.75'
            elif metric == 'nc':
                assert lines[1] == '2018-03,1'
            elif metric == 'entropy':
                assert lines[1] == '2018-03,0.0'

    timeframes = ['2010']

    analyze(projects, timeframes, entropy_alpha)

    metrics = ['gini', 'nc', 'entropy']
    for metric in metrics:
        output_file = OUTPUT_DIR / f'{metric}.csv'
        assert output_file.is_file()

        with open(output_file) as f:
            lines = f.readlines()
            assert len(lines) == 2
            assert lines[0] == 'timeframe,sample_bitcoin\n'
            assert lines[1] == '2010,'
