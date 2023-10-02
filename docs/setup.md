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
in the `raw_block_data/` directory, each file named as `<project_name>_raw_data.json` (e.g., `bitcoin_raw_data.json`).
By default,
there is a (very small) sample input file for some supported projects; to use it, remove the prefix `sample_`.

Run `python run.py --ledgers <ledger_1> <ledger_n> --timeframe <timeframe> --aggregate-by <unit to aggregate by>` to
analyze the n specified ledgers for the given timeframe, aggregated using the given granularity.
All arguments are optional, so it's possible to omit any of them; in this case, the default values
will be used. Specifically:

- `ledgers` accepts any number of the supported ledgers (case-insensitive). For example, `--ledgers bitcoin` 
  would run the analysis for Bitcoin, while `--ledgers Bitcoin Ethereum Cardano` would run the analysis for Bitcoin, 
  Ethereum and Cardano. If the `ledgers` argument is omitted, then the analysis is performed for the ledgers 
  specified in the `config.yaml` file, which are typically all supported ledgers.
- The `timeframe` argument accepts one or two values of the form `YYYY-MM-DD` (month and day can be
  omitted), which indicate the beginning and end of the time period that will be analyzed. For example, 
  `--timeframe 2022` would run the analysis for the year 2022 (so from January 1st 2022 to 
  December 31st 2022), while we could also get the same result using `--timeframe 2022-01 2022-12` or 
  `--timeframe 2022-01-01 2022-12-31`. Similarly, `--timeframe 2022-02` or `--timeframe 2022-02-01 2022-02-28` would 
  do it for the month of February 2022 (February 1st 2022 to February 28th 2022), while `--timeframe 2022-02-03` 
  would do it for a single day (Feburary 3rd 2022). Last, `--timeframe 2018 2022` would run the analysis for the 
  entire time period between January 1st 2018 and December 31st 2022. If the `timeframe` argument is omitted, then 
  the start date and end dates of the time frame are sourced from the `config.yaml` file.
- `aggregate_by` corresponds to the unit of time to aggregate the data by, i.e. the granularity of the analysis. 
  It can be one of: `day`, `week`, `month`, `year`, `all` and by default it is `month`. Note that in the case of 
  weekly aggregation, we consider a week to be 7 consecutive days, starting from the first day of the time period 
  under consideration (so not necessarily Monday to Sunday). If "all" is chosen, then no aggregation will be 
  performed, meaning that the given timeframe will be treated as a single unit of time in the context of our 
  analysis. In all other cases, the given timeframe will be divided into units of the given granularity and the 
  result will be a time series.

Additionally, there are three flags that can be used to customize an execution:

- `--force-map` forces the parsing, mapping and aggregation to be performed on all data, even if the relevant output
  files already exist. This can be useful for when mapping info is updated for some blockchain. By default, this flag is
  set to False and the tool only performs the mapping and aggregation when the relevant output files do not exist.
- `--plot` enables the generation of graphs at the end of the execution. Specifically, the output of each 
implemented metric is plotted for the specified ledgers and timeframe, as well as the block production dynamics for each
specified ledger. By default, this flag is set to False and no plots are generated.
- `--animated` enables the generation of (additional) animated graphs at the end of the execution. By default, this flag
is set to False and no animated plots are generated. Note that this flag is ignored if `--plot` is set to False.


All output files can then be found under the `output/` directory, which is automatically created the first time the tool
is run.
