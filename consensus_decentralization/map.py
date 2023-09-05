import argparse
import logging
import consensus_decentralization.helper as hlp
from consensus_decentralization.mappings.default_mapping import DefaultMapping
from consensus_decentralization.mappings.ethereum_mapping import EthereumMapping
from consensus_decentralization.mappings.cardano_mapping import CardanoMapping
from consensus_decentralization.mappings.tezos_mapping import TezosMapping
from consensus_decentralization.helper import OUTPUT_DIR

ledger_mapping = {
    'bitcoin': DefaultMapping,
    'ethereum': EthereumMapping,
    'bitcoin_cash': DefaultMapping,
    'dogecoin': DefaultMapping,
    'cardano': CardanoMapping,
    'litecoin': DefaultMapping,
    'zcash': DefaultMapping,
    'tezos': TezosMapping,
}


def apply_mapping(project, output_dir, force_map):
    """
    Applies the appropriate mapping to the parsed data of a ledger. If the mapping has already
    been applied for this project (i.e. the corresponding output file already exists) then nothing happens,
    unless the relevant flag is set.
    :param project: string that corresponds to the ledger whose data should be mapped
    :param output_dir: path to the general output directory
    :param force_map: bool. If True, then the mapping will be performed, regardless of whether
    mapped data for the project already exists
    """
    project_output_dir = output_dir / project
    parsed_data = hlp.read_parsed_project_data(project_output_dir)
    mapping = ledger_mapping[project](project, project_output_dir, parsed_data)

    output_file = project_output_dir / 'mapped_data.json'
    if not output_file.is_file() or force_map:
        logging.info(f'Mapping {project} blocks to their creators..')
        mapping.perform_mapping()


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
        '--force-map',
        action='store_true',
        help='Flag to specify whether to map the parsed data, regardless if the mapped data files exist.'
    )
    args = parser.parse_args()

    apply_mapping(args.ledgers, OUTPUT_DIR, args.force_map)
