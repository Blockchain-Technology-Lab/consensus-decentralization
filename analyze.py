from process import process
from metrics.gini import compute_gini
from metrics.nc import compute_nc
from metrics.entropy import compute_entropy
from collections import defaultdict
import sys
import json
import pathlib


START_YEAR = 2018
END_YEAR = 2023
PROJECTS = [
    'bitcoin',
    'ethereum',
    'bitcoin_cash',
    'dogecoin',
    'cardano',
    'litecoin',
    'tezos',
    'zcash',
]


def analyze_data(project_name, timeframe, yearly_entities):
    blocks_per_entity = {}
    with open('ledgers/{}/{}.csv'.format(project_name, timeframe)) as f:
        for idx, line in enumerate(f.readlines()):
            if idx > 0:
                row = (','.join([i for i in line.split(',')[:-1]]), line.split(',')[-1])
                blocks_per_entity[row[0]] = int(row[1])

        if blocks_per_entity.keys():
            for entity in yearly_entities[timeframe[:4]]:
                if entity not in blocks_per_entity.keys():
                    blocks_per_entity[entity] = 0

            gini = compute_gini(blocks_per_entity)
            nc = compute_nc(blocks_per_entity)
            entropy = compute_entropy(blocks_per_entity)
        else:
            gini, nc, entropy = '', ('', ''), ''

        return gini, nc, entropy


def analyze(projects, timeframe_argument=False):
    gini_csv = {'0': 'timeframe'}
    nc_csv = {'0': 'timeframe'}
    entropy_csv = {'0': 'timeframe'}

    for project_name in projects:
        gini_csv['0'] += ',' + project_name
        nc_csv['0'] += ',' + project_name
        entropy_csv['0'] += ',' + project_name

        yearly_entities = {}
        if timeframe_argument:
            timeframes = [timeframe_argument]
            start = int(timeframe_argument[:4])
            end = start + 1
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

            year = timeframe[:4]
            if year not in yearly_entities.keys():
                yearly_entities[year] = set()
                try:
                    with open('ledgers/{}/{}.csv'.format(project_name, year)) as f:
                        for idx, line in enumerate(f.readlines()):
                            if idx > 0:
                                row = (','.join([i for i in line.split(',')[:-1]]), line.split(',')[-1])
                                yearly_entities[year].add(row[0])
                except FileNotFoundError:
                    project_dir = str(pathlib.Path(__file__).parent.resolve()) + '/ledgers/{}'.format(project_name)
                    with open(project_dir + '/data.json') as f:
                        data = json.load(f)
                    process(project_name, data, year)
            
            gini, nc, entropy = analyze_data(project_name, timeframe, yearly_entities)

            gini_csv[timeframe] += ',{}'.format(gini)
            nc_csv[timeframe] += ',{}'.format(nc[0])
            entropy_csv[timeframe] += ',{}'.format(entropy)

            if gini != '':
                print('[{0:12} {1:7}] \t Gini: {2:.6f}   NC: {3:3} ({4:.2f}%)   Entropy: {5:.6f}'.format(project_name, timeframe, gini, nc[0], nc[1], entropy))
            else:
                print('[{}, {}] No data'.format(project_name, timeframe))

    with open('gini.csv', 'w') as f:
        f.write('\n'.join([i[1] for i in sorted(gini_csv.items(), key=lambda x: x[0])]))
    with open('nc.csv', 'w') as f:
        f.write('\n'.join([i[1] for i in sorted(nc_csv.items(), key=lambda x: x[0])]))
    with open('entropy.csv', 'w') as f:
        f.write('\n'.join([i[1] for i in sorted(entropy_csv.items(), key=lambda x: x[0])]))

if __name__ == '__main__':
    try:
        if sys.argv[1] in PROJECTS:
            projects = [sys.argv[1]]
        else:
            projects = PROJECTS
            timeframe = sys.argv[1]
    except IndexError:
        projects = PROJECTS
        timeframe = False

    analyze(projects, timeframe)
