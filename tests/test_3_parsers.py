import json
import shutil
import pytest
from src.parse import parse, ledger_parser
from src.parsers.default_parser import DefaultParser
from src.parsers.dummy_parser import DummyParser
from src.helpers.helper import INPUT_DIR, OUTPUT_DIR


@pytest.fixture
def setup_and_cleanup():
    """
    This function can be used to set up the right conditions for a test and also clean up after the test is finished.
    The part before the yield command is run before the test (setup) and the part after the yield command is run
    after (cleanup)
    """
    print("Setting up")
    test_input_dir = INPUT_DIR
    test_output_dir = OUTPUT_DIR / "test_output"
    yield test_input_dir, test_output_dir
    print("Cleaning up")
    shutil.rmtree(test_output_dir)


def compare_parsed_samples(correct_data, parsed_file):
    with open(parsed_file) as f:
        test_data = json.load(f)

    for item in test_data:
        for sample in correct_data:
            if sample['number'] == item['number']:
                assert all([
                    sample['timestamp'] == item['timestamp'],
                    sample['identifiers'] == item['identifiers'],
                    (sample['reward_addresses'] is None and item['reward_addresses'] is None)
                    or set(sample['reward_addresses'].split(',')) == set(item['reward_addresses'].split(','))
                ])


def test_default_parser(setup_and_cleanup):
    test_input_dir, test_output_dir = setup_and_cleanup
    sample_parsed_data = [
        {"number": "507516", "timestamp": "2018-02-04 02:36:23 UTC", "identifiers": 'b"\\x03|\\xbe\\x07A\\xd6\\x9d\\x9cj\\xcc\\xe4\\xd1A\\xd6\\x9d\\x9ci\\xf9\\xbe\\xf5/BTC.TOP/\\xfa\\xbemm\\x141 \\xf7\\xb3\\xda\\x91\\x8f\\x12\\xff\\xb3(\\xab\\x93_\\xbf\\xe2\\xd1\\xcd\\x9b\\xb4pre\\xd7\\xfe\\xe2?\\xd6\\xcf7\'\\x80\\x00\\x00\\x00\\x00\\x00\\x00\\x00ZD\\xca\\xcf\\x00\\x00\\xf8\\xa4A \\x00\\x00"', "reward_addresses": "137YB5cpBLxLKvy8T6qXsycJ699iJjWCHH,1FVKW4rp5rN23dqFVk2tYGY4niAXMB8eZC"},
        {"number": "507715", "timestamp": "2018-02-05 04:54:34 UTC", "identifiers": "b'\\x03C\\xbf\\x07\\x13/mined by gbminers/,\\xfa\\xbemm\\x94\\x97n\\xce\\xbb\\xc7;=B\\x14\\xb3\\xd7\\xab3\\r\\xca!)\\xeb\\xfc\\xc8c\\xfaub<o\\x95\\x89\\x1esF\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x10\\xaf\\x8bf\\x00-\\xa9\\x10\\xef@\\x8cwhR\\x84\\x01\\x00'", "reward_addresses": "1J7FCFaafPRxqu4X9VsaiMZr1XMemx69GR,131RUhDyyjxXSbSPxGRCm3t6vcei1TB6MB"},
        {"number": "508242", "timestamp": "2018-03-08 10:57:02 UTC", "identifiers": "b'\\x03R\\xc1\\x07\\x04\\xff,|Z/\\x08|\\xf5@Dl\\x01\\x00\\x00\\x00\\x00\\x00'", "reward_addresses": "1AM2fYfpY3ZeMeCKXmN66haoWxvB89pJUx"},
        {"number": "508434", "timestamp": "2018-02-09 22:17:45 UTC", "identifiers": "b'\\x03\\x12\\xc2\\x07\\x04\\n\\x1e~Z/\\x08y\\xde\\xff\\xab\\xf9\\x01\\x00\\x00\\x00\\x00\\x00'", "reward_addresses": "1AM2fYfpY3ZeMeCKXmN66haoWxvB89pJUx,3G7y14BudP2a4kjPAuecg4iUKM84GgPPWb"},
        {"number": "509373", "timestamp": "2018-02-15 23:50:04 UTC", "identifiers": "b'\\x03\\xbd\\xc5\\x07\\x04\\xae\\x1c\\x86Z/\\x07\\xa6\\xe2\\x83\\x1b\\x1e\\x01\\x00\\x00\\x00\\x00\\x00'", "reward_addresses": "1AM2fYfpY3ZeMeCKXmN66haoWxvB89pJUx,3G7y14BudP2a4kjPAuecg4iUKM84GgPPWb"},
        {"number": "509432", "timestamp": "2018-02-16 09:25:03 UTC", "identifiers": "b'\\x03\\xf8\\xc5\\x07\\x04p\\xa3\\x86Z/\\x08\\xa3\\\\\\xe4\\x80J\\x01\\x00\\x00\\x00\\x00\\x00'", "reward_addresses": "1AM2fYfpY3ZeMeCKXmN66haoWxvB89pJUx,3G7y14BudP2a4kjPAuecg4iUKM84GgPPWb"},
        {"number": "510199", "timestamp": "2018-02-21 06:43:35 UTC", "identifiers": "b'\\x03\\xf7\\xc8\\x07\\x04\\x18\\x15\\x8dZ/\\x08\\xb03\\xa0\\xa1[\\x02\\x00\\x00\\x00\\x00\\x00'", "reward_addresses": "1AM2fYfpY3ZeMeCKXmN66haoWxvB89pJUx,3G7y14BudP2a4kjPAuecg4iUKM84GgPPWb"},
        {"number": "510888", "timestamp": "2018-02-25 18:02:53 UTC", "identifiers": "b'\\x03\\xa8\\xcb\\x07A\\xd6\\xa4\\xbe\\x8b^\\xc5\\x01A\\xd6\\xa4\\xbe\\x8a\\xed\\xce\\xda/E2M & BTC.TOP/\\xfa\\xbemm\\xfb\\x93\\x00\\xef&\\x04\\x02\\xc0\\x8b4\\xb5\\xd1\\xddW\\x90N\\xdf\\x0e\\x9e\\x16~\\x99\\xc5\\x1d}\\xbe_\\x0c\\x06\\xd6\\xb3\\x1d\\x80\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\xe6\\x00X\\x9d\\xbd\\xab\\xaa\\xca\\x00\\x00\\x00\\x00'", "reward_addresses": "137YB5cpBLxLKvy8T6qXsycJ699iJjWCHH,1FVKW4rp5rN23dqFVk2tYGY4niAXMB8eZC"},
        {"number": "511342", "timestamp": "2018-02-28 16:12:07 UTC", "identifiers": "b'\\x03n\\xcd\\x07\\x13/mined by gbminers/,\\xfa\\xbemmYE\\xc2\\xc6L\\xd6\\xa7`\\xe0\\x1b\\xc5\\x86\\xce\\xe9\\x12F)\\xc0\\xb0\\xd6\\xcf\\xa3~\\xfc\\xf3\\xd1\\xb9\\x12\\xed|\\x94g\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x10\\x92We\\x00o\\xa2 \\x02\\xc8\\x9d\\x08ut\\x8f\\xe38'", "reward_addresses": "1J7FCFaafPRxqu4X9VsaiMZr1XMemx69GR,131RUhDyyjxXSbSPxGRCm3t6vcei1TB6MB"},
        {"number": "682736", "timestamp": "2021-05-09 11:12:32 UTC", "identifiers": "b'\\x03\\xf0j\\n /ViaBTC/Mined by javidsaeid7073/,\\xfa\\xbemmnC\\xef.\\x06\\xf7\\x13{\\x89q\\x808\\x84\\x03\\xeeP\\x19\\xb8\\xff\\x0c\\xa4\\xa0E\\xea<\\xd8.>Ab\\x0f\\xe9\\x10\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x10Tb\\xa2\\x0f\\xc2\\x15\\x91\\xf7\\x0ei\\x19\\x05f\\x0b\\x00\\x00'", "reward_addresses": "18cBEMRxXHqzWWCxZNtU91F5sbUNKhL5PX"}
    ]

    project_name = 'sample_bitcoin'

    parser = DefaultParser(project_name, test_input_dir, test_output_dir)
    parser.parse()

    parsed_file = test_output_dir / f'{project_name}/parsed_data.json'
    assert parsed_file.is_file()

    compare_parsed_samples(sample_parsed_data, parsed_file)


