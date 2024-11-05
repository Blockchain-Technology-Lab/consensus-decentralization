import csv
import logging
import consensus_decentralization.helper as hlp
from consensus_decentralization.metrics.gini import compute_gini  # noqa: F401
from consensus_decentralization.metrics.nakamoto_coefficient import compute_nakamoto_coefficient  # noqa: F401
from consensus_decentralization.metrics.entropy import compute_entropy, compute_entropy_percentage  # noqa: F401
from consensus_decentralization.metrics.herfindahl_hirschman_index import compute_hhi  # noqa: F401
from consensus_decentralization.metrics.theil_index import compute_theil_index  # noqa: F401
from consensus_decentralization.metrics.max_power_ratio import compute_max_power_ratio  # noqa: F401
from consensus_decentralization.metrics.tau_index import compute_tau_index  # noqa: F401
from consensus_decentralization.metrics.total_entities import compute_total_entities  # noqa: F401


def analyze(projects, aggregated_data_filename, output_dir):
    """
    Calculates all available metrics for the given ledgers and timeframes. Outputs one file for each metric.
    :param projects: list of strings that correspond to the ledgers whose data should be analyzed
    :param aggregated_data_filename: string that corresponds to the name of the file that contains the aggregated data
    :returns: a list with the names of all the metrics that were used

    Using multiple projects and timeframes is necessary here to produce collective csv files.
    """
    logging.info('Calculating metrics on aggregated data..')
    metrics = hlp.get_metrics_config()
    metric_params = []
    for key, args in metrics.items():
        if args:
            for val in args:
                metric_params.append((f'{key}={val}', key, val))
        else:
            metric_params.append((key, key, None))
    metric_names = [name for name, _, _ in metric_params]

    aggregate_output = {}

    csv_contents = {}
    for metric in metric_names:
        # Each metric list is of the form [['<timeframe>', '<comma-separated values for different projects']].
        # The special entry ['timeframe', '<comma-separated names of projects>'] is for the csv header
        csv_contents[metric] = [['timeframe'] + projects]

    for column_index, project in enumerate(projects):
        logging.info(f'Calculating {project} metrics')
        aggregate_output[project] = {}
        aggregated_data_dir = output_dir / project / 'blocks_per_entity'
        dates, blocks_per_entity = hlp.get_blocks_per_entity_from_file(aggregated_data_dir / aggregated_data_filename)
        for date in dates:
            aggregate_output[project][date] = {}

        dates_with_blocks = set()
        for block_values in blocks_per_entity.values():
            for date, nblocks in block_values.items():
                if nblocks > 0:
                    dates_with_blocks.add(date)

        for row_index, date in enumerate(dates):
            date_blocks_per_entity = {}
            if column_index == 0:
                for metric_name, _, _ in metric_params:
                    csv_contents[metric_name].append([date])
            if date in dates_with_blocks:
                for entity, block_values in blocks_per_entity.items():
                    try:
                        date_blocks_per_entity[entity] = block_values[date]
                    except KeyError:
                        pass
            sorted_date_blocks = sorted(date_blocks_per_entity.values(), reverse=True)

            for metric_name, metric, param in metric_params:
                func = eval(f'compute_{metric}')
                if param:
                    result = func(sorted_date_blocks, param)
                else:
                    result = func(sorted_date_blocks)
                csv_contents[metric_name][row_index + 1].append(result)
                aggregate_output[project][date][metric_name] = result

    for metric in metric_names:
        with open(output_dir / f'{metric}.csv', 'w') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerows(csv_contents[metric])

    clustering_flag = hlp.get_config_data()['analyze_flags']['clustering']
    aggregate_csv_output = [['ledger', 'date', 'clustering'] + metric_names]
    for project, timeframes in aggregate_output.items():
        for date, results in timeframes.items():
            metric_values = [results[metric] for metric in metric_names]
            if any(metric_values):
                aggregate_csv_output.append([project, date, clustering_flag] + metric_values)
    with open(output_dir / 'output.csv', 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(aggregate_csv_output)

    return metric_names
