# Pooling Analysis

This repository provides scripts for analysing pooling behaviour in various blockchains.

## Analyse

To analyse Bitcoin data, put the block data in the `bitcoin` folder as `bitcoin_data.json`.

## BigQuery

Block data are retrieved using [Google BigQuery](https://console.cloud.google.com/bigquery).

Data are also available in the following links:
- [Bitcoin data](https://drive.google.com/file/d/1-bwOew789plh4L988S_AejGJmmy4Zlrn/view)
- [Ethereum data](https://drive.google.com/file/d/1yh0hX_0_VesGxqraPd-qM1aSVNMqH63w/view)

### Example queries:

```
SELECT *
FROM  `bigquery-public-data.crypto_bitcoin.transactions`
JOIN  `bigquery-public-data.crypto_bitcoin.blocks` ON `bigquery-public-data.crypto_bitcoin.transactions`.block_number = `bigquery-public-data.crypto_bitcoin.blocks`.number
WHERE is_coinbase is TRUE
AND block_number > 501960 -- last block of 2017 for Bitcoin
```

```
SELECT number, timestamp, miner, extra_data
FROM  `bigquery-public-data.crypto_ethereum.blocks`
WHERE number > 6988614 -- last block of 2018
```