def test_dummy_parser(setup_and_cleanup):
    test_input_dir, test_output_dir = setup_and_cleanup
    sample_parsed_data = [
        {"number": "1649812", "timestamp": "2021-08-30 00:36:18 UTC", "identifiers": None, "reward_addresses": "tz1Kf25fX1VdmYGSEzwFy1wNmkbSEZ2V83sY"},
        {"number": "1650474", "timestamp": "2021-08-30 06:11:58 UTC", "identifiers": None, "reward_addresses": "tz1Vd1rXpV8hTHbFXCXN3c3qzCsgcU5BZw1e"},
        {"number": "1650309", "timestamp": "2021-08-30 04:49:28 UTC", "identifiers": None, "reward_addresses": "tz1Kf25fX1VdmYGSEzwFy1wNmkbSEZ2V83sY"},
        {"number": "1651794", "timestamp": "2021-08-30 17:41:08 UTC", "identifiers": None, "reward_addresses": None},
        {"number": "1649839", "timestamp": "2021-08-30 00:49:48 UTC", "identifiers": None, "reward_addresses": "tz1Kt4P8BCaP93AEV4eA7gmpRryWt5hznjCP"},
        {"number": "0000000", "timestamp": "2018-08-30 00:36:18 UTC", "identifiers": None, "reward_addresses": "tz0000000000000000000000000000000000"},
    ]

    project_name = 'sample_tezos'

    parser = DummyParser(project_name, test_input_dir, test_output_dir)
    parser.parse()

    parsed_file = test_output_dir / f'{project_name}/parsed_data.json'
    assert parsed_file.is_file()

    compare_parsed_samples(sample_parsed_data, parsed_file)


