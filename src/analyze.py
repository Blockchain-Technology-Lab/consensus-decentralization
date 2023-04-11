import argparse
from collections import defaultdict
from src.metrics.gini import compute_gini
from src.metrics.nakamoto_coefficient import compute_nakamoto_coefficient
from src.metrics.entropy import compute_entropy
from src.metrics.herfindahl_hirschman_index import compute_hhi
from src.helpers.helper import OUTPUT_DIR

START_YEAR = 2018
END_YEAR = 2024

metrics_funcs = {
    'gini': compute_gini,
    'nc': compute_nakamoto_coefficient,
    'entropy': compute_entropy,
    'hhi': compute_hhi
}

additional_metric_args = {
    'entropy': ['entropy_alpha']
}


def analyze(projects, timeframes, entropy_alpha, output_dir):
    """
    Calculates all available metrics for the given ledgers and timeframes. Outputs one file for each metric.
    :param projects: list of strings that correspond to the ledgers whose data should be analyzed
    :param timeframes: list of strings that correspond to the timeframes under consideration (in YYYY-MM-DD,
    YYYY-MM or YYYY format)
    :param entropy_alpha: float that corresponds to the alpha parameter for the entropy calculation

    Using multiple projects and timeframes is necessary here to produce collective csv files.
    """
    csv_contents = {}
    for metric in metrics_funcs.keys():
        csv_contents[metric] = {'0': 'timeframe'}

    for project in projects:
        # Each metric dict is of the form {'<timeframe>': '<comma-separated values for different projects'}.
        # The special entry '0': '<comma-separated names of projects>' is for the csv header
        for metric in metrics_funcs.keys():
            csv_contents[metric]['0'] += f',{project},{project}_unknowns_grouped'

        for timeframe in timeframes:
            for metric in metrics_funcs.keys():
                if timeframe not in csv_contents[metric].keys():
                    csv_contents[metric][timeframe] = timeframe

            # Get mapped data for the year that corresponds to the timeframe.
            # This is needed because the Gini coefficient is computed over all entities per each year.
            year = timeframe[:4]
            yearly_entities = set()
            yearly_entity_groups = set()
            with open(output_dir / f'{project}/{year}.csv') as f:
                for line in f.readlines()[1:]:
                    entity_group, entity, _ = line.split(',')
                    yearly_entities.add(entity)
                    yearly_entity_groups.add(entity_group)

            # Get mapped data for the defined timeframe.
            with open(output_dir / f'{project}/{timeframe}.csv') as f:
                blocks_per_entity = {}
                blocks_per_entity_group = defaultdict(int, {'Unknown': 0})
                for line in f.readlines()[1:]:
                    entity_group, entity, resources = line.split(',')
                    blocks_per_entity[entity] = int(resources)
                    blocks_per_entity_group[entity_group] += int(resources)

            results = {}
            results_unknowns_grouped = {}
            # If the project data exist for the given timeframe, compute the metrics on them.
            if blocks_per_entity.keys():
                for entity in yearly_entities:
                    if entity not in blocks_per_entity.keys():
                        blocks_per_entity[entity] = 0
                        if entity in yearly_entity_groups:
                            blocks_per_entity_group[entity] = 0

                scope = locals()
                for metric, func in metrics_funcs.items():
                    if metric in additional_metric_args.keys():
                        results[metric] = func(
                            blocks_per_entity,
                            *[eval(arg, scope) for arg in additional_metric_args[metric]]
                        )
                        results_unknowns_grouped[metric] = func(
                            blocks_per_entity_group,
                            *[eval(arg, scope) for arg in additional_metric_args[metric]]
                        )
                    else:
                        results[metric] = func(blocks_per_entity)
                        results_unknowns_grouped[metric] = func(blocks_per_entity_group)
                # max_entropy = compute_entropy({entity: 1 for entity in yearly_entities}, entropy_alpha)
                # entropy_percentage = 100 * entropy / max_entropy if max_entropy != 0 else 0
                # print(
                #    f'[{project:12} {timeframe:7}] \t Gini: {gini:.6f}   NC: {nc[0]:3} ({nc[1]:.2f}%)   HHI:
                #    {hhi:.6f} '
                #    f'Entropy: {entropy:.6f} ({entropy_percentage:.1f}% out of max {max_entropy:.6f})'
                # )
            else:
                for metric, func in metrics_funcs.items():
                    results[metric] = ''
                    results_unknowns_grouped[metric] = ''

            for metric in metrics_funcs.keys():
                csv_contents[metric][timeframe] += f',{results[metric]},{results_unknowns_grouped[metric]}'

    for metric in metrics_funcs.keys():
        with open(output_dir / f'{metric}.csv', 'w') as f:
            f.write('\n'.join([i[1] for i in sorted(csv_contents[metric].items(), key=lambda x: x[0])]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--ledgers',
        nargs="*",
        type=str.lower,
        default=None,
        help='The ledgers that will be analyzed.'
    )
    parser.add_argument(
        '--timeframe',
        nargs="?",
        type=str,
        default=None,
        help='The timeframe that will be analyzed.'
    )
    parser.add_argument(
        '--entropy-alpha',
        nargs="?",
        type=int,
        default=1,
        help='The alpha parameter for entropy computation. Default Shannon entropy. Examples: -1: min, 0: Hartley, '
             '1: Shannon, 2: collision.'
    )

    args = parser.parse_args()

    timeframe = args.timeframe
    if timeframe:
        timeframes = [timeframe]
    else:
        timeframes = []
        for year in range(START_YEAR, END_YEAR):
            for month in range(1, 13):
                timeframes.append(f'{year}-{str(month).zfill(2)}')

    analyze(args.ledgers, timeframes, args.entropy_alpha, OUTPUT_DIR)
