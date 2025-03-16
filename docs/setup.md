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

Run `python run.py` to run the analysis with the parameters specified in the `config.yaml` file.

The parameters that can be specified in the `config.yaml` file are:

- `metrics`: a list with the metrics that will be calculated. By default, includes all implemented metrics.
- `ledgers`: a list with the ledgers that will be analyzed. By default, includes all supported ledgers.
- `force-map`: a flag that can force the parsing, mapping and aggregation to be performed on all data, even if the
  relevant output files already exist. This can be useful for when mapping info is updated for some blockchain. By
  default, this flag is set to False and the tool only performs the mapping and aggregation when the relevant output
  files do not exist.
- `clustering`: a flag that specifies whether block producers will be clustered based on the available mapping 
  information. By default, this flag is set to True.
- `start_date`: a value of the form `YYYY-MM-DD` (month and day can be omitted), which indicates the beginning of the
  time period that will be analyzed. 
- `end_date`: a value of the form `YYYY-MM-DD` (month and day can be omitted), which indicates the end of the time
  period that will be analyzed.
- `estimation_window`: the number of days that will be used to aggregate the data. For example,
  `estimation_window 7` means that every data point will use 7 days of blocks to calculate the distribution of
  blocks to entities. If left empty, then the entire time frame will be used (only valid when combined with empty
  frequency).
- `frequency`: number of days that determines how frequently to sample the data. If left empty, then only one data
  point will be analyzed (snapshot instead of longitudinal analysis), but this is only valid when combined with an 
  empty estimation_window.
- `population_windows`: number that defines the number of windows to look back and forward when calculating the
  population of block producers. For example, `population_windows 3`, combined with `estimation_window 7` means that the 
  population of block producers will be calculated using the blocks produced in the 3 weeks before and after each 
  week under consideration. If `all` is specified, then the entire time frame will be used to determine the population.
- `plot`: a flag that enables the generation of graphs at the end of the execution. Specifically, the output of each 
implemented metric is plotted for the specified ledgers and timeframe, as well as the block production dynamics for each
specified ledger. By default, this flag is set to False and no plots are generated.
- `animated`: a flag that enables the generation of (additional) animated graphs at the end of the execution. By 
  default, this flag is set to False and no animated plots are generated. Note that this flag is ignored if `plot` is
  set to False.


All output files can then be found under the `results/` directory, which is automatically created the first time the 
tool is run. Interim files that are produced by some modules and are used by others can be found under the 
`processed_data/` directory.
