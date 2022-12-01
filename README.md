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

## Execute

First, store the data and pool information files as needed (see below).

To produce a csv of the data for analysis, run `python process.py <project_name> <timeframe>`.

To mass produce and analyze data for various ledgers, run `python analyze.py` (possibly after making relevant changes).

## Development

To add a new project, first create a folder in the `ledgers` directory named as the project (e.g., `bitcoin`, `ethereum`, etc).

### Data Parsing

In the ledger project's directory, store a file named `data.json` structured as follows:

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

### Data Mapping

Create a mapping in the `mappings` folder, or reuse an existing one. 

The mapping should define a function `process` that takes as inputs:
- a json file of parsed data (structured as above)
- a time period in the form `yyyy-mm-dd`, e.g., '2022' for the year 2022, '2022-11' for the month November 2022,  '2022-11-12' for the year 12 November 2022, 

The function returns a dictionary of the form `{'<entity name>': <number of resources>}` and outputs a csv file of the form `Entity,Resources` of the distribution of resources to entities in the defined time period.

To assist the mapping, in the project's directory store a file named `pools.json`, with relevant pool information, structured as follows:

```
{
  "legal_links": {
      "<year>": {
          "<name of pool>": "<name of parent company>"
      }
  },
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
- `legal_links` refers to well-known links between pools (e.g., owned by the same company)
- `coinbase_address_links` refers to pools with shared coinbase addresses (i.e., two blocks created by the pools with common coinbase addresses)
- `<pool tag>` is the tag that a pool inserts in a block's coinbase parameter (to claim a block as being mined by the pool)

## Example data

The queries for Bitcoin, Bitcoin Cash, Dogecoin, Litecoin, Zcash return data that should be parsed using the `bitcoin` parser in `parsers`. The rest return data that is already in the necessary parsed form.

### Bitcoin

Sample Bitcoin data are available [here](https://drive.google.com/file/d/1IyLNi2_qvxWj0SQ_S0ZKxqMgwuBk6mRF/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_bitcoin.transactions`.outputs
FROM `bigquery-public-data.crypto_bitcoin.transactions`
JOIN `bigquery-public-data.crypto_bitcoin.blocks` ON `bigquery-public-data.crypto_bitcoin.transactions`.block_number = `bigquery-public-data.crypto_bitcoin.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2017-12-31'
```

### Ethereum

Sample Ethereum data are available [here](https://drive.google.com/file/d/1UEDsoz1Q2njR-pd6TO0ZLQBXFcV3T--4/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT number, timestamp, miner as coinbase_addresses, extra_data as coinbase_param
FROM `bigquery-public-data.crypto_ethereum.blocks`
WHERE timestamp > '2018-12-31'
```

### Bitcoin Cash

Sample Bitcoin Cash data are available [here](https://drive.google.com/file/d/1klKbtWESX4Zga_NoZhPxEEolV6lf02_j/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_bitcoin_cash.transactions`.outputs
FROM `bigquery-public-data.crypto_bitcoin_cash.transactions`
JOIN `bigquery-public-data.crypto_bitcoin_cash.blocks` ON `bigquery-public-data.crypto_bitcoin_cash.transactions`.block_number = `bigquery-public-data.crypto_bitcoin_cash.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2018-12-31'
```

### Dogecoin

Sample Dogecoin data are available [here](https://drive.google.com/file/d/1m51Zh7hM2nj9qykrzxfN8JEM0-DLqELa/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_dogecoin.transactions`.outputs
FROM `bigquery-public-data.crypto_dogecoin.transactions`
JOIN `bigquery-public-data.crypto_dogecoin.blocks` ON `bigquery-public-data.crypto_dogecoin.transactions`.block_number = `bigquery-public-data.crypto_dogecoin.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2019-12-31'
```

### Cardano

Sample Cardano data are available [here](https://drive.google.com/file/d/17aT9Yh-WfmErYHvp1GdffcDmDeHa3Zn3/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT `iog-data-analytics.cardano_mainnet.block`.slot_no as number, `iog-data-analytics.cardano_mainnet.pool_offline_data`.pool_hash as coinbase_addresses, `iog-data-analytics.cardano_mainnet.pool_offline_data`.ticker_name as coinbase_param, `iog-data-analytics.cardano_mainnet.block`.block_time as timestamp
FROM `iog-data-analytics.cardano_mainnet.block`
JOIN `iog-data-analytics.cardano_mainnet.pool_offline_data` ON `iog-data-analytics.cardano_mainnet.block`.pool_hash = `iog-data-analytics.cardano_mainnet.pool_offline_data`.pool_hash
WHERE `iog-data-analytics.cardano_mainnet.block`.epoch_no > 256 -- 31 March 2021 (start of epoch 257) was the first time with 100% decentralized block production: https://twitter.com/InputOutputHK/status/1377376420540735489
```

### Litecoin

Sample Litecoin data are available [here](https://drive.google.com/file/d/1iaK1Pfkvc9EoArOv2vyXiAq7UdbLfXYQ/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_litecoin.transactions`.outputs
FROM `bigquery-public-data.crypto_litecoin.transactions`
JOIN `bigquery-public-data.crypto_litecoin.blocks` ON `bigquery-public-data.crypto_litecoin.transactions`.block_number = `bigquery-public-data.crypto_litecoin.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2018-12-31'
```

### Zcash

Sample Zcash data are available [here](https://drive.google.com/file/d/1oMLnCcG4W79wLaMSpCQImp0EvKKWGZ7P/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number as number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_zcash.transactions`.outputs
FROM `bigquery-public-data.crypto_zcash.transactions`
JOIN `bigquery-public-data.crypto_zcash.blocks` ON `bigquery-public-data.crypto_zcash.transactions`.block_number = `bigquery-public-data.crypto_zcash.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2018-12-31'
```

### Tezos

Sample Tezos data are available [here](https://drive.google.com/file/d/15_ZPb6l9JC3YilPv6tyzPqIztEAK-iYk/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT level as number, timestamp, baker as coinbase_addresses
FROM `public-data-finance.crypto_tezos.blocks`
WHERE timestamp > '2020-12-31'
```
