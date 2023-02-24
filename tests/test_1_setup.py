import os
import pathlib


def test_setup():
    output_dir = pathlib.Path(__file__).resolve().parent.parent / 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
