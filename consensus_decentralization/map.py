import logging
from consensus_decentralization.mappings.default_mapping import DefaultMapping
from consensus_decentralization.mappings.ethereum_mapping import EthereumMapping
from consensus_decentralization.mappings.cardano_mapping import CardanoMapping
from consensus_decentralization.mappings.tezos_mapping import TezosMapping

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


def apply_mapping(project, parsed_data, output_dir):
    """
    Applies the appropriate mapping to the parsed data of a ledger. If the mapping has already
    been applied for this project (i.e. the corresponding output file already exists) then nothing happens,
    unless the relevant flag is set.
    :param project: string that corresponds to the ledger whose data should be mapped
    :param parsed_data: list of dictionaries. The parsed data of the project
    :param output_dir: path to the general output directory
    :returns: a list of dictionaries (mapped block data)
    """
    logging.info(f'Mapping {project} blocks to their creators..')
    project_output_dir = output_dir / project
    mapping = ledger_mapping[project](project, project_output_dir, parsed_data)
    return mapping.perform_mapping()
