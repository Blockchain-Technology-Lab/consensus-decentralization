import argparse
from src.parsers.default_parser import DefaultParser
from src.parsers.cardano_parser import CardanoParser
from src.parsers.dummy_parser import DummyParser
from src.helpers.helper import OUTPUT_DIR

ledger_parser = {
    'bitcoin': DefaultParser,
    'ethereum': DummyParser,
    'bitcoin_cash': DefaultParser,
    'dogecoin': DefaultParser,
    'cardano': CardanoParser,
    'litecoin': DefaultParser,
    'zcash': DefaultParser,
    'tezos': DummyParser,
    'dash': DefaultParser,
}


def parse(project, force_parse=False):
    """
    Parse raw data, unless already parsed
    :param project: the ledger whose data should be parsed
    :param force_parse: if True, then raw data will be parsed, regardless of whether parsed data for the some or all of the projects already exist
    """
    parsed_data_file = OUTPUT_DIR / project / 'parsed_data.json'
    if force_parse or not parsed_data_file.is_file():
        parser = ledger_parser[project](project)
        parser.parse()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--ledger',
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

    parse(args.ledger, args.force_parse)
