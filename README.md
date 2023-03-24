# Pooling Analysis

This repository provides a tool for analyzing pooling behavior of various blockchains and measuring their subsequent
decentralization levels. Please refer to the project's
[documentation pages](https://blockchain-technology-lab.github.io/pooling-analysis/) for details on its architecture,
required input, produced output, and more.

Currently, the supported blockchains are:
- Bitcoin
- Bitcoin Cash
- Cardano
- Dash
- Dogecoin
- Ethereum
- Litecoin
- Tezos
- Zcash

## Installation 

To install the pooling analysis tool, simply clone this project:

    git clone https://github.com/Blockchain-Technology-Lab/pooling-analysis.git

The [requirements file](requirements.txt) lists the dependencies of the project.
Make sure you have all of them installed before running the scripts. To install
all of them in one go, run the following command from the root directory of the
project:

    python -m pip install -r requirements.txt

## Run the tool

Place all raw data (which could be collected from BigQuery for example) in the `input` directory, each file named as
`<project_name>_raw_data.json` (e.g. `bitcoin_raw_data.json`). By default, there
is a (very small) sample input file for some supported projects. To use the
samples, remove the prefix `sample_`. For more extended raw data and instructions on how to retrieve it, see
[here](https://blockchain-technology-lab.github.io/pooling-analysis/data/).

Run `python run.py --ledgers <ledger_1> <ledger_n> --timeframe <timeframe>` to produce a csv of the mapped data.
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

### Pooling information

You can update and/or add clustering information for any ledger as follows. In
all cases, the information should be submitted via a Github PR.

Information about legal links between entities is defined in
`src/helpers/legal_links.json`. This file defines information for all supported
ledgers. For a specific description on how to add information see
[here](https://github.com/Blockchain-Technology-Lab/pooling-analysis/tree/main/src/helpers).

Information about entities of a specific ledger is defined in
`src/helpers/pool_information`. For every supported ledger, there exists a
distinct file `src/helpers/pool_information/<project name>.json`. For a
specific description on how to add information see
[here](https://github.com/Blockchain-Technology-Lab/pooling-analysis/tree/main/src/helpers/pool_information).

### Support for ledgers

You can add support for an extra ledger, which is not already supported, as
follows.

In the directory `helpers/pool_information` store a file named `<project_name>.json` that contains the relevant pool
information (see the [mapping documentation](https://blockchain-technology-lab.github.io/pooling-analysis/mappings/)
for details on the file's structure).

In the directory `parsers` create a file named `<project_name>_parser.py` and a corresponding class, or reuse an
existing parser if fit for purpose. The class should inherit from the `DefaultParser` class of `default_parser.py`
and override its `parse` method.

In the directory `mappings` create a file named `<project_name>_mapping.py` and a corresponding class, or reuse an
existing mapping. The class should inherit from the `Mapping` class of `mapping.py` and override its `process` method,
which takes as input a time period in the form `yyyy-mm-dd` (e.g., '2022' for the year 2022, '2022-11' for the month
November 2022, '2022-11-12' for the day 12 November 2022) and returns a dictionary of the form
`{'<entity name>': <number of resources>}` and outputs a csv file of mapped data.

In the script `src/parse.py`, import the parser class and assign it to the project's name in the
dictionary `ledger_parser`. Do the same in the script `src/map.py` for the
mapping class in the dictionary `ledger_mapping`.
Note: You should provide an entry in the `ledger_mapping` and `ledger_parser` regardless of whether you are using a new or existing mapping or parser.

To add a new metric, create a relevant script in `metrics`, then import and run the metric function in the script `src/analyze.py`.

## License

The code of this repository is released under the [MIT License](https://github.com/Blockchain-Technology-Lab/pooling-analysis/blob/main/LICENSE).
The documentation pages are released under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
