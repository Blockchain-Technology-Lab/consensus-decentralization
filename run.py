import argparse
import pathlib
import re
from src.metrics.gini import compute_gini
from src.metrics.nakamoto_coefficient import compute_nakamoto_coefficient
from src.metrics.entropy import compute_entropy
from src.mappings.bitcoin import BitcoinMapping
from src.mappings.ethereum import EthereumMapping
from src.mappings.cardano import CardanoMapping
from src.mappings.tezos import TezosMapping
from src.helpers.helper import OUTPUT_DIR
from src.parse import parse

ledger_mapping = {
    'bitcoin': BitcoinMapping,
    'ethereum': EthereumMapping,
    'bitcoin_cash': BitcoinMapping,
    'dogecoin': BitcoinMapping,
    'cardano': CardanoMapping,
    'litecoin': BitcoinMapping,
    'zcash': BitcoinMapping,
    'tezos': TezosMapping,
    'dash': BitcoinMapping,
}

START_YEAR = 2018
END_YEAR = 2024
PROJECTS = ledger_mapping.keys()

ENTROPY_ALPHA = 1  # -1: min entropy, 1: Shannon entropy, 2: collision entropy, 0: Hartley entropy


def analyze(projects, timeframe_argument):
    """
    todo complete function docstring

    :param projects:
    :param timeframe_argument:
    """
    gini_csv = {'0': 'timeframe'}
    nc_csv = {'0': 'timeframe'}
    entropy_csv = {'0': 'timeframe'}

    for project_name in projects:
        # Each metric dict is of the form {'<timeframe>': '<comma-separated values for different projects'}.
        # The special entry '0': '<comma-separated names of projects>' is for the csv title.
        gini_csv['0'] += f',{project_name}'
        nc_csv['0'] += f',{project_name}'
        entropy_csv['0'] += f',{project_name}'

        yearly_entities = {}

        # Create the list of all timeframes to analyze
        if timeframe_argument:
            timeframes = [timeframe_argument]
        else:
            timeframes = []
            for year in range(START_YEAR, END_YEAR):
                for month in range(1, 13):
                    timeframes.append(f'{year}-{str(month).zfill(2)}')

        project_dir = str(pathlib.Path(__file__).parent.resolve()) + f'/output/{project_name}'
        mapping = ledger_mapping[project_name](project_name, project_dir)

        for timeframe in timeframes:
            if timeframe not in gini_csv.keys():
                gini_csv[timeframe] = timeframe
                nc_csv[timeframe] = timeframe
                entropy_csv[timeframe] = timeframe

            # Get mapped data for the year that corresponds to the timeframe.
            # This is needed because the Gini coefficient is computed over all entities per each year.
            year = timeframe[:4]
            if year not in yearly_entities.keys():
                yearly_entities[year] = set()
                mapping_file = pathlib.Path(f'{mapping.io_dir}/{year}.csv')
                if not mapping_file.is_file():
                    mapping.perform_mapping(year)
                with open(mapping_file) as f:
                    for line in f.readlines()[1:]:
                        row = (','.join([i for i in line.split(',')[:-1]]), line.split(',')[-1])
                        yearly_entities[year].add(row[0])

            # Get mapped data for the defined timeframe.
            try:
                with open(f'output/{project_name}/{timeframe}.csv') as f:
                    blocks_per_entity = {}
                    for line in f.readlines()[1:]:
                        blocks_per_entity[line.split(',')[0]] = int(line.split(',')[1])
            except FileNotFoundError:
                blocks_per_entity = mapping.perform_mapping(timeframe)

            # If the project data exist for the given timeframe, compute the metrics on them.
            if blocks_per_entity.keys():
                for entity in yearly_entities[timeframe[:4]]:
                    if entity not in blocks_per_entity.keys():
                        blocks_per_entity[entity] = 0
                gini = compute_gini(blocks_per_entity)
                nc = compute_nakamoto_coefficient(blocks_per_entity)
                entropy = compute_entropy(blocks_per_entity, ENTROPY_ALPHA)
                max_entropy = compute_entropy({entity: 1 for entity in yearly_entities[year]}, ENTROPY_ALPHA)
                entropy_percentage = 100 * entropy / max_entropy if max_entropy != 0 else 0
                print(
                    f'[{project_name:12} {timeframe:7}] \t Gini: {gini:.6f}   NC: {nc[0]:3} ({nc[1]:.2f}%)   '
                    f'Entropy: {entropy:.6f} ({entropy_percentage:.1f}% out of max {max_entropy:.6f})'
                )
            else:
                gini, nc, entropy = '', ('', ''), ''
                print(f'[{project_name:12} {timeframe:7}] No data')

            gini_csv[timeframe] += f',{gini}'
            nc_csv[timeframe] += f',{nc[0]}'
            entropy_csv[timeframe] += f',{entropy}'

    with open(OUTPUT_DIR / 'gini.csv', 'w') as f:
        f.write('\n'.join([i[1] for i in sorted(gini_csv.items(), key=lambda x: x[0])]))
    with open(OUTPUT_DIR / 'nc.csv', 'w') as f:
        f.write('\n'.join([i[1] for i in sorted(nc_csv.items(), key=lambda x: x[0])]))
    with open(OUTPUT_DIR / 'entropy.csv', 'w') as f:
        f.write('\n'.join([i[1] for i in sorted(entropy_csv.items(), key=lambda x: x[0])]))


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
    parser.add_argument(  # todo allow user to input custom range for timeframe argument
        '--timeframe',
        nargs="?",
        type=valid_date,
        default=None,
        help='The timeframe that will be analyzed.'
    )
    args = parser.parse_args()

    timeframe = args.timeframe
    projects = args.ledgers

    print(f"The ledgers that will be analyzed are: {','.join(projects)}")
    for project in projects:
        parse(project)
    analyze(projects, timeframe)  # todo separate into different map + analyze functions
