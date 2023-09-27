import argparse
import logging
from consensus_decentralization.map import apply_mapping
from consensus_decentralization.analyze import analyze
from consensus_decentralization.parse import parse
from consensus_decentralization.plot import plot
import consensus_decentralization.helper as hlp

logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)


def main(projects, timeframes, force_parse, force_map, make_plots, make_animated_plots, output_dir=hlp.OUTPUT_DIR):
    """
    Executes the entire pipeline (parsing, mapping, analyzing) for some projects and timeframes.
    :param projects: list of strings that correspond to the ledgers whose data should be analyzed
    :param timeframes: list of strings that correspond to the timeframes under consideration (in YYYY-MM-DD,
        YYYY-MM or YYYY format)
    :param force_parse: bool. If True, then raw data will be parsed, regardless of whether parsed data for some or all
        of the projects already exist
    :param force_map: bool. If True, then the mapping will be performed, regardless of whether
        mapped data for some or all of the projects already exist
    :param make_plots: bool. If True, then plots are generated and saved for the results
    :param make_animated_plots: bool. If True (and make_plots also True) then animated plots are also generated.
        Warning: generating animated plots might take a long time
    """
    logging.info(f"The ledgers that will be analyzed are: {','.join(projects)}")
    for project in projects:
        parse(project, hlp.RAW_DATA_DIR, output_dir, force_parse)
        apply_mapping(project, timeframes, output_dir, force_map)

    used_metrics = analyze(projects, timeframes, output_dir)

    if make_plots:
        plot(projects, used_metrics, make_animated_plots)


if __name__ == '__main__':
    default_ledgers = hlp.get_default_ledgers()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--ledgers',
        nargs="*",
        type=str.lower,
        default=default_ledgers,
        choices=[ledger for ledger in default_ledgers],
        help='The ledgers that will be analyzed.'
    )
    parser.add_argument(
        '--timeframe',
        nargs="?",
        type=hlp.valid_date,
        default=None,
        help='The timeframe that will be analyzed.'
    )
    parser.add_argument(
        '--force-parse',
        action='store_true',
        help='Flag to specify whether to parse the raw data, regardless if the parsed data file exists.'
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

    projects = args.ledgers

    start_year, end_year = hlp.get_start_end_years()

    timeframe = args.timeframe
    if timeframe:
        timeframes = [timeframe]
    else:
        timeframes = []
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                timeframes.append(f'{year}-{str(month).zfill(2)}')

    main(projects, timeframes, args.force_parse, args.force_map, args.plot, args.animated)
    logging.info('Done. Please check the output directory for results.')
