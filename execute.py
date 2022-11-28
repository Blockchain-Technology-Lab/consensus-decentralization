import json
from analyzers.gini import compute_gini
from analyzers.nc import compute_nc
from preprocessors.bitcoin import process as bitcoin_preprocessor
from preprocessors.ethereum import process as ethereum_preprocessor
from preprocessors.cardano import process as cardano_preprocessor
from preprocessors.tezos import process as tezos_preprocessor
import sys
import pathlib

processor = {
    'bitcoin': bitcoin_preprocessor,
    'ethereum': ethereum_preprocessor,
    'bitcoin_cash': bitcoin_preprocessor,
    'dogecoin': bitcoin_preprocessor,
    'cardano': cardano_preprocessor,
    'litecoin': bitcoin_preprocessor,
    'zcash': bitcoin_preprocessor,
    'tezos': tezos_preprocessor,
}


def execute(project_name, timeframe):
    project_dir = str(pathlib.Path(__file__).parent.resolve()) + '/ledgers/{}'.format(project_name)

    blocks_per_entity = processor[project_name](project_dir, timeframe)
    if blocks_per_entity.keys():
        gini = compute_gini(list(blocks_per_entity.values()))
        nc = compute_nc(blocks_per_entity)
        print('[{}, {}] Gini: {}, NC: {} ({:.2f}%)'.format(project_name, timeframe, gini, nc[0], nc[1]))

if __name__ == '__main__':
    project_name = sys.argv[1]
    timeframe = sys.argv[2]
    execute(project_name, timeframe)
