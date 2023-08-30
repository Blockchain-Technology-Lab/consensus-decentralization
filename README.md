# Consensus Blockchain Decentralization

This repository provides a CLI tool for analyzing the block production of various blockchains and measuring their 
subsequent levels of decentralization. Please refer to the project's
[documentation pages](https://blockchain-technology-lab.github.io/consensus-decentralization/) for details on its architecture,
required input, produced output, and more.

Currently, the supported blockchains are:
- Bitcoin
- Bitcoin Cash
- Cardano
- Dogecoin
- Ethereum
- Litecoin
- Tezos
- Zcash

We intend to add more ledgers to this list in the future.

## Installation

To install the tool, simply clone this project:

    git clone https://github.com/Blockchain-Technology-Lab/consensus-decentralization.git

The [requirements file](requirements.txt) lists the dependencies of the project.
Make sure you have all of them installed (preferably within a [`virtualenv`](https://docs.python.org/3/library/venv.html)) 
before running the scripts. To install all of them in one go, 
run the following commands from the root directory of the project:

    python -m pip install -r requirements.txt

## Run the tool

Place all raw data (which could be collected from [BigQuery](https://cloud.google.com/bigquery/) for example) in the `raw_block_data` directory, each file named as
`<project_name>_raw_data.json` (e.g. `bitcoin_raw_data.json`). By default, there
is a (very small) sample input file for some supported projects. To use the
samples, remove the prefix `sample_`. For more extended raw data and instructions on how to retrieve it, see
[here](https://blockchain-technology-lab.github.io/consensus-decentralization/data/).

Run `python run.py --ledgers <ledger_1> ... <ledger_n> --timeframe <timeframe>` to produce a csv of the mapped data.
Note that both arguments are optional, so it's possible to omit one or both of them (in which case the default values
will be used). Specifically:

- The `ledgers` argument accepts any number of supported ledgers (case-insensitive). 
For example, `--ledgers bitcoin` runs the analysis for Bitcoin, `--ledgers Bitcoin Ethereum Cardano` runs the analysis 
for Bitcoin, Ethereum and Cardano, etc. Ledgers with  more words should be defined with an underscore; for example 
Bitcoin Cash should be set as `bitcoin_cash`.
- The `timeframe` argument should be of the form `YYYY-MM-DD` (month and day can be omitted). 
For example,  `--timeframe 2022` runs the analysis for the year 2022, `--timeframe 2022-02` runs it for February 2022, 
etc.

`run.py` prints the output of each implemented metric for the specified ledgers and timeframe.

To mass produce and analyze data, omit one or both arguments. If only the
`ledgers` is given, all data since January 2018 for the given ledgers will be
analyzed. If only the timeframe is specified, all ledgers will be analyzed for
the given timeframe. If no arguments are given, all ledgers will be analyzed for
all months since January 2018.

Three files `nc.csv`, `gini.csv`, `entropy.csv` are also created in the `output` directory, containing the data from the 
last execution of `run.py`.

## Contributing

Everyone is welcome to contribute ideas, report bugs, and make the code more efficient. We especially welcome contributions to the following areas:

- Add support for a ledger that is not already supported.
- Update and/or add mapping information for a ledger.
- Add a new metric.

For detailed information on how to contribute see the relevant [documentation
page](https://blockchain-technology-lab.github.io/consensus-decentralization/contribute/).

## Maintainers

The tool is actively maintained by the following developers:

- [Dimitris Karakostas](https://github.com/dimkarakostas)
- [Christina Ovezik](https://github.com/LadyChristina)

*Note*: When opening a Pull Request, you must request a review from at least *2*
people in the above list.

## License

The code of this repository is released under the [MIT License](https://github.com/Blockchain-Technology-Lab/consensus-decentralization/blob/main/LICENSE).
The documentation pages are released under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
