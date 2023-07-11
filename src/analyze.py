import argparse
from collections import defaultdict
from src.metrics.gini import compute_gini  # noqa: F401
from src.metrics.nakamoto_coefficient import compute_nakamoto_coefficient  # noqa: F401
from src.metrics.entropy import compute_entropy, compute_entropy_percentage  # noqa: F401
from src.metrics.herfindahl_hirschman_index import compute_hhi  # noqa: F401
from src.metrics.theil_index import compute_theil  # noqa: F401
from src.metrics.centralization_level import compute_centralization_level  # noqa: F401
from src.metrics.parties import compute_num_parties  # noqa: F401
from src.metrics.mining_power_ratio import compute_mining_power_ratio  # noqa: F401
from src.helpers.helper import OUTPUT_DIR, get_metrics_config

START_YEAR = 2018
END_YEAR = 2024

def analyze(projects, timeframes, output_dir):
    """
    Calculates all available metrics for the given ledgers and timeframes. Outputs one file for each metric.
    :param projects: list of strings that correspond to the ledgers whose data should be analyzed
    :param timeframes: list of strings that correspond to the timeframes under consideration (in YYYY-MM-DD,
    YYYY-MM or YYYY format)
    :returns: a list with the names of all the metrics that were used

    Using multiple projects and timeframes is necessary here to produce collective csv files.
    """
    metrics = get_metrics_config()

    csv_contents = {}
    for metric in metrics.keys():
        csv_contents[metric] = {'0': 'timeframe'}

    for project in projects:
        print(f'Calculating metrics for {project} data..')
        # Each metric dict is of the form {'<timeframe>': '<comma-separated values for different projects'}.
        # The special entry '0': '<comma-separated names of projects>' is for the csv header
        for metric in metrics.keys():
            csv_contents[metric]['0'] += f',{project},{project}_unknowns_grouped'

        for timeframe in timeframes:
            for metric in metrics.keys():
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
                for metric, args_dict in metrics.items():
                    func = eval(f'compute_{metric}')
                    results[metric] = func(blocks_per_entity, **args_dict) if args_dict else func(blocks_per_entity)
                    results_unknowns_grouped[metric] = func(blocks_per_entity_group,
                                                            **args_dict) if args_dict else func(blocks_per_entity_group)
            else:
                for metric in metrics.keys():
                    results[metric] = ''
                    results_unknowns_grouped[metric] = ''

            for metric in metrics.keys():
                csv_contents[metric][timeframe] += f',{results[metric]},{results_unknowns_grouped[metric]}'

    for metric in metrics.keys():
        with open(output_dir / f'{metric}.csv', 'w') as f:
            f.write('\n'.join([i[1] for i in sorted(csv_contents[metric].items(), key=lambda x: x[0])]))

    return list(metrics.keys())

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
        '--theil-alpha',
        nargs="?",
        type=int,
        default=1,
        help='The alpha parameter for Theil index computation. Default Theil-t. Examples: 0: Theil-L, 1: Theil-T'
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
    analyze(args.ledgers, timeframes, OUTPUT_DIR)
