from src.map import ledger_mapping
from src.parse import ledger_parser


def test_project_dicts():
    assert set(ledger_mapping.keys()) == set(ledger_parser.keys())
