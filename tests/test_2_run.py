import argparse
import pytest
from run import valid_date


def test_valid_date():
    for d in [
        '2022',
        '2022-01',
        '2022-01-01',
        '2022-01-1',
        '2022-1-1',
        '2022-1-01',
        '2022-1',
    ]:
        assert valid_date(d)

    for d in [
        '2022/1/01',
        '2022/01/1',
        '2022/1',
        '2022/01',
        '2022.1.01',
        '2022.01.1',
        '2022.1',
        '2022.01',
        'blah'
    ]:
        with pytest.raises(argparse.ArgumentTypeError) as e_info:
            valid_date(d)
        assert e_info.type == argparse.ArgumentTypeError
