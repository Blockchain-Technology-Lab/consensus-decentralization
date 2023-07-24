import argparse
from src.mappings.bitcoin_mapping import BitcoinMapping
from src.mappings.ethereum_mapping import EthereumMapping
from src.mappings.cardano_mapping import CardanoMapping
from src.mappings.tezos_mapping import TezosMapping
from src.helpers.helper import OUTPUT_DIR, get_start_end_years

ledger_mapping = {
    'bitcoin': BitcoinMapping,
    'ethereum': EthereumMapping,
    'bitcoin_cash': BitcoinMapping,
    'dogecoin': BitcoinMapping,
    'cardano': CardanoMapping,
    'litecoin': BitcoinMapping,
    'zcash': BitcoinMapping,
    'tezos': TezosMapping,
    'dash': BitcoinMapping
}


def apply_mapping(project, timeframes, output_dir, force_map):
    """
    Applies the appropriate mapping to the parsed data of a ledger over some timeframes. If the mapping has already
    been applied for some timeframe (i.e. the corresponding output file already exists) then nothing happens for that
    timeframe.
    :param project: string that corresponds to the ledger whose data should be mapped
    :param timeframes: list of strings that correspond to the timeframes under consideration (in YYYY-MM-DD,
    YYYY-MM or YYYY format). Using multiple timeframes is more efficient here, since every new mapping has a heavy I/O
    operation for retrieving the parsed data.
    :param force_map: bool. If True, then the mapping will be performed, regardless of whether
    mapped data for some or all of the projects already exist
    """
    print(f'Applying mapping to {project} data..')
    project_output_dir = output_dir / f'{project}'
    mapping = ledger_mapping[project](project, project_output_dir)

    for timeframe in timeframes:
        output_file = project_output_dir / f'{timeframe}.csv'
        if not output_file.is_file() or force_map:
            mapping.perform_mapping(timeframe)

            # Get mapped data for the year that corresponds to the timeframe.
            # This is needed because the Gini coefficient is computed over all entities per each year.
            year = timeframe[:4]
            year_file = project_output_dir / f'{year}.csv'
            if not year_file.is_file() or force_map:
                mapping.perform_mapping(year)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--ledgers',
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
    parser.add_argument(
        '--force-map',
        action='store_true',
        help='Flag to specify whether to map the parsed data, regardless if the mapped data files exist.'
    )
    args = parser.parse_args()

    start_year, end_year = get_start_end_years()

    timeframe = args.timeframe
    if timeframe:
        timeframes = [timeframe]
    else:
        timeframes = []
        for year in range(start_year, end_year+1):
            for month in range(1, 13):
                timeframes.append(f'{year}-{str(month).zfill(2)}')

    apply_mapping(args.ledgers, timeframes, OUTPUT_DIR, args.force_map)
