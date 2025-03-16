import logging
from consensus_decentralization.aggregate import aggregate
from consensus_decentralization.map import apply_mapping
from consensus_decentralization.analyze import analyze
from consensus_decentralization.parse import parse
from consensus_decentralization.plot import plot
import consensus_decentralization.helper as hlp

logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)


def process_data(force_map, ledger_dir, ledger, output_dir):
    clustering_flag = hlp.get_clustering_flag()
    mapped_data_file = ledger_dir / hlp.get_mapped_data_filename(clustering_flag)
    if force_map or not mapped_data_file.is_file():
        parsed_data = parse(ledger, input_dir=hlp.RAW_DATA_DIR)
        return apply_mapping(ledger, parsed_data=parsed_data, output_dir=output_dir)
    return None


def main(ledgers, timeframe, estimation_window, frequency, interim_dir=hlp.INTERIM_DIR,
         results_dir=hlp.RESULTS_DIR):
    """
    Executes the entire pipeline (parsing, mapping, analyzing) for some projects and timeframes.
    :param ledgers: list of strings that correspond to the ledgers whose data should be analyzed
    :param timeframe: tuple of (start_date, end_date) where each date is a datetime.date object.
    :param estimation_window: int or None. The number of days to consider for the estimation of the power of an entity (
        i.e. counting all the blocks produced by the entity within estimation_window days). If None, the entire
        timeframe will be considered.
    :param frequency: int or None. The number of days to consider for the frequency of the analysis (i.e. the number
        of days between each data point considered in the analysis). If None, only one data point will be considered,
        spanning the entire timeframe (i.e. it needs to be combined with None estimation_window).
    :param interim_dir: pathlib.PosixPath object of the directory where the output data will be saved
    """
    logging.info(f"The ledgers that will be analyzed are: {','.join(ledgers)}")

    force_map = hlp.get_force_map_flag()

    for ledger in ledgers:
        ledger_dir = interim_dir / ledger
        ledger_dir.mkdir(parents=True, exist_ok=True)  # create ledger output directory if it doesn't already exist

        mapped_data = process_data(force_map, ledger_dir, ledger, interim_dir)

        aggregate(
            ledger,
            interim_dir,
            timeframe,
            estimation_window,
            frequency,
            force_map,
            mapped_data=mapped_data
        )

    aggregated_data_filename = hlp.get_blocks_per_entity_filename(timeframe, estimation_window, frequency)
    metrics_dir = results_dir / 'metrics'
    metrics_dir.mkdir(parents=True, exist_ok=True)

    used_metrics = analyze(
        projects=ledgers,
        aggregated_data_filename=aggregated_data_filename,
        input_dir=interim_dir,
        output_dir=metrics_dir
    )

    if hlp.get_plot_flag():
        figures_dir = results_dir / 'figures'
        figures_dir.mkdir(parents=True, exist_ok=True)
        plot(
            ledgers=ledgers,
            metrics=used_metrics,
            aggregated_data_filename=aggregated_data_filename,
            animated=hlp.get_plot_config_data()['animated'],
            metrics_dir=metrics_dir,
            figures_dir=figures_dir
        )


if __name__ == '__main__':
    ledgers = hlp.get_ledgers()

    estimation_window, frequency = hlp.get_estimation_window_and_frequency()

    results_dir = hlp.get_results_dir(estimation_window, frequency)
    results_dir.mkdir(parents=True, exist_ok=True)

    start_date, end_date = hlp.get_start_end_dates()
    timeframe_start = hlp.get_timeframe_beginning(start_date)
    timeframe_end = hlp.get_timeframe_end(end_date)
    if timeframe_end < timeframe_start:
        raise ValueError('Invalid --timeframe values. Please note that if providing a second date, it must occur after '
                         'the first date.')
    timeframe = (timeframe_start, timeframe_end)

    main(ledgers, timeframe, estimation_window, frequency, results_dir=results_dir)

    logging.info('Done. Please check the output directory for results.')
