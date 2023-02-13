import pathlib
import argparse
from src.metrics.gini import compute_gini
from src.metrics.nakamoto_coefficient import compute_nakamoto_coefficient
from src.metrics.entropy import compute_entropy
from src.mappings.bitcoin import BitcoinMapping
from src.mappings.ethereum import EthereumMapping
from src.mappings.cardano import CardanoMapping
from src.mappings.tezos import TezosMapping
from src.parsers.default_parser import DefaultParser
from src.parsers.cardano_parser import CardanoParser
from src.parsers.dummy_parser import DummyParser
from src.helpers.helper import OUTPUT_DIR

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

ledger_parser = {
    'bitcoin': DefaultParser,
    'ethereum': DummyParser,
    'bitcoin_cash': DefaultParser,
    'dogecoin': DefaultParser,
    'cardano': CardanoParser,
    'litecoin': DefaultParser,
    'zcash': DefaultParser,
    'tezos': DummyParser,
    'dash': DefaultParser,
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
                entropy_percentage = 100*entropy/max_entropy if max_entropy != 0 else 0
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

    with open('gini.csv', 'w') as f:
        f.write('\n'.join([i[1] for i in sorted(gini_csv.items(), key=lambda x: x[0])]))
    with open('nc.csv', 'w') as f:
        f.write('\n'.join([i[1] for i in sorted(nc_csv.items(), key=lambda x: x[0])]))
    with open('entropy.csv', 'w') as f:
        f.write('\n'.join([i[1] for i in sorted(entropy_csv.items(), key=lambda x: x[0])]))


def parse(projects, force_parse=False):
    """
    Parse raw data, unless already parsed
    :param projects: the ledgers whose data should be parsed
    :param force_parse: if True, then raw data will be parsed, regardless of whether parsed data for the some or all of
     the projects already exist
    """
    for project in projects:
        parsed_data_file = OUTPUT_DIR / project / 'parsed_data.json'
        if force_parse or not parsed_data_file.is_file():
            parser = ledger_parser[project](project)
            parser.parse()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--timeframe', type=str, required=False)
    parser.add_argument('--project', type=str, required=False)

    args = parser.parse_args()

    timeframe = args.timeframe
    projects = [args.project]
    if not projects[0]:
        projects = PROJECTS

    print(projects)
    parse(projects)
    analyze(projects, timeframe)  # todo separate into different map + analyze functions