def test_parse(setup_and_cleanup):
    test_input_dir, test_output_dir = setup_and_cleanup
    sample_block = {"number": "682736", "timestamp": "2021-05-09 11:12:32 UTC", "identifiers": "03f06a0a202f5669614254432f4d696e6564206279206a617669647361656964373037332f2cfabe6d6d6e43ef2e06f7137b897180388403ee5019b8ff0ca4a045ea3cd82e3e41620fe91000000000000000105462a20fc21591f70e691905660b0000", "reward_addresses": "18cBEMRxXHqzWWCxZNtU91F5sbUNKhL5PX"}

    project = 'sample_bitcoin'
    ledger_parser[project] = DefaultParser

    parsed_file = test_output_dir / f'{project}/parsed_data.json'
    input_file = test_input_dir / f'{project}_raw_data.json'

    parse(project, test_input_dir, test_output_dir)
    with open(parsed_file) as f:
        test_data = json.load(f)
        for item in test_data:
            if item['number'] == '682736':
                assert item['reward_addresses'] == sample_block['reward_addresses']

    with open(input_file) as f:
        sample_data = f.read()
    sample_data = sample_data.replace("18cBEMRxXHqzWWCxZNtU91F5sbUNKhL5PX", "----------------------------------")
    with open(input_file, 'w') as f:
        f.write(sample_data)

    parse(project, test_input_dir, test_output_dir)
    with open(parsed_file) as f:
        test_data = json.load(f)
        for item in test_data:
            if item['number'] == '682736':
                assert item['reward_addresses'] == sample_block['reward_addresses']

    parse(project, test_input_dir, test_output_dir, True)
    with open(parsed_file) as f:
        test_data = json.load(f)
        for item in test_data:
            if item['number'] == '682736':
                assert item['reward_addresses'] == "----------------------------------"

    with open(input_file) as f:
        sample_data = f.read()
    sample_data = sample_data.replace("----------------------------------", "18cBEMRxXHqzWWCxZNtU91F5sbUNKhL5PX")  #
    with open(input_file, 'w') as f:
        f.write(sample_data)


def test_default_parse_identifiers():
    parsed_identifiers = DefaultParser.parse_identifiers('0343bf07132f6d696e65642062792067626d696e6572732f2cfabe6d6d94976ecebbc73b3d4214b3d7ab330dca2129ebfcc863fa75623c6f95891e7346010000000000000010af8b66002da910ef408c776852840100')
    assert parsed_identifiers == "b'\\x03C\\xbf\\x07\\x13/mined by gbminers/,\\xfa\\xbemm\\x94\\x97n\\xce\\xbb\\xc7;=B\\x14\\xb3\\xd7\\xab3\\r\\xca!)\\xeb\\xfc\\xc8c\\xfaub<o\\x95\\x89\\x1esF\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x10\\xaf\\x8bf\\x00-\\xa9\\x10\\xef@\\x8cwhR\\x84\\x01\\x00'"
