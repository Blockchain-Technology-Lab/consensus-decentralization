import argparse
from src.mappings.bitcoin import BitcoinMapping
from src.mappings.ethereum import EthereumMapping
from src.mappings.cardano import CardanoMapping
from src.mappings.tezos import TezosMapping
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


def apply_mapping(project, timeframe):
    """
    :param project: the ledger whose data should be mapped
    :param timeframe: the timeframe (of the form yyyy-mm-dd) over which data should be mapped
    """
    project_output_dir = OUTPUT_DIR / f'{project}'
    mapping = ledger_mapping[project](project, project_output_dir)

    output_file = project_output_dir / f'{timeframe}.csv'
    if not output_file.is_file():
        mapping.perform_mapping(timeframe)

        # Get mapped data for the year that corresponds to the timeframe.
        # This is needed because the Gini coefficient is computed over all entities per each year.
        year = timeframe[:4]
        year_file = project_output_dir / f'{year}.csv'
        if not year_file.is_file():
            mapping.perform_mapping(year)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--ledger',
        nargs="*",
        type=str.lower,
        default=None,
        choices=[ledger for ledger in ledger_mapping],
        help='The ledgers that will be analyzed.'
    )
    parser.add_argument(
        '--timeframe',
        nargs="?",
        type=str,
        default=None,
        help='The timeframe that will be analyzed.'
    )
    args = parser.parse_args()

    apply_mapping(args.ledger, args.timeframe)
