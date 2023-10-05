# Aggregator

The aggregator obtains the mapped data of a ledger (from `output/<project_name>/mapped_data.json`), aggregates it
over the given timeframe(s) and outputs one or more `csv` files with the distribution of block to entities,
structured as follows:

```
Entity,Resources
<name of entity>,<(int) number of blocks>
```

Specifically, if the `timeframe` argument is provided during execution, then the mapping outputs a single `csv` 
file that corresponds to that timeframe. Otherwise, it outputs a `csv` file for each month contained in the default 
time range (as specified in the [config file](https://github.com/Blockchain-Technology-Lab/pooling-analysis/blob/main/config.yaml)). 
It also outputs a `csv` file for each year contained in the relevant time frames.

Each `csv` file is named after the timeframe over which the mapping was executed (e.g., `2021-04.csv`) and is
stored in a dedicated folder in the project's output directory (`output/<project_name>/blocks_per_entity/`).
