from execute import execute
import csv
from analyzers.gini import compute_gini
from analyzers.nc import compute_nc

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
    for year in range(START_YEAR, END_YEAR):
        for month in range(1, 13):
            blocks_per_entity = {}
            timeframe = '{}-{}'.format(year, str(month).zfill(2))
            print(project_name, timeframe)
            try:
                with open('ledgers/{}/{}.csv'.format(project_name, timeframe)) as f:
                    reader = csv.reader(f)
                    for idx, row in enumerate(reader):
                        if idx > 0:
                            blocks_per_entity[row[0]] = int(row[1])

                    if blocks_per_entity.keys():
                        gini = compute_gini(list(blocks_per_entity.values()))
                        nc = compute_nc(blocks_per_entity)
                        print('  Gini: {}, NC: {} ({:.2f}%)'.format(gini, nc[0], nc[1]))
            except FileNotFoundError:
                execute(project_name, timeframe)
