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

months = []
gini_series = {}
nc_series = {}
for project_name in PROJECTS:
    gini_series[project_name] = []
    nc_series[project_name] = []

    yearly_entities = {}
    for idx, year in enumerate(range(START_YEAR, END_YEAR)):
        yearly_entities[year] = set()
        for month in range(1, 13):
            timeframe = '{}-{}'.format(year, str(month).zfill(2))
            if timeframe not in months:
                months.append(timeframe)
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

                        gini_series[project_name].append(gini)
                        nc_series[project_name].append(nc[0])
                    else:
                        print('[{}, {}] No data'.format(project_name, timeframe))

                        gini_series[project_name].append(0)
                        nc_series[project_name].append(0)
            except FileNotFoundError:
                process(project_name, timeframe)

gini_csv = ['Month']
nc_csv = ['Month']
for month in months:
    gini_csv.append(month)
    nc_csv.append(month)

for i, project_name in enumerate(PROJECTS):
    gini_csv[0] += ',' + project_name
    nc_csv[0] += ',' + project_name

    for j, data in enumerate(gini_series[project_name]):
        gini_csv[j+1] += ',{}'.format(data if data else '')

    for j, data in enumerate(nc_series[project_name]):
        nc_csv[j+1] += ',{}'.format(data if data else '')

with open('gini.csv', 'w') as f:
    f.write('\n'.join(gini_csv))
with open('nc.csv', 'w') as f:
    f.write('\n'.join(nc_csv))
