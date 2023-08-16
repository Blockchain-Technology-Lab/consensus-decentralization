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

### Support for ledgers

You can add support for a ledger that is not already supported as follows.

In the directory `mapping_information`, there exist three folders (`addresses`,
`clusters`, `identifiers`). In each folder, add a file named
`<project_name>.json`, if there exist such information for the new ledger (for
more details on what type of information each folder corresponds to see the
[mapping
documentation](https://blockchain-technology-lab.github.io/pooling-analysis/mappings/)).

In the directory `src/parsers`, create a file named `<project_name>_parser.py`,
if no existing parser can be reused. In this file create a new class, which
inherits from the `DefaultParser` class of `default_parser.py`. Then,
override its `parse` method in order to implement the new parser (or override another
method if there are only small changes needed, e.g. `parse_identifiers` if the only thing
that is different from the default parser is the way identifiers are decoded).

In the directory `src/mappings`, create a file named
`<project_name>_mapping.py`, if no existing mapping can be reused. In this file
create a new class, which inherits from the `DefaultMapping` class of `default_mapping.py`.
Then, override its `process` method. This method takes as input a time period in
the form `yyyy-mm-dd` (e.g., '2022' for the year 2022, '2022-11' for November
2022, '2022-11-12' for 12 November 2022), returns a dictionary of the form
`{'<entity name>': <number of resources>}`, and creates a csv file with the mapped
data for this timeframe in the `output` directory.

Finally, you should add support for the new ledger in the parser and mapping module scripts.
Specifically:

- in the script `src/parse.py`, import the parser class and assign it to the
  project's name in the `ledger_parser` dictionary – if no new parser class was created for
  the project, simply assign the suitable parser class (e.g. DefaultParser) to the
  project's name in the dictionary;
- in the script `src/map.py`, import the mapping class and assign it to the
  project's name in the `ledger_mapping` dictionary – if no new mapping class was created for
  the project, simply assign the suitable mapping class (e.g. DefaultMapping) to the
  project's name in the dictionary.


### Mapping information

You can update and/or add mapping information for any ledger as follows. In
all cases, the information should be submitted via a GitHub PR.

For a detailed description on how to add such information see
[here](https://github.com/Blockchain-Technology-Lab/pooling-analysis/tree/main/mapping_information/README.md).

### Metrics

To add a new metric, you should do the following steps.

First, create a relevant script in the folder `src/metrics`. The script should
include a function named `compute_{metric_name}` that, given a dictionary of
entities (as keys) to number of blocks (as values), outputs a single value (the
outcome of the metric).

Second, import this new function to `src/analyze.py`.

Finally, add the name of the metric (which should be the same as the one used in
the filename above) and any parameter values it might require to the file
`config.yaml`, under `metrics`.

## License

The code of this repository is released under the [MIT License](https://github.com/Blockchain-Technology-Lab/pooling-analysis/blob/main/LICENSE).
The documentation pages are released under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
