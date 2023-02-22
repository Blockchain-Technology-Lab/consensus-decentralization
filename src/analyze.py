from src.metrics.gini import compute_gini
from src.metrics.nakamoto_coefficient import compute_nakamoto_coefficient
from src.metrics.entropy import compute_entropy
from src.helpers.helper import OUTPUT_DIR


def analyze(project, timeframe, entropy_alpha):
    """
    :param project: the ledger whose data should be analyzed
    :param timeframe: the timeframe (of the form yyyy-mm-dd) over which data should be analyzed
    """
    gini_csv = {'0': 'timeframe'}
    nc_csv = {'0': 'timeframe'}
    entropy_csv = {'0': 'timeframe'}

    # Each metric dict is of the form {'<timeframe>': '<comma-separated values for different projects'}.
    # The special entry '0': '<comma-separated names of projects>' is for the csv title.
    gini_csv['0'] += f',{project}'
    nc_csv['0'] += f',{project}'
    entropy_csv['0'] += f',{project}'

    if timeframe not in gini_csv.keys():
        gini_csv[timeframe] = timeframe
        nc_csv[timeframe] = timeframe
        entropy_csv[timeframe] = timeframe

    # Get mapped data for the year that corresponds to the timeframe.
    # This is needed because the Gini coefficient is computed over all entities per each year.
    year = timeframe[:4]
    yearly_entities = set()
    with open(OUTPUT_DIR / f'{project}/{year}.csv') as f:
        for line in f.readlines()[1:]:
            row = (','.join([i for i in line.split(',')[:-1]]), line.split(',')[-1])
            yearly_entities.add(row[0])

    # Get mapped data for the defined timeframe.
    with open(OUTPUT_DIR / f'{project}/{timeframe}.csv') as f:
        blocks_per_entity = {}
        for line in f.readlines()[1:]:
            blocks_per_entity[line.split(',')[0]] = int(line.split(',')[1])

    # If the project data exist for the given timeframe, compute the metrics on them.
    if blocks_per_entity.keys():
        for entity in yearly_entities:
            if entity not in blocks_per_entity.keys():
                blocks_per_entity[entity] = 0
        gini = compute_gini(blocks_per_entity)
        nc = compute_nakamoto_coefficient(blocks_per_entity)
        entropy = compute_entropy(blocks_per_entity, entropy_alpha)
        max_entropy = compute_entropy({entity: 1 for entity in yearly_entities}, entropy_alpha)
        entropy_percentage = 100 * entropy / max_entropy if max_entropy != 0 else 0
        print(
            f'[{project:12} {timeframe:7}] \t Gini: {gini:.6f}   NC: {nc[0]:3} ({nc[1]:.2f}%)   '
            f'Entropy: {entropy:.6f} ({entropy_percentage:.1f}% out of max {max_entropy:.6f})'
        )
    else:
        gini, nc, entropy = '', ('', ''), ''
        print(f'[{project:12} {timeframe:7}] No data')

    gini_csv[timeframe] += f',{gini}'
    nc_csv[timeframe] += f',{nc[0]}'
    entropy_csv[timeframe] += f',{entropy}'

    with open(OUTPUT_DIR / 'gini.csv', 'w') as f:
        f.write('\n'.join([i[1] for i in sorted(gini_csv.items(), key=lambda x: x[0])]))
    with open(OUTPUT_DIR / 'nc.csv', 'w') as f:
        f.write('\n'.join([i[1] for i in sorted(nc_csv.items(), key=lambda x: x[0])]))
    with open(OUTPUT_DIR / 'entropy.csv', 'w') as f:
        f.write('\n'.join([i[1] for i in sorted(entropy_csv.items(), key=lambda x: x[0])]))
