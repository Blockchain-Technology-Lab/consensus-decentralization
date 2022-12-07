import sys
import json
import pathlib
from collections import defaultdict
from metrics.gini import compute_gini
from metrics.nc import compute_nc
from metrics.entropy import compute_entropy
from mappings.bitcoin import process as bitcoin_mapping
from mappings.ethereum import process as ethereum_mapping
from mappings.cardano import process as cardano_mapping
from mappings.tezos import process as tezos_mapping

ledger_mapping = {
    'bitcoin': bitcoin_mapping,
    'ethereum': ethereum_mapping,
    'bitcoin_cash': bitcoin_mapping,
    'dogecoin': bitcoin_mapping,
    'cardano': cardano_mapping,
    'litecoin': bitcoin_mapping,
    'zcash': bitcoin_mapping,
    'tezos': tezos_mapping,
    'dash': bitcoin_mapping,
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
        gini_csv['0'] += ',' + project_name
        nc_csv['0'] += ',' + project_name
        entropy_csv['0'] += ',' + project_name

        yearly_entities = {}

        # Create the list of all timeframes to analyze
        if timeframe_argument:
            timeframes = [timeframe_argument]
        else:
            timeframes = []
            for year in range(START_YEAR, END_YEAR):
                for month in range(1, 13):
                    timeframes.append('{}-{}'.format(year, str(month).zfill(2)))

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
                try:
                    with open('ledgers/{}/{}.csv'.format(project_name, year)) as f:
                        for line in f.readlines()[1:]:
                            row = (','.join([i for i in line.split(',')[:-1]]), line.split(',')[-1])
                            yearly_entities[year].add(row[0])
                except FileNotFoundError:
                    project_dir = str(pathlib.Path(__file__).parent.resolve()) + '/ledgers/{}'.format(project_name)
                    with open(project_dir + '/data.json') as f:
                        data = json.load(f)
                    ledger_mapping[project_name](project_name, data, year)

            # Get mapped data for the defined timeframe.
            try:
                with open('ledgers/{}/{}.csv'.format(project_name, timeframe)) as f:
                    blocks_per_entity = {}
                    for line in f.readlines()[1:]:
                        blocks_per_entity[line.split(',')[0]] = int(line.split(',')[1])
            except FileNotFoundError:
                project_dir = str(pathlib.Path(__file__).parent.resolve()) + '/ledgers/{}'.format(project_name)
                with open(project_dir + '/data.json') as f:
                    data = json.load(f)
                blocks_per_entity = ledger_mapping[project_name](project_name, data, timeframe)

            # If the project data exist for the given timeframe, compute the metrics on them.
            if blocks_per_entity.keys():
                for entity in yearly_entities[timeframe[:4]]:
                    if entity not in blocks_per_entity.keys():
                        blocks_per_entity[entity] = 0

                gini = compute_gini(blocks_per_entity)
                nc = compute_nc(blocks_per_entity)
                entropy = compute_entropy(blocks_per_entity)
            else:
                gini, nc, entropy = '', ('', ''), ''

            gini_csv[timeframe] += ',{}'.format(gini)
            nc_csv[timeframe] += ',{}'.format(nc[0])
            entropy_csv[timeframe] += ',{}'.format(entropy)

            if gini:
                print('[{0:12} {1:7}] \t Gini: {2:.6f}   NC: {3:3} ({4:.2f}%)   Entropy: {5:.6f}'.format(project_name, timeframe, gini, nc[0], nc[1], entropy))
            else:
                print('[{0:12} {1:7}] No data'.format(project_name, timeframe))

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
            timeframe = sys.argv[1]
    else:
        projects = PROJECTS
        timeframe = False

    analyze(projects, timeframe)
