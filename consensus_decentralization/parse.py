import logging
from consensus_decentralization.parsers.default_parser import DefaultParser
from consensus_decentralization.parsers.dummy_parser import DummyParser
from consensus_decentralization.parsers.ethereum_parser import EthereumParser


ledger_parser = {
    'bitcoin': DefaultParser,
    'ethereum': EthereumParser,
    'bitcoin_cash': DefaultParser,
    'dogecoin': DefaultParser,
    'cardano': DummyParser,
    'litecoin': DefaultParser,
    'zcash': DefaultParser,
    'tezos': DummyParser,
}


def parse(project, input_dir):
    """
    Parses raw data
    :param project: string that corresponds to the ledger whose data should be parsed
    :param input_dir: path to the directory of the raw block data
    :returns: list of dictionaries (the parsed data of the project)
    """
    logging.info(f'Parsing {project} data..')
    parser = ledger_parser[project](project_name=project, input_dir=input_dir)
    return parser.parse()
