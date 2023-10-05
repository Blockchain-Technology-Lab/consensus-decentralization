import argparse
import logging
from consensus_decentralization.aggregate import aggregate
from consensus_decentralization.map import apply_mapping
from consensus_decentralization.analyze import analyze
from consensus_decentralization.parse import parse
from consensus_decentralization.plot import plot
import consensus_decentralization.helper as hlp

logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)


def main(projects, timeframe, aggregate_by, force_map, make_plots, make_animated_plots, output_dir=hlp.OUTPUT_DIR):
    """
    Executes the entire pipeline (parsing, mapping, analyzing) for some projects and timeframes.
    :param projects: list of strings that correspond to the ledgers whose data should be analyzed
    :param timeframe: tuple of (start_date, end_date) where each date is a datetime.date object.
    :param aggregate_by: string that corresponds to the granularity that will be used for the analysis. It can be one
        of: day, week, month, year, all.
    :param force_map: bool. If True, then the parsing and mapping will be performed, regardless of whether
        mapped data for some or all of the projects already exist
    :param make_plots: bool. If True, then plots are generated and saved for the results
    :param make_animated_plots: bool. If True (and make_plots also True) then animated plots are also generated.
        Warning: generating animated plots might take a long time
    :param output_dir: pathlib.PosixPath object of the directory where the output data will be saved
    """
    logging.info(f"The ledgers that will be analyzed are: {','.join(projects)}")
    for project in projects:
        project_dir = output_dir / project
        project_dir.mkdir(parents=True, exist_ok=True)  # create project output directory if it doesn't already exist
        mapped_data_file = project_dir / 'mapped_data.json'
        if force_map or not mapped_data_file.is_file():
            parsed_data = parse(project=project, input_dir=hlp.RAW_DATA_DIR)
            mapped_data = apply_mapping(project=project, parsed_data=parsed_data, output_dir=output_dir)
        else:
            mapped_data = None
        aggregate(
            project=project,
            output_dir=output_dir,
            timeframe=timeframe,
            aggregate_by=aggregate_by,
            force_aggregate=force_map,
            mapped_data=mapped_data
        )

    used_metrics = analyze(
        projects=projects,
        aggregated_data_filename=hlp.get_blocks_per_entity_filename(aggregate_by=aggregate_by, timeframe=timeframe),
        output_dir=output_dir
    )

    if make_plots:
        plot(
            ledgers=projects,
            metrics=used_metrics,
            aggregated_data_filename=hlp.get_blocks_per_entity_filename(aggregate_by=aggregate_by, timeframe=timeframe),
            animated=make_animated_plots
        )


if __name__ == '__main__':
    default_ledgers = hlp.get_default_ledgers()
    start_date, end_date = hlp.get_default_start_end_dates()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--ledgers',
        nargs="*",
        type=str.lower,
        default=default_ledgers,
        choices=default_ledgers,
        help='The ledgers that will be analyzed.'
    )
    parser.add_argument(
        '--timeframe',
        nargs="*",
        type=hlp.valid_date,
        default=[start_date, end_date],
        help='The timeframe that will be analyzed. You can provide two values to mark the beginning and end of the '
             'time frame or a single value that encapsulates both.'
    )
    parser.add_argument(
        '--aggregate-by',
        nargs="?",
        type=str.lower,
        default='month',
        choices=['day', 'week', 'month', 'year', 'all'],
        help='The granularity that will be used for the analysis. It can be one of: "day", "week", "month", "year", '
             '"all" and by default it is month. Note that in the case of weekly aggregation, we consider a week to '
             'be 7 consecutive days, starting from the first day of the time period under consideration (so not '
             'necessarily Monday to Sunday). If "all" is chosen then no aggregation will be performed, meaning that '
             'the given timeframe will be treated as one unit of time in our analysis.'
    )
    parser.add_argument(
        '--force-map',
        action='store_true',
        help='Flag to specify whether to map the parsed data, regardless if the mapped data files exist.'
    )
    parser.add_argument(
        '--plot',
        action='store_true',
        help='Flag to specify whether to produce and save plots of the results.'
    )
    parser.add_argument(
        '--animated',
        action='store_true',
        help='Flag to specify whether to also generate animated plots.'
    )
    args = parser.parse_args()

    aggregate_by = args.aggregate_by
    timeframe = args.timeframe
    if len(timeframe) > 2:
        parser.error('Too many values given for --timeframe argument. Please provide one date to get a snapshot or '
                     'two dates to get a time series.')
    timeframe_start = hlp.get_timeframe_beginning(timeframe[0])
    timeframe_end = hlp.get_timeframe_end(timeframe[-1])
    if timeframe_end < timeframe_start:
        parser.error('Invalid --timeframe values. Please note that if providing a second date, it must occur after '
                     'the first date.')

    main(
        projects=args.ledgers,
        timeframe=(timeframe_start, timeframe_end),
        aggregate_by=aggregate_by,
        force_map=args.force_map,
        make_plots=args.plot,
        make_animated_plots=args.animated
    )

    logging.info('Done. Please check the output directory for results.')
