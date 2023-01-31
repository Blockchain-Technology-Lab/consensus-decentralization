# Pooling Analysis

This repository provides a tool for analyzing pooling behavior of various blockchains and measuring their subsequent
decentralization levels.

Currently, the supported chains are:
- Bitcoin
- Bitcoin Cash
- Cardano
- Dash
- Dogecoin
- Ethereum 
- Litecoin
- Tezos
- Zcash

## Architecture

The tool consists of the following modules:
- Parser
- Mapping
- Metrics

### Parser

The parser obtains raw data from a full node, parses them and outputs a `json` file that contains a list of entries, 
each entry corresponding to a block in the chain. Specifically, the input file should be placed in the `input` directory 
and named as `<project_name>_raw_data.json` and the output file is saved under `output/<project_name>/parsed_data.json`, 
and it is structured as follows:

```
[
    {
        "number": "<block's number>",
        "timestamp": "<block's timestamp of the form: yyyy-mm-dd hh:mm:ss UTC>",
        "coinbase_addresses": "<address1>,<address2>"
        "coinbase_param": "<coinbase parameter>"
    }
]
```
While `number` and `timestamp` are consistent among different blockchains, the exact information that is included in 
`coinbase_addresses` and `coinbase_param` may vary. Specifically, the field `coinbase_addresses` corresponds to:
- `Bitcoin`, `Bitcoin Cash`, `Dogecoin`, `Litecoin`, `Zcash`, `Dash`: a string of comma-separated addresses which appear 
in the block's coinbase transaction with non-negative value (i.e., which are given some part of the block's fees)
- `Ethereum`: the `miner` field of the block
- `Cardano`: the hash of the pool that created the data, if defined, otherwise the empty string
- `Tezos`: the `baker` field of the block.

And the field `coinbase_param` corresponds to:
- `Bitcoin`, `Bitcoin Cash`, `Dogecoin`, `Litecoin`, `Zcash`, `Dash`: the field `coinbase_param` of the block's coinbase 
transaction
- `Ethereum`: the field `extra_data` of the block
- `Cardano`: the ticker name of the pool that created the block, if defined, otherwise an empty string
- `Tezos`: there is no such field.

### Mapping

The mapping obtains the parsed data (from `output/<project_name>/parsed_data.json`) and outputs a `csv` file that maps 
blocks to entities. Specifically, the `csv` file is structured as follows:
```
Entity,Resources
<name of entity>,<(int) number of blocks>
```

The `csv` file is named as the timeframe over which the mapping was executed (e.g., `2021-04.csv`) and is stored in the 
project's output directory (i.e., `output/<project_name>`).

The logic of the mapping depends on the type of clustering we want to achieve. So, different mappings will output 
different results, even if applied on the same data. 

#### Pool Information

To assist the mapping process, the directory `helpers/pool_information` contains files named `<project_name>.json`, with 
relevant pool information, structured as follows:

```
{
  "clusters": {
    "<year>": {
      "<cluster name>": [
        ["<pool name>", "<source of information>"]
      ]
    }
  },
  "coinbase_tags": {
    "<pool tag>": {
      "name": "<pool name>",
      "link": "<pool website>"
    }
  },
  "pool_addresses: {
      "<year>" {
          "<address>": "<pool name>"
      }
  }
}
```

In this file:
- `clusters` refers to pools with shared coinbase addresses:
  - instead of `<year>`, use the keyword `all` for clusters across years
  - in projects other than Cardano, such links appear when an address appears in two blocks that are attributed to 
different pools
  - in Cardano, such links exist when two pools share the same metadata
  - the `<source of information>` should be comma-separated keywords (e.g., "homepage", "shared block", etc) or a url with the clustering information; this information should be reprodusible (a link to a community or company with information that cannot be verified independently is not acceptable)
- `<pool tag>` is the tag that a pool inserts in a block's coinbase parameter, in order to claim a block as being mined 
by the pool
  - in projects that do not rely on the coinbase parameter (e.g., Cardano, Tezos) the tag is just the name of the pool

#### Pool Ownership

The file `helpers/legal_links.json` defines legal links between pools and companies, based on off-chain information 
(e.g., when a company is the major stakeholder in a pool).

### Metrics 

