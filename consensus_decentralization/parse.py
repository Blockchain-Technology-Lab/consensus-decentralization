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


def parse(project, input_dir, output_dir, force_parse=False):
    """
    Parses raw data
    :param project: string that corresponds to the ledger whose data should be parsed
    :param force_parse: boolean. If True, then raw data will be parsed, regardless of whether parsed data for some or
    all of the projects already exist. If False, then data will be parsed only if they have not been parsed before (the
    relevant file does not exist)
    """
    parsed_data_file = output_dir / project / 'parsed_data.json'
    if force_parse or not parsed_data_file.is_file():
        logging.info(f'Parsing {project} data..')
        parser = ledger_parser[project](project, input_dir, output_dir)
        parser.parse()
