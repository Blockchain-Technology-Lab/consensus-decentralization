import os
import pathlib
import shutil
from run import main
from src.parse import ledger_parser
from src.parsers.default_parser import DefaultParser
from src.parsers.cardano_parser import CardanoParser
from src.map import ledger_mapping
from src.mappings.bitcoin import BitcoinMapping
from src.mappings.cardano import CardanoMapping
from src.helpers.helper import OUTPUT_DIR


def test_end_to_end():
    shutil.rmtree(OUTPUT_DIR)

    pool_info_dir = pathlib.Path(__file__).resolve().parent.parent / 'src' / 'helpers' / 'pool_information'

    projects = ['bitcoin', 'cardano']

    for project in projects:
        shutil.copy2(str(pool_info_dir / f'{project}.json'), str(pool_info_dir / f'sample_{project}.json'))

        if project == 'bitcoin':
            ledger_mapping[project] = BitcoinMapping
            ledger_parser[project] = DefaultParser
        elif project == 'cardano':
            ledger_mapping[project] = CardanoMapping
            ledger_parser[project] = CardanoParser

    timeframes = ['2010', '2018-02', '2018-03', '2020-12']
    force_parse = False
    entropy_alpha = 1

    projects = [f'sample_{i}' for i in projects]
    main(projects, timeframes, force_parse, entropy_alpha, False)

    for project in projects:
        os.remove(str(pool_info_dir / f'{project}.json'))

    expected_entropy = [
        'timeframe,sample_bitcoin,sample_cardano\n',
        '2010,,\n',
        '2018-02,1.5,\n',
        '2018-03,0.0,\n',
        '2020-12,,2.321928094887362'
    ]
    with open(OUTPUT_DIR / 'entropy.csv') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            assert expected_entropy[idx] == line

    expected_gini = [
        'timeframe,sample_bitcoin,sample_cardano\n',
        '2010,,\n',
        '2018-02,0.375,\n',
        '2018-03,0.75,\n',
        '2020-12,,0.0'
    ]
    with open(OUTPUT_DIR / 'gini.csv') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            assert expected_gini[idx] == line

    expected_nc = [
        'timeframe,sample_bitcoin,sample_cardano\n',
        '2010,,\n',
        '2018-02,1,\n',
        '2018-03,1,\n',
        '2020-12,,3'
    ]
    with open(OUTPUT_DIR / 'nc.csv') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            assert expected_nc[idx] == line
