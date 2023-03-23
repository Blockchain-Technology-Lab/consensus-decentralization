import argparse
from src.map import ledger_mapping, apply_mapping
from src.analyze import analyze
from src.parse import parse
from src.helpers.helper import valid_date

PROJECTS = ledger_mapping.keys()

START_YEAR = 2018
END_YEAR = 2024


def main(projects, timeframes, force_parse, entropy_alpha):
    """
    Executes the entire pipeline (parsing, mapping, analyzing) for some projects and timeframes.
    :param projects: list of strings that correspond to the ledgers whose data should be analyzed
    :param timeframes: list of strings that correspond to the timeframes under consideration (in YYYY-MM-DD,
    YYYY-MM or YYYY format)
    :param force_parse: if True, then raw data will be parsed, regardless of whether parsed data for some or all of the
    projects already exist
    :param entropy_alpha: float that corresponds to the alpha parameter for the entropy calculation
    """
    print(f"The ledgers that will be analyzed are: {','.join(projects)}")
    for project in projects:
        parse(project, force_parse)
        apply_mapping(project, timeframes)

    analyze(projects, timeframes, entropy_alpha)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # todo maybe move parsing to helper module
    parser.add_argument(
        '--ledgers',
        nargs="*",
        type=str.lower,
        default=PROJECTS,
        choices=[ledger for ledger in PROJECTS],
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
        '--force-parse',
        action='store_true',
        help='Flag to specify whether to parse the raw data, regardless if the parsed data file exists.'
    )
    parser.add_argument(
        '--entropy-alpha',
        nargs="?",
        type=int,
        default=1,
        help='The alpha parameter for entropy computation. Default Shannon entropy. Examples: -1: min, 0: Hartley, '
             '1: Shannon, 2: collision.'
    )
    args = parser.parse_args()

    projects = args.ledgers

    timeframe = args.timeframe
    if timeframe:
        timeframes = [timeframe]
    else:
        timeframes = []
        for year in range(START_YEAR, END_YEAR):
            for month in range(1, 13):
                timeframes.append(f'{year}-{str(month).zfill(2)}')

    main(projects, timeframes, args.force_parse, args.entropy_alpha)
