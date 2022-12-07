# Pooling Analysis

This repository provides scripts for analyzing pooling behavior of various blockchains.

Currently the supported cryptocurrencies are:
- Bitcoin
- Ethereum
- Bitcoin Cash
- Dogecoin
- Cardano
- Litecoin
- Zcash
- Tezos
- Dash

## Architecture

The tool consists of the following modules:
- Parser
- Mapping
- Analyzer

### Parser

The parser obtains raw data from a full node, parses them and outputs a json file that contains a list of entries, each entry corresponding to a block in the chain. Specifically, the file is structured as follows:

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

The entry `coinbase_addresses` is as follows:
- `Bitcoin`, `Bitcoin Cash`, `Dogecoin`, `Litecoin`, `Zcash`, `Dash`: a string of comma-separated addresses which appear in the block's coinbase transaction with non-negative value (i.e., which are given some part of the block's fees)
- `Ethereum`: the `miner` field of the block
- `Cardano`: the hash of the pool that created the data, if defined, otherwise the empty string
- `Tezos`: the `baker` field of the block

The entry `coinbase_param` is as follows:
- `Bitcoin`, `Bitcoin Cash`, `Dogecoin`, `Litecoin`, `Zcash`, `Dash`: the field `coinbase_param` of the block's coinbase transaction
- `Ethereum`: the field `extra_data` of the block
- `Cardano`: the ticker name of the pool that created the block, if defined, otherwise the empty string
- `Tezos`: there is no such entry

### Mapping

A mapping obtains the parsed data and outputs a csv file that maps blocks to entities. Specifically, the csv file is structured as follows:
```
Entity,Resources
<name of entity>,<(int) number of blocks>
```

The csv file is named as the timeframe over which the mapping was executed (e.g., `2021-04.csv`) and is stored in the project's directory (i.e., `ledgers/<project_name>`).

The logic of the mapping depends on the type of clustering that you want to achieve. So, different mappings will output different results, even if applied on the same data.

#### Pool information

To assist the mapping process, the directory `helpers/pool_information` contains files named `<project_name>.json`, with relevant pool information, structured as follows:

```
{
  "coinbase_address_links": {
      "<year>": {
          "<name of secondary pool>": "<name of primary pool>"
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
- `coinbase_address_links` refers to pools with shared coinbase addresses:
  - in projects other than Cardano, such links appear when an address appears in two blocks that are attributed to different pools
  - in Cardano, such links exist when two pools share the same metadata
- `<pool tag>` is the tag that a pool inserts in a block's coinbase parameter, in order to claim a block as being mined by the pool
  - in projects that do not rely on the coinbase parameter (e.g., Cardano, Tezos) the tag is just the name of the pool

#### Pool ownership

The file `helpers/legal_links.json` defines legal links between pools and companies, based on off-chain information (e.g., when a company is the major stakeholder in a pool).

### Analyzer 

An analyzer gets the mapped data (see above `Mapping`). Currently, the implemented analyzers are:
- Nakamoto coefficient: outputs a tuple of the Nakamoto coefficient and the power percentage that these entities (that form the coefficient) control
- Gini coefficient: outputs a float in [0, 1]
- Entropy: outputs a real number

Each analyzer is implemented in a separate Python script in the folder `metrics`. Each script defines a function named `compute_<metric_name>`, which takes as input a dictionary of the form `{'<entity name>': <number of resources>}` and outputs the relevant metric values.

## Run

Create a directory `ledgers`; in it, create a directory `<project_name>` for each project. In `ledgers/<project_name> store the file `data.json` of parsed data (see above).

Run `python analyze.py <project_name> <timeframe>` to produce a csv of the mapped data. The timeframe argument should be of the form `YYYY-MM-DD` (month and day can be omitted). The script will also print the output of each implemented analyzer metric.

To mass produce and analyze data, you can omit one or both arguments. If only one argument is given, it can be either a project's name (so all data between 2018-2022 for the given project will be analyzed) or a timeframe (so data for all ledgers will be analyzed for the given timeframe).

## Development

To add a new project, first create a folder in the `ledgers` directory named as the project (e.g., `bitcoin`, `ethereum`).

In the ledger project's directory, store a file named `data.json` that contains the parsed data (see above in `Parser`).

In the directory `helpers/pool_information` store a file named `<project_name>.json` that contains the relevant pool information (see above `Mapping/Pool information`).

In the directory `mappings` create a mapping script, or reuse an existing one. The script should define a function `process` that takes as inputs:
- the full path of the project's directory
- the parsed data (structured as above)
- a time period in the form `yyyy-mm-dd`, e.g., '2022' for the year 2022, '2022-11' for the month November 2022,  '2022-11-12' for the year 12 November 2022, 
and returns a dictionary of the form `{'<entity name>': <number of resources>}` and outputs a csv file of mapped data (see above `Mapping`).

In the script `analyze.py`, import the newly created `process` function and assign it to the project's name in the dictionary `ledger_mapping`.

To analyze a csv of mapped data using an existing metric, run `python <metric_name>.py <path_to_mapped_data_file>.csv`.