A metric gets the mapped data (see above `Mapping`) and outputs a relevant value as follows:
- Nakamoto coefficient: outputs a tuple of the Nakamoto coefficient and the power percentage that these entities 
(that form the coefficient) control
- Gini coefficient: outputs a decimal number in [0,1]
- Entropy: outputs a real number

Each metric is implemented in a separate Python script in the folder `metrics`. Each script defines a function named `
compute_<metric_name>`, which takes as input a dictionary of the form `{'<entity name>': <number of resources>}` and 
outputs the relevant metric values.

## Installing and running the tool

To install the pooling analysis tool, simply clone this project:

    git clone https://github.com/Blockchain-Technology-Lab/pooling-analysis.git

Take note of the [requirements file](requirements.txt), which lists the dependencies of the project, and make
sure you have all of them installed before running the scripts. To install all of them in one go, you can run the 
following command from the root directory of the project:

    python -m pip install -r requirements.txt


Place all raw data (which could be collected from BigQuery for example) in the `input` directory, each file named as 
`<project_name>_raw_data.json` (e.g. `bitcoin_raw_data.json`). By default, there is a (very small) sample input file 
for some supported projects; to use it, remove the prefix `sample_`. For more extended raw data see the links below.

Run `python run.py <project_name> <timeframe>` to produce a csv of the mapped data. The timeframe argument should be of 
the form `YYYY-MM-DD` (month and day can be omitted). The script will also print the output of each implemented metric.

To mass produce and analyze data, you can omit one or both arguments. If only one argument is given, it can be either a 
project's name (so all data between 2018-2022 for the given project will be analyzed) or a timeframe (so data for all 
ledgers will be analyzed for the given timeframe).

Three files `nc.csv`, `gini.csv`, `entropy.csv` are also created in the root directory, containing the data from the 
last execution of `run.py`.

## Contributing

To add a new project, first store the raw data under `input/<project_name>_raw_data.json`. 

In the directory `helpers/pool_information` store a file named `<project_name>.json` that contains the relevant pool 
information (see above `Pool Information`).

In the directory `parsers` create a file named `<project_name>_parser.py` and a corresponding class, or reuse an 
existing parser if it is fit for purpose. The class should inherit from the `DefaultParser` class of `default_parser.py`
and override its `parse` method.

In the directory `mappings` create a file named `<project_name>_mapping.py` and a corresponding class, or reuse an 
existing mapping. The class should inherit from the `Mapping` class of `mapping.py` and override its `process` method, 
which takes as input a time period in the form `yyyy-mm-dd`, e.g., '2022' for the year 2022, '2022-11' for the month 
November 2022, '2022-11-12' for the day 12 November 2022, and returns a dictionary of the form 
`{'<entity name>': <number of resources>}` and outputs a csv file of mapped data - (see above `Mapping`).

In the script `run.py`, import the newly created parser and mapping classes and assign them to the project's name in the 
dictionary `ledger_mapping` and `ledger_parser`. Note that you should provide an entry in the `ledger_mapping` and
`ledger_parser` regardless of whether you are using a new or existing mapping or parser.

To analyze a csv of mapped data using an existing metric, run `python <metric_name>.py <path_to_mapped_data_file>.csv`.

To add a new metric, create a relevant script in `metrics` and import the metric function in the script `run.py`.

## Example data

The queries for Bitcoin, Bitcoin Cash, Dogecoin, Litecoin, Zcash, Dash return data that are parsed using the 
`default_parser` script in `parsers`.

The query for Cardano returns data that is parsed using the `cardano_parser` script in `parsers`. 

All other queries return data already in the necessary parsed form, so they are parsed using a "dummy" parser.

Note that when saving results from BigQuery you should select the option "JSONL (newline delimited)".


### Bitcoin

