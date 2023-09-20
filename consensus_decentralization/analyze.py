import logging
import consensus_decentralization.helper as hlp
from consensus_decentralization.metrics.gini import compute_gini  # noqa: F401
from consensus_decentralization.metrics.nakamoto_coefficient import compute_nakamoto_coefficient  # noqa: F401
from consensus_decentralization.metrics.entropy import compute_entropy, compute_entropy_percentage  # noqa: F401
from consensus_decentralization.metrics.herfindahl_hirschman_index import compute_hhi  # noqa: F401


def analyze(projects, timeframes, output_dir):
    """
    Calculates all available metrics for the given ledgers and timeframes. Outputs one file for each metric.
    :param projects: list of strings that correspond to the ledgers whose data should be analyzed
    :param timeframes: list of strings that correspond to the timeframes under consideration (in YYYY-MM-DD,
    YYYY-MM or YYYY format)
    :returns: a list with the names of all the metrics that were used

    Using multiple projects and timeframes is necessary here to produce collective csv files.
    """
    metrics = hlp.get_metrics_config()

    csv_contents = {}
    for metric in metrics.keys():
        csv_contents[metric] = {'0': 'timeframe'}

    for project in projects:
        logging.info(f'Calculating metrics for {project} data..')
        # Each metric dict is of the form {'<timeframe>': '<comma-separated values for different projects'}.
        # The special entry '0': '<comma-separated names of projects>' is for the csv header
        for metric in metrics.keys():
            csv_contents[metric]['0'] += f',{project}'

        for timeframe in timeframes:
            for metric in metrics.keys():
                if timeframe not in csv_contents[metric].keys():
                    csv_contents[metric][timeframe] = timeframe

            aggregated_data_dir = output_dir / f'{project}/blocks_per_entity'
            # Get mapped data for the year that corresponds to the timeframe, if such data exists
            # This is needed because the Gini coefficient is computed over all entities per each year.
            year = timeframe[:4]
            try:
                yearly_blocks_per_entity = hlp.get_blocks_per_entity_from_file(aggregated_data_dir / f'{year}.csv')
                yearly_entities = yearly_blocks_per_entity.keys()
            except FileNotFoundError:
                yearly_entities = set()
            try:
                # Get aggregated data for the defined timeframe, if such data exists
                blocks_per_entity = hlp.get_blocks_per_entity_from_file(aggregated_data_dir / f'{timeframe}.csv')
            except FileNotFoundError:
                blocks_per_entity = dict()

            results = {}
            # If the project data exist for the given timeframe, compute the metrics on them.
            if blocks_per_entity.keys():
                for entity in yearly_entities:
                    if entity not in blocks_per_entity.keys():
                        blocks_per_entity[entity] = 0

                for metric, args_dict in metrics.items():
                    func = eval(f'compute_{metric}')
                    results[metric] = func(blocks_per_entity, **args_dict) if args_dict else func(blocks_per_entity)
            else:
                for metric in metrics.keys():
                    results[metric] = ''

            for metric in metrics.keys():
                csv_contents[metric][timeframe] += f',{results[metric]}'

    for metric in metrics.keys():
        with open(output_dir / f'{metric}.csv', 'w') as f:
            f.write('\n'.join([i[1] for i in sorted(csv_contents[metric].items(), key=lambda x: x[0])]))

    return list(metrics.keys())
