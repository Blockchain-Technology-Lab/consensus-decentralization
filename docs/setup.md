# Setup

## Installation

To install the pooling analysis tool, simply clone this GitHub repository:

    git clone https://github.com/Blockchain-Technology-Lab/pooling-analysis.git

The tool is written in Python 3, therefore a Python 3 interpreter is required in order to run it locally.

The [requirements file](requirements.txt) lists the dependencies of the project.
Make sure you have all of them installed before running the scripts. To install
all of them in one go, run the following command from the root directory of the
project:

    python -m pip install -r requirements.txt


## Execution

The pooling analysis tool is a CLI tool.
The `run.py` script in the root directory of the project invokes the required parsers, mappings and metrics, but it is
also possible to execute each module individually. The following process describes the most typical workflow.

Place all raw data (which could be collected from BigQuery for example; see [Data Collection](data.md) for more details)
in the `input` directory, each file named as `<project_name>_raw_data.json` (e.g., `bitcoin_raw_data.json`). By default,
there is a (very small) sample input file for some supported projects; to use it, remove the prefix `sample_`.

Run `python run.py --ledgers <ledger_1> <ledger_n> --timeframe <timeframe>` to
analyze the n specified ledgers for the given timeframe.
Both arguments are optional, so it's possible to omit one or both of them; in this case, the default values
will be used. Specifically:

- `ledgers` accepts any number of the supported ledgers (case-insensitive). For example, `--ledgers bitcoin`
would run the analysis for Bitcoin, while `--ledgers Bitcoin Ethereum Cardano` would run the analysis for Bitcoin,
Ethereum and Cardano. If the `ledgers` argument is omitted, then all supported ledgers are analyzed.
- The `timeframe` argument should be of the form `YYYY-MM-DD` (month and day can be omitted). For example,
`--timeframe 2022` would run the analysis for the year 2022, while `--timeframe 2022-02` would do it for the month of
February 2022. If the `timeframe` argument is omitted, then a monthly analysis is performed for each month between
January 2018 and the current month.

The script will print the output of each implemented metric for the specified ledgers and timeframe.
All output files can then be found under the `output` directory, which is automatically created the first time the tool is run.
