import csv
import logging
import consensus_decentralization.helper as hlp
from consensus_decentralization.metrics.gini import compute_gini  # noqa: F401
from consensus_decentralization.metrics.nakamoto_coefficient import compute_nakamoto_coefficient  # noqa: F401
from consensus_decentralization.metrics.entropy import compute_entropy, compute_entropy_percentage  # noqa: F401
from consensus_decentralization.metrics.herfindahl_hirschman_index import compute_hhi  # noqa: F401


def analyze(projects, aggregated_data_filename, output_dir):
    """
    Calculates all available metrics for the given ledgers and timeframes. Outputs one file for each metric.
    :param projects: list of strings that correspond to the ledgers whose data should be analyzed
    :param aggregated_data_filename: string that corresponds to the name of the file that contains the aggregated data
    :returns: a list with the names of all the metrics that were used

    Using multiple projects and timeframes is necessary here to produce collective csv files.
    """
    logging.info(f'Calculating metrics on aggregated data..')
    metrics = hlp.get_metrics_config()

    csv_contents = {}
    for metric, args_dict in metrics.items():
        # Each metric list is of the form [['<timeframe>', '<comma-separated values for different projects']].
        # The special entry ['timeframe', '<comma-separated names of projects>'] is for the csv header
        csv_contents[metric] = [['timeframe'] + projects]

        for column_index, project in enumerate(projects):
            aggregated_data_dir = output_dir / project / 'blocks_per_entity'
            time_chunks, blocks_per_entity = hlp.get_blocks_per_entity_from_file(aggregated_data_dir / aggregated_data_filename)

            for row_index, time_chunk in enumerate(time_chunks):
                if column_index == 0:
                    csv_contents[metric].append([time_chunk])
                time_chunk_blocks_per_entity = {entity: blocks[row_index] for entity, blocks in blocks_per_entity.items()}
                func = eval(f'compute_{metric}')
                result = func(time_chunk_blocks_per_entity, **args_dict) if args_dict else func(
                    time_chunk_blocks_per_entity)
                csv_contents[metric][row_index + 1].append(result)

        with open(output_dir / f'{metric}.csv', 'w') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerows(csv_contents[metric])

    return list(metrics.keys())
