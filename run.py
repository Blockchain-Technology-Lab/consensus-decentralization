import logging
from consensus_decentralization.aggregate import aggregate
from consensus_decentralization.map import apply_mapping
from consensus_decentralization.analyze import analyze
from consensus_decentralization.parse import parse
from consensus_decentralization.plot import plot
import consensus_decentralization.helper as hlp

logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)


def process_data(force_map, ledger_dir, ledger, output_dir):
    mapped_data_file = ledger_dir / 'mapped_data.json'
    if force_map or not mapped_data_file.is_file():
        parsed_data = parse(ledger, input_dir=hlp.RAW_DATA_DIR)
        apply_mapping(ledger, parsed_data=parsed_data, output_dir=output_dir)


def main(ledgers, timeframe, granularity, output_dir=hlp.OUTPUT_DIR):
    """
    Executes the entire pipeline (parsing, mapping, analyzing) for some projects and timeframes.
    :param ledgers: list of strings that correspond to the ledgers whose data should be analyzed
    :param timeframe: tuple of (start_date, end_date) where each date is a datetime.date object.
    :param granularity: string that corresponds to the granularity that will be used for the analysis. It can be one
        of: day, week, month, year, all.
    :param force_map: bool. If True, then the parsing and mapping will be performed, regardless of whether
        mapped data for some or all of the projects already exist
    :param make_plots: bool. If True, then plots are generated and saved for the results
    :param make_animated_plots: bool. If True (and make_plots also True) then animated plots are also generated.
        Warning: generating animated plots might take a long time
    :param output_dir: pathlib.PosixPath object of the directory where the output data will be saved
    """
    logging.info(f"The ledgers that will be analyzed are: {','.join(ledgers)}")

    force_map = hlp.get_force_map_flag()

    for ledger in ledgers:
        ledger_dir = output_dir / ledger
        ledger_dir.mkdir(parents=True, exist_ok=True)  # create ledger output directory if it doesn't already exist

        process_data(force_map, ledger_dir, ledger, output_dir)

        aggregate(
            ledger,
            output_dir,
            timeframe,
            granularity,
            force_map
        )

    used_metrics = analyze(
        ledgers,
        aggregated_data_filename=hlp.get_blocks_per_entity_filename(granularity, timeframe),
        output_dir=output_dir
    )

    if hlp.get_plot_flag():
        plot(
            ledgers,
            metrics=used_metrics,
            aggregated_data_filename=hlp.get_blocks_per_entity_filename(granularity, timeframe),
            animated=hlp.get_plot_config_data()['animated']
        )


if __name__ == '__main__':
    ledgers = hlp.get_ledgers()

    granularity = hlp.get_granularity()

    start_date, end_date = hlp.get_start_end_dates()
    timeframe_start = hlp.get_timeframe_beginning(start_date)
    timeframe_end = hlp.get_timeframe_end(end_date)
    if timeframe_end < timeframe_start:
        raise ValueError('Invalid --timeframe values. Please note that if providing a second date, it must occur after '
                         'the first date.')
    timeframe = (timeframe_start, timeframe_end)

    main(ledgers, timeframe, granularity)

    logging.info('Done. Please check the output directory for results.')
