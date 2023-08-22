import argparse
import logging
from src.parsers.default_parser import DefaultParser
from src.parsers.dummy_parser import DummyParser
from src.parsers.ethereum_parser import EthereumParser
from src.helper import INPUT_DIR, OUTPUT_DIR


ledger_parser = {
    'bitcoin': DefaultParser,
    'bitcoin_new': DefaultParser,
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--ledgers',
        nargs="*",
        type=str.lower,
        default=None,
        choices=[ledger for ledger in ledger_parser],
        help='The ledgers that will be analyzed.'
    )
    parser.add_argument(
        '--force-parse',
        action='store_true',
        help='Flag to specify whether to parse the raw data, regardless if the parsed data file exists.'
    )
    args = parser.parse_args()

    parse(args.ledger, INPUT_DIR, OUTPUT_DIR, args.force_parse)
