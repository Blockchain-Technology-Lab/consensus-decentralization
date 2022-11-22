# Pooling Analysis

This repository provides scripts for analysing pooling behaviour in various blockchains.

Currently the supported cryptocurrencies are:
- Bitcoin
- Ethereum
- Bitcoin Cash
- Dogecoin
- Cardano
- Ethereum Classic
- Litecoin
- Zcash

## Execute

To run an analysis:
- set the appropriate flags in `config.py`
- run `make parse` to generate the parsed data
- run `make` to analyse the data and output the results

## Development

To add a new project, you should do the following.

Create a parser in the `parsers` folder, or reuse an existing one. The parser should define a function `parse_raw_data` with outputs a json file, in the project's directory named `parsed_data.json`, as follows:

```
{
    "block_data": [
        {
            "number": "<block's number>",
            "timestamp": "<block's timestamp of the form: yyyy-mm-dd hh:mm:ss UTC>",
            "creator": "<name of the block's creator>",
            "coinbase_addresses": [
                "<address>"
            ]
        }
    ],
    "addresses_in_multiple_pools": {
        "<year>": {
            "<address>": [
                "<pool name>"
            ]
    }
}
```

In `analyse.py`, import the project's `parse_raw_data` function and define it in the `parse_functions` dictionary.

In `Makefile`, add the relevant entries (similar as the existing projects).

Create a folder named as the project (e.g., `bitcoin`, `ethereum`, etc). The project folder should define a json file, `pools.json`,  with pool information as follows.

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
  }
}
```

## Example data

### Bitcoin

Bitcoin data between 2018-2022 are available [here](https://drive.google.com/file/d/1D4Q0o5nARvUvTinSNcIt3yxwjZko-Twn/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_bitcoin.transactions`.outputs
FROM  `bigquery-public-data.crypto_bitcoin.transactions`
JOIN  `bigquery-public-data.crypto_bitcoin.blocks` ON `bigquery-public-data.crypto_bitcoin.transactions`.block_number = `bigquery-public-data.crypto_bitcoin.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2017-12-31'
```

### Ethereum

Ethereum data between 2019-2022 are available [here](https://drive.google.com/file/d/1yh0hX_0_VesGxqraPd-qM1aSVNMqH63w/view).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT number, timestamp, miner, extra_data
FROM  `bigquery-public-data.crypto_ethereum.blocks`
WHERE timestamp > '2018-12-31'
```

### Bitcoin Cash

Bitcoin Cash data between 2019-2022 are available [here](https://drive.google.com/file/d/1ufi1BikyJ57RAagScayo8F_WcdHqScf8/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_bitcoin_cash.transactions`.outputs
FROM  `bigquery-public-data.crypto_bitcoin_cash.transactions`
JOIN  `bigquery-public-data.crypto_bitcoin_cash.blocks` ON `bigquery-public-data.crypto_bitcoin_cash.transactions`.block_number = `bigquery-public-data.crypto_bitcoin_cash.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2018-12-31'
```

### Dogecoin

Dogecoin data between 2019-2022 are available [here](https://drive.google.com/file/d/1twiMtddYK7CMFdDUdPuKq5nfcERt_wrd/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_dogecoin.transactions`.outputs
FROM  `bigquery-public-data.crypto_dogecoin.transactions`
JOIN  `bigquery-public-data.crypto_dogecoin.blocks` ON `bigquery-public-data.crypto_dogecoin.transactions`.block_number = `bigquery-public-data.crypto_dogecoin.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2019-12-31'
```

### Cardano

Cardano data from April 2021 are available [here](https://drive.google.com/file/d/1pkuciKw0zFsOHpCAP4BURcJg-WM-VdmQ/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT `iog-data-analytics.cardano_mainnet.block`.epoch_no, `iog-data-analytics.cardano_mainnet.block`.slot_no, `iog-data-analytics.cardano_mainnet.pool_offline_data`.pool_hash, `iog-data-analytics.cardano_mainnet.pool_offline_data`.ticker_name, `iog-data-analytics.cardano_mainnet.pool_offline_data`.metadata_url, `iog-data-analytics.cardano_mainnet.block`.block_time
FROM  `iog-data-analytics.cardano_mainnet.block`
JOIN  `iog-data-analytics.cardano_mainnet.pool_offline_data` ON `iog-data-analytics.cardano_mainnet.block`.pool_hash = `iog-data-analytics.cardano_mainnet.pool_offline_data`.pool_hash
WHERE `iog-data-analytics.cardano_mainnet.block`.epoch_no > 256 -- 31 March 2021 (start of epoch 257) was the first time with 100% decentralized block production: https://twitter.com/InputOutputHK/status/1377376420540735489
```

### Ethereum Classic

Ethereum Classic data between 2019-2022 are available [here](https://drive.google.com/file/d/1FbOJT8fMOFC1grm3l1vlNfIHgI6psHnR/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT number, timestamp, miner, extra_data
FROM  `bigquery-public-data.crypto_ethereum_classic.blocks`
WHERE timestamp > '2018-12-31'
```

### Litecoin

Litecoin data between 2019-2022 are available [here](https://drive.google.com/file/d/19UURIwOKM45aLXX3M1lU4VHqGxJ1-NwU/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_litecoin.transactions`.outputs
FROM  `bigquery-public-data.crypto_litecoin.transactions`
JOIN  `bigquery-public-data.crypto_litecoin.blocks` ON `bigquery-public-data.crypto_litecoin.transactions`.block_number = `bigquery-public-data.crypto_litecoin.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2018-12-31'
```

### Zcash

Zcash data between 2019-2022 are available [here](https://drive.google.com/file/d/1ede9TbCbu7eElQzNgBzHUBdAU-vpZVbC/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_zcash.transactions`.outputs
FROM  `bigquery-public-data.crypto_zcash.transactions`
JOIN  `bigquery-public-data.crypto_zcash.blocks` ON `bigquery-public-data.crypto_zcash.transactions`.block_number = `bigquery-public-data.crypto_zcash.blocks`.number
WHERE is_coinbase is TRUE
AND timestamp > '2018-12-31'
```
