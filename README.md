# Pooling Analysis

This repository provides scripts for analysing pooling behaviour in various blockchains.

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
AND block_number > 501960 -- last block of 2017
```

### Ethereum

Ethereum data between 2019-2022 are available [here](https://drive.google.com/file/d/1yh0hX_0_VesGxqraPd-qM1aSVNMqH63w/view).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT number, timestamp, miner, extra_data
FROM  `bigquery-public-data.crypto_ethereum.blocks`
WHERE number > 6988614 -- last block of 2018
```

### Bitcoin Cash

Bitcoin Cash data between 2019-2022 are available [here](https://drive.google.com/file/d/1ufi1BikyJ57RAagScayo8F_WcdHqScf8/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_bitcoin_cash.transactions`.outputs
FROM  `bigquery-public-data.crypto_bitcoin_cash.transactions`
JOIN  `bigquery-public-data.crypto_bitcoin_cash.blocks` ON `bigquery-public-data.crypto_bitcoin_cash.transactions`.block_number = `bigquery-public-data.crypto_bitcoin_cash.blocks`.number
WHERE is_coinbase is TRUE
AND block_number > 563314 -- last block of 2018
```

### Dogecoin

Dogecoin data between 2019-2022 are available [here](https://drive.google.com/file/d/1twiMtddYK7CMFdDUdPuKq5nfcERt_wrd/view?usp=sharing).

They can be retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery) with the following query:

```
SELECT block_number, block_timestamp as timestamp, coinbase_param, `bigquery-public-data.crypto_dogecoin.transactions`.outputs
FROM  `bigquery-public-data.crypto_dogecoin.transactions`
JOIN  `bigquery-public-data.crypto_dogecoin.blocks` ON `bigquery-public-data.crypto_dogecoin.transactions`.block_number = `bigquery-public-data.crypto_dogecoin.blocks`.number
WHERE is_coinbase is TRUE
AND block_number > 3043796 -- last block of 2019
```
