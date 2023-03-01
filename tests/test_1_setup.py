import os
import pathlib
from src.map import ledger_mapping
from src.parse import ledger_parser


def test_setup():
    output_dir = pathlib.Path(__file__).resolve().parent.parent / 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


def test_project_dicts():
    assert set(ledger_mapping.keys()) == set(ledger_parser.keys())
