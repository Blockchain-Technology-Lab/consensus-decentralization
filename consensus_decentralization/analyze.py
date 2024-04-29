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
    metric_values = []
    metric_names = []
    for key, args in metrics.items():
        if args:
            for val in args:
                metric_values.append((key, val))
                metric_names.append(f'{key}={val}')
        else:
            metric_values.append((key, None))
            metric_names.append(key)

    aggregate_output = {}

    csv_contents = {}
    for metric in metric_names:
        # Each metric list is of the form [['<timeframe>', '<comma-separated values for different projects']].
        # The special entry ['timeframe', '<comma-separated names of projects>'] is for the csv header
        csv_contents[metric] = [['timeframe'] + projects]

    for column_index, project in enumerate(projects):
        aggregate_output[project] = {}
        aggregated_data_dir = output_dir / project / 'blocks_per_entity'
        time_chunks, blocks_per_entity = hlp.get_blocks_per_entity_from_file(aggregated_data_dir / aggregated_data_filename)
        for time_chunk in time_chunks:
            aggregate_output[project][time_chunk] = {}

        chunks_with_blocks = set()
        for block_values in blocks_per_entity.values():
            for tchunk, nblocks in block_values.items():
                if nblocks > 0:
                    chunks_with_blocks.add(tchunk)
        for metric, param in metric_values:
            if param:
                metric_name = f'{metric}={param}'
            else:
                metric_name = metric

            for row_index, time_chunk in enumerate(time_chunks):
                time_chunk_blocks_per_entity = {}
                if column_index == 0:
                    csv_contents[metric_name].append([time_chunk])
                if time_chunk in chunks_with_blocks:
                    for entity, block_values in blocks_per_entity.items():
                        try:
                            time_chunk_blocks_per_entity[entity] = block_values[time_chunk]
                        except KeyError:
                            time_chunk_blocks_per_entity[entity] = 0
                func = eval(f'compute_{metric}')
                if param:
                    result = func(time_chunk_blocks_per_entity, param)
                else:
                    result = func(time_chunk_blocks_per_entity)
                csv_contents[metric_name][row_index + 1].append(result)
                aggregate_output[project][time_chunk][metric_name] = result

    for metric in metric_names:
        with open(output_dir / f'{metric}.csv', 'w') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerows(csv_contents[metric])

    clustering_flag = hlp.get_config_data()['analyze_flags']['clustering']
    aggregate_csv_output = [['ledger', 'snapshot_date', 'clustering'] + metric_names]
    for project, timeframes in aggregate_output.items():
        for time_chunk, results in timeframes.items():
            metric_values = [results[metric] for metric in metric_names]
            if any(metric_values):
                aggregate_csv_output.append([project, time_chunk, clustering_flag] + metric_values)
    with open(output_dir / 'output.csv', 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(aggregate_csv_output)

    return metric_names
