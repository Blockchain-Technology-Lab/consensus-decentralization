from process import process
from metrics.gini import compute_gini
from metrics.nc import compute_nc

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

START_YEAR = 2018
END_YEAR = 2023

for project_name in PROJECTS:
    yearly_entities = {}
    for year in range(START_YEAR, END_YEAR):
        yearly_entities[year] = set()
        for month in range(1, 13):
            timeframe = '{}-{}'.format(year, str(month).zfill(2))
            try:
                with open('ledgers/{}/{}.csv'.format(project_name, timeframe)) as f:
                    for idx, line in enumerate(f.readlines()):
                        if idx > 0:
                            row = (','.join([i for i in line.split(',')[:-1]]), line.split(',')[-1])
                            yearly_entities[year].add(row[0])
            except FileNotFoundError:
                process(project_name, timeframe)

        for month in range(1, 13):
            timeframe = '{}-{}'.format(year, str(month).zfill(2))
            blocks_per_entity = {}
            try:
                with open('ledgers/{}/{}.csv'.format(project_name, timeframe)) as f:
                    for idx, line in enumerate(f.readlines()):
                        if idx > 0:
                            row = (','.join([i for i in line.split(',')[:-1]]), line.split(',')[-1])
                            blocks_per_entity[row[0]] = int(row[1])

                    if blocks_per_entity.keys():
                        for entity in yearly_entities[year]:
                            if entity not in blocks_per_entity.keys():
                                blocks_per_entity[entity] = 0

                        gini = compute_gini(list(blocks_per_entity.values()))
                        nc = compute_nc(blocks_per_entity)
                        print('[{}, {}] Gini: {:.9f} (population: {}), NC: {} ({:.2f}%)'.format(project_name, timeframe, gini, len(yearly_entities[year]), nc[0], nc[1]))
                    else:
                        print('[{}, {}] No data'.format(project_name, timeframe))
            except FileNotFoundError:
                process(project_name, timeframe)
