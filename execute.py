import json
from preprocessors.bitcoin import process as bitcoin_preprocessor
from preprocessors.ethereum import process as ethereum_preprocessor
from preprocessors.cardano import process as cardano_preprocessor
import sys
import pathlib

processor = {
    'bitcoin': bitcoin_preprocessor,
    'ethereum': ethereum_preprocessor,
    'bitcoin_cash': bitcoin_preprocessor,
    'dogecoin': bitcoin_preprocessor,
    'cardano': cardano_preprocessor,
    'ethereum_classic': ethereum_preprocessor,
    'litecoin': bitcoin_preprocessor,
    'zcash': bitcoin_preprocessor,
    'tezos': ethereum_preprocessor,
}


def execute(project_name, timeframe):
    project_dir = str(pathlib.Path(__file__).parent.resolve()) + '/ledgers/{}'.format(project_name)

    print('[{}]'.format(project_name), 'Time range:', timeframe)

    processor[project_name](project_dir, timeframe)

if __name__ == '__main__':
    project_name = sys.argv[1]
    timeframe = sys.argv[2]
    execute(project_name, timeframe)