To add a new analyzer, create a relevant script in `analyzers` and import the analyzer function in the script `analyze.py`.

## Example data

The queries for Bitcoin, Bitcoin Cash, Dogecoin, Litecoin, Zcash, Dash return data that should be parsed using the `bitcoin` parser in `parsers`.

The query for Cardano returns data that should be parsed using the `cardano` parser in `parsers`. 

All other queries return data already in the necessary parsed form.

### Bitcoin

Sample parsed Bitcoin data are available [here](https://drive.google.com/file/d/1IyLNi2_qvxWj0SQ_S0ZKxqMgwuBk6mRF/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_bitcoin.transactions`.outputs
FROM `bigquery-public-data.crypto_bitcoin.transactions`
JOIN `bigquery-public-data.crypto_bitcoin.blocks` ON `bigquery-public-data.crypto_bitcoin.transactions`.block_number = `bigquery-public-data.crypto_bitcoin.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2017-12-31'
```

### Ethereum

Sample parsed Ethereum data are available [here](https://drive.google.com/file/d/1UEDsoz1Q2njR-pd6TO0ZLQBXFcV3T--4/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT number, timestamp, miner as coinbase_addresses, extra_data as coinbase_param
FROM `bigquery-public-data.crypto_ethereum.blocks`
WHERE timestamp > '2018-12-31'
```

### Bitcoin Cash

Sample parsed Bitcoin Cash data are available [here](https://drive.google.com/file/d/1klKbtWESX4Zga_NoZhPxEEolV6lf02_j/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_bitcoin_cash.transactions`.outputs
FROM `bigquery-public-data.crypto_bitcoin_cash.transactions`
JOIN `bigquery-public-data.crypto_bitcoin_cash.blocks` ON `bigquery-public-data.crypto_bitcoin_cash.transactions`.block_number = `bigquery-public-data.crypto_bitcoin_cash.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2018-12-31'
```

### Dogecoin

Sample parsed Dogecoin data are available [here](https://drive.google.com/file/d/1m51Zh7hM2nj9qykrzxfN8JEM0-DLqELa/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_dogecoin.transactions`.outputs
FROM `bigquery-public-data.crypto_dogecoin.transactions`
JOIN `bigquery-public-data.crypto_dogecoin.blocks` ON `bigquery-public-data.crypto_dogecoin.transactions`.block_number = `bigquery-public-data.crypto_dogecoin.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2019-12-31'
```

### Cardano

Sample parsed Cardano data are available [here](https://drive.google.com/file/d/1V97Vy6JMLholargAqSa4yrPsyHxeOf6U/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT `iog-data-analytics.cardano_mainnet.block`.slot_no as number, `iog-data-analytics.cardano_mainnet.pool_offline_data`.ticker_name as coinbase_param, `iog-data-analytics.cardano_mainnet.block`.block_time as timestamp, `iog-data-analytics.cardano_mainnet.block`.pool_hash
FROM `iog-data-analytics.cardano_mainnet.block` 
LEFT JOIN `iog-data-analytics.cardano_mainnet.pool_offline_data` ON `iog-data-analytics.cardano_mainnet.block`.pool_hash = `iog-data-analytics.cardano_mainnet.pool_offline_data`.pool_hash
WHERE `iog-data-analytics.cardano_mainnet.block`.block_time > '2020-12-31'
```

### Litecoin

Sample parsed Litecoin data are available [here](https://drive.google.com/file/d/1iaK1Pfkvc9EoArOv2vyXiAq7UdbLfXYQ/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_litecoin.transactions`.outputs
FROM `bigquery-public-data.crypto_litecoin.transactions`
JOIN `bigquery-public-data.crypto_litecoin.blocks` ON `bigquery-public-data.crypto_litecoin.transactions`.block_number = `bigquery-public-data.crypto_litecoin.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2018-12-31'
```

### Zcash

Sample parsed Zcash data are available [here](https://drive.google.com/file/d/1oMLnCcG4W79wLaMSpCQImp0EvKKWGZ7P/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_zcash.transactions`.outputs
FROM `bigquery-public-data.crypto_zcash.transactions`
JOIN `bigquery-public-data.crypto_zcash.blocks` ON `bigquery-public-data.crypto_zcash.transactions`.block_number = `bigquery-public-data.crypto_zcash.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2018-12-31'
```

### Tezos

Sample parsed Tezos data are available [here](https://drive.google.com/file/d/15_ZPb6l9JC3YilPv6tyzPqIztEAK-iYk/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT level as number, timestamp, baker as coinbase_addresses
FROM `public-data-finance.crypto_tezos.blocks`
WHERE timestamp > '2020-12-31'
```

### Dash

Sample parsed Dash data are available [here](https://drive.google.com/file/d/1atorp5kizjyYdQRrDCf3ps5ybiPGlZL6/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_dash.transactions`.outputs
FROM `bigquery-public-data.crypto_dash.transactions`
JOIN `bigquery-public-data.crypto_dash.blocks` ON `bigquery-public-data.crypto_dash.transactions`.block_number = `bigquery-public-data.crypto_dash.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2018-12-31'
```
