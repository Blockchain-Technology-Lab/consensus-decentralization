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
    :param force_parse: if True, then raw data will be parsed, regardless of whether parsed data for the some or all of
     the projects already exist
    """
    parsed_data_file = OUTPUT_DIR / project / 'parsed_data.json'
    if force_parse or not parsed_data_file.is_file():
        parser = ledger_parser[project](project)
        parser.parse()