Sample raw Bitcoin data are available
[here](https://drive.google.com/file/d/12sd6xn8aZE5yBrUFoxE6vVPFIuE_Sw4F/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_bitcoin.transactions`.outputs
FROM `bigquery-public-data.crypto_bitcoin.transactions`
JOIN `bigquery-public-data.crypto_bitcoin.blocks` ON `bigquery-public-data.crypto_bitcoin.transactions`.block_number = `bigquery-public-data.crypto_bitcoin.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2017-12-31'
```

### Ethereum

Sample raw Ethereum data are available
[here](https://drive.google.com/file/d/1i9veHVB8nuitXMXWxk3oTOXY6rI_Ex8a/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT number, timestamp, miner as coinbase_addresses, extra_data as coinbase_param
FROM `bigquery-public-data.crypto_ethereum.blocks`
WHERE timestamp > '2018-12-31'
```

### Bitcoin Cash

Sample raw Bitcoin Cash data are available
[here](https://drive.google.com/file/d/1560i6dbicv5h8bqcYMIPNKZTMgT44qNE/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_bitcoin_cash.transactions`.outputs
FROM `bigquery-public-data.crypto_bitcoin_cash.transactions`
JOIN `bigquery-public-data.crypto_bitcoin_cash.blocks` ON `bigquery-public-data.crypto_bitcoin_cash.transactions`.block_number = `bigquery-public-data.crypto_bitcoin_cash.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2018-12-31'
```

### Dogecoin

Sample raw Dogecoin data are available
[here](https://drive.google.com/file/d/1eVHop4ciT0f8veLiy2nEd61AeC1iyd-1/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_dogecoin.transactions`.outputs
FROM `bigquery-public-data.crypto_dogecoin.transactions`
JOIN `bigquery-public-data.crypto_dogecoin.blocks` ON `bigquery-public-data.crypto_dogecoin.transactions`.block_number = `bigquery-public-data.crypto_dogecoin.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2019-12-31'
```

### Cardano

Sample raw Cardano data are available
[here](https://drive.google.com/file/d/1qetBLr7sHccnoTbVTD_t_bCOeWfIjH3D/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT `iog-data-analytics.cardano_mainnet.block`.slot_no as number, `iog-data-analytics.cardano_mainnet.pool_offline_data`.ticker_name as coinbase_param, `iog-data-analytics.cardano_mainnet.block`.block_time as timestamp, `iog-data-analytics.cardano_mainnet.block`.pool_hash
FROM `iog-data-analytics.cardano_mainnet.block` 
LEFT JOIN `iog-data-analytics.cardano_mainnet.pool_offline_data` ON `iog-data-analytics.cardano_mainnet.block`.pool_hash = `iog-data-analytics.cardano_mainnet.pool_offline_data`.pool_hash
WHERE `iog-data-analytics.cardano_mainnet.block`.block_time > '2020-12-31'
```

### Litecoin

Sample raw Litecoin data are available
[here](https://drive.google.com/file/d/1XR8t0NZ9IfuBBzCGyBw8c_nFyFjSsxd7/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_litecoin.transactions`.outputs
FROM `bigquery-public-data.crypto_litecoin.transactions`
JOIN `bigquery-public-data.crypto_litecoin.blocks` ON `bigquery-public-data.crypto_litecoin.transactions`.block_number = `bigquery-public-data.crypto_litecoin.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2018-12-31'
```

### Zcash

Sample raw Zcash data are available
[here](https://drive.google.com/file/d/1WEkUAaIaRsGXuemAZj_DbNIlhkWtOn5A/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_zcash.transactions`.outputs
FROM `bigquery-public-data.crypto_zcash.transactions`
JOIN `bigquery-public-data.crypto_zcash.blocks` ON `bigquery-public-data.crypto_zcash.transactions`.block_number = `bigquery-public-data.crypto_zcash.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2018-12-31'
```

### Tezos

Sample raw Tezos data are available
[here](https://drive.google.com/file/d/1Jn4A2hxanwniiexzHySFa6CFU8aS03mB/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT level as number, timestamp, baker as coinbase_addresses
FROM `public-data-finance.crypto_tezos.blocks`
WHERE timestamp > '2020-12-31'
```

### Dash

Sample raw Dash data are available
[here](https://drive.google.com/file/d/1DkjAZ7hq45zIan278NA6KVv3B45OG9GU/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_dash.transactions`.outputs
FROM `bigquery-public-data.crypto_dash.transactions`
JOIN `bigquery-public-data.crypto_dash.blocks` ON `bigquery-public-data.crypto_dash.transactions`.block_number = `bigquery-public-data.crypto_dash.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2018-12-31'
```
