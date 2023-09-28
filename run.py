import argparse
import logging
from consensus_decentralization.aggregate import aggregate
from consensus_decentralization.map import apply_mapping
from consensus_decentralization.analyze import analyze
from consensus_decentralization.parse import parse
from consensus_decentralization.plot import plot
from consensus_decentralization.helper import valid_date, RAW_DATA_DIR, OUTPUT_DIR, get_default_ledgers, \
    get_start_end_dates

logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)


def main(projects, timeframes, force_map, make_plots, make_animated_plots, output_dir=OUTPUT_DIR):
    """
    Executes the entire pipeline (parsing, mapping, analyzing) for some projects and timeframes.
    :param projects: list of strings that correspond to the ledgers whose data should be analyzed
    :param timeframes: list of strings that correspond to the timeframes under consideration (in YYYY-MM-DD,
        YYYY-MM or YYYY format)
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
            parsed_data = parse(project=project, input_dir=RAW_DATA_DIR)
            mapped_data = apply_mapping(project=project, parsed_data=parsed_data, output_dir=output_dir)
        else:
            mapped_data = None
        aggregate(project=project, output_dir=output_dir, timeframes=timeframes, force_aggregate=force_map, mapped_data=mapped_data)

    used_metrics = analyze(projects, timeframes, output_dir)

    if make_plots:
        plot(projects, used_metrics, make_animated_plots)


if __name__ == '__main__':
    default_ledgers = get_default_ledgers()

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
        type=valid_date,
        default=None,
        help='The timeframe that will be analyzed.'
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

    start_date, end_date = get_start_end_dates()

    timeframe = args.timeframe
    if timeframe:
        timeframes = [timeframe]
    else:
        timeframes = []
        for year in range(start_date, end_date + 1):
            for month in range(1, 13):
                timeframes.append(f'{year}-{str(month).zfill(2)}')

    main(projects=projects, timeframes=timeframes, force_map=args.force_map, make_plots=args.plot,
         make_animated_plots=args.animated)
    logging.info('Done. Please check the output directory for results.')
