import argparse
import re
from src.map import ledger_mapping, apply_mapping
from src.analyze import analyze
from src.parse import parse

PROJECTS = ledger_mapping.keys()

START_YEAR = 2018
END_YEAR = 2024


def valid_date(date_string):
    # note: this regex assumes that all months have 31 days, so a few invalid dates get accepted (but most don't)
    pattern = r'\d{4}(\-(0[1-9]|1[012]))?(\-(0[1-9]|[12][0-9]|3[01]))?'
    match = re.fullmatch(pattern, date_string)
    if match is None:
        raise argparse.ArgumentTypeError("Please use the format YYYY-MM-DD for the timeframe argument "
                                         "(day and / or month can be omitted).")
    return date_string


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

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

    print(f"The ledgers that will be analyzed are: {','.join(projects)}")
    for project in projects:
        parse(project)
        for timeframe in timeframes:
            apply_mapping(project, timeframe)
            analyze(project, timeframe)
