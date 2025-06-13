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


def parse(ledger, input_dirs):
    """
    Parses raw data
    :param ledger: string that corresponds to the ledger whose data should be parsed
    :param input_dirs: list of paths that point to the directories that contain raw block data
    :returns: list of dictionaries (the parsed data of the project)
    """
    logging.info(f'Parsing {ledger} data..')
    parser = ledger_parser[ledger](ledger=ledger, input_dirs=input_dirs)
    return parser.parse()
