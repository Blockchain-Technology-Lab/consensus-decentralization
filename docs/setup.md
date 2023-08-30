# Setup

## Installation

To install the consensus decentralization analysis tool, simply clone this GitHub repository:

    git clone https://github.com/Blockchain-Technology-Lab/consensus-decentralization.git

The tool is written in Python 3, therefore a Python 3 interpreter is required in order to run it locally.

The [requirements file](https://github.com/Blockchain-Technology-Lab/consensus-decentralization/blob/main/requirements.txt) lists 
the dependencies of the project.
Make sure you have all of them installed before running the scripts. To install
all of them in one go, run the following command from the root directory of the
project:

    python -m pip install -r requirements.txt


## Execution

The consensus decentralization analysis tool is a CLI tool.
The `run.py` script in the root directory of the project invokes the required parsers, mappings and metrics, but it is
also possible to execute each module individually. The following process describes the most typical workflow.

Place all raw data (which could be collected from BigQuery for example; see [Data Collection](data.md) for more details)
in the `raw_block_data` directory, each file named as `<project_name>_raw_data.json` (e.g., `bitcoin_raw_data.json`). By default,
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
February 2022 and `--timeframe 2022-02-03` would do it for a single day (Feburary 3rd 2022). If the `timeframe` 
argument is omitted, then a monthly analysis is performed for each month between January 2010 and the current month 
or the subset of this time period for which relevant data exists.

Additionally, there are four flags that can be used to customize an execution:

- `--force-parse` forces the re-parsing of all raw data files, even if the corresponding parsed data files already
exist. This can be useful for when raw data gets updated for some blockchain. By default, this flag is set to False and 
the tool only parses blockchain data for which no parsed data file exists.
- `--force-map` forces the re-mapping of all parsed data files, even if the corresponding mapped data files already
exist. This can be useful for when mapping info is updated for some blockchain. By default, this flag is set to False 
and the tool only performs the mapping when the relevant mapped data files do not exist.
- `--plot` enables the generation of graphs at the end of the execution. Specifically, the output of each 
implemented metric is plotted for the specified ledgers and timeframe, as well as the block production dynamics for each
specified ledger. By default, this flag is set to False and no plots are generated.
- `--animated` enables the generation of (additional) animated graphs at the end of the execution. By default, this flag
is set to False and no animated plots are generated. Note that this flag is ignored if `--plot` is set to False.


All output files can then be found under the `output` directory, which is automatically created the first time the tool
is run.
