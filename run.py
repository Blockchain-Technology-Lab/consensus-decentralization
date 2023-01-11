import sys
import json
import pathlib
from src.metrics.gini import compute_gini
from src.metrics.nakamoto_coefficient import compute_nakamoto_coefficient
from src.metrics.entropy import compute_entropy
from src.mappings.bitcoin import BitcoinMapping
from src.mappings.ethereum import EthereumMapping
from src.mappings.cardano import CardanoMapping
from src.mappings.tezos import TezosMapping


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
END_YEAR = 2023
PROJECTS = ledger_mapping.keys()


def analyze(projects, timeframe_argument):
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
                mapping_file = pathlib.Path.cwd() / f'src/ledgers/{project_name}/{year}.csv'
                if not mapping_file.is_file():
                    project_dir = str(pathlib.Path(__file__).parent.resolve()) + f'/src/ledgers/{project_name}'
                    with open(project_dir + '/data.json') as f:
                        data = json.load(f)
                    mapping = ledger_mapping[project_name](project_name, data)
                    mapping.process(year)
                with open(mapping_file) as f:
                    for line in f.readlines()[1:]:
                        row = (','.join([i for i in line.split(',')[:-1]]), line.split(',')[-1])
                        yearly_entities[year].add(row[0])

            # Get mapped data for the defined timeframe.
            try:
                with open(f'src/ledgers/{project_name}/{timeframe}.csv') as f:
                    blocks_per_entity = {}
                    for line in f.readlines()[1:]:
                        blocks_per_entity[line.split(',')[0]] = int(line.split(',')[1])
            except FileNotFoundError:
                project_dir = str(pathlib.Path(__file__).parent.resolve()) + f'/src/ledgers/{project_name}'
                with open(project_dir + '/data.json') as f:
                    data = json.load(f)
                mapping = ledger_mapping[project_name](project_name, data)
                blocks_per_entity = mapping.process(timeframe)

            # If the project data exist for the given timeframe, compute the metrics on them.
            if blocks_per_entity.keys():
                for entity in yearly_entities[timeframe[:4]]:
                    if entity not in blocks_per_entity.keys():
                        blocks_per_entity[entity] = 0

                gini = compute_gini(blocks_per_entity)
                nc = compute_nakamoto_coefficient(blocks_per_entity)
                entropy = compute_entropy(blocks_per_entity)
                max_entropy = compute_entropy({entity: 1 for entity in yearly_entities[year]})
                print(f'[{project_name:12} {timeframe:7}] \t Gini: {gini:.6f}   NC: {nc[0]:3} ({nc[1]:.2f}%)   Entropy: {entropy:.6f} ({100*entropy/max_entropy:.1f}% out of max {max_entropy:.6f})')
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


if __name__ == '__main__':
    if len(sys.argv) == 3:
        projects = [sys.argv[1]]
        timeframe = sys.argv[2]
    elif len(sys.argv) == 2:
        if sys.argv[1] in PROJECTS:
            projects = [sys.argv[1]]
            timeframe = False
        else:
            projects = PROJECTS
            timeframe = sys.argv[1]
    else:
        projects = PROJECTS
        timeframe = False

    analyze(projects, timeframe)
