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
        for sample in correct_data:  # todo parser always sorts data so we know the final order, no reason to check
            # every sample for every item. if we stick to this at least continue after match is found
            if sample['number'] == item['number']:
                assert all([
                    sample['timestamp'] == item['timestamp'],
                    sample['identifiers'] == item['identifiers'],
                    set(sample['reward_addresses'].split(',')) == set(item['reward_addresses'].split(','))
                ])


def test_default_parser(setup_and_cleanup):
    test_input_dir, test_output_dir = setup_and_cleanup
    sample_parsed_data = [
        {"number": "507516", "timestamp": "2018-02-04 02:36:23 UTC", "identifiers": "037cbe0741d69d9c6acce4d141d69d9c69f9bef52f4254432e544f502ffabe6d6d143120f7b3da918f12ffb328ab935fbfe2d1cd9bb4707265d7fee23fd6cf372780000000000000005a44cacf0000f8a441200000", "reward_addresses": "137YB5cpBLxLKvy8T6qXsycJ699iJjWCHH,1FVKW4rp5rN23dqFVk2tYGY4niAXMB8eZC"},
        {"number": "507715", "timestamp": "2018-02-05 04:54:34 UTC", "identifiers": "0343bf07132f6d696e65642062792067626d696e6572732f2cfabe6d6d94976ecebbc73b3d4214b3d7ab330dca2129ebfcc863fa75623c6f95891e7346010000000000000010af8b66002da910ef408c776852840100", "reward_addresses": "1J7FCFaafPRxqu4X9VsaiMZr1XMemx69GR,131RUhDyyjxXSbSPxGRCm3t6vcei1TB6MB"},
        {"number": "508242", "timestamp": "2018-03-08 10:57:02 UTC", "identifiers": "0352c10704ff2c7c5a2f087cf540446c010000000000", "reward_addresses": "1AM2fYfpY3ZeMeCKXmN66haoWxvB89pJUx"},
        {"number": "508434", "timestamp": "2018-02-09 22:17:45 UTC", "identifiers": "0312c207040a1e7e5a2f0879deffabf9010000000000", "reward_addresses": "1AM2fYfpY3ZeMeCKXmN66haoWxvB89pJUx,3G7y14BudP2a4kjPAuecg4iUKM84GgPPWb"},
        {"number": "509373", "timestamp": "2018-02-15 23:50:04 UTC", "identifiers": "03bdc50704ae1c865a2f07a6e2831b1e010000000000", "reward_addresses": "1AM2fYfpY3ZeMeCKXmN66haoWxvB89pJUx,3G7y14BudP2a4kjPAuecg4iUKM84GgPPWb"},
        {"number": "509432", "timestamp": "2018-02-16 09:25:03 UTC", "identifiers": "03f8c5070470a3865a2f08a35ce4804a010000000000", "reward_addresses": "1AM2fYfpY3ZeMeCKXmN66haoWxvB89pJUx,3G7y14BudP2a4kjPAuecg4iUKM84GgPPWb"},
        {"number": "510199", "timestamp": "2018-02-21 06:43:35 UTC", "identifiers": "03f7c8070418158d5a2f08b033a0a15b020000000000", "reward_addresses": "1AM2fYfpY3ZeMeCKXmN66haoWxvB89pJUx,3G7y14BudP2a4kjPAuecg4iUKM84GgPPWb"},
        {"number": "510888", "timestamp": "2018-02-25 18:02:53 UTC", "identifiers": "03a8cb0741d6a4be8b5ec50141d6a4be8aedceda2f45324d2026204254432e544f502ffabe6d6dfb9300ef260402c08b34b5d1dd57904edf0e9e167e99c51d7dbe5f0c06d6b31d8000000000000000e600589dbdabaaca00000000", "reward_addresses": "137YB5cpBLxLKvy8T6qXsycJ699iJjWCHH,1FVKW4rp5rN23dqFVk2tYGY4niAXMB8eZC"},
        {"number": "511342", "timestamp": "2018-02-28 16:12:07 UTC", "identifiers": "036ecd07132f6d696e65642062792067626d696e6572732f2cfabe6d6d5945c2c64cd6a760e01bc586cee9124629c0b0d6cfa37efcf3d1b912ed7c9467010000000000000010925765006fa22002c89d0875748fe338", "reward_addresses": "1J7FCFaafPRxqu4X9VsaiMZr1XMemx69GR,131RUhDyyjxXSbSPxGRCm3t6vcei1TB6MB"},
        {"number": "682736", "timestamp": "2021-05-09 11:12:32 UTC", "identifiers": "03f06a0a202f5669614254432f4d696e6564206279206a617669647361656964373037332f2cfabe6d6d6e43ef2e06f7137b897180388403ee5019b8ff0ca4a045ea3cd82e3e41620fe91000000000000000105462a20fc21591f70e691905660b0000", "reward_addresses": "18cBEMRxXHqzWWCxZNtU91F5sbUNKhL5PX"}
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
        {"number": "11181062", "timestamp": "2020-11-03 00:56:48 UTC", "reward_addresses": "0xe9b54a47e3f401d37798fc4e22f14b78475c2afc", "identifiers": "0x36"},
        {"number": "11183702", "timestamp": "2020-11-03 10:37:32 UTC", "reward_addresses": "0xe9b54a47e3f401d37798fc4e22f14b78475c2afc", "identifiers": "0x36"},
        {"number": "11183739", "timestamp": "2020-11-03 10:44:14 UTC", "reward_addresses": "0xe9b54a47e3f401d37798fc4e22f14b78475c2afc", "identifiers": "0x3"},
        {"number": "11183793", "timestamp": "2020-11-03 10:56:07 UTC", "reward_addresses": "0x8595dd9e0438640b5e1254f9df579ac12a86865f", "identifiers": "0x657a696c2e6d65"},
        {"number": "11183969", "timestamp": "2020-11-03 11:33:44 UTC", "reward_addresses": "0x8595dd9e0438640b5e1254f9df579ac12a86865f", "identifiers": "0x657a696c2e6d65"},
        {"number": "11184329", "timestamp": "2020-11-03 12:56:41 UTC", "reward_addresses": "0x8595dd9e0438640b5e1254f9df579ac12a86865f", "identifiers": "0x657a696c2e6d65"},
        {"number": "11184490", "timestamp": "2020-11-03 13:33:18 UTC", "reward_addresses": "0x45133a7e1cc7e18555ae8a4ee632a8a61de90df6", "identifiers": "0x20"},
        {"number": "11185799", "timestamp": "2020-11-03 18:34:11 UTC", "reward_addresses": "0xe9b54a47e3f401d37798fc4e22f14b78475c2afc", "identifiers": "0x36"},
        {"number": "11186643", "timestamp": "2020-11-03 21:33:27 UTC", "reward_addresses": "0xe9b54a47e3f401d37798fc4e22f14b78475c2afc", "identifiers": "0x36"},
        {"number": "16382083", "timestamp": "2023-01-11 07:29:47 UTC", "reward_addresses": "0x3bee5122e2a2fbe11287aafb0cb918e22abb5436", "identifiers": "0x"}
    ]

    project_name = 'sample_ethereum'

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

